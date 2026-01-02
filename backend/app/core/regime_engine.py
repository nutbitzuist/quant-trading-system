"""
Regime Engine (Layer 1)
Detects market regime (BULL/BEAR/SIDEWAYS) and volatility conditions
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import pandas as pd
import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM
from app.api.routes.diagnostics import log_event

from app.models.base import Regime, VolatilityRegime, RegimeState, WEIGHT_MATRIX


@dataclass
class BreadthData:
    """Market breadth indicators"""
    pct_above_50ma: float
    pct_above_200ma: float
    new_highs: int
    new_lows: int
    advance_decline_ratio: float


class RegimeEngine:
    """
    Master Regime Detection System
    
    Combines multiple regime indicators into a unified view:
    1. Trend regime: BULL, BEAR, SIDEWAYS
    2. Volatility regime: LOW, NORMAL, HIGH, SPIKE
    
    The regime determines:
    - Which models to activate
    - What weights to apply to each model
    - Position sizing multiplier
    """
    
    # Model activation by regime
    MODEL_ACTIVATION = {
        Regime.BULL: [
            "hqm", "clenow", "dual_momentum", "roc_multi", "52w_high",  # Momentum
            "adx", "multi_ema", "supertrend", "ichimoku", "psar",       # Trend
            "garp", "magic_formula",                                     # Growth-focused fundamental
        ],
        Regime.BEAR: [
            "quality", "altman_z", "dividend",                          # Defensive fundamental
            "vol_regime", "correlation", "mean_reversion",              # Risk management
            "adx", "supertrend",                                        # Trend for shorts
        ],
        Regime.SIDEWAYS: [
            "mean_reversion", "rsi_divergence",                         # Range-bound strategies
            "quality", "dividend", "garp",                              # Stable fundamentals
            "adx", "multi_ema",                                         # Trend confirmation
        ],
    }
    
    # Position sizing by volatility regime
    POSITION_MULTIPLIERS = {
        VolatilityRegime.LOW: 1.25,
        VolatilityRegime.NORMAL: 1.0,
        VolatilityRegime.HIGH: 0.5,
        VolatilityRegime.SPIKE: 0.25,
    }
    
    def __init__(
        self,
        trend_lookback: int = 50,
        vol_lookback: int = 20,
        vol_history: int = 252,
    ):
        """
        Initialize regime engine.
        
        Args:
            trend_lookback: Days to look back for trend detection
            vol_lookback: Days for current volatility calculation
            vol_history: Days of vol history for percentile
        """
        self.trend_lookback = trend_lookback
        self.vol_lookback = vol_lookback
        self.vol_history = vol_history
        self.hmm_model = None
        self.hmm_states_map = {} # Map state_id -> Regime (0 -> BEAR, 1 -> BULL)
    
    def _train_hmm(self, prices: pd.Series) -> bool:
        """Train Gaussian HMM on historical data."""
        try:
            # Prepare data: Returns and Volatility
            returns = prices.pct_change().dropna()
            vol = returns.rolling(10).std().dropna()
            
            # Align indices
            common = returns.index.intersection(vol.index)
            data = pd.DataFrame({
                'returns': returns.loc[common],
                'vol': vol.loc[common]
            })
            
            # Observations matrix
            X = data.values
            
            # Train model
            self.hmm_model = GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
            self.hmm_model.fit(X)
            
            # Identify states
            means = self.hmm_model.means_
            # means[:, 0] is returns mean
            # Sort states by return mean
            state_order = np.argsort(means[:, 0])
            
            # Map: Lowest return = BEAR, Middle = SIDEWAYS, Highest = BULL
            self.hmm_states_map = {
                state_order[0]: Regime.BEAR,
                state_order[1]: Regime.SIDEWAYS,
                state_order[2]: Regime.BULL
            }
            
            log_event("info", f"HMM Trained. States: {self.hmm_states_map}")
            return True
            
        except Exception as e:
            log_event("error", f"HMM Training failed: {e}")
            return False

    def _predict_hmm_regime(self, prices: pd.Series) -> Tuple[Regime, float]:
        """Predict current regime using HMM."""
        if self.hmm_model is None:
            # Train on available history
            success = self._train_hmm(prices)
            if not success:
                return Regime.SIDEWAYS, 0.0
        
        try:
            # Prepare recent data sequence
            returns = prices.pct_change().dropna()
            vol = returns.rolling(10).std().dropna()
            common = returns.index.intersection(vol.index)
            
            # Use last 50 days to predict current state path
            recent = common[-50:]
            X = pd.DataFrame({
                'returns': returns.loc[recent],
                'vol': vol.loc[recent]
            }).values
            
            hidden_states = self.hmm_model.predict(X)
            current_state = hidden_states[-1]
            
            regime = self.hmm_states_map.get(current_state, Regime.SIDEWAYS)
            
            # Confidence based on posterior probability
            posteriors = self.hmm_model.predict_proba(X)
            confidence = posteriors[-1][current_state]
            
            return regime, round(confidence, 2)
            
        except Exception as e:
            log_event("error", f"HMM Prediction failed: {e}")
            return Regime.SIDEWAYS, 0.0
    
    def detect_regime(
        self,
        market_data: pd.DataFrame,
        universe_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> RegimeState:
        """
        Detect current market regime.
        
        Args:
            market_data: SET Index data with OHLCV columns
            universe_data: Optional dict of ticker -> price data for breadth
            
        Returns:
            RegimeState with trend, volatility, active models, weights
        """
        # Try HMM Detection first (Primary)
        # We need historical data for HMM. 
        # market_data provided here might be short (just OHLCV).
        # We implicitly assume market_data has enough history (e.g. 1 year+)
        
        hmm_regime = Regime.SIDEWAYS
        hmm_conf = 0.0
        
        if len(market_data) > 200:
            hmm_regime, hmm_conf = self._predict_hmm_regime(market_data['close'])
            trend_regime = hmm_regime
            trend_confidence = hmm_conf
        else:
            # Fallback to Rule-based if not enough data
            trend_regime, trend_confidence = self._detect_trend_regime(market_data)
        
        # Detect volatility regime
        vol_regime, vol_data = self._detect_volatility_regime(market_data)
        
        # Optional: Calculate breadth if universe data provided
        if universe_data:
            breadth = self._calculate_breadth(universe_data)
            # Adjust trend confidence based on breadth
            if breadth.pct_above_50ma > 70:
                trend_confidence = min(1.0, trend_confidence + 0.1)
            elif breadth.pct_above_50ma < 30:
                trend_confidence = min(1.0, trend_confidence + 0.1)
        
        # Get active models for this regime
        active_models = self._get_active_models(trend_regime)
        
        # Calculate weights for each model
        model_weights = self._get_model_weights(active_models, trend_regime)
        
        # Get position size multiplier
        position_multiplier = self.POSITION_MULTIPLIERS[vol_regime]
        
        return RegimeState(
            trend_regime=trend_regime,
            volatility_regime=vol_regime,
            confidence=trend_confidence,
            active_models=active_models,
            model_weights=model_weights,
            position_size_multiplier=position_multiplier
        )
    
    def _detect_trend_regime(
        self, 
        data: pd.DataFrame
    ) -> Tuple[Regime, float]:
        """
        Detect trend regime using multiple indicators.
        
        Uses:
        1. Price vs 50-day MA
        2. Price vs 200-day MA
        3. MA slope (20-day rate of change of 50-day MA)
        4. ADX-like trend strength
        
        Returns:
            Tuple of (Regime, confidence)
        """
        close = data['close']
        
        # Calculate moving averages
        ma_50 = close.rolling(50).mean()
        ma_200 = close.rolling(200).mean()
        
        # Current values
        current_price = close.iloc[-1]
        current_ma50 = ma_50.iloc[-1]
        current_ma200 = ma_200.iloc[-1]
        
        # MA slope (20-day change in 50-day MA)
        ma50_slope = (ma_50.iloc[-1] - ma_50.iloc[-20]) / ma_50.iloc[-20] * 100
        
        # Calculate returns for volatility
        returns = close.pct_change()
        recent_return = (close.iloc[-1] / close.iloc[-self.trend_lookback] - 1) * 100
        
        # Scoring system
        bull_score = 0
        bear_score = 0
        sideways_score = 0
        
        # Price above/below MAs
        if current_price > current_ma50:
            bull_score += 2
        else:
            bear_score += 2
            
        if current_price > current_ma200:
            bull_score += 2
        else:
            bear_score += 2
        
        # MA alignment (golden/death cross)
        if current_ma50 > current_ma200:
            bull_score += 1
        else:
            bear_score += 1
        
        # MA slope (trend strength)
        if ma50_slope > 2:
            bull_score += 2
        elif ma50_slope < -2:
            bear_score += 2
        else:
            sideways_score += 2
        
        # Recent return
        if recent_return > 5:
            bull_score += 1
        elif recent_return < -5:
            bear_score += 1
        else:
            sideways_score += 1
        
        # Determine regime
        total_score = bull_score + bear_score + sideways_score
        
        if bull_score >= bear_score and bull_score >= sideways_score:
            regime = Regime.BULL
            confidence = bull_score / total_score
        elif bear_score >= bull_score and bear_score >= sideways_score:
            regime = Regime.BEAR
            confidence = bear_score / total_score
        else:
            regime = Regime.SIDEWAYS
            confidence = sideways_score / total_score
        
        return regime, round(confidence, 2)
    
    def _detect_volatility_regime(
        self, 
        data: pd.DataFrame
    ) -> Tuple[VolatilityRegime, Dict]:
        """
        Detect volatility regime.
        
        Regimes based on current vol vs historical percentile:
        - LOW: < 25th percentile
        - NORMAL: 25th - 75th percentile
        - HIGH: > 75th percentile
        - SPIKE: > 90th percentile AND increased >50% in 5 days
        """
        close = data['close']
        returns = close.pct_change()
        
        # Current volatility (20-day)
        current_vol = returns.rolling(self.vol_lookback).std().iloc[-1] * np.sqrt(252)
        
        # Historical volatility for percentile
        vol_series = returns.rolling(self.vol_lookback).std() * np.sqrt(252)
        vol_history = vol_series.iloc[-self.vol_history:]
        
        # Calculate percentile
        percentile = (vol_history < current_vol).mean() * 100
        
        # Check for spike (rapid increase)
        vol_5d_ago = vol_series.iloc[-5] if len(vol_series) >= 5 else current_vol
        vol_change = (current_vol - vol_5d_ago) / vol_5d_ago if vol_5d_ago > 0 else 0
        
        # Determine regime
        if percentile > 90 and vol_change > 0.5:
            regime = VolatilityRegime.SPIKE
        elif percentile > 75:
            regime = VolatilityRegime.HIGH
        elif percentile < 25:
            regime = VolatilityRegime.LOW
        else:
            regime = VolatilityRegime.NORMAL
        
        vol_data = {
            "current_vol": round(current_vol * 100, 2),  # As percentage
            "percentile": round(percentile, 1),
            "vol_change_5d": round(vol_change * 100, 1),  # As percentage
        }
        
        return regime, vol_data
    
    def _calculate_breadth(
        self, 
        universe_data: Dict[str, pd.DataFrame]
    ) -> BreadthData:
        """
        Calculate market breadth indicators.
        
        Metrics:
        - % stocks above 50-day MA
        - % stocks above 200-day MA
        - New highs vs new lows (52-week)
        """
        above_50ma = 0
        above_200ma = 0
        new_highs = 0
        new_lows = 0
        total = len(universe_data)
        
        for ticker, data in universe_data.items():
            if len(data) < 252:
                continue
                
            close = data['close']
            current_price = close.iloc[-1]
            
            # Moving averages
            ma_50 = close.rolling(50).mean().iloc[-1]
            ma_200 = close.rolling(200).mean().iloc[-1]
            
            # 52-week high/low
            high_52w = close.iloc[-252:].max()
            low_52w = close.iloc[-252:].min()
            
            # Count
            if current_price > ma_50:
                above_50ma += 1
            if current_price > ma_200:
                above_200ma += 1
            if current_price >= high_52w * 0.98:  # Within 2% of high
                new_highs += 1
            if current_price <= low_52w * 1.02:  # Within 2% of low
                new_lows += 1
        
        pct_above_50ma = (above_50ma / total * 100) if total > 0 else 50
        pct_above_200ma = (above_200ma / total * 100) if total > 0 else 50
        adv_dec_ratio = new_highs / max(new_lows, 1)
        
        return BreadthData(
            pct_above_50ma=round(pct_above_50ma, 1),
            pct_above_200ma=round(pct_above_200ma, 1),
            new_highs=new_highs,
            new_lows=new_lows,
            advance_decline_ratio=round(adv_dec_ratio, 2)
        )
    
    def _get_active_models(self, regime: Regime) -> List[str]:
        """Get list of active models for the current regime."""
        return self.MODEL_ACTIVATION.get(regime, self.MODEL_ACTIVATION[Regime.SIDEWAYS])
    
    def _get_model_weights(
        self, 
        active_models: List[str], 
        regime: Regime
    ) -> Dict[str, float]:
        """Get weight for each active model based on regime."""
        regime_idx = {Regime.BULL: 0, Regime.BEAR: 1, Regime.SIDEWAYS: 2}
        idx = regime_idx.get(regime, 2)
        
        weights = {}
        for model in active_models:
            if model in WEIGHT_MATRIX:
                weights[model] = WEIGHT_MATRIX[model][idx]
            else:
                weights[model] = 0.5  # Default weight
        
        return weights

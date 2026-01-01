"""
HMM Regime Detection Model
Model M16 - Quantitative Category

Hidden Markov Model for market regime classification
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class HMMRegimeModel(BaseModel):
    """
    HMM Regime Detection Model
    
    Uses Hidden Markov Model concepts for regime detection.
    This is a simplified version for scoring - the full HMM
    is in regime_engine.py.
    
    Features:
        - Rolling returns
        - Rolling volatility
        - MA slope
        - Volume trend
    
    States:
        0: Bear market
        1: Neutral/Transition
        2: Bull market
    """
    
    name = "hmm_regime"
    category = "quant"
    description = "HMM Regime: Hidden Markov state classification"
    
    REGIME_PARAMS = {
        "BULL": {"lookback": 60},
        "BEAR": {"lookback": 60},
        "SIDEWAYS": {"lookback": 60},
        "NEUTRAL": {"lookback": 60},
    }
    
    def __init__(self):
        super().__init__()
    
    def get_regime_params(self, regime: str) -> Dict[str, Any]:
        return self.REGIME_PARAMS.get(regime, self.REGIME_PARAMS["NEUTRAL"])
    
    def calculate(
        self,
        prices: pd.DataFrame,
        fundamentals: Optional[Dict[str, Any]] = None,
        regime: str = "NEUTRAL"
    ) -> List[ModelResult]:
        params = self.get_regime_params(regime)
        lookback = params["lookback"]
        results = []
        
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(ticker, ticker_data, lookback, regime)
                results.append(result)
        else:
            result = self._calculate_single("STOCK", prices, lookback, regime)
            results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        data: pd.DataFrame,
        lookback: int,
        regime: str
    ) -> ModelResult:
        try:
            if len(data) < lookback:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            close = data['close']
            volume = data.get('volume', pd.Series([1]*len(data)))
            
            # Feature 1: Rolling returns
            returns = close.pct_change()
            rolling_return = returns.rolling(20).mean().iloc[-1] * 252
            
            # Feature 2: Rolling volatility
            rolling_vol = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
            
            # Feature 3: MA slope
            ma_50 = close.rolling(50).mean()
            ma_slope = (ma_50.iloc[-1] - ma_50.iloc[-20]) / ma_50.iloc[-20] if ma_50.iloc[-20] > 0 else 0
            
            # Feature 4: Volume trend
            vol_ma = volume.rolling(20).mean()
            vol_trend = vol_ma.iloc[-1] / vol_ma.iloc[-20] - 1 if vol_ma.iloc[-20] > 0 else 0
            
            # Simple state classification based on features
            bull_score = 0
            bear_score = 0
            
            # Returns signal
            if rolling_return > 0.1:
                bull_score += 25
            elif rolling_return < -0.1:
                bear_score += 25
            
            # Volatility signal (low vol = bullish)
            if rolling_vol < 0.15:
                bull_score += 15
            elif rolling_vol > 0.30:
                bear_score += 15
            
            # MA slope signal
            if ma_slope > 0.02:
                bull_score += 30
            elif ma_slope < -0.02:
                bear_score += 30
            
            # Volume confirmation
            if vol_trend > 0.1 and rolling_return > 0:
                bull_score += 10
            elif vol_trend > 0.1 and rolling_return < 0:
                bear_score += 10
            
            # Calculate final score
            if bull_score > bear_score:
                state = "BULL"
                score = 50 + bull_score
            elif bear_score > bull_score:
                state = "BEAR"
                score = 50 - bear_score
            else:
                state = "NEUTRAL"
                score = 50
            
            score = max(0, min(100, score))
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "detected_state": state,
                    "rolling_return_annual": round(rolling_return * 100, 2),
                    "rolling_volatility": round(rolling_vol * 100, 2),
                    "ma_slope_pct": round(ma_slope * 100, 2),
                    "volume_trend": round(vol_trend * 100, 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

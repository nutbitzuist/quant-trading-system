"""
ADX Trend Strength Model
Model M6 - Trend Category

Measures trend strength using Average Directional Index (ADX)
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class ADXTrendModel(BaseModel):
    """
    ADX Trend Strength Model
    
    The Average Directional Index (ADX) measures trend strength.
    Combined with +DI and -DI for trend direction.
    
    Components:
        - ADX: Trend strength (0-100)
        - +DI: Positive directional indicator
        - -DI: Negative directional indicator
    
    Interpretation:
        - ADX > 25: Strong trend
        - ADX < 20: No trend (ranging)
        - +DI > -DI: Uptrend
        - -DI > +DI: Downtrend
    
    Regime Adjustments:
        BULL: Lower ADX threshold (20) to catch emerging trends
        BEAR: Higher ADX threshold (30) for strong downtrends only
        SIDEWAYS: Focus on ADX < 20 for range-bound
    """
    
    name = "adx"
    category = "trend"
    description = "ADX Trend Strength: Trend strength 0-100 with direction"
    
    # Regime-specific parameters
    REGIME_PARAMS = {
        "BULL": {
            "period": 14,
            "trend_threshold": 20,
            "strong_trend_threshold": 30,
            "favor_direction": "UP",
        },
        "BEAR": {
            "period": 14,
            "trend_threshold": 25,
            "strong_trend_threshold": 35,
            "favor_direction": "DOWN",
        },
        "SIDEWAYS": {
            "period": 14,
            "trend_threshold": 20,
            "strong_trend_threshold": 25,
            "favor_direction": "NONE",
        },
        "NEUTRAL": {
            "period": 14,
            "trend_threshold": 25,
            "strong_trend_threshold": 30,
            "favor_direction": "UP",
        },
    }
    
    def __init__(self):
        """Initialize ADX model."""
        super().__init__()
    
    def get_regime_params(self, regime: str) -> Dict[str, Any]:
        """Get regime-specific parameters."""
        return self.REGIME_PARAMS.get(regime, self.REGIME_PARAMS["NEUTRAL"])
    
    def calculate(
        self,
        prices: pd.DataFrame,
        fundamentals: Optional[Dict[str, Any]] = None,
        regime: str = "NEUTRAL"
    ) -> List[ModelResult]:
        """
        Calculate ADX score for all stocks.
        
        Args:
            prices: DataFrame with OHLCV data
            fundamentals: Not used
            regime: Current market regime
            
        Returns:
            List of ModelResult for each ticker
        """
        params = self.get_regime_params(regime)
        period = params["period"]
        trend_threshold = params["trend_threshold"]
        favor_direction = params["favor_direction"]
        
        results = []
        
        # Handle different DataFrame formats
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(
                    ticker, ticker_data, period, trend_threshold, favor_direction, regime
                )
                results.append(result)
        else:
            # Assume single stock or need to identify tickers
            result = self._calculate_single(
                prices.get('ticker', ['UNKNOWN'])[0] if 'ticker' in prices else 'STOCK',
                prices, period, trend_threshold, favor_direction, regime
            )
            results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        data: pd.DataFrame,
        period: int,
        trend_threshold: float,
        favor_direction: str,
        regime: str
    ) -> ModelResult:
        """Calculate ADX for a single stock."""
        try:
            high = data['high']
            low = data['low']
            close = data['close']
            
            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Calculate Directional Movement
            plus_dm = high.diff()
            minus_dm = -low.diff()
            
            # Only keep positive values where appropriate
            plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
            minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)
            
            # Smooth using Wilder's smoothing (EMA with alpha = 1/period)
            alpha = 1 / period
            
            atr = tr.ewm(alpha=alpha, adjust=False).mean()
            plus_di = 100 * pd.Series(plus_dm).ewm(alpha=alpha, adjust=False).mean() / atr
            minus_di = 100 * pd.Series(minus_dm).ewm(alpha=alpha, adjust=False).mean() / atr
            
            # Calculate DX and ADX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
            adx = dx.ewm(alpha=alpha, adjust=False).mean()
            
            # Get current values
            current_adx = adx.iloc[-1]
            current_plus_di = plus_di.iloc[-1]
            current_minus_di = minus_di.iloc[-1]
            
            # Handle NaN
            if pd.isna(current_adx):
                return ModelResult(
                    ticker=ticker,
                    score=50,
                    signal=Signal.HOLD,
                    confidence=0.0,
                    metadata={"error": "Insufficient data"}
                )
            
            # Determine trend state
            if current_adx > trend_threshold:
                if current_plus_di > current_minus_di:
                    trend = "STRONG_UPTREND"
                else:
                    trend = "STRONG_DOWNTREND"
            elif current_adx < 20:
                trend = "RANGING"
            else:
                if current_plus_di > current_minus_di:
                    trend = "WEAK_UPTREND"
                else:
                    trend = "WEAK_DOWNTREND"
            
            # Calculate score based on regime preference
            score = self._calculate_score(
                current_adx, current_plus_di, current_minus_di,
                trend_threshold, favor_direction
            )
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "adx": round(current_adx, 2),
                    "plus_di": round(current_plus_di, 2),
                    "minus_di": round(current_minus_di, 2),
                    "trend": trend,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker,
                score=50,
                signal=Signal.HOLD,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _calculate_score(
        self,
        adx: float,
        plus_di: float,
        minus_di: float,
        trend_threshold: float,
        favor_direction: str
    ) -> float:
        """
        Calculate score based on ADX and direction.
        
        Scoring logic:
        - For BULL/UP preference: High score for strong uptrend
        - For BEAR/DOWN preference: High score for strong downtrend
        - For SIDEWAYS/NONE: High score for low ADX (ranging)
        """
        di_diff = plus_di - minus_di
        
        if favor_direction == "UP":
            # Bull market: want strong uptrend
            if adx > trend_threshold and di_diff > 0:
                # Strong uptrend: high score
                base_score = 50 + min(adx, 50)
                direction_bonus = min(di_diff, 30)
                score = base_score + direction_bonus * 0.5
            elif di_diff > 0:
                # Weak uptrend: moderate score
                score = 50 + di_diff * 0.5
            else:
                # Downtrend: low score
                score = 50 + di_diff * 0.5  # di_diff is negative
                
        elif favor_direction == "DOWN":
            # Bear market: want downtrend (for defensive/short)
            if adx > trend_threshold and di_diff < 0:
                # Strong downtrend: avoid (low score for long)
                score = 50 - min(adx, 50)
            elif di_diff < 0:
                # Weak downtrend: cautious
                score = 50 + di_diff * 0.5
            else:
                # Uptrend in bear market: cautious buy
                score = 50 + di_diff * 0.3
                
        else:  # NONE - sideways preference
            # Sideways: prefer low ADX
            if adx < 20:
                # Range-bound: good for mean reversion
                score = 70 + (20 - adx) * 1.5
            else:
                # Trending: less preferred in sideways
                score = 50 - (adx - 20) * 0.5
        
        return max(0, min(100, score))

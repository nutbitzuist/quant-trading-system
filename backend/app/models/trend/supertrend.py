"""
Supertrend Model
Model M8 - Trend Category

ATR-based trend indicator with dynamic stop levels
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class SupertrendModel(BaseModel):
    """
    Supertrend Model
    
    ATR-based trend following indicator.
    
    Formula:
        Upper Band = (High + Low) / 2 + Multiplier × ATR
        Lower Band = (High + Low) / 2 - Multiplier × ATR
        Supertrend = LowerBand if uptrend else UpperBand
    
    Regime Adjustments:
        HIGH_VOLATILITY: multiplier = 4.0 (wider bands)
        LOW_VOLATILITY: multiplier = 2.5 (tighter bands)
        NORMAL: multiplier = 3.0
    """
    
    name = "supertrend"
    category = "trend"
    description = "Supertrend: ATR-based trend with dynamic stops"
    
    REGIME_PARAMS = {
        "BULL": {"atr_period": 10, "multiplier": 2.5},
        "BEAR": {"atr_period": 10, "multiplier": 4.0},
        "SIDEWAYS": {"atr_period": 10, "multiplier": 3.0},
        "NEUTRAL": {"atr_period": 10, "multiplier": 3.0},
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
        results = []
        
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(ticker, ticker_data, params, regime)
                results.append(result)
        else:
            result = self._calculate_single("STOCK", prices, params, regime)
            results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        data: pd.DataFrame,
        params: Dict[str, Any],
        regime: str
    ) -> ModelResult:
        try:
            atr_period = params["atr_period"]
            multiplier = params["multiplier"]
            
            if len(data) < atr_period + 10:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            high = data['high']
            low = data['low']
            close = data['close']
            
            # Calculate ATR
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(atr_period).mean()
            
            # Calculate basic bands
            hl2 = (high + low) / 2
            upper_band = hl2 + multiplier * atr
            lower_band = hl2 - multiplier * atr
            
            # Determine trend
            supertrend = pd.Series(index=data.index, dtype=float)
            direction = pd.Series(index=data.index, dtype=int)
            
            supertrend.iloc[atr_period] = upper_band.iloc[atr_period]
            direction.iloc[atr_period] = -1
            
            for i in range(atr_period + 1, len(data)):
                if close.iloc[i] > supertrend.iloc[i-1]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
                elif close.iloc[i] < supertrend.iloc[i-1]:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    direction.iloc[i] = -1
                else:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                    direction.iloc[i] = direction.iloc[i-1]
            
            current_price = close.iloc[-1]
            current_st = supertrend.iloc[-1]
            current_dir = direction.iloc[-1]
            
            # Calculate score
            is_bullish = current_dir == 1
            distance_pct = abs(current_price - current_st) / current_price * 100
            
            if is_bullish:
                trend = "BULLISH"
                base_score = 70 + min(30, distance_pct * 3)
            else:
                trend = "BEARISH"
                base_score = 30 - min(30, distance_pct * 3)
            
            # Days in current trend
            trend_days = 0
            for i in range(len(direction) - 1, -1, -1):
                if direction.iloc[i] == current_dir:
                    trend_days += 1
                else:
                    break
            
            score = max(0, min(100, base_score))
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "trend": trend,
                    "supertrend_level": round(current_st, 2),
                    "distance_to_stop_pct": round(distance_pct, 2),
                    "days_in_trend": trend_days,
                    "atr": round(atr.iloc[-1], 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

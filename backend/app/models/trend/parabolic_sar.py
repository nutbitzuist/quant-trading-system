"""
Parabolic SAR Model
Model M10 - Trend Category

Parabolic Stop and Reverse indicator
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class ParabolicSARModel(BaseModel):
    """
    Parabolic SAR Model
    
    Trend following indicator with trailing stops.
    
    Formula:
        SAR_next = SAR_current + AF × (EP - SAR_current)
        AF starts at 0.02, increases by 0.02 at each new EP, max 0.20
        EP = Extreme Point (highest high in uptrend, lowest low in downtrend)
    
    Regime Adjustments:
        TRENDING: Use standard AF (0.02)
        RANGING: Use higher AF (0.03) for faster reversals
    """
    
    name = "psar"
    category = "trend"
    description = "Parabolic SAR: Stop and reverse system"
    
    REGIME_PARAMS = {
        "BULL": {"af_start": 0.02, "af_increment": 0.02, "af_max": 0.20},
        "BEAR": {"af_start": 0.02, "af_increment": 0.02, "af_max": 0.20},
        "SIDEWAYS": {"af_start": 0.03, "af_increment": 0.03, "af_max": 0.25},
        "NEUTRAL": {"af_start": 0.02, "af_increment": 0.02, "af_max": 0.20},
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
            af_start = params["af_start"]
            af_increment = params["af_increment"]
            af_max = params["af_max"]
            
            if len(data) < 10:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            high = data['high'].values
            low = data['low'].values
            close = data['close'].values
            
            n = len(close)
            psar = np.zeros(n)
            direction = np.zeros(n)  # 1 = long, -1 = short
            ep = np.zeros(n)
            af = np.zeros(n)
            
            # Initialize
            psar[0] = close[0]
            direction[0] = 1 if close[1] > close[0] else -1
            ep[0] = high[0] if direction[0] == 1 else low[0]
            af[0] = af_start
            
            for i in range(1, n):
                # Calculate SAR
                if direction[i-1] == 1:  # Long
                    psar[i] = psar[i-1] + af[i-1] * (ep[i-1] - psar[i-1])
                    psar[i] = min(psar[i], low[i-1], low[i-2] if i >= 2 else low[i-1])
                    
                    if low[i] < psar[i]:  # Reversal
                        direction[i] = -1
                        psar[i] = ep[i-1]
                        ep[i] = low[i]
                        af[i] = af_start
                    else:
                        direction[i] = 1
                        if high[i] > ep[i-1]:
                            ep[i] = high[i]
                            af[i] = min(af[i-1] + af_increment, af_max)
                        else:
                            ep[i] = ep[i-1]
                            af[i] = af[i-1]
                else:  # Short
                    psar[i] = psar[i-1] + af[i-1] * (ep[i-1] - psar[i-1])
                    psar[i] = max(psar[i], high[i-1], high[i-2] if i >= 2 else high[i-1])
                    
                    if high[i] > psar[i]:  # Reversal
                        direction[i] = 1
                        psar[i] = ep[i-1]
                        ep[i] = high[i]
                        af[i] = af_start
                    else:
                        direction[i] = -1
                        if low[i] < ep[i-1]:
                            ep[i] = low[i]
                            af[i] = min(af[i-1] + af_increment, af_max)
                        else:
                            ep[i] = ep[i-1]
                            af[i] = af[i-1]
            
            current_psar = psar[-1]
            current_dir = direction[-1]
            current_price = close[-1]
            
            # Count days in trend
            trend_days = 0
            for i in range(n-1, -1, -1):
                if direction[i] == current_dir:
                    trend_days += 1
                else:
                    break
            
            # Calculate score
            distance_pct = abs(current_price - current_psar) / current_price * 100
            
            if current_dir == 1:  # Bullish
                trend = "BULLISH"
                score = 60 + min(40, distance_pct * 4 + trend_days * 0.5)
            else:  # Bearish
                trend = "BEARISH"
                score = 40 - min(40, distance_pct * 4 + trend_days * 0.5)
            
            score = max(0, min(100, score))
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "trend": trend,
                    "psar_level": round(current_psar, 2),
                    "distance_to_sar_pct": round(distance_pct, 2),
                    "days_in_trend": trend_days,
                    "current_af": round(af[-1], 3),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

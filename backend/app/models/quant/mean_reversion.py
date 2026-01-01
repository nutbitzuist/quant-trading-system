"""
Mean Reversion Model
Model M18 - Quantitative Category

Bollinger Band-based mean reversion signals
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class MeanReversionModel(BaseModel):
    """
    Mean Reversion Model
    
    Uses Bollinger Bands and Z-score for mean reversion signals.
    Best suited for sideways/ranging markets.
    
    Formula:
        Z-Score = (Price - MA_20) / StdDev_20
        BB%B = (Price - Lower_Band) / (Upper_Band - Lower_Band)
    
    Signals:
        BUY: Z < -2 (oversold)
        SELL: Z > +2 (overbought)
    
    Regime Adjustments:
        BULL: Asymmetric - only buy dips, don't short tops
        BEAR: Asymmetric - only short tops, careful with dips
        SIDEWAYS: Symmetric mean reversion
    """
    
    name = "mean_reversion"
    category = "quant"
    description = "Mean Reversion: Bollinger z-score strategy"
    
    REGIME_PARAMS = {
        "BULL": {"period": 20, "std_mult": 2.0, "mode": "BUY_DIP"},
        "BEAR": {"period": 20, "std_mult": 2.0, "mode": "SHORT_TOP"},
        "SIDEWAYS": {"period": 20, "std_mult": 2.0, "mode": "SYMMETRIC"},
        "NEUTRAL": {"period": 20, "std_mult": 2.0, "mode": "SYMMETRIC"},
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
                result = self._calculate_single(ticker, ticker_data['close'], params, regime)
                results.append(result)
        else:
            if 'close' in prices.columns:
                result = self._calculate_single("STOCK", prices['close'], params, regime)
                results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        close: pd.Series,
        params: Dict[str, Any],
        regime: str
    ) -> ModelResult:
        try:
            period = params["period"]
            std_mult = params["std_mult"]
            mode = params["mode"]
            
            if len(close) < period + 10:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            # Calculate Bollinger Bands
            ma = close.rolling(period).mean()
            std = close.rolling(period).std()
            
            upper_band = ma + std_mult * std
            lower_band = ma - std_mult * std
            
            current_price = close.iloc[-1]
            current_ma = ma.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            
            # Z-Score
            z_score = (current_price - current_ma) / std.iloc[-1] if std.iloc[-1] > 0 else 0
            
            # %B (Percent B)
            pct_b = (current_price - current_lower) / (current_upper - current_lower) if (current_upper - current_lower) > 0 else 0.5
            
            # Calculate score based on mode
            if mode == "BUY_DIP":
                # In bull market, buy dips only
                if z_score < -2:
                    score = 90  # Strong buy on dip
                elif z_score < -1:
                    score = 75
                elif z_score < 0:
                    score = 60
                else:
                    score = 50  # Neutral when extended
                    
            elif mode == "SHORT_TOP":
                # In bear market, fade rallies
                if z_score > 2:
                    score = 10  # Avoid overbought
                elif z_score > 1:
                    score = 25
                elif z_score > 0:
                    score = 40
                else:
                    score = 60  # Oversold could bounce
                    
            else:  # SYMMETRIC
                # Full mean reversion
                if z_score < -2:
                    score = 90  # Strongly oversold
                elif z_score < -1:
                    score = 75
                elif z_score > 2:
                    score = 10  # Strongly overbought
                elif z_score > 1:
                    score = 25
                else:
                    score = 50 - z_score * 10  # Linear in middle
            
            score = max(0, min(100, score))
            
            # Determine signal
            if z_score < -2:
                mr_signal = "OVERSOLD"
            elif z_score > 2:
                mr_signal = "OVERBOUGHT"
            elif z_score < -1:
                mr_signal = "NEAR_LOWER"
            elif z_score > 1:
                mr_signal = "NEAR_UPPER"
            else:
                mr_signal = "NEUTRAL"
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            # Higher confidence at extremes
            if abs(z_score) > 2:
                confidence = min(1.0, confidence + 0.2)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "z_score": round(z_score, 2),
                    "percent_b": round(pct_b, 2),
                    "mr_signal": mr_signal,
                    "upper_band": round(current_upper, 2),
                    "lower_band": round(current_lower, 2),
                    "ma_20": round(current_ma, 2),
                    "mode": mode,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

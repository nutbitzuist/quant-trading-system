"""
RSI Divergence Model
Model M20 - Quantitative Category

Price/RSI divergence detection for reversals
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class RSIDivergenceModel(BaseModel):
    """
    RSI Divergence Model
    
    Detects bullish and bearish divergences between price and RSI.
    
    Divergence Types:
        Bullish: Price makes lower low, RSI makes higher low (reversal up)
        Bearish: Price makes higher high, RSI makes lower high (reversal down)
        Hidden Bullish: Price makes higher low, RSI makes lower low (continuation)
        Hidden Bearish: Price makes lower high, RSI makes higher high (continuation)
    
    Also used for IBD Relative Strength style analysis.
    """
    
    name = "rsi_divergence"
    category = "quant"
    description = "RSI Divergence: Price/RSI divergence detection"
    
    REGIME_PARAMS = {
        "BULL": {"rsi_period": 14, "divergence_window": 10},
        "BEAR": {"rsi_period": 14, "divergence_window": 10},
        "SIDEWAYS": {"rsi_period": 14, "divergence_window": 10},
        "NEUTRAL": {"rsi_period": 14, "divergence_window": 10},
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
            rsi_period = params["rsi_period"]
            div_window = params["divergence_window"]
            
            if len(data) < rsi_period + div_window + 10:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            close = data['close']
            
            # Calculate RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(rsi_period).mean()
            avg_loss = loss.rolling(rsi_period).mean()
            
            rs = avg_gain / avg_loss.replace(0, 1e-10)
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            current_price = close.iloc[-1]
            
            # Find local extremes
            recent_prices = close.iloc[-div_window*2:]
            recent_rsi = rsi.iloc[-div_window*2:]
            
            # Price highs/lows
            price_high_idx = recent_prices.idxmax()
            price_low_idx = recent_prices.idxmin()
            
            # RSI at those points
            rsi_at_price_high = recent_rsi.get(price_high_idx, 50)
            rsi_at_price_low = recent_rsi.get(price_low_idx, 50)
            
            # Detect divergences (simplified)
            divergence_type = "NONE"
            
            # Check for bullish divergence (price lower, RSI higher)
            prev_low_price = close.iloc[-div_window*2:-div_window].min()
            curr_low_price = close.iloc[-div_window:].min()
            prev_low_rsi = rsi.iloc[-div_window*2:-div_window].min()
            curr_low_rsi = rsi.iloc[-div_window:].min()
            
            if curr_low_price < prev_low_price and curr_low_rsi > prev_low_rsi:
                divergence_type = "BULLISH"
            
            # Check for bearish divergence (price higher, RSI lower)
            prev_high_price = close.iloc[-div_window*2:-div_window].max()
            curr_high_price = close.iloc[-div_window:].max()
            prev_high_rsi = rsi.iloc[-div_window*2:-div_window].max()
            curr_high_rsi = rsi.iloc[-div_window:].max()
            
            if curr_high_price > prev_high_price and curr_high_rsi < prev_high_rsi:
                divergence_type = "BEARISH"
            
            # Base score on RSI level
            if current_rsi >= 70:
                rsi_zone = "OVERBOUGHT"
                base_score = 30
            elif current_rsi <= 30:
                rsi_zone = "OVERSOLD"
                base_score = 70
            else:
                rsi_zone = "NEUTRAL"
                base_score = 50
            
            # Adjust for divergence
            if divergence_type == "BULLISH":
                score = min(100, base_score + 25)
            elif divergence_type == "BEARISH":
                score = max(0, base_score - 25)
            else:
                score = base_score
            
            # RSI momentum
            rsi_slope = (current_rsi - rsi.iloc[-5]) / 5
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            # Higher confidence for divergences
            if divergence_type != "NONE":
                confidence = min(1.0, confidence + 0.2)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "rsi": round(current_rsi, 2),
                    "rsi_zone": rsi_zone,
                    "divergence_type": divergence_type,
                    "rsi_slope": round(rsi_slope, 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

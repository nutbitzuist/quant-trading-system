"""
52-Week High Momentum Model
Model M5 - Momentum Category

Distance to 52-week high as momentum indicator
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class FiftyTwoWeekHighModel(BaseModel):
    """
    52-Week High Momentum Model
    
    Stocks trading near their 52-week highs tend to continue outperforming.
    
    Formula:
        distance_to_high = Price_today / 52W_High × 100
        new_high_count = count(new_highs_last_60_days)
        score = 0.7 × distance_to_high + 0.3 × new_high_frequency
    
    Regime Adjustments:
        BULL: BUY if > 95% of high (breakout plays)
        BEAR: BUY if > 90% and improving (relative strength)
        SIDEWAYS: BUY if > 85% with low volatility
    """
    
    name = "52w_high"
    category = "momentum"
    description = "52-Week High: Distance to high and new high frequency"
    
    REGIME_PARAMS = {
        "BULL": {"buy_threshold": 95, "new_high_window": 60},
        "BEAR": {"buy_threshold": 90, "new_high_window": 60},
        "SIDEWAYS": {"buy_threshold": 85, "new_high_window": 60},
        "NEUTRAL": {"buy_threshold": 90, "new_high_window": 60},
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
        buy_threshold = params["buy_threshold"]
        new_high_window = params["new_high_window"]
        
        results = []
        
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(
                    ticker, ticker_data['close'], buy_threshold, new_high_window, regime
                )
                results.append(result)
        else:
            if 'close' in prices.columns:
                result = self._calculate_single(
                    "STOCK", prices['close'], buy_threshold, new_high_window, regime
                )
                results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        close: pd.Series,
        buy_threshold: float,
        new_high_window: int,
        regime: str
    ) -> ModelResult:
        try:
            if len(close) < 252:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data for 52W"}
                )
            
            current_price = close.iloc[-1]
            
            # 52-week high and low
            high_52w = close.iloc[-252:].max()
            low_52w = close.iloc[-252:].min()
            
            # Distance to high as percentage
            distance_to_high = (current_price / high_52w) * 100
            
            # Distance from low (range position)
            range_position = (current_price - low_52w) / (high_52w - low_52w) * 100 if (high_52w - low_52w) > 0 else 50
            
            # Count new highs in window
            if len(close) >= new_high_window:
                recent_prices = close.iloc[-new_high_window:]
                new_highs = 0
                running_high = close.iloc[-new_high_window - 252:-new_high_window].max() if len(close) > new_high_window + 252 else close.iloc[-new_high_window]
                
                for i, price in enumerate(recent_prices):
                    if price > running_high:
                        new_highs += 1
                        running_high = price
                
                new_high_freq = (new_highs / new_high_window) * 100
            else:
                new_high_freq = 0
            
            # Composite score
            score = 0.7 * distance_to_high + 0.3 * min(100, new_high_freq * 5)
            
            # Bonus for being at or near new high
            if distance_to_high >= 98:
                score = min(100, score + 10)  # At new high bonus
            elif distance_to_high >= buy_threshold:
                score = min(100, score + 5)   # Near high bonus
            
            # Penalty for being far from high
            if distance_to_high < 70:
                score = max(0, score - 15)
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "distance_to_high": round(distance_to_high, 2),
                    "range_position": round(range_position, 2),
                    "new_high_frequency": round(new_high_freq, 2),
                    "high_52w": round(high_52w, 2),
                    "low_52w": round(low_52w, 2),
                    "at_new_high": distance_to_high >= 99,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

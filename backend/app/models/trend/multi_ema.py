"""
Multi-EMA Matrix Model
Model M7 - Trend Category

Multiple EMA stack alignment analysis
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class MultiEMAModel(BaseModel):
    """
    Multi-EMA Matrix Model
    
    Analyzes alignment of multiple EMAs (Fibonacci-based periods).
    
    Formula:
        ema_stack = [EMA_8, EMA_13, EMA_21, EMA_34, EMA_55, EMA_89]
        price_position = count(price > ema) / 6
        stack_alignment = is_perfectly_ordered(ema_stack)
    
    Scoring:
        Perfect bull stack: 100 (Price > EMA8 > EMA13 > ... > EMA89)
        Perfect bear stack: 0 (Price < EMA8 < EMA13 < ... < EMA89)
        Mixed: proportional score
    """
    
    name = "multi_ema"
    category = "trend"
    description = "Multi-EMA Matrix: EMA stack alignment analysis"
    
    EMA_PERIODS = [8, 13, 21, 34, 55, 89]
    
    REGIME_PARAMS = {
        "BULL": {"require_alignment": True, "min_above_count": 4},
        "BEAR": {"require_alignment": False, "min_above_count": 2},
        "SIDEWAYS": {"require_alignment": False, "min_above_count": 3},
        "NEUTRAL": {"require_alignment": False, "min_above_count": 3},
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
            if len(close) < max(self.EMA_PERIODS):
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            current_price = close.iloc[-1]
            
            # Calculate all EMAs
            emas = {}
            for period in self.EMA_PERIODS:
                emas[period] = close.ewm(span=period, adjust=False).mean().iloc[-1]
            
            # Count price above EMAs
            above_count = sum(1 for p in self.EMA_PERIODS if current_price > emas[p])
            
            # Check stack alignment
            ema_values = [emas[p] for p in self.EMA_PERIODS]
            is_bull_stack = all(ema_values[i] > ema_values[i+1] for i in range(len(ema_values)-1))
            is_bear_stack = all(ema_values[i] < ema_values[i+1] for i in range(len(ema_values)-1))
            
            # Calculate score
            base_score = (above_count / len(self.EMA_PERIODS)) * 100
            
            if is_bull_stack and current_price > emas[8]:
                score = 100
                alignment = "PERFECT_BULL"
            elif is_bear_stack and current_price < emas[8]:
                score = 0
                alignment = "PERFECT_BEAR"
            elif is_bull_stack:
                score = 85
                alignment = "BULL_ALIGNED"
            elif is_bear_stack:
                score = 15
                alignment = "BEAR_ALIGNED"
            else:
                score = base_score
                alignment = "MIXED"
            
            # EMA slope (trend direction)
            ema_21_slope = (emas[21] - close.ewm(span=21).mean().iloc[-10]) / emas[21] * 100
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            # Boost confidence for aligned stacks
            if alignment in ["PERFECT_BULL", "PERFECT_BEAR"]:
                confidence = min(1.0, confidence + 0.2)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "above_count": above_count,
                    "total_emas": len(self.EMA_PERIODS),
                    "alignment": alignment,
                    "is_bull_stack": is_bull_stack,
                    "is_bear_stack": is_bear_stack,
                    "ema_21_slope": round(ema_21_slope, 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

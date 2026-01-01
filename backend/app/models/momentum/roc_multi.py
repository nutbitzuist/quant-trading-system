"""
ROC Multi-Timeframe Model
Model M4 - Momentum Category

Rate of Change across multiple timeframes
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class ROCMultiTimeframeModel(BaseModel):
    """
    ROC Multi-Timeframe Model
    
    Simple but effective momentum measure using Rate of Change
    across multiple timeframes.
    
    Formula:
        ROC_n = (Price_today / Price_n_days_ago - 1) × 100
        composite = weighted_avg(ROC_5, ROC_10, ROC_20, ROC_60)
    
    Regime Adjustments:
        BULL: favor shorter periods [0.3, 0.3, 0.25, 0.15]
        BEAR: favor longer periods [0.1, 0.15, 0.3, 0.45]
        SIDEWAYS: balanced [0.2, 0.25, 0.3, 0.25]
    """
    
    name = "roc_multi"
    category = "momentum"
    description = "ROC Multi-Timeframe: Weighted rate of change composite"
    
    PERIODS = [5, 10, 20, 60]
    
    REGIME_PARAMS = {
        "BULL": {"weights": [0.30, 0.30, 0.25, 0.15]},
        "BEAR": {"weights": [0.10, 0.15, 0.30, 0.45]},
        "SIDEWAYS": {"weights": [0.20, 0.25, 0.30, 0.25]},
        "NEUTRAL": {"weights": [0.20, 0.25, 0.30, 0.25]},
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
        weights = params["weights"]
        
        results = []
        
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(ticker, ticker_data['close'], weights, regime)
                results.append(result)
        else:
            if 'close' in prices.columns:
                result = self._calculate_single("STOCK", prices['close'], weights, regime)
                results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        close: pd.Series,
        weights: List[float],
        regime: str
    ) -> ModelResult:
        try:
            if len(close) < max(self.PERIODS):
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            rocs = {}
            for period in self.PERIODS:
                roc = (close.iloc[-1] / close.iloc[-period] - 1) * 100
                rocs[f"roc_{period}"] = roc
            
            # Weighted composite
            composite = sum(
                weights[i] * rocs[f"roc_{self.PERIODS[i]}"]
                for i in range(len(self.PERIODS))
            )
            
            # Normalize: typical range -30% to +30%
            score = self.normalize_score(composite, -30, 30)
            
            # Momentum consistency bonus
            all_positive = all(rocs[f"roc_{p}"] > 0 for p in self.PERIODS)
            all_negative = all(rocs[f"roc_{p}"] < 0 for p in self.PERIODS)
            
            if all_positive:
                score = min(100, score * 1.1)
            elif all_negative:
                score = max(0, score * 0.9)
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    **{k: round(v, 2) for k, v in rocs.items()},
                    "composite": round(composite, 2),
                    "consistent": all_positive or all_negative,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

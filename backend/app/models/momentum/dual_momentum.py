"""
Dual Momentum Model
Model M3 - Momentum Category

Gary Antonacci's Dual Momentum combining absolute and relative momentum
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class DualMomentumModel(BaseModel):
    """
    Dual Momentum Model
    
    Based on Gary Antonacci's methodology.
    Combines Absolute Momentum (vs risk-free) and Relative Momentum (vs peers).
    
    Formula:
        absolute_momentum = return_12m > risk_free_return
        relative_momentum = percentile_rank(return_12m) among universe
        dual_signal = absolute_momentum AND (relative_momentum > threshold)
    
    Regime Adjustments:
        BULL: threshold = 40th percentile (more permissive)
        BEAR: threshold = 70th percentile (only top quality)
        SIDEWAYS: threshold = 50th percentile (neutral)
    """
    
    name = "dual_momentum"
    category = "momentum"
    description = "Dual Momentum: Absolute + Relative momentum combined"
    
    REGIME_PARAMS = {
        "BULL": {"lookback": 252, "threshold": 40, "risk_free_rate": 0.02},
        "BEAR": {"lookback": 252, "threshold": 70, "risk_free_rate": 0.02},
        "SIDEWAYS": {"lookback": 252, "threshold": 50, "risk_free_rate": 0.02},
        "NEUTRAL": {"lookback": 252, "threshold": 50, "risk_free_rate": 0.02},
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
        threshold = params["threshold"]
        risk_free_rate = params["risk_free_rate"]
        
        results = []
        all_returns = {}
        
        # Calculate returns for all tickers
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                if len(ticker_data) >= lookback:
                    ret = (ticker_data['close'].iloc[-1] / 
                           ticker_data['close'].iloc[-lookback] - 1)
                    all_returns[ticker] = ret
        
        # Calculate percentile ranks
        if all_returns:
            returns_series = pd.Series(all_returns)
            percentiles = returns_series.rank(pct=True) * 100
            
            for ticker in all_returns:
                result = self._calculate_single(
                    ticker, all_returns[ticker], percentiles[ticker],
                    threshold, risk_free_rate, regime
                )
                results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        abs_return: float,
        rel_percentile: float,
        threshold: float,
        risk_free_rate: float,
        regime: str
    ) -> ModelResult:
        try:
            # Absolute momentum check
            has_absolute_momentum = abs_return > risk_free_rate
            
            # Relative momentum check
            has_relative_momentum = rel_percentile > threshold
            
            # Dual momentum signal
            if has_absolute_momentum and has_relative_momentum:
                # Strong dual momentum
                base_score = 60 + (rel_percentile - threshold) * 0.8
                signal_type = "DUAL_POSITIVE"
            elif has_relative_momentum:
                # Only relative momentum
                base_score = 40 + (rel_percentile - threshold) * 0.4
                signal_type = "RELATIVE_ONLY"
            elif has_absolute_momentum:
                # Only absolute momentum
                base_score = 45 + (abs_return - risk_free_rate) * 100
                signal_type = "ABSOLUTE_ONLY"
            else:
                # No momentum
                base_score = 20 + rel_percentile * 0.3
                signal_type = "NONE"
            
            score = max(0, min(100, base_score))
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "absolute_return": round(abs_return * 100, 2),
                    "relative_percentile": round(rel_percentile, 1),
                    "has_absolute_momentum": has_absolute_momentum,
                    "has_relative_momentum": has_relative_momentum,
                    "signal_type": signal_type,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

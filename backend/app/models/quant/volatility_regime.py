"""
Volatility Regime Model
Model M17 - Quantitative Category

Volatility percentile classification for risk management
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class VolatilityRegimeModel(BaseModel):
    """
    Volatility Regime Model
    
    Classifies stocks by their volatility regime for position sizing.
    
    Regimes:
        LOW: < 25th percentile (favorable for larger positions)
        NORMAL: 25th-75th percentile
        HIGH: > 75th percentile (reduce positions)
        SPIKE: > 90th percentile AND rising (defensive mode)
    
    Score reflects risk-adjusted attractiveness:
        Low vol + uptrend = high score
        High vol + downtrend = low score
    """
    
    name = "vol_regime"
    category = "quant"
    description = "Volatility Regime: Vol percentile for risk management"
    
    REGIME_PARAMS = {
        "BULL": {"vol_lookback": 20, "history_days": 252},
        "BEAR": {"vol_lookback": 20, "history_days": 252},
        "SIDEWAYS": {"vol_lookback": 20, "history_days": 252},
        "NEUTRAL": {"vol_lookback": 20, "history_days": 252},
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
            vol_lookback = params["vol_lookback"]
            history_days = params["history_days"]
            
            if len(data) < history_days:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            close = data['close']
            returns = close.pct_change()
            
            # Current volatility (annualized)
            current_vol = returns.iloc[-vol_lookback:].std() * np.sqrt(252)
            
            # Historical volatility series
            vol_series = returns.rolling(vol_lookback).std() * np.sqrt(252)
            vol_history = vol_series.iloc[-history_days:]
            
            # Percentile
            percentile = (vol_history < current_vol).mean() * 100
            
            # Vol change (spike detection)
            vol_5d_ago = vol_series.iloc[-5]
            vol_change = (current_vol - vol_5d_ago) / vol_5d_ago if vol_5d_ago > 0 else 0
            
            # Determine regime
            is_spike = percentile > 90 and vol_change > 0.5
            
            if is_spike:
                vol_regime = "SPIKE"
                base_score = 15
            elif percentile > 75:
                vol_regime = "HIGH"
                base_score = 30
            elif percentile < 25:
                vol_regime = "LOW"
                base_score = 80
            else:
                vol_regime = "NORMAL"
                base_score = 55
            
            # Adjust by trend
            trend_return = (close.iloc[-1] / close.iloc[-20] - 1)
            if trend_return > 0.05:
                score = min(100, base_score + 15)
            elif trend_return < -0.05:
                score = max(0, base_score - 15)
            else:
                score = base_score
            
            # Position sizing recommendation
            if vol_regime == "SPIKE":
                position_mult = 0.25
            elif vol_regime == "HIGH":
                position_mult = 0.5
            elif vol_regime == "LOW":
                position_mult = 1.25
            else:
                position_mult = 1.0
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "vol_regime": vol_regime,
                    "current_vol_pct": round(current_vol * 100, 2),
                    "vol_percentile": round(percentile, 1),
                    "vol_change_5d_pct": round(vol_change * 100, 1),
                    "is_spike": is_spike,
                    "position_multiplier": position_mult,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

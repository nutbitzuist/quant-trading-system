"""
Dividend Quality Model
Model M15 - Fundamental Category

Dividend yield, growth, and sustainability analysis
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class DividendModel(BaseModel):
    """
    Dividend Quality Model
    
    Evaluates dividend stocks on yield, growth, and sustainability.
    
    Components:
        1. Dividend Yield (30%): Current yield vs market average
        2. Dividend Growth (30%): 5-year dividend CAGR
        3. Payout Ratio (20%): Sustainable payout (30-70% ideal)
        4. Dividend Streak (20%): Years of consecutive increases
    
    Regime Adjustments:
        BULL: Lower yield acceptable if growth is high
        BEAR: Higher yield preferred, lower payout preferred
        SIDEWAYS: Balanced approach
    """
    
    name = "dividend"
    category = "fundamental"
    description = "Dividend Quality: Yield + Growth + Sustainability"
    
    REGIME_PARAMS = {
        "BULL": {"min_yield": 1.5, "yield_weight": 0.25, "growth_weight": 0.35},
        "BEAR": {"min_yield": 3.0, "yield_weight": 0.35, "growth_weight": 0.20},
        "SIDEWAYS": {"min_yield": 2.0, "yield_weight": 0.30, "growth_weight": 0.30},
        "NEUTRAL": {"min_yield": 2.0, "yield_weight": 0.30, "growth_weight": 0.30},
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
        if fundamentals is None:
            fundamentals = {}
        
        params = self.get_regime_params(regime)
        results = []
        
        for ticker, fund_data in fundamentals.items():
            result = self._calculate_single(ticker, fund_data, params, regime)
            results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        fund_data: Dict[str, Any],
        params: Dict[str, Any],
        regime: str
    ) -> ModelResult:
        try:
            div_yield = fund_data.get('dividend_yield', 0)
            div_growth = fund_data.get('dividend_growth', 0)
            payout_ratio = fund_data.get('payout_ratio', 0.5)
            div_streak = fund_data.get('dividend_streak', 
                        fund_data.get('years_increasing', 0))
            
            # Convert to percentages if needed
            if div_yield < 1:
                div_yield *= 100
            if div_growth < 1:
                div_growth *= 100
            if payout_ratio > 1:
                payout_ratio /= 100
            
            min_yield = params["min_yield"]
            yield_weight = params["yield_weight"]
            growth_weight = params["growth_weight"]
            payout_weight = 0.20
            streak_weight = 1 - yield_weight - growth_weight - payout_weight
            
            # Yield score
            if div_yield >= 5:
                yield_score = 100
            elif div_yield >= min_yield:
                yield_score = 60 + (div_yield - min_yield) / (5 - min_yield) * 40
            elif div_yield > 0:
                yield_score = 30 + (div_yield / min_yield) * 30
            else:
                yield_score = 20  # No dividend
            
            # Growth score
            if div_growth >= 15:
                growth_score = 100
            elif div_growth >= 10:
                growth_score = 80
            elif div_growth >= 5:
                growth_score = 60
            elif div_growth >= 0:
                growth_score = 40
            else:
                growth_score = 20  # Dividend cut
            
            # Payout ratio score (30-70% is ideal)
            if 0.30 <= payout_ratio <= 0.70:
                payout_score = 100
            elif payout_ratio < 0.30:
                payout_score = 60 + payout_ratio / 0.30 * 30
            elif payout_ratio <= 0.85:
                payout_score = 60 - (payout_ratio - 0.70) / 0.15 * 30
            else:
                payout_score = 20  # Unsustainable
            
            # Streak score (Dividend Aristocrat = 25+ years)
            if div_streak >= 25:
                streak_score = 100
            elif div_streak >= 10:
                streak_score = 70 + (div_streak - 10) / 15 * 30
            elif div_streak >= 5:
                streak_score = 50 + (div_streak - 5) / 5 * 20
            else:
                streak_score = 30 + div_streak / 5 * 20
            
            # Composite score
            score = (yield_weight * yield_score +
                    growth_weight * growth_score +
                    payout_weight * payout_score +
                    streak_weight * streak_score)
            
            # Penalty for no dividend
            if div_yield == 0:
                score = min(score, 30)
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "dividend_yield_pct": round(div_yield, 2),
                    "dividend_growth_pct": round(div_growth, 2),
                    "payout_ratio": round(payout_ratio, 2),
                    "dividend_streak_years": div_streak,
                    "yield_score": round(yield_score, 2),
                    "growth_score": round(growth_score, 2),
                    "payout_score": round(payout_score, 2),
                    "streak_score": round(streak_score, 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

"""
GARP (Growth at Reasonable Price) Model
Model M12 - Fundamental Category

PEG-based growth at value approach
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class GARPModel(BaseModel):
    """
    GARP Model
    
    Growth at Reasonable Price - finding growth stocks at fair valuations.
    
    Formula:
        PEG = P/E Ratio / Earnings Growth Rate
        GARP_Score = f(PEG, Sales Growth, ROE)
    
    Ideal PEG: 0.5 - 1.5 (undervalued growth)
    """
    
    name = "garp"
    category = "fundamental"
    description = "GARP: Growth at Reasonable Price using PEG"
    
    REGIME_PARAMS = {
        "BULL": {"max_peg": 2.0, "min_growth": 10},
        "BEAR": {"max_peg": 1.0, "min_growth": 15},
        "SIDEWAYS": {"max_peg": 1.5, "min_growth": 12},
        "NEUTRAL": {"max_peg": 1.5, "min_growth": 12},
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
            pe_ratio = fund_data.get('pe_ratio', fund_data.get('pe', None))
            earnings_growth = fund_data.get('earnings_growth', 
                             fund_data.get('eps_growth', None))
            sales_growth = fund_data.get('sales_growth', 
                          fund_data.get('revenue_growth', 0))
            roe = fund_data.get('roe', fund_data.get('return_on_equity', 0))
            
            max_peg = params["max_peg"]
            min_growth = params["min_growth"]
            
            # Calculate PEG
            if pe_ratio and earnings_growth and earnings_growth > 0:
                peg = pe_ratio / (earnings_growth * 100)  # earnings_growth as %
            else:
                peg = None
            
            # Score components
            peg_score = 50
            growth_score = 50
            quality_score = 50
            
            # PEG scoring
            if peg is not None:
                if peg <= 0.5:
                    peg_score = 100  # Very undervalued
                elif peg <= 1.0:
                    peg_score = 80
                elif peg <= max_peg:
                    peg_score = 60
                elif peg <= 2.5:
                    peg_score = 40
                else:
                    peg_score = 20  # Overvalued
            
            # Growth scoring
            growth = max(earnings_growth or 0, sales_growth or 0) * 100
            if growth >= 25:
                growth_score = 90
            elif growth >= min_growth:
                growth_score = 70
            elif growth >= 5:
                growth_score = 50
            else:
                growth_score = 30
            
            # Quality (ROE) scoring
            roe_pct = roe * 100 if roe < 1 else roe
            if roe_pct >= 20:
                quality_score = 90
            elif roe_pct >= 15:
                quality_score = 70
            elif roe_pct >= 10:
                quality_score = 50
            else:
                quality_score = 30
            
            # Composite GARP score
            score = 0.4 * peg_score + 0.35 * growth_score + 0.25 * quality_score
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "peg_ratio": round(peg, 2) if peg else None,
                    "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
                    "earnings_growth_pct": round(growth, 2),
                    "roe_pct": round(roe_pct, 2),
                    "peg_score": round(peg_score, 2),
                    "growth_score": round(growth_score, 2),
                    "quality_score": round(quality_score, 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

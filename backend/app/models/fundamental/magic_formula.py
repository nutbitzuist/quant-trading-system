"""
Magic Formula Model
Model M11 - Fundamental Category

Joel Greenblatt's Magic Formula (Earnings Yield + Return on Capital)
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class MagicFormulaModel(BaseModel):
    """
    Magic Formula Model
    
    Based on Joel Greenblatt's "The Little Book That Beats the Market".
    
    Formula:
        Earnings Yield = EBIT / Enterprise Value
        Return on Capital = EBIT / (Net Fixed Assets + Working Capital)
        Magic Formula Rank = avg(EY_rank + ROC_rank)
    
    Higher EY = cheaper stock
    Higher ROC = better quality business
    """
    
    name = "magic_formula"
    category = "fundamental"
    description = "Magic Formula: Greenblatt's EY + ROC rank"
    
    REGIME_PARAMS = {
        "BULL": {"ey_weight": 0.4, "roc_weight": 0.6},  # Favor quality
        "BEAR": {"ey_weight": 0.6, "roc_weight": 0.4},  # Favor value
        "SIDEWAYS": {"ey_weight": 0.5, "roc_weight": 0.5},
        "NEUTRAL": {"ey_weight": 0.5, "roc_weight": 0.5},
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
        
        # Calculate EY and ROC for all stocks
        all_ey = {}
        all_roc = {}
        
        for ticker, fund_data in fundamentals.items():
            ey = self._calculate_earnings_yield(fund_data)
            roc = self._calculate_return_on_capital(fund_data)
            if ey is not None:
                all_ey[ticker] = ey
            if roc is not None:
                all_roc[ticker] = roc
        
        # Rank them
        ey_ranks = pd.Series(all_ey).rank(ascending=False, pct=True) * 100
        roc_ranks = pd.Series(all_roc).rank(ascending=False, pct=True) * 100
        
        for ticker in fundamentals.keys():
            ey_rank = ey_ranks.get(ticker, 50)
            roc_rank = roc_ranks.get(ticker, 50)
            
            score = (params["ey_weight"] * ey_rank + 
                    params["roc_weight"] * roc_rank)
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            results.append(ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "earnings_yield": round(all_ey.get(ticker, 0) * 100, 2),
                    "return_on_capital": round(all_roc.get(ticker, 0) * 100, 2),
                    "ey_rank": round(ey_rank, 2),
                    "roc_rank": round(roc_rank, 2),
                    "regime": regime,
                }
            ))
        
        return results
    
    def _calculate_earnings_yield(self, fund_data: Dict) -> Optional[float]:
        """Calculate EBIT / Enterprise Value"""
        ebit = fund_data.get('ebit', fund_data.get('operating_income', 0))
        market_cap = fund_data.get('market_cap', 0)
        total_debt = fund_data.get('total_debt', 0)
        cash = fund_data.get('cash', fund_data.get('cash_equivalents', 0))
        
        ev = market_cap + total_debt - cash
        
        if ev <= 0:
            return None
        
        return ebit / ev
    
    def _calculate_return_on_capital(self, fund_data: Dict) -> Optional[float]:
        """Calculate EBIT / (Net Fixed Assets + Working Capital)"""
        ebit = fund_data.get('ebit', fund_data.get('operating_income', 0))
        net_fixed_assets = fund_data.get('net_fixed_assets', fund_data.get('ppe', 0))
        current_assets = fund_data.get('current_assets', 0)
        current_liabilities = fund_data.get('current_liabilities', 0)
        
        working_capital = current_assets - current_liabilities
        capital = net_fixed_assets + working_capital
        
        if capital <= 0:
            return None
        
        return ebit / capital

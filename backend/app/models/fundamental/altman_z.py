"""
Altman Z-Score Model
Model M14 - Fundamental Category

Financial distress prediction using Altman Z-Score
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class AltmanZScoreModel(BaseModel):
    """
    Altman Z-Score Model
    
    Predicts bankruptcy probability for public companies.
    
    Formula (for public manufacturing firms):
        Z = 1.2×A + 1.4×B + 3.3×C + 0.6×D + 1.0×E
        
        A = Working Capital / Total Assets
        B = Retained Earnings / Total Assets
        C = EBIT / Total Assets
        D = Market Value of Equity / Total Liabilities
        E = Sales / Total Assets
    
    Interpretation:
        Z > 2.99: Safe Zone
        1.81 < Z < 2.99: Grey Zone
        Z < 1.81: Distress Zone
    
    CRITICAL: Stocks with Z < 1.1 → AVOID list
    """
    
    name = "altman_z"
    category = "fundamental"
    description = "Altman Z-Score: Financial distress prediction"
    
    # Z-Score thresholds
    SAFE_ZONE = 2.99
    GREY_ZONE_UPPER = 2.99
    GREY_ZONE_LOWER = 1.81
    DISTRESS_ZONE = 1.81
    CRITICAL_THRESHOLD = 1.1  # Auto-AVOID
    
    REGIME_PARAMS = {
        "BULL": {"safe_threshold": 2.5},
        "BEAR": {"safe_threshold": 3.0},  # More conservative
        "SIDEWAYS": {"safe_threshold": 2.7},
        "NEUTRAL": {"safe_threshold": 2.7},
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
            # Extract components
            working_capital = (fund_data.get('current_assets', 0) - 
                              fund_data.get('current_liabilities', 0))
            total_assets = fund_data.get('total_assets', 1)
            retained_earnings = fund_data.get('retained_earnings', 0)
            ebit = fund_data.get('ebit', fund_data.get('operating_income', 0))
            market_cap = fund_data.get('market_cap', 0)
            total_liabilities = fund_data.get('total_liabilities', 1)
            sales = fund_data.get('revenue', fund_data.get('sales', 0))
            
            # Prevent division by zero
            if total_assets <= 0:
                total_assets = 1
            if total_liabilities <= 0:
                total_liabilities = 1
            
            # Calculate ratios
            A = working_capital / total_assets
            B = retained_earnings / total_assets
            C = ebit / total_assets
            D = market_cap / total_liabilities
            E = sales / total_assets
            
            # Calculate Z-Score
            z_score = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
            
            # Determine zone
            if z_score >= self.SAFE_ZONE:
                zone = "SAFE"
                base_score = 80 + min(20, (z_score - self.SAFE_ZONE) * 5)
            elif z_score >= self.GREY_ZONE_LOWER:
                zone = "GREY"
                # Linear interpolation in grey zone
                base_score = 40 + ((z_score - self.GREY_ZONE_LOWER) / 
                                   (self.GREY_ZONE_UPPER - self.GREY_ZONE_LOWER)) * 40
            elif z_score >= self.CRITICAL_THRESHOLD:
                zone = "DISTRESS"
                base_score = 20 + ((z_score - self.CRITICAL_THRESHOLD) / 
                                   (self.GREY_ZONE_LOWER - self.CRITICAL_THRESHOLD)) * 20
            else:
                zone = "CRITICAL"
                base_score = 0  # Force AVOID
            
            # CRITICAL: Auto-AVOID for very low Z-scores
            if z_score < self.CRITICAL_THRESHOLD:
                signal = Signal.STRONG_AVOID
                score = 0
            else:
                score = max(0, min(100, base_score))
                signal = self.score_to_signal(score)
            
            confidence = self.calculate_confidence(score)
            
            # Higher confidence for extreme zones
            if zone in ["SAFE", "CRITICAL"]:
                confidence = min(1.0, confidence + 0.2)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "z_score": round(z_score, 2),
                    "zone": zone,
                    "is_auto_avoid": z_score < self.CRITICAL_THRESHOLD,
                    "components": {
                        "A_wc_ta": round(A, 3),
                        "B_re_ta": round(B, 3),
                        "C_ebit_ta": round(C, 3),
                        "D_mv_tl": round(D, 3),
                        "E_sales_ta": round(E, 3),
                    },
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

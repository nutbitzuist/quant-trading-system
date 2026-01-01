"""
Quality Factor Model
Model M13 - Fundamental Category

Measures earnings quality, stability, and financial strength
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class QualityModel(BaseModel):
    """
    Quality Factor Composite Model
    
    Measures company quality through three components:
    
    Components:
        1. ROE Stability (35%): Low variance in ROE over 5 years
        2. Earnings Quality (35%): CFO/Net Income ratio (>1 is good)
        3. Leverage Quality (30%): Low debt-to-equity
    
    Formula:
        Quality = 0.35×ROE_Stability + 0.35×Earnings_Quality + 0.30×Leverage_Quality
    
    Regime Adjustments:
        BULL: Lower weight on quality (growth matters more)
        BEAR: Maximum weight on quality (defensive)
        SIDEWAYS: Moderate weight on quality
    """
    
    name = "quality"
    category = "fundamental"
    description = "Quality Factor: ROE stability + earnings quality + low leverage"
    
    # Component weights by regime
    REGIME_WEIGHTS = {
        "BULL": {
            "roe_stability": 0.30,
            "earnings_quality": 0.35,
            "leverage_quality": 0.35,
            "min_roe": 8,  # Lower threshold in bull market
            "max_debt_equity": 2.5,
        },
        "BEAR": {
            "roe_stability": 0.40,
            "earnings_quality": 0.35,
            "leverage_quality": 0.25,
            "min_roe": 12,  # Higher threshold in bear market
            "max_debt_equity": 1.5,
        },
        "SIDEWAYS": {
            "roe_stability": 0.35,
            "earnings_quality": 0.35,
            "leverage_quality": 0.30,
            "min_roe": 10,
            "max_debt_equity": 2.0,
        },
        "NEUTRAL": {
            "roe_stability": 0.35,
            "earnings_quality": 0.35,
            "leverage_quality": 0.30,
            "min_roe": 10,
            "max_debt_equity": 2.0,
        },
    }
    
    def __init__(self):
        """Initialize Quality model."""
        super().__init__()
    
    def get_regime_params(self, regime: str) -> Dict[str, Any]:
        """Get regime-specific parameters."""
        return self.REGIME_WEIGHTS.get(regime, self.REGIME_WEIGHTS["NEUTRAL"])
    
    def calculate(
        self,
        prices: pd.DataFrame,
        fundamentals: Optional[Dict[str, Any]] = None,
        regime: str = "NEUTRAL"
    ) -> List[ModelResult]:
        """
        Calculate Quality score for all stocks.
        
        Args:
            prices: DataFrame with price data (for data quality checks)
            fundamentals: Dict of ticker -> fundamental data
            regime: Current market regime
            
        Returns:
            List of ModelResult for each ticker
        """
        if fundamentals is None:
            fundamentals = {}
        
        params = self.get_regime_params(regime)
        results = []
        
        # Get tickers from fundamentals or prices
        tickers = list(fundamentals.keys())
        if not tickers and isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique().tolist()
        
        for ticker in tickers:
            fund_data = fundamentals.get(ticker, {})
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
        """Calculate quality score for a single stock."""
        try:
            # Extract component weights
            w_roe = params["roe_stability"]
            w_earnings = params["earnings_quality"]
            w_leverage = params["leverage_quality"]
            
            # Calculate ROE Stability
            roe_stability = self._calculate_roe_stability(fund_data)
            
            # Calculate Earnings Quality
            earnings_quality = self._calculate_earnings_quality(fund_data)
            
            # Calculate Leverage Quality
            leverage_quality = self._calculate_leverage_quality(
                fund_data, params["max_debt_equity"]
            )
            
            # Composite score
            quality_score = (
                w_roe * roe_stability +
                w_earnings * earnings_quality +
                w_leverage * leverage_quality
            )
            
            # Generate signal and confidence
            signal = self.score_to_signal(quality_score)
            confidence = self.calculate_confidence(quality_score)
            
            # Determine quality tier
            if quality_score >= 80:
                tier = "HIGH_QUALITY"
            elif quality_score >= 60:
                tier = "GOOD_QUALITY"
            elif quality_score >= 40:
                tier = "MODERATE_QUALITY"
            else:
                tier = "LOW_QUALITY"
            
            return ModelResult(
                ticker=ticker,
                score=round(quality_score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "roe_stability": round(roe_stability, 2),
                    "earnings_quality": round(earnings_quality, 2),
                    "leverage_quality": round(leverage_quality, 2),
                    "quality_tier": tier,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker,
                score=50,
                signal=Signal.HOLD,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _calculate_roe_stability(self, fund_data: Dict[str, Any]) -> float:
        """
        Calculate ROE stability score.
        
        Lower variance in ROE = higher stability = higher score
        
        Args:
            fund_data: Dict containing 'roe_history' or 'roe' values
            
        Returns:
            Score 0-100
        """
        # Try to get ROE history
        roe_history = fund_data.get('roe_history', fund_data.get('roe_5yr', []))
        
        if not roe_history or len(roe_history) < 2:
            # If no history, use single ROE value
            current_roe = fund_data.get('roe', fund_data.get('return_on_equity', 0))
            if current_roe > 0.15:  # > 15% ROE
                return 70
            elif current_roe > 0.10:
                return 55
            elif current_roe > 0.05:
                return 40
            else:
                return 25
        
        # Calculate stability from history
        roe_array = np.array(roe_history)
        roe_mean = np.mean(roe_array)
        roe_std = np.std(roe_array)
        
        if roe_mean <= 0:
            return 20  # Negative average ROE is bad
        
        # Coefficient of variation (lower is more stable)
        cv = roe_std / roe_mean if roe_mean != 0 else 1
        
        # Convert to score (lower CV = higher score)
        # CV of 0.1 = very stable = 100
        # CV of 1.0 = very unstable = 0
        stability_score = max(0, 100 - cv * 100)
        
        # Bonus for high average ROE
        if roe_mean > 0.15:
            stability_score = min(100, stability_score + 15)
        elif roe_mean > 0.10:
            stability_score = min(100, stability_score + 10)
        
        return stability_score
    
    def _calculate_earnings_quality(self, fund_data: Dict[str, Any]) -> float:
        """
        Calculate earnings quality score.
        
        CFO/Net Income > 1 indicates high-quality earnings
        (cash flow backs up reported earnings)
        
        Args:
            fund_data: Dict containing 'cash_from_operations' and 'net_income'
            
        Returns:
            Score 0-100
        """
        cfo = fund_data.get(
            'cash_from_operations', 
            fund_data.get('operating_cash_flow', 0)
        )
        net_income = fund_data.get('net_income', fund_data.get('earnings', 1))
        
        # Avoid division by zero
        if net_income == 0:
            return 50  # Neutral if no earnings data
        
        if net_income < 0:
            # Negative earnings: check if CFO is positive
            if cfo > 0:
                return 40  # Earnings negative but cash positive
            else:
                return 20  # Both negative
        
        # Calculate ratio
        quality_ratio = cfo / net_income
        
        # Convert to score
        # Ratio of 1.5 = excellent = 100
        # Ratio of 1.0 = good = 70
        # Ratio of 0.5 = poor = 30
        # Ratio of 0 = very poor = 0
        
        if quality_ratio >= 1.5:
            score = 100
        elif quality_ratio >= 1.0:
            score = 70 + (quality_ratio - 1.0) * 60  # 70-100
        elif quality_ratio >= 0.5:
            score = 30 + (quality_ratio - 0.5) * 80  # 30-70
        else:
            score = quality_ratio * 60  # 0-30
        
        return max(0, min(100, score))
    
    def _calculate_leverage_quality(
        self, 
        fund_data: Dict[str, Any],
        max_debt_equity: float
    ) -> float:
        """
        Calculate leverage quality score.
        
        Lower debt-to-equity = higher score
        
        Args:
            fund_data: Dict containing 'debt_to_equity' or components
            max_debt_equity: Maximum acceptable D/E ratio
            
        Returns:
            Score 0-100
        """
        debt_equity = fund_data.get(
            'debt_to_equity', 
            fund_data.get('de_ratio', None)
        )
        
        # Try to calculate from components if not available
        if debt_equity is None:
            total_debt = fund_data.get('total_debt', fund_data.get('debt', 0))
            total_equity = fund_data.get('total_equity', fund_data.get('equity', 1))
            
            if total_equity > 0:
                debt_equity = total_debt / total_equity
            else:
                debt_equity = 1.0  # Default moderate
        
        # Handle negative equity (very bad)
        if debt_equity < 0:
            return 10
        
        # Convert to score
        # D/E of 0 = excellent = 100
        # D/E of 1 = good = 60
        # D/E of max = acceptable = 30
        # D/E > max = poor = 0-20
        
        if debt_equity <= 0.5:
            score = 90 + (0.5 - debt_equity) * 20  # 90-100
        elif debt_equity <= 1.0:
            score = 60 + (1.0 - debt_equity) * 60  # 60-90
        elif debt_equity <= max_debt_equity:
            score = 30 + (max_debt_equity - debt_equity) / (max_debt_equity - 1.0) * 30  # 30-60
        else:
            score = max(0, 30 - (debt_equity - max_debt_equity) * 15)  # 0-30
        
        return max(0, min(100, score))

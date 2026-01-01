"""
Sector Momentum Analyzer
Multi-timeframe momentum analysis for sectors
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class SectorMomentum:
    """Momentum data for a sector."""
    sector: str
    momentum_1w: float
    momentum_1m: float
    momentum_3m: float
    momentum_6m: float
    composite_score: float
    trend: str  # UP, DOWN, SIDEWAYS
    rank: int


class SectorMomentumAnalyzer:
    """
    Analyzes sector momentum across multiple timeframes.
    
    Combines short-term and long-term momentum to identify
    sectors with strongest price trends.
    """
    
    # Timeframe weights
    TIMEFRAME_WEIGHTS = {
        "1w": 0.15,
        "1m": 0.25,
        "3m": 0.35,
        "6m": 0.25,
    }
    
    # Trading days per period
    PERIODS = {
        "1w": 5,
        "1m": 21,
        "3m": 63,
        "6m": 126,
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize analyzer.
        
        Args:
            weights: Optional custom weights for timeframes
        """
        self.weights = weights or self.TIMEFRAME_WEIGHTS
    
    def analyze(
        self,
        sector_prices: Dict[str, pd.Series],
    ) -> List[SectorMomentum]:
        """
        Analyze momentum for all sectors.
        
        Args:
            sector_prices: Dict of sector_name -> price series
            
        Returns:
            List of SectorMomentum, sorted by composite score
        """
        results = []
        
        for sector_name, prices in sector_prices.items():
            momentum = self._calculate_momentum(sector_name, prices)
            results.append(momentum)
        
        # Sort by composite score and assign ranks
        results.sort(key=lambda x: x.composite_score, reverse=True)
        for i, m in enumerate(results):
            m.rank = i + 1
        
        return results
    
    def _calculate_momentum(
        self,
        sector_name: str,
        prices: pd.Series
    ) -> SectorMomentum:
        """Calculate momentum for a single sector."""
        
        if len(prices) < self.PERIODS["6m"]:
            return SectorMomentum(
                sector=sector_name,
                momentum_1w=0,
                momentum_1m=0,
                momentum_3m=0,
                momentum_6m=0,
                composite_score=50,
                trend="SIDEWAYS",
                rank=0
            )
        
        current_price = prices.iloc[-1]
        
        # Calculate returns for each period
        mom_1w = (current_price / prices.iloc[-self.PERIODS["1w"]] - 1) * 100
        mom_1m = (current_price / prices.iloc[-self.PERIODS["1m"]] - 1) * 100
        mom_3m = (current_price / prices.iloc[-self.PERIODS["3m"]] - 1) * 100
        mom_6m = (current_price / prices.iloc[-self.PERIODS["6m"]] - 1) * 100
        
        # Weighted composite
        composite = (
            self.weights["1w"] * self._normalize_momentum(mom_1w) +
            self.weights["1m"] * self._normalize_momentum(mom_1m) +
            self.weights["3m"] * self._normalize_momentum(mom_3m) +
            self.weights["6m"] * self._normalize_momentum(mom_6m)
        )
        
        # Determine trend
        if mom_1m > 2 and mom_3m > 5:
            trend = "UP"
        elif mom_1m < -2 and mom_3m < -5:
            trend = "DOWN"
        else:
            trend = "SIDEWAYS"
        
        return SectorMomentum(
            sector=sector_name,
            momentum_1w=round(mom_1w, 2),
            momentum_1m=round(mom_1m, 2),
            momentum_3m=round(mom_3m, 2),
            momentum_6m=round(mom_6m, 2),
            composite_score=round(composite, 2),
            trend=trend,
            rank=0
        )
    
    def _normalize_momentum(self, momentum: float) -> float:
        """Normalize momentum to 0-100 scale."""
        # Typical range: -30% to +30%
        normalized = 50 + momentum * (50 / 30)
        return max(0, min(100, normalized))
    
    def get_top_sectors(
        self,
        results: List[SectorMomentum],
        n: int = 3
    ) -> List[str]:
        """Get top N sectors by momentum."""
        return [m.sector for m in results[:n]]
    
    def get_bottom_sectors(
        self,
        results: List[SectorMomentum],
        n: int = 3
    ) -> List[str]:
        """Get bottom N sectors by momentum."""
        return [m.sector for m in results[-n:]]
    
    def get_improving_sectors(
        self,
        results: List[SectorMomentum]
    ) -> List[str]:
        """Get sectors with improving momentum (short > long)."""
        return [
            m.sector for m in results
            if m.momentum_1m > m.momentum_3m
        ]
    
    def get_deteriorating_sectors(
        self,
        results: List[SectorMomentum]
    ) -> List[str]:
        """Get sectors with deteriorating momentum (short < long)."""
        return [
            m.sector for m in results
            if m.momentum_1m < m.momentum_3m and m.momentum_3m > 0
        ]

"""
Relative Rotation Graph (RRG) Calculator
Sector rotation analysis using RS-Ratio and RS-Momentum
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class RRGPoint:
    """A single point on the RRG for a sector."""
    sector: str
    rs_ratio: float      # Relative strength ratio (x-axis)
    rs_momentum: float   # RS momentum (y-axis)
    quadrant: str        # LEADING, WEAKENING, LAGGING, IMPROVING
    rotation_direction: str  # CLOCKWISE, COUNTER_CLOCKWISE, STABLE
    distance_from_center: float


@dataclass
class SectorRRG:
    """Complete RRG data for a sector over time."""
    sector: str
    points: List[RRGPoint]
    current_quadrant: str
    trend: str  # IMPROVING, DECLINING, STABLE
    weeks_in_quadrant: int


# Thai SET sector classifications
THAI_SET_SECTORS = {
    "AGRO": "Agro & Food Industry",
    "CONSUMP": "Consumer Products",
    "FINCIAL": "Financials",
    "INDUS": "Industrials",
    "PROPCON": "Property & Construction",
    "RESOURC": "Resources",
    "SERVICE": "Services",
    "TECH": "Technology",
}


class RRGCalculator:
    """
    Relative Rotation Graph Calculator
    
    RRG plots sectors on a 2D plane:
    - X-axis: RS-Ratio (relative strength vs benchmark)
    - Y-axis: RS-Momentum (rate of change of RS-Ratio)
    
    Quadrants:
    - LEADING (top-right): Strong and improving
    - WEAKENING (bottom-right): Strong but declining
    - LAGGING (bottom-left): Weak and declining
    - IMPROVING (top-left): Weak but improving
    
    Typical rotation: Leading → Weakening → Lagging → Improving → Leading
    """
    
    def __init__(
        self,
        benchmark_name: str = "SET",
        rs_lookback: int = 52,  # weeks
        momentum_lookback: int = 10,  # weeks for momentum
    ):
        """
        Initialize RRG calculator.
        
        Args:
            benchmark_name: Name of benchmark index
            rs_lookback: Weeks for RS-Ratio calculation
            momentum_lookback: Weeks for RS-Momentum calculation
        """
        self.benchmark_name = benchmark_name
        self.rs_lookback = rs_lookback
        self.momentum_lookback = momentum_lookback
    
    def calculate(
        self,
        sector_prices: Dict[str, pd.Series],
        benchmark_prices: pd.Series,
        periods: int = 12,  # Return last N periods
    ) -> Dict[str, SectorRRG]:
        """
        Calculate RRG data for all sectors.
        
        Args:
            sector_prices: Dict of sector_name -> price series (weekly)
            benchmark_prices: Benchmark index price series
            periods: Number of periods to return
            
        Returns:
            Dict of sector_name -> SectorRRG
        """
        results = {}
        
        for sector_name, prices in sector_prices.items():
            # Calculate RS-Ratio series
            rs_ratio = self._calculate_rs_ratio(prices, benchmark_prices)
            
            # Calculate RS-Momentum series
            rs_momentum = self._calculate_rs_momentum(rs_ratio)
            
            # Normalize to 100-centered scale
            rs_ratio_norm = self._normalize_to_100(rs_ratio)
            rs_momentum_norm = self._normalize_to_100(rs_momentum)
            
            # Generate RRG points
            points = []
            for i in range(-periods, 0):
                if i >= -len(rs_ratio_norm) and i >= -len(rs_momentum_norm):
                    ratio = rs_ratio_norm.iloc[i]
                    momentum = rs_momentum_norm.iloc[i]
                    
                    quadrant = self._get_quadrant(ratio, momentum)
                    distance = np.sqrt((ratio - 100)**2 + (momentum - 100)**2)
                    
                    points.append(RRGPoint(
                        sector=sector_name,
                        rs_ratio=round(ratio, 2),
                        rs_momentum=round(momentum, 2),
                        quadrant=quadrant,
                        rotation_direction="",  # Set after
                        distance_from_center=round(distance, 2)
                    ))
            
            # Determine rotation direction
            for i, point in enumerate(points):
                if i >= 2:
                    point.rotation_direction = self._get_rotation_direction(
                        points[i-2], points[i-1], point
                    )
                else:
                    point.rotation_direction = "STABLE"
            
            # Trend and weeks in quadrant
            if points:
                current = points[-1]
                weeks_in_quad = self._count_weeks_in_quadrant(points)
                
                # Determine trend
                if len(points) >= 3:
                    recent_momentum = [p.rs_momentum for p in points[-3:]]
                    if recent_momentum[-1] > recent_momentum[0]:
                        trend = "IMPROVING"
                    elif recent_momentum[-1] < recent_momentum[0]:
                        trend = "DECLINING"
                    else:
                        trend = "STABLE"
                else:
                    trend = "STABLE"
                
                results[sector_name] = SectorRRG(
                    sector=sector_name,
                    points=points,
                    current_quadrant=current.quadrant,
                    trend=trend,
                    weeks_in_quadrant=weeks_in_quad
                )
        
        return results
    
    def _calculate_rs_ratio(
        self, 
        sector_prices: pd.Series, 
        benchmark_prices: pd.Series
    ) -> pd.Series:
        """Calculate relative strength ratio."""
        # Align indices
        aligned = pd.concat([sector_prices, benchmark_prices], axis=1).dropna()
        if len(aligned) < 2:
            return pd.Series([100])
        
        sector = aligned.iloc[:, 0]
        benchmark = aligned.iloc[:, 1]
        
        # RS = Sector / Benchmark (normalized)
        rs_raw = sector / benchmark
        
        # Smooth with SMA
        rs_smooth = rs_raw.rolling(self.rs_lookback // 4).mean()
        
        return rs_smooth
    
    def _calculate_rs_momentum(self, rs_ratio: pd.Series) -> pd.Series:
        """Calculate rate of change of RS-Ratio."""
        if len(rs_ratio) < self.momentum_lookback:
            return pd.Series([100])
        
        # Momentum = current RS / RS N periods ago
        momentum = rs_ratio / rs_ratio.shift(self.momentum_lookback)
        
        return momentum
    
    def _normalize_to_100(self, series: pd.Series) -> pd.Series:
        """Normalize series to 100-centered scale."""
        if len(series) < 2:
            return series
        
        mean = series.mean()
        std = series.std()
        
        if std == 0:
            return pd.Series([100] * len(series), index=series.index)
        
        # Z-score normalization, then scale to 100 +/- 
        normalized = 100 + (series - mean) / std * 10
        
        return normalized
    
    def _get_quadrant(self, rs_ratio: float, rs_momentum: float) -> str:
        """Determine RRG quadrant."""
        if rs_ratio >= 100 and rs_momentum >= 100:
            return "LEADING"
        elif rs_ratio >= 100 and rs_momentum < 100:
            return "WEAKENING"
        elif rs_ratio < 100 and rs_momentum < 100:
            return "LAGGING"
        else:  # rs_ratio < 100 and rs_momentum >= 100
            return "IMPROVING"
    
    def _get_rotation_direction(
        self, 
        p1: RRGPoint, 
        p2: RRGPoint, 
        p3: RRGPoint
    ) -> str:
        """Determine if rotation is clockwise or counter-clockwise."""
        # Cross product of vectors (p1→p2) and (p2→p3)
        v1 = (p2.rs_ratio - p1.rs_ratio, p2.rs_momentum - p1.rs_momentum)
        v2 = (p3.rs_ratio - p2.rs_ratio, p3.rs_momentum - p2.rs_momentum)
        
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        
        if cross > 0.5:
            return "COUNTER_CLOCKWISE"  # Unusually bullish
        elif cross < -0.5:
            return "CLOCKWISE"  # Normal rotation
        else:
            return "STABLE"
    
    def _count_weeks_in_quadrant(self, points: List[RRGPoint]) -> int:
        """Count consecutive weeks in current quadrant."""
        if not points:
            return 0
        
        current_quad = points[-1].quadrant
        count = 0
        
        for point in reversed(points):
            if point.quadrant == current_quad:
                count += 1
            else:
                break
        
        return count
    
    def get_sector_recommendations(
        self,
        rrg_data: Dict[str, SectorRRG],
        regime: str = "NEUTRAL"
    ) -> Dict[str, str]:
        """
        Generate sector recommendations based on RRG position.
        
        Returns:
            Dict of sector -> recommendation (OVERWEIGHT, NEUTRAL, UNDERWEIGHT)
        """
        recommendations = {}
        
        for sector, data in rrg_data.items():
            quadrant = data.current_quadrant
            trend = data.trend
            weeks = data.weeks_in_quadrant
            
            if quadrant == "LEADING":
                if trend == "IMPROVING" or weeks < 4:
                    rec = "OVERWEIGHT"
                elif trend == "DECLINING" and weeks > 8:
                    rec = "NEUTRAL"  # About to weaken
                else:
                    rec = "OVERWEIGHT"
                    
            elif quadrant == "IMPROVING":
                if trend == "IMPROVING":
                    rec = "OVERWEIGHT" if regime != "BEAR" else "NEUTRAL"
                else:
                    rec = "NEUTRAL"
                    
            elif quadrant == "WEAKENING":
                if weeks < 3:
                    rec = "NEUTRAL"  # Just entering, wait
                else:
                    rec = "UNDERWEIGHT"
                    
            else:  # LAGGING
                if trend == "IMPROVING" and weeks > 4:
                    rec = "NEUTRAL"  # About to improve
                else:
                    rec = "UNDERWEIGHT"
            
            recommendations[sector] = rec
        
        return recommendations

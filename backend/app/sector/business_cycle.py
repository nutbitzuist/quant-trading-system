"""
Business Cycle Detector for Thailand
Maps economic indicators to cycle phases for sector allocation
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np


class CyclePhase(Enum):
    """Business cycle phases"""
    EARLY_EXPANSION = "EARLY_EXPANSION"      # Recovery
    MID_EXPANSION = "MID_EXPANSION"          # Growth
    LATE_EXPANSION = "LATE_EXPANSION"        # Peak approaching
    EARLY_CONTRACTION = "EARLY_CONTRACTION"  # Slowdown
    LATE_CONTRACTION = "LATE_CONTRACTION"    # Recession


# Sector recommendations by cycle phase for Thai market
THAI_CYCLE_SECTORS = {
    CyclePhase.EARLY_EXPANSION: {
        "overweight": ["FINCIAL", "PROPCON", "CONSUMP"],
        "neutral": ["INDUS", "TECH"],
        "underweight": ["RESOURC", "SERVICE"],
    },
    CyclePhase.MID_EXPANSION: {
        "overweight": ["TECH", "INDUS", "SERVICE"],
        "neutral": ["FINCIAL", "CONSUMP"],
        "underweight": ["PROPCON", "AGRO"],
    },
    CyclePhase.LATE_EXPANSION: {
        "overweight": ["RESOURC", "INDUS"],
        "neutral": ["TECH", "FINCIAL"],
        "underweight": ["PROPCON", "CONSUMP"],
    },
    CyclePhase.EARLY_CONTRACTION: {
        "overweight": ["CONSUMP", "SERVICE", "AGRO"],
        "neutral": ["FINCIAL"],
        "underweight": ["INDUS", "PROPCON", "TECH"],
    },
    CyclePhase.LATE_CONTRACTION: {
        "overweight": ["FINCIAL", "PROPCON"],  # Early recovery plays
        "neutral": ["CONSUMP", "AGRO"],
        "underweight": ["RESOURC", "INDUS"],
    },
}


@dataclass
class EconomicIndicators:
    """Key Thai economic indicators"""
    gdp_growth: Optional[float] = None          # YoY %
    interest_rate: Optional[float] = None       # BOT policy rate
    inflation: Optional[float] = None           # CPI YoY %
    pmi: Optional[float] = None                 # Manufacturing PMI
    consumer_confidence: Optional[float] = None # Index
    set_index_trend: Optional[str] = None       # UP, DOWN, SIDEWAYS
    credit_growth: Optional[float] = None       # YoY %
    exports_growth: Optional[float] = None      # YoY %


@dataclass
class CycleResult:
    """Result from cycle detection"""
    phase: CyclePhase
    confidence: float
    indicators_used: List[str]
    sector_recommendations: Dict[str, str]
    transition_probability: Dict[str, float]


class BusinessCycleDetector:
    """
    Detects business cycle phase for Thai economy.
    
    Uses multiple economic indicators:
    1. GDP Growth
    2. Interest Rates (BOT)
    3. Inflation (CPI)
    4. PMI
    5. Consumer Confidence
    6. SET Index Trend
    7. Credit Growth
    8. Exports Growth
    
    Combines indicators to determine cycle phase.
    """
    
    def __init__(self):
        """Initialize detector."""
        self.phase_history: List[CyclePhase] = []
    
    def detect_phase(
        self,
        indicators: EconomicIndicators
    ) -> CycleResult:
        """
        Detect current business cycle phase.
        
        Args:
            indicators: Current economic indicators
            
        Returns:
            CycleResult with phase and recommendations
        """
        scores = {phase: 0.0 for phase in CyclePhase}
        indicators_used = []
        
        # Score each indicator
        if indicators.gdp_growth is not None:
            indicators_used.append("gdp_growth")
            self._score_gdp(indicators.gdp_growth, scores)
        
        if indicators.interest_rate is not None:
            indicators_used.append("interest_rate")
            self._score_interest_rate(indicators.interest_rate, scores)
        
        if indicators.inflation is not None:
            indicators_used.append("inflation")
            self._score_inflation(indicators.inflation, scores)
        
        if indicators.pmi is not None:
            indicators_used.append("pmi")
            self._score_pmi(indicators.pmi, scores)
        
        if indicators.consumer_confidence is not None:
            indicators_used.append("consumer_confidence")
            self._score_confidence(indicators.consumer_confidence, scores)
        
        if indicators.set_index_trend is not None:
            indicators_used.append("set_index_trend")
            self._score_market_trend(indicators.set_index_trend, scores)
        
        # Find highest scoring phase
        if not indicators_used:
            # Default to mid-expansion if no data
            phase = CyclePhase.MID_EXPANSION
            confidence = 0.5
        else:
            total = sum(scores.values())
            if total > 0:
                # Normalize scores to probabilities
                for p in scores:
                    scores[p] /= total
            
            phase = max(scores, key=scores.get)
            confidence = scores[phase]
        
        # Get sector recommendations
        sector_recs = self._get_sector_recommendations(phase)
        
        # Transition probabilities
        transitions = self._calculate_transitions(phase, scores)
        
        return CycleResult(
            phase=phase,
            confidence=round(confidence, 2),
            indicators_used=indicators_used,
            sector_recommendations=sector_recs,
            transition_probability=transitions
        )
    
    def _score_gdp(self, gdp: float, scores: Dict[CyclePhase, float]):
        """Score based on GDP growth."""
        if gdp > 4.0:
            scores[CyclePhase.MID_EXPANSION] += 2
            scores[CyclePhase.LATE_EXPANSION] += 1
        elif gdp > 2.5:
            scores[CyclePhase.MID_EXPANSION] += 1.5
            scores[CyclePhase.EARLY_EXPANSION] += 1
        elif gdp > 1.0:
            scores[CyclePhase.EARLY_EXPANSION] += 1.5
            scores[CyclePhase.LATE_EXPANSION] += 0.5
        elif gdp > 0:
            scores[CyclePhase.EARLY_CONTRACTION] += 1.5
            scores[CyclePhase.LATE_CONTRACTION] += 1
        else:
            scores[CyclePhase.LATE_CONTRACTION] += 2
            scores[CyclePhase.EARLY_CONTRACTION] += 1
    
    def _score_interest_rate(self, rate: float, scores: Dict[CyclePhase, float]):
        """Score based on BOT policy rate."""
        # Thai rates typically 0.5% - 3.5%
        if rate < 1.0:
            scores[CyclePhase.EARLY_EXPANSION] += 1.5  # Low rates = recovery
            scores[CyclePhase.LATE_CONTRACTION] += 1
        elif rate < 2.0:
            scores[CyclePhase.MID_EXPANSION] += 1
        elif rate < 2.5:
            scores[CyclePhase.LATE_EXPANSION] += 1.5  # Rising rates
        else:
            scores[CyclePhase.EARLY_CONTRACTION] += 1.5  # High rates
    
    def _score_inflation(self, inflation: float, scores: Dict[CyclePhase, float]):
        """Score based on inflation."""
        if inflation < 0:
            scores[CyclePhase.LATE_CONTRACTION] += 2  # Deflation
        elif inflation < 1.5:
            scores[CyclePhase.EARLY_EXPANSION] += 1.5
        elif inflation < 3.0:
            scores[CyclePhase.MID_EXPANSION] += 1
        elif inflation < 5.0:
            scores[CyclePhase.LATE_EXPANSION] += 1.5
        else:
            scores[CyclePhase.EARLY_CONTRACTION] += 1.5  # High inflation
    
    def _score_pmi(self, pmi: float, scores: Dict[CyclePhase, float]):
        """Score based on PMI (50 = neutral)."""
        if pmi > 55:
            scores[CyclePhase.MID_EXPANSION] += 2
        elif pmi > 52:
            scores[CyclePhase.MID_EXPANSION] += 1
            scores[CyclePhase.LATE_EXPANSION] += 1
        elif pmi > 50:
            scores[CyclePhase.EARLY_EXPANSION] += 1
        elif pmi > 47:
            scores[CyclePhase.EARLY_CONTRACTION] += 1.5
        else:
            scores[CyclePhase.LATE_CONTRACTION] += 2
    
    def _score_confidence(self, conf: float, scores: Dict[CyclePhase, float]):
        """Score based on consumer confidence."""
        # Thai consumer confidence typically 50-90
        if conf > 80:
            scores[CyclePhase.MID_EXPANSION] += 1
        elif conf > 70:
            scores[CyclePhase.EARLY_EXPANSION] += 1
        elif conf > 60:
            scores[CyclePhase.LATE_EXPANSION] += 1
        elif conf > 50:
            scores[CyclePhase.EARLY_CONTRACTION] += 1
        else:
            scores[CyclePhase.LATE_CONTRACTION] += 1.5
    
    def _score_market_trend(self, trend: str, scores: Dict[CyclePhase, float]):
        """Score based on SET Index trend."""
        if trend == "UP":
            scores[CyclePhase.EARLY_EXPANSION] += 1
            scores[CyclePhase.MID_EXPANSION] += 1
        elif trend == "DOWN":
            scores[CyclePhase.EARLY_CONTRACTION] += 1
            scores[CyclePhase.LATE_CONTRACTION] += 1
        # SIDEWAYS adds no score
    
    def _get_sector_recommendations(self, phase: CyclePhase) -> Dict[str, str]:
        """Get sector recommendations for phase."""
        phase_sectors = THAI_CYCLE_SECTORS.get(phase, {})
        
        recommendations = {}
        for sector in phase_sectors.get("overweight", []):
            recommendations[sector] = "OVERWEIGHT"
        for sector in phase_sectors.get("neutral", []):
            recommendations[sector] = "NEUTRAL"
        for sector in phase_sectors.get("underweight", []):
            recommendations[sector] = "UNDERWEIGHT"
        
        return recommendations
    
    def _calculate_transitions(
        self, 
        current: CyclePhase, 
        scores: Dict[CyclePhase, float]
    ) -> Dict[str, float]:
        """Calculate probability of transitioning to next phases."""
        # Typical cycle progression
        next_phases = {
            CyclePhase.EARLY_EXPANSION: CyclePhase.MID_EXPANSION,
            CyclePhase.MID_EXPANSION: CyclePhase.LATE_EXPANSION,
            CyclePhase.LATE_EXPANSION: CyclePhase.EARLY_CONTRACTION,
            CyclePhase.EARLY_CONTRACTION: CyclePhase.LATE_CONTRACTION,
            CyclePhase.LATE_CONTRACTION: CyclePhase.EARLY_EXPANSION,
        }
        
        next_phase = next_phases.get(current, CyclePhase.MID_EXPANSION)
        
        return {
            "stay": round(scores.get(current, 0.5), 2),
            "next": round(scores.get(next_phase, 0.3), 2),
        }

# 🔄 Sector Rotation Module for Thai SET Market
## Complete Framework: When to Overweight, Underweight, and Switch Sectors

---

## 📊 Overview: What This Module Does

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SECTOR ROTATION DECISION ENGINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INPUT:                                                                     │
│   ├── SET Index + Sector Index Prices                                       │
│   ├── Economic Indicators (GDP, Interest Rates, Inflation)                  │
│   └── Your 20-Model Regime Detection Output                                 │
│                                                                              │
│   PROCESSING:                                                                │
│   ├── Layer 1: Relative Rotation Graph (RRG) - WHERE are sectors now?       │
│   ├── Layer 2: Business Cycle Mapping - WHERE should they be?               │
│   ├── Layer 3: Momentum & Trend Analysis - WHERE are they heading?          │
│   └── Layer 4: Confluence Scoring - HIGH CONVICTION signals                 │
│                                                                              │
│   OUTPUT:                                                                    │
│   ├── OVERWEIGHT: Top 2-3 sectors (with conviction score)                   │
│   ├── UNDERWEIGHT: Bottom 2-3 sectors (with conviction score)               │
│   ├── ROTATION ALERTS: "Switch from X to Y"                                 │
│   └── SECTOR WEIGHTS: Recommended allocation per sector                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏦 Thai SET Sector Classification

### The 8 Industry Groups & 28 Sectors

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INDUSTRY GROUP          │  SECTORS                    │  SET INDEX CODE    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. AGRO & FOOD (AGRO)                                                      │
│     ├── Agribusiness                                    │  AGRI             │
│     └── Food & Beverage                                 │  FOOD             │
│                                                                              │
│  2. CONSUMER PRODUCTS (CONSUMP)                                             │
│     ├── Fashion                                         │  FASHION          │
│     ├── Home & Office Products                          │  HOME             │
│     └── Personal Products & Pharmaceuticals             │  PERSON           │
│                                                                              │
│  3. FINANCIALS (FINCIAL)                                                    │
│     ├── Banking                                         │  BANK             │
│     ├── Finance & Securities                            │  FIN              │
│     └── Insurance                                       │  INSUR            │
│                                                                              │
│  4. INDUSTRIALS (INDUS)                                                     │
│     ├── Automotive                                      │  AUTO             │
│     ├── Industrial Materials & Machinery                │  IMM              │
│     ├── Packaging                                       │  PKG              │
│     ├── Paper & Printing Materials                      │  PAPER            │
│     ├── Petrochemicals & Chemicals                      │  PETRO            │
│     └── Steel                                           │  STEEL            │
│                                                                              │
│  5. PROPERTY & CONSTRUCTION (PROPCON)                                       │
│     ├── Construction Materials                          │  CONMAT           │
│     ├── Construction Services                           │  CONS             │
│     └── Property Development                            │  PROP             │
│                                                                              │
│  6. RESOURCES (RESOURC)                                                     │
│     ├── Energy & Utilities                              │  ENERG            │
│     └── Mining                                          │  MINE             │
│                                                                              │
│  7. SERVICES (SERVICE)                                                      │
│     ├── Commerce                                        │  COMM             │
│     ├── Health Care Services                            │  HELTH            │
│     ├── Media & Publishing                              │  MEDIA            │
│     ├── Professional Services                           │  PROF             │
│     ├── Tourism & Leisure                               │  TOURISM          │
│     └── Transportation & Logistics                      │  TRANS            │
│                                                                              │
│  8. TECHNOLOGY (TECH)                                                       │
│     ├── Electronic Components                           │  ETRON            │
│     ├── Information & Communication Technology          │  ICT              │
│     └── Technology                                      │  TECH             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Simplified 8-Sector Model (Recommended for Rotation)

For practical rotation, we'll use **8 main industry groups** rather than 28 sub-sectors:

| Code | Industry Group | Characteristics | Cycle Sensitivity |
|------|---------------|-----------------|-------------------|
| **AGRO** | Agro & Food | Defensive, stable demand | LOW |
| **CONSUMP** | Consumer Products | Discretionary spending | HIGH |
| **FINCIAL** | Financials | Interest rate sensitive | HIGH |
| **INDUS** | Industrials | Economic growth sensitive | HIGH |
| **PROPCON** | Property & Construction | Rate & growth sensitive | VERY HIGH |
| **RESOURC** | Resources | Commodity prices | HIGH |
| **SERVICE** | Services | Mixed (tourism high, healthcare low) | MEDIUM |
| **TECH** | Technology | Growth & innovation | MEDIUM-HIGH |

---

## 🎯 Layer 1: Relative Rotation Graph (RRG)

### What is RRG?

The RRG plots each sector on a 2D graph based on:
- **X-axis: RS-Ratio** (Relative Strength vs benchmark) - Is sector outperforming?
- **Y-axis: RS-Momentum** (Rate of change of RS-Ratio) - Is outperformance accelerating?

### The Four Quadrants

```
                          RS-Momentum (Y-axis)
                                 ↑
                                 │
         IMPROVING               │               LEADING
         (Bottom-Left → Top)     │          (Top-Right)
                                 │
         • Underperforming       │          • Outperforming
         • BUT momentum rising   │          • AND momentum rising
         • WATCH - potential     │          • OVERWEIGHT
           rotation candidate    │          • Strongest sectors
                                 │
    ─────────────────────────────┼─────────────────────────────→ RS-Ratio (X-axis)
                                 │                                    100
         LAGGING                 │               WEAKENING
         (Bottom-Left)           │          (Top-Right → Bottom)
                                 │
         • Underperforming       │          • Still outperforming
         • AND momentum falling  │          • BUT momentum falling
         • UNDERWEIGHT           │          • WATCH - may be peaking
         • Weakest sectors       │          • Reduce exposure
                                 │
                                 ↓
```

### RRG Rotation Pattern (Clockwise)

```
Typical sector rotation follows CLOCKWISE pattern:

    IMPROVING ──────→ LEADING
        ↑                │
        │                │
        │                ↓
    LAGGING ←────── WEAKENING

Timeline:
- IMPROVING → LEADING: 4-8 weeks (entry opportunity)
- LEADING → WEAKENING: varies (take profits gradually)
- WEAKENING → LAGGING: 4-8 weeks (exit opportunity)
- LAGGING → IMPROVING: varies (watch for turnaround)
```

### Python Implementation: RRG Calculator

```python
"""
Relative Rotation Graph (RRG) Calculator
Based on Julius de Kempenaer's methodology
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class RRGQuadrant(Enum):
    LEADING = "LEADING"        # RS-Ratio > 100, RS-Momentum > 100
    WEAKENING = "WEAKENING"    # RS-Ratio > 100, RS-Momentum < 100
    LAGGING = "LAGGING"        # RS-Ratio < 100, RS-Momentum < 100
    IMPROVING = "IMPROVING"    # RS-Ratio < 100, RS-Momentum > 100


@dataclass
class RRGPoint:
    """Single point on the RRG for a sector"""
    sector: str
    rs_ratio: float           # X-axis (relative strength)
    rs_momentum: float        # Y-axis (momentum of RS)
    quadrant: RRGQuadrant
    distance_from_center: float
    rotation_direction: str   # "CLOCKWISE", "COUNTER_CLOCKWISE", "STABLE"
    tail_length: float        # How fast it's moving
    signal: str               # "OVERWEIGHT", "UNDERWEIGHT", "HOLD", "WATCH"


class RelativeRotationGraph:
    """
    Calculate RRG positions for Thai SET sectors
    
    Key Parameters:
        - RS-Ratio uses 10-period smoothed relative strength
        - RS-Momentum uses 10-period ROC of RS-Ratio
        - Both normalized to oscillate around 100
    """
    
    def __init__(self, 
                 benchmark: str = "SET",
                 rs_period: int = 10,
                 momentum_period: int = 10,
                 smoothing_period: int = 10):
        """
        Args:
            benchmark: Index to compare against (SET Index)
            rs_period: Period for relative strength calculation
            momentum_period: Period for momentum of RS
            smoothing_period: Smoothing for both indicators
        """
        self.benchmark = benchmark
        self.rs_period = rs_period
        self.momentum_period = momentum_period
        self.smoothing_period = smoothing_period
        
    def calculate_rs_ratio(self, 
                          sector_prices: pd.Series, 
                          benchmark_prices: pd.Series) -> pd.Series:
        """
        Calculate RS-Ratio (JdK RS-Ratio)
        
        Formula:
            1. raw_rs = sector_price / benchmark_price
            2. rs_ratio = 100 + ((raw_rs / SMA(raw_rs, period)) - 1) * 100
            
        Interpretation:
            > 100: Sector outperforming benchmark
            < 100: Sector underperforming benchmark
        """
        # Raw relative strength
        raw_rs = sector_prices / benchmark_prices
        
        # Normalize around 100
        rs_sma = raw_rs.rolling(self.rs_period).mean()
        rs_ratio = 100 + ((raw_rs / rs_sma) - 1) * 100
        
        # Apply smoothing
        rs_ratio_smoothed = rs_ratio.ewm(span=self.smoothing_period).mean()
        
        return rs_ratio_smoothed
    
    def calculate_rs_momentum(self, rs_ratio: pd.Series) -> pd.Series:
        """
        Calculate RS-Momentum (JdK RS-Momentum)
        
        Formula:
            rs_momentum = 100 + ROC(rs_ratio, period)
            
        Interpretation:
            > 100: RS-Ratio is rising (momentum positive)
            < 100: RS-Ratio is falling (momentum negative)
        """
        # Rate of change of RS-Ratio
        roc = (rs_ratio / rs_ratio.shift(self.momentum_period) - 1) * 100
        
        # Normalize around 100
        rs_momentum = 100 + roc
        
        # Apply smoothing
        rs_momentum_smoothed = rs_momentum.ewm(span=self.smoothing_period).mean()
        
        return rs_momentum_smoothed
    
    def determine_quadrant(self, rs_ratio: float, rs_momentum: float) -> RRGQuadrant:
        """Determine which quadrant based on RS-Ratio and RS-Momentum"""
        if rs_ratio >= 100 and rs_momentum >= 100:
            return RRGQuadrant.LEADING
        elif rs_ratio >= 100 and rs_momentum < 100:
            return RRGQuadrant.WEAKENING
        elif rs_ratio < 100 and rs_momentum < 100:
            return RRGQuadrant.LAGGING
        else:  # rs_ratio < 100 and rs_momentum >= 100
            return RRGQuadrant.IMPROVING
    
    def calculate_rotation_direction(self, 
                                    current_ratio: float, 
                                    current_momentum: float,
                                    prev_ratio: float, 
                                    prev_momentum: float) -> str:
        """
        Determine if sector is rotating clockwise (normal) or counter-clockwise
        
        Clockwise (bullish pattern):
            IMPROVING → LEADING → WEAKENING → LAGGING → IMPROVING
            
        Counter-clockwise (unusual, watch carefully):
            Reversed pattern - often indicates choppy/uncertain conditions
        """
        # Calculate angle change
        current_angle = np.arctan2(current_momentum - 100, current_ratio - 100)
        prev_angle = np.arctan2(prev_momentum - 100, prev_ratio - 100)
        
        angle_change = current_angle - prev_angle
        
        # Normalize to [-π, π]
        if angle_change > np.pi:
            angle_change -= 2 * np.pi
        elif angle_change < -np.pi:
            angle_change += 2 * np.pi
        
        if abs(angle_change) < 0.05:  # ~3 degrees
            return "STABLE"
        elif angle_change < 0:  # Clockwise in standard RRG orientation
            return "CLOCKWISE"
        else:
            return "COUNTER_CLOCKWISE"
    
    def generate_signal(self, 
                       quadrant: RRGQuadrant, 
                       rotation: str,
                       distance: float,
                       tail_length: float) -> str:
        """
        Generate trading signal based on RRG position and movement
        
        Signals:
            STRONG_OVERWEIGHT: Leading quadrant, strong momentum, clockwise
            OVERWEIGHT: Leading or Improving with clockwise rotation
            HOLD: Stable or mixed signals
            UNDERWEIGHT: Weakening with falling momentum
            STRONG_UNDERWEIGHT: Lagging quadrant, falling further
        """
        if quadrant == RRGQuadrant.LEADING:
            if rotation == "CLOCKWISE" and tail_length > 1.5:
                return "STRONG_OVERWEIGHT"
            elif rotation != "COUNTER_CLOCKWISE":
                return "OVERWEIGHT"
            else:
                return "HOLD"  # Leading but unusual rotation
                
        elif quadrant == RRGQuadrant.IMPROVING:
            if rotation == "CLOCKWISE" and tail_length > 1.0:
                return "OVERWEIGHT"  # Moving toward Leading
            else:
                return "WATCH_BULLISH"
                
        elif quadrant == RRGQuadrant.WEAKENING:
            if rotation == "CLOCKWISE":
                return "UNDERWEIGHT"  # Moving toward Lagging
            else:
                return "HOLD"  # Might recover
                
        elif quadrant == RRGQuadrant.LAGGING:
            if rotation == "CLOCKWISE" and tail_length > 1.5:
                return "STRONG_UNDERWEIGHT"
            elif rotation == "COUNTER_CLOCKWISE":
                return "WATCH_BULLISH"  # Unusual, but might be turning
            else:
                return "UNDERWEIGHT"
        
        return "HOLD"
    
    def calculate_rrg(self, 
                     sector_data: Dict[str, pd.DataFrame],
                     benchmark_data: pd.DataFrame,
                     lookback_weeks: int = 5) -> Dict[str, RRGPoint]:
        """
        Calculate RRG positions for all sectors
        
        Args:
            sector_data: Dict of sector ticker -> price DataFrame
            benchmark_data: SET Index price DataFrame
            lookback_weeks: Number of weeks for tail calculation
            
        Returns:
            Dict of sector -> RRGPoint
        """
        results = {}
        benchmark_prices = benchmark_data['close']
        
        for sector, data in sector_data.items():
            sector_prices = data['close']
            
            # Calculate RS-Ratio and RS-Momentum
            rs_ratio = self.calculate_rs_ratio(sector_prices, benchmark_prices)
            rs_momentum = self.calculate_rs_momentum(rs_ratio)
            
            # Get current and previous values
            current_ratio = rs_ratio.iloc[-1]
            current_momentum = rs_momentum.iloc[-1]
            prev_ratio = rs_ratio.iloc[-lookback_weeks * 5]  # ~5 days per week
            prev_momentum = rs_momentum.iloc[-lookback_weeks * 5]
            
            # Determine quadrant
            quadrant = self.determine_quadrant(current_ratio, current_momentum)
            
            # Calculate distance from center (100, 100)
            distance = np.sqrt((current_ratio - 100)**2 + (current_momentum - 100)**2)
            
            # Calculate tail length (movement over lookback period)
            tail_length = np.sqrt(
                (current_ratio - prev_ratio)**2 + 
                (current_momentum - prev_momentum)**2
            )
            
            # Determine rotation direction
            rotation = self.calculate_rotation_direction(
                current_ratio, current_momentum,
                prev_ratio, prev_momentum
            )
            
            # Generate signal
            signal = self.generate_signal(quadrant, rotation, distance, tail_length)
            
            results[sector] = RRGPoint(
                sector=sector,
                rs_ratio=current_ratio,
                rs_momentum=current_momentum,
                quadrant=quadrant,
                distance_from_center=distance,
                rotation_direction=rotation,
                tail_length=tail_length,
                signal=signal
            )
        
        return results
    
    def get_rotation_recommendations(self, 
                                    rrg_results: Dict[str, RRGPoint]) -> dict:
        """
        Generate sector rotation recommendations
        
        Returns:
            {
                "overweight": [...],
                "underweight": [...],
                "watch_bullish": [...],
                "watch_bearish": [...],
                "rotation_alerts": [...]
            }
        """
        overweight = []
        underweight = []
        watch_bullish = []
        watch_bearish = []
        
        for sector, point in rrg_results.items():
            entry = {
                "sector": sector,
                "quadrant": point.quadrant.value,
                "rs_ratio": round(point.rs_ratio, 2),
                "rs_momentum": round(point.rs_momentum, 2),
                "rotation": point.rotation_direction,
                "tail_length": round(point.tail_length, 2),
                "signal": point.signal
            }
            
            if point.signal in ["STRONG_OVERWEIGHT", "OVERWEIGHT"]:
                overweight.append(entry)
            elif point.signal in ["STRONG_UNDERWEIGHT", "UNDERWEIGHT"]:
                underweight.append(entry)
            elif point.signal == "WATCH_BULLISH":
                watch_bullish.append(entry)
            elif point.quadrant == RRGQuadrant.WEAKENING:
                watch_bearish.append(entry)
        
        # Sort by conviction
        overweight.sort(key=lambda x: x['rs_ratio'] + x['rs_momentum'], reverse=True)
        underweight.sort(key=lambda x: x['rs_ratio'] + x['rs_momentum'])
        
        # Generate rotation alerts
        rotation_alerts = []
        
        # Alert: Sectors about to enter LEADING from IMPROVING
        for point in rrg_results.values():
            if (point.quadrant == RRGQuadrant.IMPROVING and 
                point.rotation_direction == "CLOCKWISE" and
                point.rs_ratio > 98):  # Close to crossing into Leading
                rotation_alerts.append({
                    "type": "ENTRY_SIGNAL",
                    "sector": point.sector,
                    "message": f"{point.sector} approaching LEADING quadrant - consider adding",
                    "urgency": "HIGH" if point.tail_length > 2 else "MEDIUM"
                })
        
        # Alert: Sectors about to exit LEADING into WEAKENING
        for point in rrg_results.values():
            if (point.quadrant == RRGQuadrant.LEADING and 
                point.rotation_direction == "CLOCKWISE" and
                point.rs_momentum < 102):  # Close to crossing into Weakening
                rotation_alerts.append({
                    "type": "EXIT_WARNING",
                    "sector": point.sector,
                    "message": f"{point.sector} losing momentum - consider reducing",
                    "urgency": "MEDIUM"
                })
        
        # Alert: Sectors in LAGGING showing improvement
        for point in rrg_results.values():
            if (point.quadrant == RRGQuadrant.LAGGING and 
                point.rotation_direction == "COUNTER_CLOCKWISE"):
                rotation_alerts.append({
                    "type": "TURNAROUND_WATCH",
                    "sector": point.sector,
                    "message": f"{point.sector} showing early reversal signs - add to watchlist",
                    "urgency": "LOW"
                })
        
        return {
            "overweight": overweight[:3],  # Top 3
            "underweight": underweight[:3],  # Bottom 3
            "watch_bullish": watch_bullish,
            "watch_bearish": watch_bearish,
            "rotation_alerts": rotation_alerts
        }
```

---

## 📈 Layer 2: Business Cycle Mapping

### Thai Economic Cycle & Sector Performance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BUSINESS CYCLE SECTOR ROTATION MAP                        │
│                         (Adapted for Thailand)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ECONOMIC EXPANSION                              │
│                                     ↑                                        │
│                                     │                                        │
│         EARLY EXPANSION             │            MID EXPANSION               │
│         ─────────────────           │            ──────────────              │
│         GDP: Accelerating           │            GDP: Strong                 │
│         Rates: Low → Rising         │            Rates: Rising               │
│         Inflation: Low              │            Inflation: Rising           │
│                                     │                                        │
│         OVERWEIGHT:                 │            OVERWEIGHT:                 │
│         • FINCIAL (Banks)           │            • INDUS (Industrials)       │
│         • CONSUMP (Consumer)        │            • RESOURC (Energy)          │
│         • PROPCON (Property)        │            • TECH (Technology)         │
│                                     │                                        │
│         UNDERWEIGHT:                │            UNDERWEIGHT:                │
│         • RESOURC (Energy)          │            • FINCIAL (Banks)           │
│         • AGRO (Defensive)          │            • AGRO (Defensive)          │
│                                     │                                        │
│  RECOVERY ──────────────────────────┼────────────────────────────── PEAK    │
│         │                           │                               │        │
│         │                           │                               │        │
│         LATE RECESSION              │            LATE EXPANSION              │
│         ────────────────            │            ───────────────             │
│         GDP: Bottoming              │            GDP: Slowing                │
│         Rates: Falling              │            Rates: High/Peak            │
│         Inflation: Falling          │            Inflation: High             │
│                                     │                                        │
│         OVERWEIGHT:                 │            OVERWEIGHT:                 │
│         • AGRO (Defensive)          │            • RESOURC (Commodities)     │
│         • SERVICE-Health            │            • AGRO (Defensive)          │
│         • FINCIAL (early)           │            • SERVICE-Health            │
│                                     │                                        │
│         UNDERWEIGHT:                │            UNDERWEIGHT:                │
│         • INDUS                     │            • CONSUMP                   │
│         • PROPCON                   │            • PROPCON                   │
│         • TECH                      │            • FINCIAL                   │
│                                     │                                        │
│         EARLY RECESSION             │            MID RECESSION               │
│         ───────────────             │            ─────────────               │
│         GDP: Contracting            │            GDP: Weak                   │
│         Rates: Falling              │            Rates: Low                  │
│         Inflation: Falling          │            Inflation: Low              │
│                                     │                                        │
│         OVERWEIGHT:                 │            OVERWEIGHT:                 │
│         • AGRO (Staples)            │            • AGRO (Staples)            │
│         • SERVICE-Health            │            • SERVICE-Health            │
│         • Utilities                 │            • FINCIAL (bottom)          │
│                                     │                                        │
│         UNDERWEIGHT:                │            UNDERWEIGHT:                │
│         • CONSUMP                   │            • INDUS                     │
│         • PROPCON                   │            • RESOURC                   │
│         • INDUS                     │            • TECH                      │
│                                     │                                        │
│                                     ↓                                        │
│                              ECONOMIC CONTRACTION                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Business Cycle Detection for Thailand

```python
"""
Business Cycle Detector for Thailand
Uses multiple economic indicators to determine cycle phase
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class BusinessCyclePhase(Enum):
    EARLY_EXPANSION = "EARLY_EXPANSION"    # Recovery beginning
    MID_EXPANSION = "MID_EXPANSION"        # Strong growth
    LATE_EXPANSION = "LATE_EXPANSION"      # Growth slowing, inflation rising
    EARLY_RECESSION = "EARLY_RECESSION"    # Contraction beginning
    MID_RECESSION = "MID_RECESSION"        # Deep contraction
    LATE_RECESSION = "LATE_RECESSION"      # Contraction ending


@dataclass
class EconomicIndicators:
    """Thai economic indicators for cycle detection"""
    gdp_growth_yoy: float           # GDP growth year-over-year
    gdp_growth_qoq: float           # GDP growth quarter-over-quarter
    policy_rate: float              # BOT policy rate
    rate_direction: str             # "RISING", "FALLING", "STABLE"
    cpi_yoy: float                  # Inflation year-over-year
    pmi_manufacturing: float        # Manufacturing PMI
    consumer_confidence: float      # Consumer confidence index
    set_index_ma_trend: str         # SET Index trend vs 200-day MA
    credit_growth: float            # Private credit growth
    unemployment_rate: float        # Unemployment rate


class ThaiBusinessCycleDetector:
    """
    Detect current phase of Thai business cycle
    
    Uses:
        1. GDP growth trajectory
        2. BOT policy rate direction
        3. Inflation trend
        4. PMI (leading indicator)
        5. Consumer confidence
        6. Stock market trend
    """
    
    # Sector recommendations by cycle phase
    SECTOR_RECOMMENDATIONS = {
        BusinessCyclePhase.EARLY_EXPANSION: {
            "overweight": ["FINCIAL", "CONSUMP", "PROPCON"],
            "underweight": ["RESOURC", "AGRO"],
            "rationale": "Low rates favor banks, property. Consumers start spending."
        },
        BusinessCyclePhase.MID_EXPANSION: {
            "overweight": ["INDUS", "RESOURC", "TECH"],
            "underweight": ["AGRO", "SERVICE"],
            "rationale": "Strong growth favors cyclicals. Commodity demand rises."
        },
        BusinessCyclePhase.LATE_EXPANSION: {
            "overweight": ["RESOURC", "AGRO", "SERVICE"],
            "underweight": ["CONSUMP", "PROPCON", "FINCIAL"],
            "rationale": "Inflation hedges. Defensive positioning as cycle peaks."
        },
        BusinessCyclePhase.EARLY_RECESSION: {
            "overweight": ["AGRO", "SERVICE", "FINCIAL"],
            "underweight": ["CONSUMP", "PROPCON", "INDUS"],
            "rationale": "Defensive sectors. Healthcare stable. Banks benefit from rate cuts."
        },
        BusinessCyclePhase.MID_RECESSION: {
            "overweight": ["AGRO", "SERVICE"],
            "underweight": ["INDUS", "RESOURC", "TECH", "PROPCON"],
            "rationale": "Maximum defense. Only staples and healthcare."
        },
        BusinessCyclePhase.LATE_RECESSION: {
            "overweight": ["FINCIAL", "PROPCON", "CONSUMP"],
            "underweight": ["RESOURC"],
            "rationale": "Anticipate recovery. Rate-sensitive sectors first."
        }
    }
    
    def detect_cycle_phase(self, indicators: EconomicIndicators) -> Dict:
        """
        Determine current business cycle phase
        
        Returns:
            {
                "phase": BusinessCyclePhase,
                "confidence": float (0-1),
                "indicators_analysis": {...},
                "sector_recommendations": {...}
            }
        """
        scores = {phase: 0 for phase in BusinessCyclePhase}
        
        # GDP Growth Analysis
        if indicators.gdp_growth_yoy > 4:
            if indicators.gdp_growth_qoq > indicators.gdp_growth_yoy / 4:
                scores[BusinessCyclePhase.MID_EXPANSION] += 2
            else:
                scores[BusinessCyclePhase.LATE_EXPANSION] += 2
        elif indicators.gdp_growth_yoy > 2:
            if indicators.gdp_growth_qoq > 0:
                scores[BusinessCyclePhase.EARLY_EXPANSION] += 2
            else:
                scores[BusinessCyclePhase.LATE_EXPANSION] += 1
        elif indicators.gdp_growth_yoy > 0:
            scores[BusinessCyclePhase.LATE_RECESSION] += 2
        else:
            if indicators.gdp_growth_qoq < 0:
                scores[BusinessCyclePhase.MID_RECESSION] += 2
            else:
                scores[BusinessCyclePhase.EARLY_RECESSION] += 2
        
        # Interest Rate Direction
        if indicators.rate_direction == "RISING":
            scores[BusinessCyclePhase.MID_EXPANSION] += 1
            scores[BusinessCyclePhase.LATE_EXPANSION] += 1
        elif indicators.rate_direction == "FALLING":
            scores[BusinessCyclePhase.EARLY_RECESSION] += 1
            scores[BusinessCyclePhase.MID_RECESSION] += 1
            scores[BusinessCyclePhase.LATE_RECESSION] += 1
        else:  # STABLE
            if indicators.policy_rate < 2:
                scores[BusinessCyclePhase.EARLY_EXPANSION] += 1
            else:
                scores[BusinessCyclePhase.LATE_EXPANSION] += 1
        
        # Inflation
        if indicators.cpi_yoy > 3:
            scores[BusinessCyclePhase.LATE_EXPANSION] += 2
        elif indicators.cpi_yoy > 1.5:
            scores[BusinessCyclePhase.MID_EXPANSION] += 1
        elif indicators.cpi_yoy > 0:
            scores[BusinessCyclePhase.EARLY_EXPANSION] += 1
        else:
            scores[BusinessCyclePhase.MID_RECESSION] += 1
        
        # PMI (Leading indicator)
        if indicators.pmi_manufacturing > 55:
            scores[BusinessCyclePhase.MID_EXPANSION] += 2
        elif indicators.pmi_manufacturing > 50:
            scores[BusinessCyclePhase.EARLY_EXPANSION] += 1
            scores[BusinessCyclePhase.LATE_EXPANSION] += 1
        elif indicators.pmi_manufacturing > 45:
            scores[BusinessCyclePhase.LATE_RECESSION] += 1
        else:
            scores[BusinessCyclePhase.MID_RECESSION] += 2
        
        # Consumer Confidence
        if indicators.consumer_confidence > 100:
            scores[BusinessCyclePhase.MID_EXPANSION] += 1
        elif indicators.consumer_confidence > 80:
            scores[BusinessCyclePhase.EARLY_EXPANSION] += 1
        elif indicators.consumer_confidence > 60:
            scores[BusinessCyclePhase.LATE_RECESSION] += 1
        else:
            scores[BusinessCyclePhase.MID_RECESSION] += 1
        
        # Stock Market Trend
        if indicators.set_index_ma_trend == "ABOVE_200MA":
            scores[BusinessCyclePhase.EARLY_EXPANSION] += 1
            scores[BusinessCyclePhase.MID_EXPANSION] += 1
        else:
            scores[BusinessCyclePhase.EARLY_RECESSION] += 1
            scores[BusinessCyclePhase.MID_RECESSION] += 1
        
        # Determine phase with highest score
        max_score = max(scores.values())
        detected_phase = max(scores, key=scores.get)
        
        # Calculate confidence
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0
        
        return {
            "phase": detected_phase,
            "confidence": round(confidence, 2),
            "scores": {phase.value: score for phase, score in scores.items()},
            "indicators_summary": {
                "gdp_growth": indicators.gdp_growth_yoy,
                "policy_rate": indicators.policy_rate,
                "rate_direction": indicators.rate_direction,
                "inflation": indicators.cpi_yoy,
                "pmi": indicators.pmi_manufacturing
            },
            "sector_recommendations": self.SECTOR_RECOMMENDATIONS[detected_phase]
        }
```

---

## 🔀 Layer 3: Sector Momentum & Trend

### Multi-Timeframe Sector Momentum

```python
"""
Sector Momentum Analysis
Analyzes momentum across multiple timeframes for trend confirmation
"""

class SectorMomentumAnalyzer:
    """
    Analyze sector momentum using multiple timeframes
    
    Timeframes:
        - Short: 1 month (21 trading days)
        - Medium: 3 months (63 trading days)
        - Long: 6 months (126 trading days)
        - Very Long: 12 months (252 trading days)
    """
    
    def __init__(self):
        self.timeframes = {
            "1m": 21,
            "3m": 63,
            "6m": 126,
            "12m": 252
        }
    
    def calculate_sector_momentum(self, 
                                 sector_data: Dict[str, pd.DataFrame],
                                 benchmark_data: pd.DataFrame) -> Dict[str, dict]:
        """
        Calculate momentum metrics for each sector
        
        Returns:
            {
                "FINCIAL": {
                    "absolute_momentum": {...},
                    "relative_momentum": {...},
                    "trend_strength": {...},
                    "composite_score": float,
                    "signal": str
                },
                ...
            }
        """
        results = {}
        benchmark_close = benchmark_data['close']
        
        for sector, data in sector_data.items():
            sector_close = data['close']
            
            # Absolute Momentum (sector's own performance)
            abs_momentum = {}
            for tf_name, days in self.timeframes.items():
                if len(sector_close) > days:
                    ret = (sector_close.iloc[-1] / sector_close.iloc[-days] - 1) * 100
                    abs_momentum[tf_name] = round(ret, 2)
                else:
                    abs_momentum[tf_name] = None
            
            # Relative Momentum (vs benchmark)
            rel_momentum = {}
            for tf_name, days in self.timeframes.items():
                if len(sector_close) > days and len(benchmark_close) > days:
                    sector_ret = sector_close.iloc[-1] / sector_close.iloc[-days] - 1
                    bench_ret = benchmark_close.iloc[-1] / benchmark_close.iloc[-days] - 1
                    rel_ret = (sector_ret - bench_ret) * 100
                    rel_momentum[tf_name] = round(rel_ret, 2)
                else:
                    rel_momentum[tf_name] = None
            
            # Trend Strength (ADX-based)
            trend_strength = self._calculate_trend_strength(data)
            
            # Moving Average Alignment
            ma_alignment = self._calculate_ma_alignment(sector_close)
            
            # Composite Score
            composite = self._calculate_composite_score(
                abs_momentum, rel_momentum, trend_strength, ma_alignment
            )
            
            # Generate Signal
            signal = self._generate_signal(composite, rel_momentum, ma_alignment)
            
            results[sector] = {
                "absolute_momentum": abs_momentum,
                "relative_momentum": rel_momentum,
                "trend_strength": trend_strength,
                "ma_alignment": ma_alignment,
                "composite_score": composite,
                "signal": signal
            }
        
        return results
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> dict:
        """Calculate ADX-based trend strength"""
        # Simplified ADX calculation
        high = data['high']
        low = data['low']
        close = data['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        
        # Directional Movement
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        plus_di = 100 * pd.Series(plus_dm).rolling(14).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(14).mean() / atr
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(14).mean()
        
        current_adx = adx.iloc[-1] if not np.isnan(adx.iloc[-1]) else 0
        current_plus_di = plus_di.iloc[-1] if not np.isnan(plus_di.iloc[-1]) else 0
        current_minus_di = minus_di.iloc[-1] if not np.isnan(minus_di.iloc[-1]) else 0
        
        if current_adx > 25:
            if current_plus_di > current_minus_di:
                trend = "STRONG_UPTREND"
            else:
                trend = "STRONG_DOWNTREND"
        elif current_adx > 20:
            if current_plus_di > current_minus_di:
                trend = "WEAK_UPTREND"
            else:
                trend = "WEAK_DOWNTREND"
        else:
            trend = "NO_TREND"
        
        return {
            "adx": round(current_adx, 1),
            "plus_di": round(current_plus_di, 1),
            "minus_di": round(current_minus_di, 1),
            "trend": trend
        }
    
    def _calculate_ma_alignment(self, prices: pd.Series) -> dict:
        """Check if price is above/below key moving averages"""
        current_price = prices.iloc[-1]
        
        ma_20 = prices.rolling(20).mean().iloc[-1]
        ma_50 = prices.rolling(50).mean().iloc[-1]
        ma_100 = prices.rolling(100).mean().iloc[-1]
        ma_200 = prices.rolling(200).mean().iloc[-1]
        
        above_count = sum([
            current_price > ma_20,
            current_price > ma_50,
            current_price > ma_100,
            current_price > ma_200
        ])
        
        # Check MA stack (bullish: 20 > 50 > 100 > 200)
        bullish_stack = ma_20 > ma_50 > ma_100 > ma_200
        bearish_stack = ma_20 < ma_50 < ma_100 < ma_200
        
        if bullish_stack and above_count == 4:
            alignment = "PERFECT_BULLISH"
        elif above_count >= 3:
            alignment = "BULLISH"
        elif above_count == 2:
            alignment = "NEUTRAL"
        elif bearish_stack and above_count == 0:
            alignment = "PERFECT_BEARISH"
        else:
            alignment = "BEARISH"
        
        return {
            "above_ma_count": above_count,
            "alignment": alignment,
            "price_vs_200ma": round((current_price / ma_200 - 1) * 100, 2)
        }
    
    def _calculate_composite_score(self,
                                  abs_mom: dict,
                                  rel_mom: dict,
                                  trend: dict,
                                  ma: dict) -> float:
        """Calculate composite momentum score (0-100)"""
        score = 50  # Start neutral
        
        # Relative momentum contribution (40 points max)
        if rel_mom.get('3m') is not None:
            score += min(20, max(-20, rel_mom['3m'] * 2))
        if rel_mom.get('6m') is not None:
            score += min(10, max(-10, rel_mom['6m']))
        if rel_mom.get('12m') is not None:
            score += min(10, max(-10, rel_mom['12m'] * 0.5))
        
        # Trend strength contribution (20 points max)
        if trend['trend'] == "STRONG_UPTREND":
            score += 20
        elif trend['trend'] == "WEAK_UPTREND":
            score += 10
        elif trend['trend'] == "STRONG_DOWNTREND":
            score -= 20
        elif trend['trend'] == "WEAK_DOWNTREND":
            score -= 10
        
        # MA alignment contribution (20 points max)
        if ma['alignment'] == "PERFECT_BULLISH":
            score += 20
        elif ma['alignment'] == "BULLISH":
            score += 10
        elif ma['alignment'] == "PERFECT_BEARISH":
            score -= 20
        elif ma['alignment'] == "BEARISH":
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_signal(self, 
                        composite: float, 
                        rel_mom: dict, 
                        ma: dict) -> str:
        """Generate trading signal based on analysis"""
        if composite >= 75 and ma['alignment'] in ["PERFECT_BULLISH", "BULLISH"]:
            return "STRONG_OVERWEIGHT"
        elif composite >= 60:
            return "OVERWEIGHT"
        elif composite <= 25 and ma['alignment'] in ["PERFECT_BEARISH", "BEARISH"]:
            return "STRONG_UNDERWEIGHT"
        elif composite <= 40:
            return "UNDERWEIGHT"
        else:
            return "NEUTRAL"
```

---

## 🎯 Layer 4: Confluence Scoring & Final Recommendations

### Combining All Signals

```python
"""
Sector Rotation Confluence Engine
Combines RRG, Business Cycle, and Momentum for final recommendations
"""

@dataclass
class SectorRotationSignal:
    sector: str
    rrg_signal: str
    rrg_quadrant: str
    cycle_recommendation: str
    momentum_signal: str
    momentum_score: float
    confluence_score: float
    final_recommendation: str
    weight_recommendation: float  # -1 to +1 (-1 = max underweight, +1 = max overweight)
    rotation_alert: Optional[str]


class SectorRotationEngine:
    """
    Master engine that combines all sector rotation signals
    
    Confluence Logic:
        - All 3 signals agree: HIGH CONVICTION
        - 2 of 3 signals agree: MEDIUM CONVICTION
        - Signals conflict: LOW CONVICTION / NEUTRAL
    """
    
    def __init__(self):
        self.rrg = RelativeRotationGraph()
        self.cycle_detector = ThaiBusinessCycleDetector()
        self.momentum_analyzer = SectorMomentumAnalyzer()
        
        # Weight for each signal source
        self.weights = {
            "rrg": 0.40,           # RRG is primary
            "cycle": 0.30,         # Business cycle secondary
            "momentum": 0.30       # Momentum confirmation
        }
    
    def analyze_sectors(self,
                       sector_data: Dict[str, pd.DataFrame],
                       benchmark_data: pd.DataFrame,
                       economic_indicators: EconomicIndicators) -> dict:
        """
        Complete sector rotation analysis
        
        Returns:
            {
                "timestamp": str,
                "market_regime": {...},
                "business_cycle": {...},
                "sector_signals": {...},
                "recommendations": {
                    "overweight": [...],
                    "underweight": [...],
                    "neutral": [...]
                },
                "rotation_alerts": [...],
                "suggested_allocation": {...}
            }
        """
        # Step 1: RRG Analysis
        rrg_results = self.rrg.calculate_rrg(sector_data, benchmark_data)
        rrg_recommendations = self.rrg.get_rotation_recommendations(rrg_results)
        
        # Step 2: Business Cycle Analysis
        cycle_analysis = self.cycle_detector.detect_cycle_phase(economic_indicators)
        cycle_overweight = set(cycle_analysis['sector_recommendations']['overweight'])
        cycle_underweight = set(cycle_analysis['sector_recommendations']['underweight'])
        
        # Step 3: Momentum Analysis
        momentum_results = self.momentum_analyzer.calculate_sector_momentum(
            sector_data, benchmark_data
        )
        
        # Step 4: Confluence Scoring
        sector_signals = {}
        for sector in sector_data.keys():
            # RRG signal
            rrg_point = rrg_results.get(sector)
            rrg_signal = rrg_point.signal if rrg_point else "NEUTRAL"
            rrg_quadrant = rrg_point.quadrant.value if rrg_point else "UNKNOWN"
            
            # Cycle signal
            if sector in cycle_overweight:
                cycle_signal = "OVERWEIGHT"
            elif sector in cycle_underweight:
                cycle_signal = "UNDERWEIGHT"
            else:
                cycle_signal = "NEUTRAL"
            
            # Momentum signal
            mom_data = momentum_results.get(sector, {})
            mom_signal = mom_data.get('signal', 'NEUTRAL')
            mom_score = mom_data.get('composite_score', 50)
            
            # Calculate confluence
            confluence = self._calculate_confluence(
                rrg_signal, cycle_signal, mom_signal, mom_score
            )
            
            # Generate final recommendation
            final_rec, weight = self._generate_final_recommendation(
                rrg_signal, cycle_signal, mom_signal, confluence
            )
            
            # Check for rotation alerts
            alert = self._check_rotation_alert(rrg_point, mom_data, cycle_signal)
            
            sector_signals[sector] = SectorRotationSignal(
                sector=sector,
                rrg_signal=rrg_signal,
                rrg_quadrant=rrg_quadrant,
                cycle_recommendation=cycle_signal,
                momentum_signal=mom_signal,
                momentum_score=mom_score,
                confluence_score=confluence,
                final_recommendation=final_rec,
                weight_recommendation=weight,
                rotation_alert=alert
            )
        
        # Step 5: Sort and categorize recommendations
        sorted_sectors = sorted(
            sector_signals.values(),
            key=lambda x: x.weight_recommendation,
            reverse=True
        )
        
        overweight = [s for s in sorted_sectors if s.weight_recommendation > 0.2]
        underweight = [s for s in sorted_sectors if s.weight_recommendation < -0.2]
        neutral = [s for s in sorted_sectors if -0.2 <= s.weight_recommendation <= 0.2]
        
        # Step 6: Generate allocation suggestion
        allocation = self._generate_allocation(sorted_sectors)
        
        # Collect rotation alerts
        all_alerts = [s.rotation_alert for s in sorted_sectors if s.rotation_alert]
        all_alerts.extend(rrg_recommendations.get('rotation_alerts', []))
        
        return {
            "timestamp": pd.Timestamp.now().isoformat(),
            "business_cycle": {
                "phase": cycle_analysis['phase'].value,
                "confidence": cycle_analysis['confidence']
            },
            "sector_signals": {
                sector: {
                    "rrg_quadrant": sig.rrg_quadrant,
                    "rrg_signal": sig.rrg_signal,
                    "cycle_recommendation": sig.cycle_recommendation,
                    "momentum_signal": sig.momentum_signal,
                    "momentum_score": sig.momentum_score,
                    "confluence_score": sig.confluence_score,
                    "final_recommendation": sig.final_recommendation,
                    "weight": sig.weight_recommendation
                }
                for sector, sig in sector_signals.items()
            },
            "recommendations": {
                "overweight": [
                    {"sector": s.sector, "weight": s.weight_recommendation, 
                     "confluence": s.confluence_score}
                    for s in overweight
                ],
                "underweight": [
                    {"sector": s.sector, "weight": s.weight_recommendation,
                     "confluence": s.confluence_score}
                    for s in underweight
                ],
                "neutral": [
                    {"sector": s.sector, "weight": s.weight_recommendation}
                    for s in neutral
                ]
            },
            "rotation_alerts": all_alerts,
            "suggested_allocation": allocation
        }
    
    def _calculate_confluence(self,
                             rrg: str,
                             cycle: str,
                             momentum: str,
                             mom_score: float) -> float:
        """
        Calculate confluence score (0-100)
        
        Higher score = more signals agree = higher conviction
        """
        # Normalize signals to numerical values
        signal_values = {
            "STRONG_OVERWEIGHT": 2,
            "OVERWEIGHT": 1,
            "WATCH_BULLISH": 0.5,
            "NEUTRAL": 0,
            "HOLD": 0,
            "WATCH_BEARISH": -0.5,
            "UNDERWEIGHT": -1,
            "STRONG_UNDERWEIGHT": -2
        }
        
        rrg_val = signal_values.get(rrg, 0)
        cycle_val = signal_values.get(cycle, 0)
        mom_val = signal_values.get(momentum, 0)
        
        # Check agreement
        signals = [rrg_val, cycle_val, mom_val]
        all_positive = all(s > 0 for s in signals)
        all_negative = all(s < 0 for s in signals)
        mixed = not (all_positive or all_negative)
        
        if all_positive:
            # All bullish - high confluence
            avg_strength = np.mean([abs(s) for s in signals])
            confluence = 70 + avg_strength * 15  # 70-100
        elif all_negative:
            # All bearish - high confluence (but negative)
            avg_strength = np.mean([abs(s) for s in signals])
            confluence = 70 + avg_strength * 15  # 70-100
        else:
            # Mixed signals - low confluence
            agreement = sum(1 for s in signals if s > 0) / len(signals)
            if agreement == 0:
                agreement = sum(1 for s in signals if s < 0) / len(signals)
            confluence = 30 + agreement * 40  # 30-70
        
        return round(confluence, 1)
    
    def _generate_final_recommendation(self,
                                       rrg: str,
                                       cycle: str,
                                       momentum: str,
                                       confluence: float) -> Tuple[str, float]:
        """
        Generate final recommendation and weight
        
        Returns:
            (recommendation: str, weight: float)
            weight ranges from -1 (max underweight) to +1 (max overweight)
        """
        # Count bullish vs bearish signals
        bullish_signals = sum([
            rrg in ["STRONG_OVERWEIGHT", "OVERWEIGHT", "WATCH_BULLISH"],
            cycle == "OVERWEIGHT",
            momentum in ["STRONG_OVERWEIGHT", "OVERWEIGHT"]
        ])
        
        bearish_signals = sum([
            rrg in ["STRONG_UNDERWEIGHT", "UNDERWEIGHT"],
            cycle == "UNDERWEIGHT",
            momentum in ["STRONG_UNDERWEIGHT", "UNDERWEIGHT"]
        ])
        
        # High confluence bullish
        if bullish_signals >= 2 and confluence >= 70:
            if bullish_signals == 3:
                return "STRONG_OVERWEIGHT", 1.0
            else:
                return "OVERWEIGHT", 0.6
        
        # High confluence bearish
        elif bearish_signals >= 2 and confluence >= 70:
            if bearish_signals == 3:
                return "STRONG_UNDERWEIGHT", -1.0
            else:
                return "UNDERWEIGHT", -0.6
        
        # Medium confluence
        elif bullish_signals > bearish_signals:
            return "SLIGHT_OVERWEIGHT", 0.3
        elif bearish_signals > bullish_signals:
            return "SLIGHT_UNDERWEIGHT", -0.3
        else:
            return "NEUTRAL", 0.0
    
    def _check_rotation_alert(self,
                             rrg_point: Optional[RRGPoint],
                             momentum: dict,
                             cycle: str) -> Optional[str]:
        """Check for actionable rotation alerts"""
        alerts = []
        
        if rrg_point:
            # About to enter LEADING
            if (rrg_point.quadrant == RRGQuadrant.IMPROVING and 
                rrg_point.rs_ratio > 98 and
                rrg_point.rotation_direction == "CLOCKWISE"):
                alerts.append(f"🟢 {rrg_point.sector}: Approaching LEADING quadrant")
            
            # About to exit LEADING
            if (rrg_point.quadrant == RRGQuadrant.LEADING and
                rrg_point.rs_momentum < 101):
                alerts.append(f"🟡 {rrg_point.sector}: Momentum fading in LEADING")
            
            # Potential turnaround from LAGGING
            if (rrg_point.quadrant == RRGQuadrant.LAGGING and
                rrg_point.rotation_direction == "COUNTER_CLOCKWISE"):
                alerts.append(f"👀 {rrg_point.sector}: Unusual rotation - watch for turnaround")
        
        # Momentum divergence from cycle
        if momentum.get('signal') == 'STRONG_OVERWEIGHT' and cycle == 'UNDERWEIGHT':
            alerts.append(f"⚠️ Momentum vs Cycle divergence")
        
        return " | ".join(alerts) if alerts else None
    
    def _generate_allocation(self, 
                            sorted_sectors: List[SectorRotationSignal]) -> Dict[str, float]:
        """
        Generate suggested portfolio allocation
        
        Base allocation: Equal weight (12.5% each for 8 sectors)
        Adjust based on weight_recommendation
        """
        n_sectors = len(sorted_sectors)
        base_weight = 100 / n_sectors
        
        allocation = {}
        total_adjustment = 0
        
        for sector in sorted_sectors:
            # Weight adjustment: -5% to +5% from base
            adjustment = sector.weight_recommendation * 5
            allocation[sector.sector] = base_weight + adjustment
            total_adjustment += adjustment
        
        # Normalize to ensure total = 100%
        total = sum(allocation.values())
        allocation = {k: round(v / total * 100, 1) for k, v in allocation.items()}
        
        return allocation
```

---

## 📊 Integration with Your 20-Model System

### How Sector Rotation Fits Into the Funnel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ENHANCED FUNNEL WITH SECTOR ROTATION                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   STAGE 0: MARKET REGIME DETECTION (Existing)                               │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  NEW: SECTOR ROTATION ANALYSIS                                    │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  • RRG Analysis → Which sectors are leading/lagging?             │      │
│   │  • Business Cycle → Which sectors SHOULD be leading?             │      │
│   │  • Momentum Analysis → Confirmation                              │      │
│   │                                                                   │      │
│   │  Output:                                                          │      │
│   │  • OVERWEIGHT sectors (2-3)                                      │      │
│   │  • UNDERWEIGHT sectors (2-3)                                     │      │
│   │  • Sector weight multipliers                                     │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   STAGE 1-7: STOCK SCREENING (Existing)                                     │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  ENHANCED STAGE 8: ENSEMBLE WITH SECTOR WEIGHTS                   │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │                                                                   │      │
│   │  Stock_Final_Score = Base_Score × Sector_Multiplier              │      │
│   │                                                                   │      │
│   │  Sector Multipliers:                                              │      │
│   │  • STRONG_OVERWEIGHT sector: 1.20x                               │      │
│   │  • OVERWEIGHT sector: 1.10x                                      │      │
│   │  • NEUTRAL sector: 1.00x                                         │      │
│   │  • UNDERWEIGHT sector: 0.90x                                     │      │
│   │  • STRONG_UNDERWEIGHT sector: 0.80x                              │      │
│   │                                                                   │      │
│   │  Effect: Stocks in favored sectors get boosted                   │      │
│   │          Stocks in unfavored sectors get penalized               │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   STAGE 9: FINAL OUTPUT (Enhanced)                                          │
│              │                                                               │
│              ├── TOP 20 BUY (sector-adjusted)                               │
│              ├── TOP 20 AVOID (sector-adjusted)                             │
│              └── SECTOR ALLOCATION RECOMMENDATION                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Code Integration

```python
"""
Integration point: Add sector rotation to orchestrator
"""

class EnhancedQuantOrchestrator:
    """
    Enhanced orchestrator with sector rotation
    """
    
    def __init__(self):
        # Existing components
        self.regime_engine = RegimeEngine()
        self.model_orchestrator = ModelOrchestrator()
        self.ensemble_engine = EnsembleEngine()
        
        # NEW: Sector rotation
        self.sector_rotation = SectorRotationEngine()
    
    def run_full_screening(self,
                          universe_price_data: Dict[str, pd.DataFrame],
                          universe_fundamentals: Dict[str, dict],
                          market_index_data: pd.DataFrame,
                          sector_index_data: Dict[str, pd.DataFrame],
                          economic_indicators: EconomicIndicators) -> dict:
        """
        Enhanced screening with sector rotation
        """
        # Step 1: Market Regime
        regime = self.regime_engine.detect(market_index_data)
        
        # Step 2: NEW - Sector Rotation Analysis
        sector_analysis = self.sector_rotation.analyze_sectors(
            sector_data=sector_index_data,
            benchmark_data=market_index_data,
            economic_indicators=economic_indicators
        )
        
        # Create sector multipliers
        sector_multipliers = {}
        for sector, data in sector_analysis['sector_signals'].items():
            weight = data['weight']
            if weight >= 0.6:
                sector_multipliers[sector] = 1.20
            elif weight >= 0.2:
                sector_multipliers[sector] = 1.10
            elif weight <= -0.6:
                sector_multipliers[sector] = 0.80
            elif weight <= -0.2:
                sector_multipliers[sector] = 0.90
            else:
                sector_multipliers[sector] = 1.00
        
        # Step 3-7: Run stock models (existing)
        stock_scores = self.model_orchestrator.run_all_models(
            universe_price_data,
            universe_fundamentals,
            regime
        )
        
        # Step 8: Enhanced Ensemble with Sector Multipliers
        for ticker, score_data in stock_scores.items():
            stock_sector = self._get_stock_sector(ticker)
            multiplier = sector_multipliers.get(stock_sector, 1.0)
            
            # Apply sector multiplier
            score_data['base_score'] = score_data['composite_score']
            score_data['sector_multiplier'] = multiplier
            score_data['composite_score'] = score_data['base_score'] * multiplier
            score_data['sector'] = stock_sector
            score_data['sector_recommendation'] = sector_analysis['sector_signals'].get(
                stock_sector, {}
            ).get('final_recommendation', 'NEUTRAL')
        
        # Step 9: Final Output
        sorted_stocks = sorted(
            stock_scores.items(),
            key=lambda x: x[1]['composite_score'],
            reverse=True
        )
        
        return {
            "regime": regime,
            "sector_rotation": sector_analysis,
            "sector_multipliers": sector_multipliers,
            "top_20_buy": [
                {
                    "rank": i + 1,
                    "ticker": ticker,
                    "sector": data['sector'],
                    "base_score": data['base_score'],
                    "sector_multiplier": data['sector_multiplier'],
                    "final_score": data['composite_score'],
                    "sector_recommendation": data['sector_recommendation']
                }
                for i, (ticker, data) in enumerate(sorted_stocks[:20])
            ],
            "top_20_avoid": [
                {
                    "rank": i + 1,
                    "ticker": ticker,
                    "sector": data['sector'],
                    "base_score": data['base_score'],
                    "sector_multiplier": data['sector_multiplier'],
                    "final_score": data['composite_score']
                }
                for i, (ticker, data) in enumerate(reversed(sorted_stocks[-20:]))
            ],
            "sector_allocation": sector_analysis['suggested_allocation'],
            "rotation_alerts": sector_analysis['rotation_alerts']
        }
```

---

## 📈 Example Output

```json
{
  "timestamp": "2026-01-01T10:00:00",
  "regime": {
    "trend": "BULL",
    "volatility": "NORMAL_VOL",
    "confidence": 0.78
  },
  "sector_rotation": {
    "business_cycle": {
      "phase": "MID_EXPANSION",
      "confidence": 0.72
    },
    "recommendations": {
      "overweight": [
        {"sector": "TECH", "weight": 0.85, "confluence": 88.5},
        {"sector": "INDUS", "weight": 0.62, "confluence": 75.2},
        {"sector": "RESOURC", "weight": 0.45, "confluence": 68.0}
      ],
      "underweight": [
        {"sector": "PROPCON", "weight": -0.72, "confluence": 82.1},
        {"sector": "AGRO", "weight": -0.55, "confluence": 71.3}
      ],
      "neutral": [
        {"sector": "FINCIAL", "weight": 0.12},
        {"sector": "CONSUMP", "weight": -0.08},
        {"sector": "SERVICE", "weight": 0.05}
      ]
    },
    "rotation_alerts": [
      {
        "type": "ENTRY_SIGNAL",
        "sector": "TECH",
        "message": "TECH approaching LEADING quadrant - consider adding",
        "urgency": "HIGH"
      },
      {
        "type": "EXIT_WARNING",
        "sector": "FINCIAL",
        "message": "FINCIAL losing momentum - consider reducing",
        "urgency": "MEDIUM"
      }
    ]
  },
  "sector_multipliers": {
    "TECH": 1.20,
    "INDUS": 1.10,
    "RESOURC": 1.10,
    "FINCIAL": 1.00,
    "CONSUMP": 1.00,
    "SERVICE": 1.00,
    "PROPCON": 0.85,
    "AGRO": 0.90
  },
  "suggested_allocation": {
    "TECH": 17.5,
    "INDUS": 14.2,
    "RESOURC": 13.8,
    "FINCIAL": 12.5,
    "CONSUMP": 12.3,
    "SERVICE": 12.5,
    "PROPCON": 8.5,
    "AGRO": 8.7
  },
  "top_20_buy": [
    {
      "rank": 1,
      "ticker": "DELTA",
      "sector": "TECH",
      "base_score": 88.5,
      "sector_multiplier": 1.20,
      "final_score": 106.2,
      "sector_recommendation": "STRONG_OVERWEIGHT"
    }
  ]
}
```

---

## 🎯 Quick Reference: When to Rotate

| Signal | Action |
|--------|--------|
| **RRG: IMPROVING → LEADING** | ADD to sector |
| **RRG: LEADING → WEAKENING** | START reducing |
| **RRG: WEAKENING → LAGGING** | EXIT sector |
| **RRG: LAGGING → IMPROVING** | WATCH for entry |
| **Cycle shifts to EARLY_EXPANSION** | ADD Financials, Property |
| **Cycle shifts to LATE_EXPANSION** | ADD Resources, Defensives |
| **Cycle shifts to RECESSION** | ADD Staples, Healthcare |
| **3+ signals agree OVERWEIGHT** | Maximum position |
| **3+ signals agree UNDERWEIGHT** | Zero/minimal position |

---

*Document Version: 1.0*
*Last Updated: January 2026*

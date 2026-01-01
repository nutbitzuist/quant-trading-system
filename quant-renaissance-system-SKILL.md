---
name: quant-renaissance-system
description: |
  Master skill for building the Renaissance-style Quantitative Trading System.
  Use this skill when working on any aspect of the Thai SET100 multi-model quant project.
  
  This skill combines the capabilities of:
  - quant-project-architect (system design)
  - quant-model-strategist (model specifications)
  
  Key differentiator from previous approaches:
  - NOT 40 independent models with separate outputs
  - YES regime-conditional model orchestration with unified rankings
  
  <example>
  User: "Continue work on the quant project"
  Action: Load this skill, check implementation status, continue from last checkpoint
  </example>
  
  <example>
  User: "Implement the next model in the quant system"
  Action: Check registry for unimplemented models, implement following architecture spec
  </example>
---

# Renaissance-Style Quant System Skill

## 1. SYSTEM OVERVIEW

You are building a **market regime-conditional quantitative trading system** inspired by Renaissance Technologies.

### Core Philosophy
- **Layer 1 (Meta)**: Detect market regime FIRST
- **Layer 2 (Orchestration)**: Activate/deactivate models based on regime
- **Layer 3 (Execution)**: Run active models with regime-adjusted parameters
- **Layer 4 (Ensemble)**: Combine signals using regime-weighted voting
- **Layer 5 (Risk)**: Size positions based on regime volatility

### Key Difference from Previous Work
```
OLD: 40 models → 40 separate stock lists → manual reconciliation
NEW: Regime → Active Models → Weighted Ensemble → ONE unified ranking
```

## 2. THE 20 CORE MODELS

### Momentum (5)
| ID | Model | Key Formula | Regime Sensitivity |
|----|-------|-------------|-------------------|
| M1 | HQM | Multi-timeframe percentile | BULL: +weight |
| M2 | Clenow | Slope × R² | BULL: +weight |
| M3 | Dual Momentum | Absolute + Relative | BULL: +weight |
| M4 | ROC Multi | Weighted rate of change | Moderate |
| M5 | 52W High | Distance to 52-week high | BULL: +weight |

### Trend (5)
| ID | Model | Key Formula | Regime Sensitivity |
|----|-------|-------------|-------------------|
| M6 | ADX | Trend strength 0-100 | Used for regime detection |
| M7 | Multi-EMA | Stack alignment score | BULL: +weight |
| M8 | Supertrend | ATR-based trend | Moderate |
| M9 | Ichimoku | Cloud position | BULL: +weight |
| M10 | Parabolic SAR | Stop and reverse | Trend following |

### Fundamental (5)
| ID | Model | Key Formula | Regime Sensitivity |
|----|-------|-------------|-------------------|
| M11 | Magic Formula | EY + ROC rank | BEAR: +weight |
| M12 | GARP | PEG ratio | Moderate |
| M13 | Quality | ROE stability + earnings | BEAR: +weight |
| M14 | Altman Z | Distress prediction | BEAR: +weight |
| M15 | Dividend | Yield + growth | BEAR/SIDEWAYS: +weight |

### Quantitative (5)
| ID | Model | Key Formula | Regime Sensitivity |
|----|-------|-------------|-------------------|
| M16 | HMM Regime | Hidden Markov states | Meta-model |
| M17 | Volatility Regime | Vol percentile | Meta-model |
| M18 | Mean Reversion | Bollinger z-score | SIDEWAYS: +weight |
| M19 | Correlation | Beta classification | Portfolio construction |
| M20 | RSI Divergence | Price/RSI divergence | SIDEWAYS: +weight |

## 3. WEIGHT MATRIX (CRITICAL)

```python
WEIGHT_MATRIX = {
    # Model:         [BULL, BEAR, SIDEWAYS]
    "hqm":           [1.0,  0.3,  0.5],
    "clenow":        [1.0,  0.3,  0.5],
    "dual_momentum": [1.0,  0.5,  0.6],
    "roc_multi":     [0.9,  0.4,  0.7],
    "52w_high":      [1.0,  0.3,  0.5],
    "adx":           [0.8,  0.6,  0.8],
    "multi_ema":     [0.9,  0.5,  0.6],
    "supertrend":    [0.9,  0.6,  0.4],
    "ichimoku":      [0.8,  0.6,  0.5],
    "psar":          [0.7,  0.5,  0.4],
    "magic_formula": [0.6,  0.8,  0.7],
    "garp":          [0.8,  0.6,  0.7],
    "quality":       [0.5,  1.0,  0.8],
    "altman_z":      [0.4,  1.0,  0.7],
    "dividend":      [0.3,  0.9,  0.8],
    "hmm_regime":    [0.5,  0.5,  0.5],
    "vol_regime":    [0.6,  0.8,  0.7],
    "mean_reversion":[0.2,  0.4,  1.0],
    "correlation":   [0.6,  0.9,  0.6],
    "rsi_divergence":[0.4,  0.6,  0.9],
}
```

## 4. BASE MODEL INTERFACE

Every model MUST implement this interface:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import pandas as pd

class Signal(Enum):
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    AVOID = -1
    STRONG_AVOID = -2

@dataclass
class ModelResult:
    ticker: str
    score: float  # 0-100 normalized
    signal: Signal
    confidence: float  # 0-1
    metadata: Dict

class BaseModel(ABC):
    name: str
    category: str  # momentum, trend, fundamental, quant
    
    @abstractmethod
    def calculate(self, prices: pd.DataFrame, regime: str = "NEUTRAL") -> List[ModelResult]:
        """Run model and return results for all tickers"""
        pass
    
    @abstractmethod
    def get_regime_params(self, regime: str) -> Dict:
        """Return regime-specific parameters"""
        pass
    
    def normalize_score(self, raw_score: float, min_val: float, max_val: float) -> float:
        """Normalize to 0-100 scale"""
        return min(100, max(0, (raw_score - min_val) / (max_val - min_val) * 100))
```

## 5. REGIME ENGINE

The regime engine MUST run before any other models:

```python
@dataclass
class RegimeState:
    trend_regime: str  # BULL, BEAR, SIDEWAYS
    volatility_regime: str  # LOW, NORMAL, HIGH, SPIKE
    confidence: float  # 0-1
    active_models: List[str]
    model_weights: Dict[str, float]
    position_size_multiplier: float  # 0.25-1.25

class RegimeEngine:
    def detect_regime(self, market_data: pd.DataFrame) -> RegimeState:
        # 1. Run HMM regime detection
        # 2. Run volatility regime detection
        # 3. Run breadth regime detection
        # 4. Combine with voting
        # 5. Determine active models and weights
        pass
```

## 6. PROJECT STRUCTURE

```
quant-project-v2/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── regime_engine.py    # Layer 1
│   │   │   ├── orchestrator.py     # Layer 2
│   │   │   ├── ensemble.py         # Layer 4
│   │   │   └── risk_manager.py     # Layer 5
│   │   ├── models/                 # Layer 3
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   ├── momentum/
│   │   │   ├── trend/
│   │   │   ├── fundamental/
│   │   │   └── quant/
│   │   ├── data/
│   │   └── api/
├── frontend/
└── docs/
    ├── ARCHITECTURE.md
    └── QUICKSTART.md
```

## 7. IMPLEMENTATION CHECKLIST

Track progress by updating the registry:

```python
MODEL_REGISTRY = {
    "hqm":           {"implemented": False, "tested": False},
    "clenow":        {"implemented": False, "tested": False},
    "dual_momentum": {"implemented": False, "tested": False},
    # ... all 20 models
}
```

## 8. TESTING REQUIREMENTS

Each model must pass:
1. Returns valid ModelResult objects
2. Scores are 0-100 normalized
3. Has `get_regime_params()` for all regimes
4. Works with real SET100 data
5. Handles missing data gracefully

## 9. API ENDPOINTS

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/regime` | GET | Current market regime |
| `/api/models/active` | GET | Currently active models |
| `/api/screen` | POST | Run full screening |
| `/api/rankings` | GET | Unified stock rankings |
| `/api/reports/pdf` | POST | Generate PDF report |

## 10. DASHBOARD COMPONENTS

1. **Regime Panel**: Current regime with confidence meter
2. **Model Status**: Which models are active (green) vs inactive (gray)
3. **Weight Matrix Heatmap**: Current weights by regime
4. **Unified Rankings Table**: Single sorted list with agreement scores
5. **Model Agreement Heatmap**: Per-stock agreement visualization
6. **Position Sizer**: Recommended sizes based on regime

## 11. COMMON PATTERNS

### Adding a New Model
```python
# 1. Create file: backend/app/models/{category}/{model_name}.py
# 2. Implement BaseModel interface
# 3. Add to registry.py
# 4. Add weight to WEIGHT_MATRIX
# 5. Test with regime variations
```

### Running Full Screening
```python
# 1. Fetch market data
data = fetch_set100_data()

# 2. Detect regime
regime = regime_engine.detect_regime(data)

# 3. Run active models
results = orchestrator.execute_models(data, regime)

# 4. Ensemble
rankings = ensemble.calculate_composite(results, regime)

# 5. Apply risk sizing
final = risk_manager.size_positions(rankings, regime)
```

## 12. REFERENCES

- Main Architecture: QUANT-PROJECT-MASTER-ARCHITECTURE.md
- Quick Start: QUANT-PROJECT-QUICKSTART.md
- Thailand Market Knowledge: /mnt/skills/user/thailand-equity-sales/

---

*Skill Version: 1.0 | January 2026*

# 🚀 Quant Project Quick-Start Guide
## For New Claude Code Sessions

**Purpose:** Use this document to quickly resume work on the Renaissance-style Quant Project.

---

## 📋 Session Kickstart Prompt Template

Copy and paste this into a new Claude Code session:

```
I'm working on a Renaissance-style quantitative trading system for Thai SET100 stocks.

Please read these reference files:
1. QUANT-PROJECT-MASTER-ARCHITECTURE.md (full system design)
2. This quick-start guide

PROJECT STATUS:
- Current Phase: [1/2/3/4]
- Last Completed: [describe last completed work]
- Next Task: [specific task to complete]

EXISTING CODE LOCATION:
- GitHub Repo: [your-repo-url]
- Local Path: [if applicable]

Please continue from where I left off, following the architecture document.
```

---

## 🏗️ Core System Components (Quick Reference)

### The 5 Layers

| Layer | Purpose | Key File |
|-------|---------|----------|
| **Layer 1** | Market Regime Detection | `regime_engine.py` |
| **Layer 2** | Model Orchestration | `orchestrator.py` |
| **Layer 3** | Model Execution | `models/*.py` (20 files) |
| **Layer 4** | Ensemble & Ranking | `ensemble.py` |
| **Layer 5** | Risk & Position Sizing | `risk_manager.py` |

### The 20 Models (Checklist)

**MOMENTUM (5):**
- [ ] M1: HQM (High-Quality Momentum)
- [ ] M2: Clenow Momentum
- [ ] M3: Dual Momentum
- [ ] M4: ROC Multi-Timeframe
- [ ] M5: 52-Week High

**TREND (5):**
- [ ] M6: ADX Trend Strength
- [ ] M7: Multi-EMA Matrix
- [ ] M8: Supertrend
- [ ] M9: Ichimoku Cloud
- [ ] M10: Parabolic SAR

**FUNDAMENTAL (5):**
- [ ] M11: Magic Formula
- [ ] M12: GARP
- [ ] M13: Quality Factor
- [ ] M14: Altman Z-Score
- [ ] M15: Dividend Yield

**QUANTITATIVE (5):**
- [ ] M16: HMM Regime
- [ ] M17: Volatility Regime
- [ ] M18: Mean Reversion
- [ ] M19: Correlation Regime
- [ ] M20: RSI Divergence

---

## 🎯 Key Difference: Renaissance vs Old Approach

### ❌ OLD WAY (40 separate models):
```
Model 1 → Stock List 1
Model 2 → Stock List 2
...
Model 40 → Stock List 40
→ User manually reconciles 40 different outputs
```

### ✅ NEW WAY (Regime-Conditional Ensemble):
```
Market Regime Detection (BULL/BEAR/SIDEWAYS)
    ↓
Activate relevant models (10-15 of 20)
    ↓
Run with regime-adjusted parameters
    ↓
Apply regime-based weight matrix
    ↓
Single unified stock ranking with confidence scores
```

---

## 🧩 Model Weight Matrix (Critical)

This is the **heart** of the Renaissance approach. Each model gets different weights depending on market regime:

```python
WEIGHT_MATRIX = {
    # Model:         [BULL, BEAR, SIDEWAYS]
    "hqm":           [1.0,  0.3,  0.5],  # High in bull
    "clenow":        [1.0,  0.3,  0.5],
    "quality":       [0.5,  1.0,  0.8],  # High in bear
    "mean_reversion":[0.2,  0.4,  1.0],  # High in sideways
    # ... etc for all 20 models
}
```

---

## 📂 Essential Files to Create First

### 1. Base Model Interface
```python
# backend/app/models/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
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
    score: float  # 0-100
    signal: Signal
    confidence: float  # 0-1
    metadata: Dict

class BaseModel(ABC):
    """All models must implement this interface"""
    
    @abstractmethod
    def calculate(self, 
                  prices: pd.DataFrame, 
                  regime: str = "NEUTRAL") -> List[ModelResult]:
        pass
    
    @abstractmethod
    def get_regime_params(self, regime: str) -> Dict:
        """Return regime-specific parameters"""
        pass
```

### 2. Model Registry
```python
# backend/app/models/registry.py

from typing import Dict, Type
from .base import BaseModel

MODEL_REGISTRY: Dict[str, Dict] = {
    # Momentum
    "hqm": {"class": "HQMModel", "category": "momentum", "implemented": False},
    "clenow": {"class": "ClenowMomentumModel", "category": "momentum", "implemented": False},
    # ... add all 20
}

def get_implemented_models() -> List[str]:
    return [k for k, v in MODEL_REGISTRY.items() if v["implemented"]]
```

### 3. Regime Engine
```python
# backend/app/core/regime_engine.py

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RegimeState:
    trend_regime: str  # BULL, BEAR, SIDEWAYS
    volatility_regime: str  # LOW, NORMAL, HIGH, SPIKE
    confidence: float
    active_models: List[str]
    model_weights: Dict[str, float]
    position_size_multiplier: float

class RegimeEngine:
    def detect_regime(self, market_data) -> RegimeState:
        # Implementation
        pass
```

---

## 🔄 Implementation Order (Recommended)

### Week 1: Foundation
1. Project structure
2. `base.py` (model interface)
3. `registry.py` (model tracking)
4. `regime_engine.py` (basic version)
5. 1 momentum model (HQM)
6. 1 trend model (ADX)
7. 1 fundamental model (Quality)

### Week 2: Core Logic
1. `orchestrator.py`
2. `ensemble.py`
3. Weight matrix
4. Basic API endpoints

### Week 3-4: Remaining Models
- Implement remaining 17 models
- Add to registry
- Test each model individually

### Week 5-6: Integration
- Full API
- Frontend dashboard
- PDF reports

---

## 🧪 Testing Each Model

For each model, verify:

```python
def test_model(model, test_data):
    # 1. Runs without error
    results = model.calculate(test_data)
    
    # 2. Returns valid scores (0-100)
    assert all(0 <= r.score <= 100 for r in results)
    
    # 3. Returns valid signals
    assert all(r.signal in Signal for r in results)
    
    # 4. Handles regime parameters
    for regime in ["BULL", "BEAR", "SIDEWAYS"]:
        params = model.get_regime_params(regime)
        results = model.calculate(test_data, regime=regime)
```

---

## 🔧 Common Issues & Solutions

### Issue: Context window full
**Solution:** Keep this document + architecture doc as reference. Start new session with kickstart prompt.

### Issue: Model implementations diverging
**Solution:** Always reference `base.py` interface. All models must follow same structure.

### Issue: Not sure which models are done
**Solution:** Update `registry.py` immediately after implementing each model.

### Issue: Forgetting regime logic
**Solution:** Every model MUST have `get_regime_params()` method. No exceptions.

---

## 📊 Dashboard Quick Reference

### Essential Components:
1. **Regime Indicator** - Current market regime with confidence
2. **Active Models Panel** - Which models are running
3. **Weight Visualization** - Current model weights
4. **Unified Rankings** - Single stock list, not 20 separate lists
5. **Agreement Heatmap** - How many models agree per stock
6. **Position Sizer** - Recommended position sizes

---

## 🎓 Key Concepts to Remember

### 1. Regime-Conditional Activation
Not all models run all the time. In a BEAR market, momentum models get low weight (0.3), quality models get high weight (1.0).

### 2. Model Agreement Matters
A stock ranked by 15/20 models as BUY is more reliable than one ranked by 5/20 models.

### 3. Single Unified Output
The old approach gave 40 different stock lists. The new approach gives ONE ranked list with confidence scores.

### 4. Position Sizing by Regime
- BULL + LOW_VOL: 1.25× normal position
- BEAR + HIGH_VOL: 0.5× or less

---

## 📞 Support Resources

- **Main Architecture Doc:** QUANT-PROJECT-MASTER-ARCHITECTURE.md
- **Your Skills:** /mnt/skills/user/thailand-equity-sales/
- **Past Conversations:** Search for "quant project" or "SET100 models"

---

*Quick-Start Guide v1.0 | January 2026*

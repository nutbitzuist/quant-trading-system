# 🎯 Renaissance-Style 20-Model Funnel Architecture
## From 100 Stocks → Top 20 Buy + Top 20 Avoid

**Purpose:** This document defines the exact 20 models, their roles in the funnel, and how they work together to produce high-probability trading signals.

---

## 🔄 The Funnel Flow: How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE SCREENING FUNNEL                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   SET100 Universe (100 stocks)                                              │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 0: MARKET REGIME DETECTION (runs first, affects all)      │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  • Determines: BULL / BEAR / SIDEWAYS                            │      │
│   │  • Determines: HIGH_VOL / NORMAL_VOL / LOW_VOL                   │      │
│   │  • Sets: Which models activate, what weights to use              │      │
│   │                                                                   │      │
│   │  Models: M1 (HMM Regime), M2 (Volatility Regime),                │      │
│   │          M3 (Breadth Regime)                                      │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 1: LIQUIDITY & TRADABILITY FILTER                         │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Remove stocks that are too illiquid or risky to trade  │      │
│   │  Filter: Volume > 20-day avg, No trading halts, Price > 1 THB    │      │
│   │                                                                   │      │
│   │  100 stocks → ~90 stocks pass                                    │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 2: FINANCIAL HEALTH GATE                                  │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Eliminate financially distressed companies             │      │
│   │                                                                   │      │
│   │  Models: M4 (Altman Z-Score), M5 (Quality Factor)                │      │
│   │                                                                   │      │
│   │  Gate Logic:                                                      │      │
│   │  • Altman Z < 1.1 (distress) → Automatic AVOID list              │      │
│   │  • Quality Score < 20 → Flag as HIGH RISK                        │      │
│   │                                                                   │      │
│   │  ~90 stocks → ~80 stocks pass (10 to AVOID list)                 │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 3: TREND ALIGNMENT CHECK                                  │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Identify stocks aligned with current regime            │      │
│   │                                                                   │      │
│   │  Models: M6 (ADX Trend), M7 (Multi-EMA), M8 (Supertrend)         │      │
│   │                                                                   │      │
│   │  Logic by Regime:                                                 │      │
│   │  • BULL regime: Want UPTREND stocks (ADX > 25, +DI > -DI)        │      │
│   │  • BEAR regime: Want DEFENSIVE or SHORT candidates               │      │
│   │  • SIDEWAYS: Want RANGE-BOUND stocks (ADX < 20)                  │      │
│   │                                                                   │      │
│   │  Output: Trend Score (0-100) for each stock                      │      │
│   │  ~80 stocks scored, ranked by trend alignment                    │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 4: MOMENTUM SCORING                                       │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Rank stocks by momentum strength                       │      │
│   │                                                                   │      │
│   │  Models: M9 (HQM), M10 (Clenow), M11 (Dual Momentum),            │      │
│   │          M12 (ROC Multi), M13 (52-Week High)                     │      │
│   │                                                                   │      │
│   │  Regime Weights:                                                  │      │
│   │  • BULL: Full weight (1.0) on momentum models                    │      │
│   │  • BEAR: Low weight (0.3) - momentum less reliable               │      │
│   │  • SIDEWAYS: Medium weight (0.5)                                 │      │
│   │                                                                   │      │
│   │  Output: Momentum Score (0-100) for each stock                   │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 5: VALUE & FUNDAMENTAL SCORING                            │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Find undervalued or high-quality opportunities         │      │
│   │                                                                   │      │
│   │  Models: M14 (Magic Formula), M15 (GARP), M16 (Dividend)         │      │
│   │                                                                   │      │
│   │  Regime Weights:                                                  │      │
│   │  • BULL: Low weight (0.4) - growth > value                       │      │
│   │  • BEAR: High weight (1.0) - quality/value matters               │      │
│   │  • SIDEWAYS: Medium weight (0.7) - balanced                      │      │
│   │                                                                   │      │
│   │  Output: Fundamental Score (0-100) for each stock                │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 6: MEAN REVERSION & TIMING                                │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Identify overbought/oversold conditions                │      │
│   │                                                                   │      │
│   │  Models: M17 (Bollinger Mean Rev), M18 (RSI Divergence),         │      │
│   │          M19 (Ichimoku Cloud)                                    │      │
│   │                                                                   │      │
│   │  Regime Logic:                                                    │      │
│   │  • BULL: Use for pullback buying (oversold = opportunity)        │      │
│   │  • BEAR: Use for avoiding falling knives                         │      │
│   │  • SIDEWAYS: Primary strategy (buy low, sell high)               │      │
│   │                                                                   │      │
│   │  Output: Timing Score (0-100) for each stock                     │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 7: RELATIVE STRENGTH & SECTOR                             │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Compare stock to peers and market                      │      │
│   │                                                                   │      │
│   │  Models: M20 (Relative Strength / IBD RS)                        │      │
│   │                                                                   │      │
│   │  Logic:                                                           │      │
│   │  • RS > 80: Stock is a leader (favor in BULL)                    │      │
│   │  • RS < 20: Stock is a laggard (AVOID or SHORT candidate)        │      │
│   │  • Sector rotation: Which sectors are leading?                   │      │
│   │                                                                   │      │
│   │  Output: Relative Strength Score (1-99)                          │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 8: ENSEMBLE SCORING & RANKING                             │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │  Purpose: Combine all scores into final ranking                  │      │
│   │                                                                   │      │
│   │  Formula:                                                         │      │
│   │  Final_Score = w1×Trend + w2×Momentum + w3×Fundamental +         │      │
│   │                w4×Timing + w5×RelativeStrength                   │      │
│   │                                                                   │      │
│   │  Weights by Regime:                                               │      │
│   │  ┌─────────────┬───────┬───────┬──────────┐                      │      │
│   │  │ Component   │ BULL  │ BEAR  │ SIDEWAYS │                      │      │
│   │  ├─────────────┼───────┼───────┼──────────┤                      │      │
│   │  │ Trend       │ 25%   │ 15%   │ 10%      │                      │      │
│   │  │ Momentum    │ 30%   │ 10%   │ 15%      │                      │      │
│   │  │ Fundamental │ 15%   │ 35%   │ 25%      │                      │      │
│   │  │ Timing      │ 10%   │ 20%   │ 35%      │                      │      │
│   │  │ Rel.Strength│ 20%   │ 20%   │ 15%      │                      │      │
│   │  └─────────────┴───────┴───────┴──────────┘                      │      │
│   │                                                                   │      │
│   │  Model Agreement Bonus:                                           │      │
│   │  • If 15+/20 models agree: +10% to score                         │      │
│   │  • If 12-14/20 models agree: +5% to score                        │      │
│   │  • If <8 models agree: -10% to score (low conviction)            │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│              │                                                               │
│              ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────────┐      │
│   │  STAGE 9: FINAL OUTPUT                                           │      │
│   │  ─────────────────────────────────────────────────────────────── │      │
│   │                                                                   │      │
│   │  TOP 20 BUY:                                                      │      │
│   │  • Highest composite scores                                       │      │
│   │  • Model agreement > 60%                                          │      │
│   │  • Not in AVOID list from Stage 2                                 │      │
│   │  • Ranked by: Score × Confidence                                  │      │
│   │                                                                   │      │
│   │  TOP 20 AVOID/SELL:                                               │      │
│   │  • Lowest composite scores                                        │      │
│   │  • OR flagged in Stage 2 (financial distress)                    │      │
│   │  • OR strong negative momentum + weak fundamentals               │      │
│   │  • Ranked by: Inverse Score × Risk Level                         │      │
│   │                                                                   │      │
│   │  For Each Stock:                                                  │      │
│   │  • Final Score (0-100)                                           │      │
│   │  • Confidence Level (High/Medium/Low)                            │      │
│   │  • Model Agreement (X/20 models agree)                           │      │
│   │  • Primary Signal (which models driving the score)               │      │
│   │  • Risk Flag (any concerns?)                                     │      │
│   │  • Suggested Position Size (based on confidence + regime vol)    │      │
│   └──────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 The Complete 20 Models: Organized by Stage

### STAGE 0: REGIME DETECTION MODELS (Meta-Layer)
*These run FIRST and determine how all other models behave*

| # | Model Name | Purpose | Output | When Critical |
|---|------------|---------|--------|---------------|
| **M1** | HMM Regime Detector | Classify market state using Hidden Markov Model | BULL/BEAR/SIDEWAYS + probability | Always runs first |
| **M2** | Volatility Regime | Classify volatility environment | HIGH/NORMAL/LOW/SPIKE | Always runs first |
| **M3** | Breadth Regime | Market participation analysis | BROAD/NARROW + % stocks above MA | Always runs first |

---

### STAGE 2: FINANCIAL HEALTH GATE (Safety Filter)
*Removes financially dangerous stocks before any other analysis*

| # | Model Name | Purpose | Output | Gate Logic |
|---|------------|---------|--------|------------|
| **M4** | Altman Z-Score | Bankruptcy/distress prediction | Z-Score (0-5+) | Z < 1.1 → AVOID |
| **M5** | Quality Factor | Earnings quality + stability | Score (0-100) | Score < 20 → HIGH RISK |

---

### STAGE 3: TREND ALIGNMENT (Direction Filter)
*Ensures stocks are moving in the right direction for current regime*

| # | Model Name | Purpose | Output | Key Signals |
|---|------------|---------|--------|-------------|
| **M6** | ADX Trend Strength | Measure trend strength | ADX (0-100) + Direction | ADX > 25 = trending |
| **M7** | Multi-EMA Matrix | EMA stack alignment | Stack Score (0-100) | Perfect stack = 100 |
| **M8** | Supertrend | ATR-based trend + stops | BULL/BEAR + Stop Level | Clear trend signals |

---

### STAGE 4: MOMENTUM SCORING (Strength Measurement)
*Ranks stocks by momentum quality*

| # | Model Name | Purpose | Output | Best In |
|---|------------|---------|--------|---------|
| **M9** | High-Quality Momentum (HQM) | Multi-timeframe momentum percentile | Score (0-100) | BULL regime |
| **M10** | Clenow Momentum | Regression slope × R² | Score (annualized %) | BULL regime |
| **M11** | Dual Momentum | Absolute + Relative combined | BUY/HOLD/AVOID | All regimes |
| **M12** | ROC Multi-Timeframe | Rate of change composite | Score (0-100) | BULL regime |
| **M13** | 52-Week High Proximity | Distance to 52W high | % of high + frequency | BULL regime |

---

### STAGE 5: FUNDAMENTAL SCORING (Value Measurement)
*Finds undervalued or high-quality opportunities*

| # | Model Name | Purpose | Output | Best In |
|---|------------|---------|--------|---------|
| **M14** | Magic Formula | Greenblatt's EY + ROC | Combined Rank (1-100) | BEAR regime |
| **M15** | GARP | Growth at Reasonable Price | PEG-based Score | All regimes |
| **M16** | Dividend Quality | Yield + Growth + Sustainability | Score (0-100) | BEAR/SIDEWAYS |

---

### STAGE 6: TIMING & MEAN REVERSION (Entry Optimization)
*Identifies overbought/oversold for better entries*

| # | Model Name | Purpose | Output | Best In |
|---|------------|---------|--------|---------|
| **M17** | Bollinger Mean Reversion | Z-score from mean | Oversold/Overbought + Z | SIDEWAYS regime |
| **M18** | RSI Divergence | Price vs RSI divergence | Bullish/Bearish divergence | SIDEWAYS regime |
| **M19** | Ichimoku Cloud | Complete trend + timing | Cloud position + signals | All regimes |

---

### STAGE 7: RELATIVE STRENGTH (Peer Comparison)
*Compares to market and sector peers*

| # | Model Name | Purpose | Output | Key Insight |
|---|------------|---------|--------|-------------|
| **M20** | IBD Relative Strength | Stock vs all others over 12 months | RS Rating (1-99) | Leaders vs Laggards |

---

## 🎯 Detailed Model Specifications

### M1: HMM Regime Detector
```python
"""
Hidden Markov Model for Market Regime Detection
Uses SET Index data to classify overall market state
"""

class HMMRegimeDetector:
    """
    States:
        0: BULL (high returns, low volatility, positive trend)
        1: BEAR (negative returns, high volatility, negative trend)
        2: SIDEWAYS (low returns, low volatility, no clear trend)
    
    Features Used:
        - 20-day rolling returns
        - 20-day rolling volatility
        - 50-day MA slope
        - Volume trend
    
    Output:
        regime: str ("BULL", "BEAR", "SIDEWAYS")
        probabilities: [p_bull, p_bear, p_sideways]
        confidence: float (0-1)
        days_in_regime: int
    """
    
    def __init__(self):
        self.n_states = 3
        self.model = None  # hmmlearn GaussianHMM
        
    def fit(self, market_data: pd.DataFrame, lookback_days: int = 252):
        """Train HMM on historical market data"""
        features = self._extract_features(market_data)
        self.model = GaussianHMM(n_components=3, covariance_type="full")
        self.model.fit(features)
        
    def predict(self, market_data: pd.DataFrame) -> RegimeState:
        """Predict current regime"""
        features = self._extract_features(market_data)
        state = self.model.predict(features)[-1]
        probs = self.model.predict_proba(features)[-1]
        
        regime_map = {0: "BULL", 1: "BEAR", 2: "SIDEWAYS"}
        return RegimeState(
            regime=regime_map[state],
            probabilities=probs,
            confidence=max(probs)
        )
    
    def _extract_features(self, data):
        returns = data['close'].pct_change(20)
        volatility = data['close'].pct_change().rolling(20).std()
        ma_slope = (data['close'].rolling(50).mean().pct_change(5))
        volume_trend = data['volume'].rolling(20).mean() / data['volume'].rolling(50).mean()
        
        return np.column_stack([returns, volatility, ma_slope, volume_trend])
```

### M2: Volatility Regime
```python
"""
Volatility Regime Classifier
Determines position sizing multiplier based on current volatility environment
"""

class VolatilityRegime:
    """
    Regimes:
        LOW_VOL: Current vol < 25th percentile of 1-year history
        NORMAL_VOL: 25th-75th percentile
        HIGH_VOL: > 75th percentile
        VOL_SPIKE: > 90th percentile AND increased > 50% in 5 days
    
    Position Sizing Multiplier:
        LOW_VOL: 1.25x (can take larger positions)
        NORMAL_VOL: 1.0x (standard positions)
        HIGH_VOL: 0.5x (reduce exposure)
        VOL_SPIKE: 0.25x (minimum exposure)
    """
    
    def classify(self, data: pd.DataFrame) -> dict:
        current_vol = data['close'].pct_change().rolling(20).std().iloc[-1]
        vol_history = data['close'].pct_change().rolling(20).std().iloc[-252:]
        
        percentile = (vol_history < current_vol).mean() * 100
        vol_5d_ago = vol_history.iloc[-5]
        vol_change = (current_vol - vol_5d_ago) / vol_5d_ago
        
        if percentile > 90 and vol_change > 0.5:
            regime = "VOL_SPIKE"
            multiplier = 0.25
        elif percentile > 75:
            regime = "HIGH_VOL"
            multiplier = 0.5
        elif percentile < 25:
            regime = "LOW_VOL"
            multiplier = 1.25
        else:
            regime = "NORMAL_VOL"
            multiplier = 1.0
            
        return {
            "regime": regime,
            "current_vol": current_vol,
            "percentile": percentile,
            "position_multiplier": multiplier
        }
```

### M3: Breadth Regime
```python
"""
Market Breadth Analysis
Measures how broad or narrow market participation is
"""

class BreadthRegime:
    """
    Metrics:
        - % of SET100 stocks above 50-day MA
        - % of SET100 stocks above 200-day MA
        - Advance/Decline ratio
        - New highs vs New lows
    
    Regimes:
        BROAD_BULL: >70% above 50MA, >60% above 200MA
        NARROW_BULL: <50% above 50MA but index rising (few leaders)
        BROAD_BEAR: <30% above 50MA, <40% above 200MA
        MIXED: Everything else
    """
    
    def calculate(self, universe_data: Dict[str, pd.DataFrame]) -> dict:
        above_50ma = 0
        above_200ma = 0
        new_highs = 0
        new_lows = 0
        total = len(universe_data)
        
        for ticker, data in universe_data.items():
            price = data['close'].iloc[-1]
            ma50 = data['close'].rolling(50).mean().iloc[-1]
            ma200 = data['close'].rolling(200).mean().iloc[-1]
            high_52w = data['close'].iloc[-252:].max()
            low_52w = data['close'].iloc[-252:].min()
            
            if price > ma50: above_50ma += 1
            if price > ma200: above_200ma += 1
            if price >= high_52w * 0.98: new_highs += 1
            if price <= low_52w * 1.02: new_lows += 1
        
        pct_above_50ma = above_50ma / total * 100
        pct_above_200ma = above_200ma / total * 100
        
        if pct_above_50ma > 70 and pct_above_200ma > 60:
            regime = "BROAD_BULL"
        elif pct_above_50ma < 30 and pct_above_200ma < 40:
            regime = "BROAD_BEAR"
        elif pct_above_50ma < 50:
            regime = "NARROW_BULL"
        else:
            regime = "MIXED"
            
        return {
            "regime": regime,
            "pct_above_50ma": pct_above_50ma,
            "pct_above_200ma": pct_above_200ma,
            "new_highs": new_highs,
            "new_lows": new_lows,
            "advance_decline_ratio": new_highs / max(new_lows, 1)
        }
```

### M4: Altman Z-Score
```python
"""
Altman Z-Score for Financial Distress Prediction
CRITICAL GATE: Stocks with Z < 1.1 go directly to AVOID list
"""

class AltmanZScore:
    """
    Formula (for non-manufacturing, including Thai stocks):
        Z = 6.56×X1 + 3.26×X2 + 6.72×X3 + 1.05×X4
        
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Book Value of Equity / Total Liabilities
    
    Interpretation:
        Z > 2.6: SAFE zone (green light)
        1.1 < Z < 2.6: GREY zone (proceed with caution)
        Z < 1.1: DISTRESS zone (AVOID - high bankruptcy risk)
    """
    
    def calculate(self, fundamentals: dict) -> dict:
        try:
            X1 = fundamentals['working_capital'] / fundamentals['total_assets']
            X2 = fundamentals['retained_earnings'] / fundamentals['total_assets']
            X3 = fundamentals['ebit'] / fundamentals['total_assets']
            X4 = fundamentals['book_value'] / fundamentals['total_liabilities']
            
            z_score = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
            
            if z_score > 2.6:
                zone = "SAFE"
                gate_pass = True
            elif z_score > 1.1:
                zone = "GREY"
                gate_pass = True  # Pass but with caution flag
            else:
                zone = "DISTRESS"
                gate_pass = False  # AUTOMATIC AVOID
                
            return {
                "z_score": z_score,
                "zone": zone,
                "gate_pass": gate_pass,
                "components": {"X1": X1, "X2": X2, "X3": X3, "X4": X4}
            }
        except:
            return {"z_score": None, "zone": "UNKNOWN", "gate_pass": False}
```

### M5: Quality Factor
```python
"""
Quality Factor Composite
Measures earnings quality, stability, and financial strength
"""

class QualityFactor:
    """
    Components:
        1. ROE Stability (35%): Low variance in ROE over 5 years
        2. Earnings Quality (35%): CFO/Net Income ratio (>1 is good)
        3. Leverage Quality (30%): Low debt-to-equity
    
    Formula:
        Quality = 0.35×ROE_Stability + 0.35×Earnings_Quality + 0.30×Leverage_Quality
    
    Each component normalized to 0-100
    """
    
    def calculate(self, fundamentals: dict) -> dict:
        # ROE Stability (lower variance = higher score)
        roe_history = fundamentals.get('roe_5yr', [])
        if len(roe_history) >= 3:
            roe_mean = np.mean(roe_history)
            roe_std = np.std(roe_history)
            roe_stability = max(0, 100 - (roe_std / max(roe_mean, 0.01) * 100))
        else:
            roe_stability = 50  # Neutral if no history
        
        # Earnings Quality (CFO / Net Income)
        cfo = fundamentals.get('cash_from_operations', 0)
        net_income = fundamentals.get('net_income', 1)
        earnings_quality_ratio = cfo / max(net_income, 1)
        earnings_quality = min(100, max(0, earnings_quality_ratio * 50))
        
        # Leverage Quality (lower D/E = higher score)
        debt_equity = fundamentals.get('debt_to_equity', 1)
        leverage_quality = max(0, 100 - debt_equity * 30)
        
        # Composite
        quality_score = (
            0.35 * roe_stability +
            0.35 * earnings_quality +
            0.30 * leverage_quality
        )
        
        return {
            "quality_score": quality_score,
            "roe_stability": roe_stability,
            "earnings_quality": earnings_quality,
            "leverage_quality": leverage_quality,
            "gate_pass": quality_score >= 20  # Below 20 = HIGH RISK flag
        }
```

### M6-M8: Trend Models
```python
"""
Trend Models: ADX, Multi-EMA, Supertrend
Used in Stage 3 to filter stocks by trend alignment
"""

class ADXTrend:
    """
    ADX (Average Directional Index)
    
    Components:
        - ADX: Trend strength (0-100)
        - +DI: Positive directional indicator
        - -DI: Negative directional indicator
    
    Interpretation:
        ADX > 25: Strong trend
        ADX < 20: No trend (ranging)
        +DI > -DI: Uptrend
        -DI > +DI: Downtrend
    """
    
    def calculate(self, data: pd.DataFrame, period: int = 14) -> dict:
        # Calculate +DM, -DM, TR, then smooth and create ADX
        # (Standard ADX calculation)
        
        adx = self._calculate_adx(data, period)
        plus_di = self._calculate_plus_di(data, period)
        minus_di = self._calculate_minus_di(data, period)
        
        # Determine trend state
        if adx > 25:
            if plus_di > minus_di:
                trend = "STRONG_UPTREND"
                score = min(100, 50 + adx)
            else:
                trend = "STRONG_DOWNTREND"
                score = max(0, 50 - adx)
        elif adx < 20:
            trend = "RANGING"
            score = 50  # Neutral
        else:
            if plus_di > minus_di:
                trend = "WEAK_UPTREND"
                score = 60
            else:
                trend = "WEAK_DOWNTREND"
                score = 40
                
        return {
            "adx": adx,
            "plus_di": plus_di,
            "minus_di": minus_di,
            "trend": trend,
            "score": score
        }


class MultiEMA:
    """
    Multi-EMA Stack Analysis
    
    EMAs: 8, 13, 21, 34, 55, 89 (Fibonacci-based)
    
    Perfect Bull Stack: Price > EMA8 > EMA13 > EMA21 > EMA34 > EMA55 > EMA89
    Perfect Bear Stack: Price < EMA8 < EMA13 < EMA21 < EMA34 < EMA55 < EMA89
    """
    
    EMA_PERIODS = [8, 13, 21, 34, 55, 89]
    
    def calculate(self, data: pd.DataFrame) -> dict:
        price = data['close'].iloc[-1]
        emas = {p: data['close'].ewm(span=p).mean().iloc[-1] for p in self.EMA_PERIODS}
        
        # Count how many EMAs price is above
        above_count = sum(1 for p in self.EMA_PERIODS if price > emas[p])
        
        # Check if perfectly stacked
        ema_values = [emas[p] for p in self.EMA_PERIODS]
        is_bull_stack = all(ema_values[i] > ema_values[i+1] for i in range(len(ema_values)-1))
        is_bear_stack = all(ema_values[i] < ema_values[i+1] for i in range(len(ema_values)-1))
        
        # Score calculation
        base_score = (above_count / len(self.EMA_PERIODS)) * 100
        
        if is_bull_stack and price > emas[8]:
            score = 100  # Perfect bullish
            alignment = "PERFECT_BULL"
        elif is_bear_stack and price < emas[8]:
            score = 0  # Perfect bearish
            alignment = "PERFECT_BEAR"
        else:
            score = base_score
            alignment = "MIXED"
            
        return {
            "score": score,
            "alignment": alignment,
            "above_count": above_count,
            "emas": emas,
            "is_bull_stack": is_bull_stack,
            "is_bear_stack": is_bear_stack
        }


class Supertrend:
    """
    Supertrend Indicator
    
    Formula:
        Upper Band = (High + Low) / 2 + Multiplier × ATR
        Lower Band = (High + Low) / 2 - Multiplier × ATR
        
    Parameters:
        ATR Period: 10
        Multiplier: 3.0 (adjust by volatility regime)
    """
    
    def calculate(self, data: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> dict:
        atr = self._calculate_atr(data, period)
        hl2 = (data['high'] + data['low']) / 2
        
        upper_band = hl2 + multiplier * atr
        lower_band = hl2 - multiplier * atr
        
        # Determine trend
        close = data['close'].iloc[-1]
        prev_close = data['close'].iloc[-2]
        
        # Simplified: if price > lower_band and was above, stay bullish
        if close > lower_band.iloc[-1]:
            trend = "BULLISH"
            stop_level = lower_band.iloc[-1]
            score = 70 + min(30, (close - stop_level) / close * 100)
        else:
            trend = "BEARISH"
            stop_level = upper_band.iloc[-1]
            score = 30 - min(30, (stop_level - close) / close * 100)
            
        return {
            "trend": trend,
            "stop_level": stop_level,
            "score": max(0, min(100, score)),
            "distance_to_stop": abs(close - stop_level) / close * 100
        }
```

### M9-M13: Momentum Models
```python
"""
Momentum Models: HQM, Clenow, Dual Momentum, ROC Multi, 52-Week High
Primary scoring models for BULL regime
"""

class HQM:
    """
    High-Quality Momentum Score
    
    Formula:
        HQM = weighted_avg(
            percentile_rank(return_1m),
            percentile_rank(return_3m),
            percentile_rank(return_6m),
            percentile_rank(return_12m)
        )
    
    Weights by Regime:
        BULL: [0.20, 0.25, 0.30, 0.25] - favor recent momentum
        BEAR: [0.10, 0.20, 0.30, 0.40] - favor sustained momentum
        SIDEWAYS: [0.25, 0.25, 0.25, 0.25] - equal weight
    """
    
    REGIME_WEIGHTS = {
        "BULL": [0.20, 0.25, 0.30, 0.25],
        "BEAR": [0.10, 0.20, 0.30, 0.40],
        "SIDEWAYS": [0.25, 0.25, 0.25, 0.25]
    }
    
    def calculate(self, data: pd.DataFrame, universe_returns: pd.DataFrame, regime: str) -> dict:
        """
        Args:
            data: Price data for single stock
            universe_returns: Returns for all stocks (to calculate percentile)
            regime: Current market regime
        """
        # Calculate returns for different periods
        returns = {
            '1m': data['close'].pct_change(21).iloc[-1],
            '3m': data['close'].pct_change(63).iloc[-1],
            '6m': data['close'].pct_change(126).iloc[-1],
            '12m': data['close'].pct_change(252).iloc[-1]
        }
        
        # Calculate percentile rank within universe
        percentiles = {}
        for period, ret in returns.items():
            universe_period_returns = universe_returns[period]
            percentiles[period] = (universe_period_returns < ret).mean() * 100
        
        # Apply regime weights
        weights = self.REGIME_WEIGHTS.get(regime, self.REGIME_WEIGHTS["SIDEWAYS"])
        hqm_score = (
            weights[0] * percentiles['1m'] +
            weights[1] * percentiles['3m'] +
            weights[2] * percentiles['6m'] +
            weights[3] * percentiles['12m']
        )
        
        return {
            "hqm_score": hqm_score,
            "returns": returns,
            "percentiles": percentiles,
            "signal": "BUY" if hqm_score > 80 else "HOLD" if hqm_score > 40 else "AVOID"
        }


class ClenowMomentum:
    """
    Andreas Clenow's Exponential Regression Momentum
    
    Formula:
        1. Fit exponential regression to last N days of prices
        2. annualized_slope = (1 + daily_slope)^252 - 1
        3. momentum_score = annualized_slope × R²
    
    The R² adjustment penalizes "noisy" momentum
    """
    
    def calculate(self, data: pd.DataFrame, lookback: int = 90) -> dict:
        prices = data['close'].iloc[-lookback:]
        log_prices = np.log(prices)
        
        # Linear regression on log prices
        X = np.arange(len(log_prices)).reshape(-1, 1)
        y = log_prices.values
        
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        
        daily_slope = model.coef_[0]
        r_squared = model.score(X, y)
        
        # Annualize
        annualized_return = (np.exp(daily_slope * 252) - 1) * 100  # As percentage
        
        # Quality-adjusted momentum
        momentum_score = annualized_return * r_squared
        
        return {
            "momentum_score": momentum_score,
            "annualized_return": annualized_return,
            "r_squared": r_squared,
            "signal": "BUY" if momentum_score > 20 else "HOLD" if momentum_score > 0 else "AVOID"
        }


class DualMomentum:
    """
    Gary Antonacci's Dual Momentum
    
    Two Components:
        1. Absolute Momentum: Is 12-month return > risk-free rate?
        2. Relative Momentum: Is stock outperforming peers?
    
    Signal:
        BUY: Absolute AND Relative momentum positive
        HOLD: Only one positive
        AVOID: Both negative
    """
    
    def calculate(self, data: pd.DataFrame, 
                 benchmark_return: float,
                 risk_free_rate: float = 0.02) -> dict:
        
        return_12m = data['close'].pct_change(252).iloc[-1]
        
        # Absolute momentum
        absolute_positive = return_12m > risk_free_rate
        
        # Relative momentum (vs benchmark, e.g., SET index)
        relative_positive = return_12m > benchmark_return
        
        if absolute_positive and relative_positive:
            signal = "BUY"
            score = 80 + min(20, return_12m * 100)
        elif absolute_positive or relative_positive:
            signal = "HOLD"
            score = 50
        else:
            signal = "AVOID"
            score = 20 - min(20, abs(return_12m) * 100)
            
        return {
            "score": max(0, min(100, score)),
            "return_12m": return_12m,
            "absolute_momentum": absolute_positive,
            "relative_momentum": relative_positive,
            "signal": signal
        }


class ROCMultiTimeframe:
    """
    Rate of Change across Multiple Timeframes
    
    Periods: 5, 10, 20, 60 days
    Weights: Adjusted by regime
    """
    
    REGIME_WEIGHTS = {
        "BULL": [0.20, 0.30, 0.30, 0.20],  # Favor medium-term
        "BEAR": [0.10, 0.15, 0.30, 0.45],  # Favor longer-term
        "SIDEWAYS": [0.25, 0.25, 0.25, 0.25]  # Equal
    }
    
    def calculate(self, data: pd.DataFrame, regime: str) -> dict:
        rocs = {
            '5d': (data['close'].iloc[-1] / data['close'].iloc[-5] - 1) * 100,
            '10d': (data['close'].iloc[-1] / data['close'].iloc[-10] - 1) * 100,
            '20d': (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100,
            '60d': (data['close'].iloc[-1] / data['close'].iloc[-60] - 1) * 100,
        }
        
        weights = self.REGIME_WEIGHTS.get(regime, self.REGIME_WEIGHTS["SIDEWAYS"])
        composite_roc = sum(w * rocs[p] for w, p in zip(weights, rocs.keys()))
        
        # Normalize to 0-100 score
        score = 50 + composite_roc * 2  # Rough normalization
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "rocs": rocs,
            "composite_roc": composite_roc,
            "signal": "BUY" if score > 70 else "HOLD" if score > 30 else "AVOID"
        }


class FiftyTwoWeekHigh:
    """
    52-Week High Proximity
    
    Stocks near 52-week highs tend to continue outperforming
    
    Metrics:
        1. Distance to 52W High: Current Price / 52W High
        2. New High Frequency: Count of new highs in last 60 days
    """
    
    def calculate(self, data: pd.DataFrame) -> dict:
        current_price = data['close'].iloc[-1]
        high_52w = data['high'].iloc[-252:].max()
        low_52w = data['low'].iloc[-252:].min()
        
        # Distance to high (as percentage of high)
        distance_to_high = current_price / high_52w * 100
        
        # Count new highs in last 60 days
        rolling_high = data['high'].rolling(252).max()
        new_highs_60d = (data['high'].iloc[-60:] >= rolling_high.iloc[-60:]).sum()
        
        # Score
        if distance_to_high >= 95:
            score = 90 + (new_highs_60d / 60 * 10)  # Near high + making new highs
        elif distance_to_high >= 85:
            score = 70 + (distance_to_high - 85) * 2
        elif distance_to_high >= 70:
            score = 50 + (distance_to_high - 70) * 1.3
        else:
            score = distance_to_high * 0.7
            
        return {
            "score": min(100, score),
            "distance_to_high": distance_to_high,
            "new_highs_60d": new_highs_60d,
            "current_price": current_price,
            "high_52w": high_52w,
            "signal": "BUY" if score > 75 else "HOLD" if score > 40 else "AVOID"
        }
```

### M14-M16: Fundamental Models
```python
"""
Fundamental Models: Magic Formula, GARP, Dividend Quality
Higher weight in BEAR regime
"""

class MagicFormula:
    """
    Joel Greenblatt's Magic Formula
    
    Ranks stocks by:
        1. Earnings Yield (EBIT / Enterprise Value) - higher is better
        2. Return on Capital (EBIT / (Net Fixed Assets + Working Capital)) - higher is better
    
    Combined rank determines score
    """
    
    def calculate(self, fundamentals: dict, universe_fundamentals: list) -> dict:
        # Calculate metrics for this stock
        ebit = fundamentals.get('ebit', 0)
        ev = fundamentals.get('enterprise_value', 1)
        net_fixed_assets = fundamentals.get('net_fixed_assets', 0)
        working_capital = fundamentals.get('working_capital', 0)
        
        earnings_yield = ebit / max(ev, 1)
        capital = net_fixed_assets + working_capital
        roc = ebit / max(capital, 1)
        
        # Rank within universe
        all_ey = [f.get('ebit', 0) / max(f.get('enterprise_value', 1), 1) for f in universe_fundamentals]
        all_roc = [f.get('ebit', 0) / max(f.get('net_fixed_assets', 0) + f.get('working_capital', 0), 1) for f in universe_fundamentals]
        
        ey_rank = sum(1 for ey in all_ey if ey < earnings_yield)
        roc_rank = sum(1 for r in all_roc if r < roc)
        
        combined_rank = ey_rank + roc_rank
        max_rank = len(universe_fundamentals) * 2
        
        score = (combined_rank / max_rank) * 100
        
        return {
            "score": score,
            "earnings_yield": earnings_yield,
            "return_on_capital": roc,
            "ey_rank": ey_rank,
            "roc_rank": roc_rank,
            "signal": "BUY" if score > 80 else "HOLD" if score > 40 else "AVOID"
        }


class GARP:
    """
    Growth at Reasonable Price (Peter Lynch)
    
    Core Metric: PEG Ratio = P/E / EPS Growth Rate
    
    Ideal: PEG < 1.0 means stock is cheap relative to growth
    """
    
    def calculate(self, fundamentals: dict, regime: str) -> dict:
        pe_ratio = fundamentals.get('pe_ratio', 0)
        eps_growth = fundamentals.get('eps_growth_rate', 0)  # As percentage
        
        if eps_growth <= 0 or pe_ratio <= 0:
            peg = float('inf')
        else:
            peg = pe_ratio / eps_growth
        
        # Regime-adjusted thresholds
        if regime == "BULL":
            max_acceptable_peg = 2.0
        elif regime == "BEAR":
            max_acceptable_peg = 1.0
        else:
            max_acceptable_peg = 1.5
        
        # Score calculation
        if peg == float('inf'):
            score = 0
        elif peg < 0.5:
            score = 100
        elif peg < 1.0:
            score = 90 - (peg - 0.5) * 40
        elif peg < max_acceptable_peg:
            score = 70 - (peg - 1.0) * 40
        else:
            score = max(0, 30 - (peg - max_acceptable_peg) * 20)
            
        return {
            "score": score,
            "peg_ratio": peg,
            "pe_ratio": pe_ratio,
            "eps_growth": eps_growth,
            "signal": "BUY" if score > 70 else "HOLD" if score > 40 else "AVOID"
        }


class DividendQuality:
    """
    Dividend Model
    
    Components:
        1. Current Yield
        2. Dividend Growth Rate (5-year CAGR)
        3. Payout Ratio Sustainability (<80% is sustainable)
        4. Consecutive Years of Dividends
    """
    
    def calculate(self, fundamentals: dict) -> dict:
        current_yield = fundamentals.get('dividend_yield', 0) * 100  # As percentage
        div_growth = fundamentals.get('dividend_growth_5yr', 0) * 100
        payout_ratio = fundamentals.get('payout_ratio', 0) * 100
        consecutive_years = fundamentals.get('dividend_consecutive_years', 0)
        
        # Score components
        yield_score = min(40, current_yield * 10)  # Max 40 points for 4%+ yield
        growth_score = min(30, div_growth * 3)  # Max 30 points for 10%+ growth
        
        # Sustainability (lower payout = more sustainable)
        if payout_ratio < 50:
            sustainability_score = 20
        elif payout_ratio < 80:
            sustainability_score = 15
        else:
            sustainability_score = 5
            
        # Track record bonus
        track_record_score = min(10, consecutive_years)
        
        total_score = yield_score + growth_score + sustainability_score + track_record_score
        
        return {
            "score": min(100, total_score),
            "current_yield": current_yield,
            "dividend_growth": div_growth,
            "payout_ratio": payout_ratio,
            "consecutive_years": consecutive_years,
            "signal": "BUY" if total_score > 60 else "HOLD" if total_score > 30 else "AVOID"
        }
```

### M17-M19: Timing Models
```python
"""
Timing & Mean Reversion Models
Critical in SIDEWAYS regime
"""

class BollingerMeanReversion:
    """
    Bollinger Band Mean Reversion
    
    Formula:
        Z-Score = (Price - 20-day SMA) / (2 × 20-day Std Dev)
    
    Signals:
        Z < -2: Oversold (potential buy in SIDEWAYS)
        Z > 2: Overbought (potential sell)
    """
    
    def calculate(self, data: pd.DataFrame, regime: str) -> dict:
        close = data['close']
        sma_20 = close.rolling(20).mean()
        std_20 = close.rolling(20).std()
        
        current_price = close.iloc[-1]
        current_sma = sma_20.iloc[-1]
        current_std = std_20.iloc[-1]
        
        z_score = (current_price - current_sma) / (2 * current_std)
        
        upper_band = current_sma + 2 * current_std
        lower_band = current_sma - 2 * current_std
        bandwidth = (upper_band - lower_band) / current_sma * 100
        
        # Score depends on regime
        if regime == "SIDEWAYS":
            # In sideways, oversold is good (buy low)
            if z_score < -2:
                score = 90
                signal = "BUY"
            elif z_score < -1:
                score = 70
                signal = "BUY"
            elif z_score > 2:
                score = 10
                signal = "AVOID"
            elif z_score > 1:
                score = 30
                signal = "HOLD"
            else:
                score = 50
                signal = "HOLD"
        else:
            # In trending markets, mean reversion is less reliable
            score = 50  # Neutral
            signal = "HOLD"
            
        return {
            "score": score,
            "z_score": z_score,
            "bandwidth": bandwidth,
            "upper_band": upper_band,
            "lower_band": lower_band,
            "signal": signal
        }


class RSIDivergence:
    """
    RSI with Divergence Detection
    
    Bullish Divergence: Price makes lower low, RSI makes higher low
    Bearish Divergence: Price makes higher high, RSI makes lower high
    """
    
    def calculate(self, data: pd.DataFrame, period: int = 14) -> dict:
        close = data['close']
        
        # Calculate RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Detect divergence (simplified)
        price_20d_low = close.iloc[-20:].min()
        price_20d_high = close.iloc[-20:].max()
        rsi_20d_low = rsi.iloc[-20:].min()
        rsi_20d_high = rsi.iloc[-20:].max()
        
        # Check for bullish divergence
        recent_price_low = close.iloc[-5:].min()
        recent_rsi_low = rsi.iloc[-5:].min()
        
        bullish_divergence = (recent_price_low <= price_20d_low * 1.02 and 
                             recent_rsi_low > rsi_20d_low)
        
        # Check for bearish divergence
        recent_price_high = close.iloc[-5:].max()
        recent_rsi_high = rsi.iloc[-5:].max()
        
        bearish_divergence = (recent_price_high >= price_20d_high * 0.98 and
                             recent_rsi_high < rsi_20d_high)
        
        # Score
        if bullish_divergence and current_rsi < 30:
            score = 95
            signal = "STRONG_BUY"
        elif bullish_divergence:
            score = 75
            signal = "BUY"
        elif bearish_divergence and current_rsi > 70:
            score = 5
            signal = "STRONG_AVOID"
        elif bearish_divergence:
            score = 25
            signal = "AVOID"
        elif current_rsi < 30:
            score = 70
            signal = "BUY"
        elif current_rsi > 70:
            score = 30
            signal = "HOLD"
        else:
            score = 50
            signal = "HOLD"
            
        return {
            "score": score,
            "rsi": current_rsi,
            "bullish_divergence": bullish_divergence,
            "bearish_divergence": bearish_divergence,
            "signal": signal
        }


class IchimokuCloud:
    """
    Ichimoku Kinko Hyo (Complete System)
    
    Components:
        Tenkan-sen (Conversion): (9-high + 9-low) / 2
        Kijun-sen (Base): (26-high + 26-low) / 2
        Senkou Span A: (Tenkan + Kijun) / 2, shifted 26 forward
        Senkou Span B: (52-high + 52-low) / 2, shifted 26 forward
        Chikou Span: Close, shifted 26 backward
    """
    
    def calculate(self, data: pd.DataFrame) -> dict:
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Calculate components
        tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_a = ((tenkan + kijun) / 2).shift(26)
        senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        
        current_price = close.iloc[-1]
        current_tenkan = tenkan.iloc[-1]
        current_kijun = kijun.iloc[-1]
        current_senkou_a = senkou_a.iloc[-1]
        current_senkou_b = senkou_b.iloc[-1]
        cloud_top = max(current_senkou_a, current_senkou_b)
        cloud_bottom = min(current_senkou_a, current_senkou_b)
        
        # Chikou confirmation (price 26 days ago vs current cloud)
        chikou_price = close.iloc[-26] if len(close) > 26 else close.iloc[0]
        
        # Determine position relative to cloud
        if current_price > cloud_top:
            cloud_position = "ABOVE"
            base_score = 70
        elif current_price < cloud_bottom:
            cloud_position = "BELOW"
            base_score = 30
        else:
            cloud_position = "INSIDE"
            base_score = 50
        
        # Additional signals
        tk_cross_bullish = current_tenkan > current_kijun
        price_above_kijun = current_price > current_kijun
        
        # Adjust score
        score = base_score
        if cloud_position == "ABOVE" and tk_cross_bullish and price_above_kijun:
            score = 90  # Strong bullish
            signal = "STRONG_BUY"
        elif cloud_position == "BELOW" and not tk_cross_bullish:
            score = 10  # Strong bearish
            signal = "STRONG_AVOID"
        elif cloud_position == "ABOVE":
            signal = "BUY"
        elif cloud_position == "BELOW":
            signal = "AVOID"
        else:
            signal = "HOLD"
            
        return {
            "score": score,
            "cloud_position": cloud_position,
            "tenkan": current_tenkan,
            "kijun": current_kijun,
            "cloud_top": cloud_top,
            "cloud_bottom": cloud_bottom,
            "tk_cross_bullish": tk_cross_bullish,
            "signal": signal
        }
```

### M20: Relative Strength
```python
"""
IBD Relative Strength Rating
Compares stock performance to all others in universe
"""

class RelativeStrength:
    """
    IBD-Style Relative Strength Rating (1-99)
    
    Calculation:
        1. Calculate weighted price performance
           - 40% weight: 3-month performance
           - 20% weight: 6-month performance
           - 20% weight: 9-month performance
           - 20% weight: 12-month performance
        2. Rank vs all stocks in universe
        3. Convert to 1-99 scale
    
    Interpretation:
        90-99: A+ leaders (top 10%)
        80-89: A leaders (top 20%)
        50-79: Average
        Below 50: Laggards
    """
    
    def calculate(self, data: pd.DataFrame, universe_data: Dict[str, pd.DataFrame]) -> dict:
        # Calculate weighted performance for this stock
        perf_3m = data['close'].pct_change(63).iloc[-1]
        perf_6m = data['close'].pct_change(126).iloc[-1]
        perf_9m = data['close'].pct_change(189).iloc[-1]
        perf_12m = data['close'].pct_change(252).iloc[-1]
        
        weighted_perf = 0.4 * perf_3m + 0.2 * perf_6m + 0.2 * perf_9m + 0.2 * perf_12m
        
        # Calculate for all stocks in universe
        all_perfs = []
        for ticker, ticker_data in universe_data.items():
            try:
                p3 = ticker_data['close'].pct_change(63).iloc[-1]
                p6 = ticker_data['close'].pct_change(126).iloc[-1]
                p9 = ticker_data['close'].pct_change(189).iloc[-1]
                p12 = ticker_data['close'].pct_change(252).iloc[-1]
                wp = 0.4 * p3 + 0.2 * p6 + 0.2 * p9 + 0.2 * p12
                all_perfs.append(wp)
            except:
                continue
        
        # Calculate percentile rank (1-99)
        percentile = sum(1 for p in all_perfs if p < weighted_perf) / len(all_perfs) * 98 + 1
        rs_rating = int(min(99, max(1, percentile)))
        
        # Determine category
        if rs_rating >= 90:
            category = "A+"
            signal = "STRONG_BUY"
        elif rs_rating >= 80:
            category = "A"
            signal = "BUY"
        elif rs_rating >= 50:
            category = "B"
            signal = "HOLD"
        elif rs_rating >= 30:
            category = "C"
            signal = "AVOID"
        else:
            category = "D"
            signal = "STRONG_AVOID"
            
        return {
            "rs_rating": rs_rating,
            "category": category,
            "weighted_performance": weighted_perf,
            "signal": signal,
            "score": rs_rating  # RS rating IS the score (1-99)
        }
```

---

## 🎛️ The Master Orchestrator

```python
"""
Master Orchestrator: Coordinates all 20 models through the funnel
"""

class QuantOrchestrator:
    def __init__(self):
        # Stage 0: Regime Models
        self.hmm_regime = HMMRegimeDetector()
        self.vol_regime = VolatilityRegime()
        self.breadth_regime = BreadthRegime()
        
        # Stage 2: Financial Health
        self.altman_z = AltmanZScore()
        self.quality = QualityFactor()
        
        # Stage 3: Trend
        self.adx = ADXTrend()
        self.multi_ema = MultiEMA()
        self.supertrend = Supertrend()
        
        # Stage 4: Momentum
        self.hqm = HQM()
        self.clenow = ClenowMomentum()
        self.dual_mom = DualMomentum()
        self.roc = ROCMultiTimeframe()
        self.fifty_two_week = FiftyTwoWeekHigh()
        
        # Stage 5: Fundamental
        self.magic_formula = MagicFormula()
        self.garp = GARP()
        self.dividend = DividendQuality()
        
        # Stage 6: Timing
        self.bollinger = BollingerMeanReversion()
        self.rsi_div = RSIDivergence()
        self.ichimoku = IchimokuCloud()
        
        # Stage 7: Relative Strength
        self.rs = RelativeStrength()
        
    def run_full_screening(self, 
                          universe_price_data: Dict[str, pd.DataFrame],
                          universe_fundamentals: Dict[str, dict],
                          market_index_data: pd.DataFrame) -> dict:
        """
        Run complete screening funnel
        
        Returns:
            {
                "regime": {...},
                "top_20_buy": [...],
                "top_20_avoid": [...],
                "all_scores": {...}
            }
        """
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "universe_size": len(universe_price_data),
            "stocks": {}
        }
        
        # ========== STAGE 0: REGIME DETECTION ==========
        regime = self._detect_regime(market_index_data, universe_price_data)
        results["regime"] = regime
        
        # ========== STAGE 1: LIQUIDITY FILTER ==========
        tradable_tickers = self._filter_tradable(universe_price_data)
        
        # ========== STAGE 2: FINANCIAL HEALTH GATE ==========
        avoid_list = []
        passed_tickers = []
        
        for ticker in tradable_tickers:
            fundamentals = universe_fundamentals.get(ticker, {})
            
            z_result = self.altman_z.calculate(fundamentals)
            q_result = self.quality.calculate(fundamentals)
            
            if not z_result['gate_pass']:
                avoid_list.append({
                    "ticker": ticker,
                    "reason": "FINANCIAL_DISTRESS",
                    "z_score": z_result['z_score']
                })
            elif not q_result['gate_pass']:
                avoid_list.append({
                    "ticker": ticker,
                    "reason": "LOW_QUALITY",
                    "quality_score": q_result['quality_score']
                })
            else:
                passed_tickers.append(ticker)
                results["stocks"][ticker] = {
                    "altman_z": z_result,
                    "quality": q_result
                }
        
        # ========== STAGES 3-7: SCORING ==========
        for ticker in passed_tickers:
            price_data = universe_price_data[ticker]
            fundamentals = universe_fundamentals.get(ticker, {})
            
            # Stage 3: Trend
            results["stocks"][ticker]["trend"] = {
                "adx": self.adx.calculate(price_data),
                "multi_ema": self.multi_ema.calculate(price_data),
                "supertrend": self.supertrend.calculate(price_data)
            }
            
            # Stage 4: Momentum
            results["stocks"][ticker]["momentum"] = {
                "hqm": self.hqm.calculate(price_data, self._get_universe_returns(universe_price_data), regime['trend']),
                "clenow": self.clenow.calculate(price_data),
                "dual_momentum": self.dual_mom.calculate(price_data, self._get_benchmark_return(market_index_data)),
                "roc": self.roc.calculate(price_data, regime['trend']),
                "fifty_two_week": self.fifty_two_week.calculate(price_data)
            }
            
            # Stage 5: Fundamental
            results["stocks"][ticker]["fundamental"] = {
                "magic_formula": self.magic_formula.calculate(fundamentals, list(universe_fundamentals.values())),
                "garp": self.garp.calculate(fundamentals, regime['trend']),
                "dividend": self.dividend.calculate(fundamentals)
            }
            
            # Stage 6: Timing
            results["stocks"][ticker]["timing"] = {
                "bollinger": self.bollinger.calculate(price_data, regime['trend']),
                "rsi_divergence": self.rsi_div.calculate(price_data),
                "ichimoku": self.ichimoku.calculate(price_data)
            }
            
            # Stage 7: Relative Strength
            results["stocks"][ticker]["relative_strength"] = self.rs.calculate(price_data, universe_price_data)
        
        # ========== STAGE 8: ENSEMBLE ==========
        final_scores = self._calculate_ensemble(results["stocks"], regime)
        
        # ========== STAGE 9: FINAL OUTPUT ==========
        sorted_scores = sorted(final_scores.items(), key=lambda x: x[1]['composite_score'], reverse=True)
        
        results["top_20_buy"] = [
            {
                "rank": i + 1,
                "ticker": ticker,
                **score_data
            }
            for i, (ticker, score_data) in enumerate(sorted_scores[:20])
            if score_data['composite_score'] > 60  # Minimum threshold
        ]
        
        # Bottom 20 + Financial Distress = AVOID
        bottom_20 = sorted_scores[-20:]
        results["top_20_avoid"] = avoid_list + [
            {
                "rank": i + 1,
                "ticker": ticker,
                "reason": "LOW_SCORE",
                **score_data
            }
            for i, (ticker, score_data) in enumerate(reversed(bottom_20))
            if score_data['composite_score'] < 40
        ]
        
        return results
    
    def _calculate_ensemble(self, stocks: dict, regime: dict) -> dict:
        """Calculate weighted ensemble scores"""
        
        # Weights by regime
        WEIGHTS = {
            "BULL": {"trend": 0.25, "momentum": 0.30, "fundamental": 0.15, "timing": 0.10, "rs": 0.20},
            "BEAR": {"trend": 0.15, "momentum": 0.10, "fundamental": 0.35, "timing": 0.20, "rs": 0.20},
            "SIDEWAYS": {"trend": 0.10, "momentum": 0.15, "fundamental": 0.25, "timing": 0.35, "rs": 0.15}
        }
        
        weights = WEIGHTS.get(regime['trend'], WEIGHTS['SIDEWAYS'])
        
        final_scores = {}
        
        for ticker, data in stocks.items():
            # Calculate category averages
            trend_score = np.mean([
                data['trend']['adx']['score'],
                data['trend']['multi_ema']['score'],
                data['trend']['supertrend']['score']
            ])
            
            momentum_score = np.mean([
                data['momentum']['hqm']['hqm_score'],
                data['momentum']['clenow']['momentum_score'] / 2 + 50,  # Normalize
                data['momentum']['dual_momentum']['score'],
                data['momentum']['roc']['score'],
                data['momentum']['fifty_two_week']['score']
            ])
            
            fundamental_score = np.mean([
                data['fundamental']['magic_formula']['score'],
                data['fundamental']['garp']['score'],
                data['fundamental']['dividend']['score']
            ])
            
            timing_score = np.mean([
                data['timing']['bollinger']['score'],
                data['timing']['rsi_divergence']['score'],
                data['timing']['ichimoku']['score']
            ])
            
            rs_score = data['relative_strength']['rs_rating']
            
            # Weighted composite
            composite = (
                weights['trend'] * trend_score +
                weights['momentum'] * momentum_score +
                weights['fundamental'] * fundamental_score +
                weights['timing'] * timing_score +
                weights['rs'] * rs_score
            )
            
            # Model agreement bonus
            all_signals = [
                data['trend']['adx']['signal'],
                data['momentum']['hqm']['signal'],
                data['fundamental']['magic_formula']['signal'],
                data['timing']['ichimoku']['signal'],
                data['relative_strength']['signal']
            ]
            
            buy_count = sum(1 for s in all_signals if s in ['BUY', 'STRONG_BUY'])
            agreement = buy_count / len(all_signals)
            
            if agreement > 0.8:
                composite *= 1.10  # 10% bonus for high agreement
            elif agreement < 0.4:
                composite *= 0.90  # 10% penalty for low agreement
            
            final_scores[ticker] = {
                "composite_score": min(100, composite),
                "trend_score": trend_score,
                "momentum_score": momentum_score,
                "fundamental_score": fundamental_score,
                "timing_score": timing_score,
                "rs_score": rs_score,
                "model_agreement": agreement,
                "confidence": "HIGH" if agreement > 0.7 else "MEDIUM" if agreement > 0.5 else "LOW"
            }
        
        return final_scores
```

---

## 📋 Quick Reference: Model Summary

| # | Model | Stage | Category | Primary Use | Best Regime |
|---|-------|-------|----------|-------------|-------------|
| M1 | HMM Regime | 0 | Meta | Detect market state | All |
| M2 | Volatility Regime | 0 | Meta | Position sizing | All |
| M3 | Breadth Regime | 0 | Meta | Market participation | All |
| M4 | Altman Z-Score | 2 | Gate | Bankruptcy filter | All (GATE) |
| M5 | Quality Factor | 2 | Gate | Quality filter | All (GATE) |
| M6 | ADX Trend | 3 | Trend | Trend strength | BULL |
| M7 | Multi-EMA | 3 | Trend | EMA alignment | BULL |
| M8 | Supertrend | 3 | Trend | Trend + stops | BULL |
| M9 | HQM | 4 | Momentum | Multi-TF momentum | BULL |
| M10 | Clenow | 4 | Momentum | Quality momentum | BULL |
| M11 | Dual Momentum | 4 | Momentum | Abs + Rel | All |
| M12 | ROC Multi | 4 | Momentum | Rate of change | BULL |
| M13 | 52-Week High | 4 | Momentum | Breakout | BULL |
| M14 | Magic Formula | 5 | Fundamental | Value + Quality | BEAR |
| M15 | GARP | 5 | Fundamental | Growth at value | All |
| M16 | Dividend | 5 | Fundamental | Income + Growth | BEAR/SIDEWAYS |
| M17 | Bollinger | 6 | Timing | Mean reversion | SIDEWAYS |
| M18 | RSI Divergence | 6 | Timing | Divergence | SIDEWAYS |
| M19 | Ichimoku | 6 | Timing | Complete system | All |
| M20 | Relative Strength | 7 | Comparison | Leader vs Laggard | All |

---

## 🎯 Expected Output Format

```json
{
  "timestamp": "2026-01-01T10:00:00",
  "regime": {
    "trend": "BULL",
    "volatility": "NORMAL_VOL",
    "breadth": "BROAD_BULL",
    "confidence": 0.82,
    "position_multiplier": 1.0
  },
  "top_20_buy": [
    {
      "rank": 1,
      "ticker": "DELTA",
      "composite_score": 92.5,
      "model_agreement": 0.85,
      "confidence": "HIGH",
      "trend_score": 88,
      "momentum_score": 95,
      "fundamental_score": 85,
      "timing_score": 78,
      "rs_score": 96,
      "primary_drivers": ["HQM", "Relative Strength", "Multi-EMA"],
      "suggested_position": "FULL"
    },
    // ... 19 more stocks
  ],
  "top_20_avoid": [
    {
      "rank": 1,
      "ticker": "XYZ",
      "reason": "FINANCIAL_DISTRESS",
      "z_score": 0.8,
      "composite_score": null
    },
    // ... more stocks to avoid
  ]
}
```

---

*Document Version: 1.0*
*Last Updated: January 2026*

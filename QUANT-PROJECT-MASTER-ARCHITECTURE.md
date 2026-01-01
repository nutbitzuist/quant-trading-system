# 🏛️ Renaissance-Style Quantitative Trading System
## Master Architecture Document v1.0

**Project:** Thai SET100 Multi-Model Quantitative Trading System  
**Style:** Renaissance Technologies Medallion-Inspired Architecture  
**Author:** Claude AI (Architect Session)  
**Date:** January 2026  
**Status:** Master Reference Document

---

## 🎯 Executive Summary

This document serves as the **single source of truth** for building a Renaissance-style quantitative trading system. Unlike the previous approach of 40 independent models screening stocks separately, this architecture implements **market regime-conditional model orchestration** where:

1. **Layer 1 (Meta-Models)**: Detect market regime (Bull/Bear/Sideways, High/Low Volatility)
2. **Layer 2 (Model Selection)**: Activate appropriate models based on current regime
3. **Layer 3 (Signal Generation)**: Run activated models with regime-specific parameters
4. **Layer 4 (Ensemble)**: Weight and combine signals using regime-aware logic
5. **Layer 5 (Risk Management)**: Apply position sizing based on regime and confidence

**Key Difference from Previous Approach:**
- ❌ Old: 40 models run independently → 40 separate stock lists → user manually reconciles
- ✅ New: Regime detection → conditional model activation → weighted ensemble → unified ranked output

---

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUANT TRADING SYSTEM v2.0                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 1: MARKET REGIME ENGINE                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │ HMM Regime  │  │  Volatility │  │   Breadth   │  │  Combined  │  │   │
│  │  │  Detector   │  │   Regime    │  │   Regime    │  │   Regime   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 LAYER 2: MODEL ORCHESTRATOR                          │   │
│  │                                                                       │   │
│  │   BULL REGIME          BEAR REGIME          SIDEWAYS REGIME          │   │
│  │   ────────────         ────────────         ────────────────         │   │
│  │   • Momentum ✓         • Mean Rev ✓         • Range Models ✓         │   │
│  │   • Trend ✓            • Defensive ✓        • Volatility ✓           │   │
│  │   • Breakout ✓         • Quality ✓          • Quality ✓              │   │
│  │   • Growth ✓           • Value ✓            • Yield ✓                │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              LAYER 3: ACTIVE MODEL EXECUTION                         │   │
│  │                                                                       │   │
│  │   ┌──────────────────────────────────────────────────────────────┐   │   │
│  │   │  20 CORE MODELS (Parameters Adjusted by Regime)              │   │   │
│  │   │                                                               │   │   │
│  │   │  MOMENTUM (5)     TREND (5)        FUNDAMENTAL (5)   QUANT (5)│   │   │
│  │   │  ─────────────    ─────────        ───────────────   ─────── │   │   │
│  │   │  1. HQM           6. ADX           11. Magic Formula 16. HMM  │   │   │
│  │   │  2. Clenow        7. Multi-EMA     12. GARP          17. Vol  │   │   │
│  │   │  3. Dual Mom      8. Supertrend    13. Quality       18. Mean │   │   │
│  │   │  4. ROC Multi     9. Ichimoku      14. Altman Z      19. Corr │   │   │
│  │   │  5. 52W High      10. PSAR         15. Div Yield     20. RSI  │   │   │
│  │   │                                                               │   │   │
│  │   └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              LAYER 4: ENSEMBLE & RANKING ENGINE                      │   │
│  │                                                                       │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │   │    Model     │    │   Regime-    │    │   Unified    │          │   │
│  │   │   Weights    │ →  │   Adjusted   │ →  │    Stock     │          │   │
│  │   │   Matrix     │    │    Scores    │    │   Rankings   │          │   │
│  │   └──────────────┘    └──────────────┘    └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              LAYER 5: RISK & POSITION SIZING                         │   │
│  │                                                                       │   │
│  │   Position Size = f(Confidence, Regime Volatility, Correlation)      │   │
│  │   Stop Loss = f(ATR, Regime Type, Model Agreement)                   │   │
│  │   Take Profit = f(Historical Win Rate, Expected Move)                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         OUTPUT LAYER                                 │   │
│  │                                                                       │   │
│  │   • Unified Stock Rankings (Top 10 Buy, Top 10 Avoid)               │   │
│  │   • Confidence Scores with Model Agreement Breakdown                 │   │
│  │   • Regime-Appropriate Position Sizing                               │   │
│  │   • PDF Report with Sales Commentary                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 The 20 Core Models (Detailed Specifications)

### Category 1: MOMENTUM MODELS (5 Models)

#### Model 1: High-Quality Momentum (HQM)
```python
# File: backend/app/models/momentum/hqm_model.py

class HQMModel:
    """
    High-Quality Momentum Score
    Combines multiple momentum timeframes with quality adjustment
    
    Formula:
        HQM_Score = weighted_avg(
            percentile_rank(return_1m),
            percentile_rank(return_3m),
            percentile_rank(return_6m),
            percentile_rank(return_12m)
        )
    
    Parameters:
        weights: [0.15, 0.25, 0.30, 0.30] for [1m, 3m, 6m, 12m]
        
    Regime Adjustments:
        BULL: weights = [0.20, 0.25, 0.30, 0.25]  # Favor recent momentum
        BEAR: weights = [0.10, 0.20, 0.30, 0.40]  # Favor sustained momentum
        SIDEWAYS: weights = [0.25, 0.25, 0.25, 0.25]  # Equal weight
        
    Output:
        score: 0-100 percentile rank
        signal: BUY (>80), HOLD (40-80), AVOID (<40)
    """
    
    def calculate(self, prices: pd.DataFrame, regime: str) -> dict:
        # Implementation here
        pass
```

#### Model 2: Clenow Momentum
```python
# File: backend/app/models/momentum/clenow_momentum.py

class ClenowMomentumModel:
    """
    Andreas Clenow's Exponential Regression Momentum
    Quality-adjusted momentum using regression slope and R²
    
    Formula:
        annualized_slope = (1 + daily_slope)^252 - 1
        momentum_score = annualized_slope × R²
    
    Parameters:
        lookback_period: 90 days (default)
        min_r_squared: 0.7 (quality threshold)
        
    Regime Adjustments:
        BULL: lookback = 60 days, min_r² = 0.6
        BEAR: lookback = 120 days, min_r² = 0.8
        SIDEWAYS: lookback = 90 days, min_r² = 0.7
        
    Output:
        score: momentum × R² (annualized %)
        signal: BUY (score > 20%), HOLD (0-20%), AVOID (<0%)
    """
```

#### Model 3: Dual Momentum (Absolute + Relative)
```python
# File: backend/app/models/momentum/dual_momentum.py

class DualMomentumModel:
    """
    Gary Antonacci's Dual Momentum
    Combines Absolute Momentum (vs risk-free) and Relative Momentum (vs peers)
    
    Formula:
        absolute_momentum = return_12m > risk_free_return
        relative_momentum = percentile_rank(return_12m) among universe
        dual_signal = absolute_momentum AND (relative_momentum > 50)
    
    Parameters:
        lookback: 12 months
        risk_free_proxy: "SET50" index or "TH10Y" bond yield
        
    Regime Adjustments:
        BULL: threshold = 40th percentile
        BEAR: threshold = 70th percentile (only top quality)
        SIDEWAYS: threshold = 50th percentile
    """
```

#### Model 4: ROC Multi-Timeframe
```python
# File: backend/app/models/momentum/roc_multi.py

class ROCMultiTimeframeModel:
    """
    Rate of Change across Multiple Timeframes
    Simple but effective momentum measure
    
    Formula:
        ROC_n = (Price_today / Price_n_days_ago - 1) × 100
        composite = weighted_avg(ROC_5, ROC_10, ROC_20, ROC_60)
    
    Parameters:
        periods: [5, 10, 20, 60] days
        weights: [0.1, 0.2, 0.3, 0.4]
        
    Regime Adjustments:
        BULL: favor shorter periods [0.2, 0.3, 0.3, 0.2]
        BEAR: favor longer periods [0.1, 0.1, 0.3, 0.5]
    """
```

#### Model 5: 52-Week High Momentum
```python
# File: backend/app/models/momentum/fifty_two_week.py

class FiftyTwoWeekHighModel:
    """
    Distance to 52-Week High
    Stocks near highs tend to continue outperforming
    
    Formula:
        distance_to_high = Price_today / 52W_High × 100
        new_high_count = count(new_highs_last_60_days)
        score = 0.7 × distance_to_high + 0.3 × new_high_frequency
    
    Parameters:
        lookback: 252 trading days
        new_high_window: 60 days
        
    Regime Adjustments:
        BULL: BUY if > 95% of high (breakout buy)
        BEAR: BUY if > 90% and improving (relative strength)
        SIDEWAYS: BUY if > 85% with low volatility
    """
```

---

### Category 2: TREND MODELS (5 Models)

#### Model 6: ADX Trend Strength
```python
# File: backend/app/models/trend/adx_trend.py

class ADXTrendModel:
    """
    Average Directional Index for Trend Strength
    
    Formula:
        ADX = smoothed_average(|+DI - -DI| / (+DI + -DI))
        +DI = smoothed(+DM) / ATR
        -DI = smoothed(-DM) / ATR
    
    Interpretation:
        ADX > 25: Trending market
        ADX < 20: Ranging market
        +DI > -DI: Uptrend
        -DI > +DI: Downtrend
        
    Parameters:
        period: 14 (default)
        trend_threshold: 25
        
    Regime Output:
        STRONG_UPTREND: ADX > 25, +DI > -DI
        WEAK_UPTREND: ADX < 25, +DI > -DI
        STRONG_DOWNTREND: ADX > 25, -DI > +DI
        RANGING: ADX < 20
    """
```

#### Model 7: Multi-EMA Matrix
```python
# File: backend/app/models/trend/multi_ema.py

class MultiEMAModel:
    """
    Multiple EMA Stack Analysis
    
    Formula:
        ema_stack = [EMA_8, EMA_13, EMA_21, EMA_34, EMA_55, EMA_89]
        price_position = count(price > ema) / 6
        stack_alignment = is_perfectly_ordered(ema_stack)
    
    Scoring:
        Perfect bull stack: 100 (Price > EMA8 > EMA13 > ... > EMA89)
        Perfect bear stack: 0 (Price < EMA8 < EMA13 < ... < EMA89)
        Mixed: proportional score
        
    Parameters:
        ema_periods: [8, 13, 21, 34, 55, 89] (Fibonacci-based)
        
    Signals:
        BUY: score > 80 AND stack aligned bullish
        AVOID: score < 20 AND stack aligned bearish
    """
```

#### Model 8: Supertrend
```python
# File: backend/app/models/trend/supertrend.py

class SupertrendModel:
    """
    ATR-based Trend Indicator with Stop Levels
    
    Formula:
        basic_upper = (high + low) / 2 + multiplier × ATR
        basic_lower = (high + low) / 2 - multiplier × ATR
        supertrend = upper_band if downtrend else lower_band
    
    Parameters:
        atr_period: 10
        multiplier: 3.0
        
    Regime Adjustments:
        HIGH_VOLATILITY: multiplier = 4.0 (wider bands)
        LOW_VOLATILITY: multiplier = 2.5 (tighter bands)
        
    Output:
        trend: "BULLISH" or "BEARISH"
        stop_level: Current supertrend value
        distance_to_stop: % distance to stop
    """
```

#### Model 9: Ichimoku Cloud
```python
# File: backend/app/models/trend/ichimoku.py

class IchimokuModel:
    """
    Complete Ichimoku Kinko Hyo System
    
    Components:
        tenkan_sen = (highest_9 + lowest_9) / 2
        kijun_sen = (highest_26 + lowest_26) / 2
        senkou_span_a = (tenkan + kijun) / 2, shifted 26 periods forward
        senkou_span_b = (highest_52 + lowest_52) / 2, shifted 26 forward
        chikou_span = close, shifted 26 periods backward
    
    Signals:
        STRONG_BUY: Price above cloud, tenkan > kijun, chikou > price_26_ago
        BUY: Price above cloud
        NEUTRAL: Price in cloud
        AVOID: Price below cloud
        
    Parameters:
        tenkan_period: 9
        kijun_period: 26
        senkou_b_period: 52
    """
```

#### Model 10: Parabolic SAR
```python
# File: backend/app/models/trend/parabolic_sar.py

class ParabolicSARModel:
    """
    Parabolic Stop and Reverse
    
    Formula:
        SAR_next = SAR_current + AF × (EP - SAR_current)
        AF starts at 0.02, increases by 0.02 at each new EP, max 0.20
        EP = Extreme Point (highest high in uptrend, lowest low in downtrend)
    
    Parameters:
        af_start: 0.02
        af_increment: 0.02
        af_max: 0.20
        
    Regime Adjustments:
        TRENDING: Use standard parameters
        RANGING: Increase AF for faster reversals
        
    Output:
        trend: "BULLISH" or "BEARISH"
        sar_level: Current SAR value
        days_in_trend: Consecutive days in current trend
    """
```

---

### Category 3: FUNDAMENTAL MODELS (5 Models)

#### Model 11: Magic Formula (Greenblatt)
```python
# File: backend/app/models/fundamental/magic_formula.py

class MagicFormulaModel:
    """
    Joel Greenblatt's Magic Formula
    
    Formula:
        earnings_yield = EBIT / Enterprise_Value
        return_on_capital = EBIT / (Net_Fixed_Assets + Working_Capital)
        
        rank_ey = percentile_rank(earnings_yield)
        rank_roc = percentile_rank(return_on_capital)
        combined_rank = rank_ey + rank_roc
    
    Parameters:
        min_market_cap: 1000 (million THB)
        exclude_financials: True
        exclude_utilities: True
        
    Signals:
        BUY: Combined rank in top 20%
        HOLD: Combined rank 20-50%
        AVOID: Combined rank bottom 30%
    """
```

#### Model 12: GARP (Growth at Reasonable Price)
```python
# File: backend/app/models/fundamental/garp.py

class GARPModel:
    """
    Peter Lynch's GARP Strategy
    
    Formula:
        PEG_ratio = P/E / EPS_Growth_Rate
        score = 1 / PEG_ratio (higher is better when PEG < 1)
    
    Conditions:
        eps_growth > 10%
        pe_ratio < 40
        peg_ratio < 1.5 (ideally < 1.0)
        
    Parameters:
        max_peg: 1.5
        min_growth: 10%
        max_pe: 40
        
    Regime Adjustments:
        BULL: Accept PEG up to 2.0
        BEAR: Require PEG < 1.0
    """
```

#### Model 13: Quality Factor
```python
# File: backend/app/models/fundamental/quality.py

class QualityModel:
    """
    Quality Factor Composite
    
    Components:
        ROE_stability = 1 - std(ROE_5yr) / mean(ROE_5yr)
        earnings_quality = CFO / Net_Income (>1 is good)
        leverage_quality = 1 / (1 + Debt/Equity)
        
    Formula:
        quality_score = 0.35 × ROE_stability + 
                       0.35 × earnings_quality + 
                       0.30 × leverage_quality
    
    Parameters:
        lookback_years: 5
        min_roe: 10%
        max_debt_equity: 2.0
        
    Regime Adjustments:
        BEAR/HIGH_VOL: Increase weight on quality (defensive)
    """
```

#### Model 14: Altman Z-Score
```python
# File: backend/app/models/fundamental/altman_z.py

class AltmanZScoreModel:
    """
    Altman Z-Score for Financial Health
    
    Formula (for non-manufacturing):
        Z = 6.56×X1 + 3.26×X2 + 6.72×X3 + 1.05×X4
        
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Book Value of Equity / Total Liabilities
    
    Interpretation:
        Z > 2.6: Safe zone
        1.1 < Z < 2.6: Grey zone
        Z < 1.1: Distress zone
        
    Regime Adjustments:
        BEAR: Heavily penalize Z < 2.0
        BULL: Accept Z > 1.5 for growth stories
    """
```

#### Model 15: Dividend Yield + Growth
```python
# File: backend/app/models/fundamental/dividend.py

class DividendModel:
    """
    Dividend Quality Model
    
    Components:
        current_yield = Annual_Dividend / Price
        dividend_growth = CAGR(dividends, 5yr)
        payout_sustainability = Dividend / EPS (want < 80%)
        
    Formula:
        score = yield × (1 + growth_rate) × sustainability_factor
    
    Parameters:
        min_yield: 2%
        min_growth: 0%
        max_payout: 80%
        consecutive_years: 3 (minimum years of dividends)
        
    Regime Adjustments:
        BEAR/SIDEWAYS: Increase weight (defensive income)
        BULL: Decrease weight (favor growth)
    """
```

---

### Category 4: QUANTITATIVE/STATISTICAL MODELS (5 Models)

#### Model 16: HMM Regime Detection
```python
# File: backend/app/models/quant/hmm_regime.py

class HMMRegimeModel:
    """
    Hidden Markov Model for Market Regime Detection
    
    States:
        State 0: BULL (high return, low volatility)
        State 1: BEAR (negative return, high volatility)
        State 2: SIDEWAYS (low return, low volatility)
    
    Features:
        - 20-day returns
        - 20-day volatility
        - Volume trend
        
    Output:
        current_regime: 0, 1, or 2
        regime_probability: [p_bull, p_bear, p_sideways]
        regime_stability: days in current regime
        
    Implementation:
        Library: hmmlearn
        Training: Rolling 252-day window
        Retrain: Weekly
    """
```

#### Model 17: Volatility Regime
```python
# File: backend/app/models/quant/volatility_regime.py

class VolatilityRegimeModel:
    """
    Volatility-Based Regime Classification
    
    Formula:
        current_vol = realized_vol_20d
        historical_vol = percentile(current_vol, 252d_history)
        
    Regimes:
        LOW_VOL: vol < 25th percentile
        NORMAL_VOL: vol 25th-75th percentile
        HIGH_VOL: vol > 75th percentile
        VOL_SPIKE: vol > 90th percentile AND vol_change > 50%
    
    Position Sizing Multiplier:
        LOW_VOL: 1.25× normal size
        NORMAL_VOL: 1.0× normal size
        HIGH_VOL: 0.5× normal size
        VOL_SPIKE: 0.25× normal size or cash
    """
```

#### Model 18: Mean Reversion (Bollinger)
```python
# File: backend/app/models/quant/mean_reversion.py

class MeanReversionModel:
    """
    Bollinger Band Mean Reversion
    
    Formula:
        middle_band = SMA(close, 20)
        std_dev = std(close, 20)
        upper_band = middle + 2 × std
        lower_band = middle - 2 × std
        
        z_score = (close - middle) / std_dev
        bandwidth = (upper - lower) / middle
    
    Signals:
        OVERSOLD_BUY: z_score < -2 AND bandwidth > 0.1
        OVERBOUGHT_AVOID: z_score > 2
        
    Regime Conditions:
        Only active in SIDEWAYS regime
        Disabled in strong TRENDING regime
    """
```

#### Model 19: Correlation Regime
```python
# File: backend/app/models/quant/correlation_regime.py

class CorrelationRegimeModel:
    """
    Stock-to-Market Correlation Analysis
    
    Formula:
        beta = cov(stock, market) / var(market)
        correlation = corr(stock_returns, market_returns)
        idiosyncratic_vol = std(stock - beta × market)
    
    Classification:
        HIGH_BETA (>1.3): Aggressive, amplifies market moves
        MARKET_LIKE (0.8-1.2): Tracks market
        LOW_BETA (<0.8): Defensive
        NEGATIVE_BETA (<0): Hedge
    
    Regime Usage:
        BULL: Prefer HIGH_BETA for leverage
        BEAR: Prefer LOW_BETA or NEGATIVE_BETA
        SIDEWAYS: Prefer HIGH idiosyncratic (stock pickers)
    """
```

#### Model 20: RSI Divergence
```python
# File: backend/app/models/quant/rsi_divergence.py

class RSIDivergenceModel:
    """
    RSI with Divergence Detection
    
    Formula:
        RSI = 100 - (100 / (1 + RS))
        RS = avg_gain / avg_loss over 14 periods
        
    Divergence Types:
        BULLISH: Price makes lower low, RSI makes higher low
        BEARISH: Price makes higher high, RSI makes lower high
    
    Parameters:
        rsi_period: 14
        divergence_lookback: 20 bars
        min_divergence_bars: 5
        
    Signals:
        STRONG_BUY: Bullish divergence + RSI < 30
        STRONG_AVOID: Bearish divergence + RSI > 70
    """
```

---

## 🎛️ Market Regime Engine (Layer 1)

The regime engine is the **brain** of the system. It runs first and determines how all other models behave.

```python
# File: backend/app/models/regime/regime_engine.py

class RegimeEngine:
    """
    Master Regime Detection System
    Combines multiple regime indicators into a unified view
    """
    
    def __init__(self):
        self.hmm_model = HMMRegimeModel()
        self.vol_model = VolatilityRegimeModel()
        self.breadth_model = BreadthRegimeModel()
        self.adx_model = ADXTrendModel()
    
    def detect_regime(self, market_data: pd.DataFrame) -> RegimeState:
        """
        Returns unified regime classification
        
        Output:
            RegimeState:
                trend_regime: BULL | BEAR | SIDEWAYS
                volatility_regime: LOW | NORMAL | HIGH | SPIKE
                confidence: 0.0 - 1.0
                active_models: List[str] (which models to activate)
                model_weights: Dict[str, float] (weight adjustments)
                position_size_multiplier: 0.25 - 1.25
        """
        
        # Get individual regime signals
        hmm_regime = self.hmm_model.predict(market_data)
        vol_regime = self.vol_model.classify(market_data)
        breadth = self.breadth_model.calculate(market_data)
        trend = self.adx_model.analyze(market_data)
        
        # Combine with voting/weighting
        combined = self._combine_regimes(hmm_regime, vol_regime, breadth, trend)
        
        # Determine which models to activate
        active_models = self._get_active_models(combined)
        
        # Determine model weight adjustments
        weights = self._get_model_weights(combined)
        
        return RegimeState(
            trend_regime=combined.trend,
            volatility_regime=combined.volatility,
            confidence=combined.confidence,
            active_models=active_models,
            model_weights=weights,
            position_size_multiplier=self._get_position_multiplier(combined)
        )
    
    def _get_active_models(self, regime: CombinedRegime) -> List[str]:
        """Determine which models should be active based on regime"""
        
        MODEL_ACTIVATION = {
            "BULL": {
                "always_on": ["hqm", "clenow", "dual_momentum", "roc_multi", "52w_high",
                             "adx", "multi_ema", "supertrend", "ichimoku", "psar"],
                "weight_increased": ["momentum", "trend", "growth"],
                "weight_decreased": ["mean_reversion", "defensive"],
            },
            "BEAR": {
                "always_on": ["quality", "altman_z", "dividend", "vol_regime", "correlation"],
                "weight_increased": ["quality", "value", "defensive"],
                "weight_decreased": ["momentum", "growth"],
            },
            "SIDEWAYS": {
                "always_on": ["mean_reversion", "rsi_divergence", "bollinger", "quality", "dividend"],
                "weight_increased": ["mean_reversion", "range_bound"],
                "weight_decreased": ["trend_following"],
            }
        }
        
        return MODEL_ACTIVATION[regime.trend]["always_on"]
```

---

## ⚖️ Model Orchestrator (Layer 2)

```python
# File: backend/app/core/orchestrator.py

class ModelOrchestrator:
    """
    Coordinates model execution based on current regime
    """
    
    # Model weight matrix by regime
    WEIGHT_MATRIX = {
        # Rows: Models, Columns: Regimes (BULL, BEAR, SIDEWAYS)
        "hqm":           [1.0, 0.3, 0.5],
        "clenow":        [1.0, 0.3, 0.5],
        "dual_momentum": [1.0, 0.5, 0.6],
        "roc_multi":     [0.9, 0.4, 0.7],
        "52w_high":      [1.0, 0.3, 0.5],
        "adx":           [0.8, 0.6, 0.8],
        "multi_ema":     [0.9, 0.5, 0.6],
        "supertrend":    [0.9, 0.6, 0.4],
        "ichimoku":      [0.8, 0.6, 0.5],
        "psar":          [0.7, 0.5, 0.4],
        "magic_formula": [0.6, 0.8, 0.7],
        "garp":          [0.8, 0.6, 0.7],
        "quality":       [0.5, 1.0, 0.8],
        "altman_z":      [0.4, 1.0, 0.7],
        "dividend":      [0.3, 0.9, 0.8],
        "hmm_regime":    [0.5, 0.5, 0.5],  # Meta-model, always same weight
        "vol_regime":    [0.6, 0.8, 0.7],
        "mean_reversion":[0.2, 0.4, 1.0],  # Only high in sideways
        "correlation":   [0.6, 0.9, 0.6],
        "rsi_divergence":[0.4, 0.6, 0.9],
    }
    
    def execute_models(self, 
                       universe: List[str], 
                       regime: RegimeState) -> pd.DataFrame:
        """
        Execute all active models with regime-adjusted weights
        
        Returns:
            DataFrame with columns: ticker, model_1_score, model_2_score, ..., 
                                   weighted_composite, rank
        """
        
        results = pd.DataFrame(index=universe)
        
        for model_name in regime.active_models:
            model = self.model_registry[model_name]
            weight = self._get_weight(model_name, regime.trend_regime)
            
            # Execute model with regime-specific parameters
            model_params = self._get_regime_params(model_name, regime)
            scores = model.calculate(universe, **model_params)
            
            results[f"{model_name}_score"] = scores
            results[f"{model_name}_weight"] = weight
        
        # Calculate weighted composite
        results["composite_score"] = self._calculate_composite(results, regime)
        results["rank"] = results["composite_score"].rank(ascending=False)
        
        return results.sort_values("rank")
```

---

## 📊 Ensemble & Ranking Engine (Layer 4)

```python
# File: backend/app/core/ensemble.py

class EnsembleEngine:
    """
    Combines all model outputs into unified stock rankings
    """
    
    def calculate_composite(self, 
                           model_results: pd.DataFrame,
                           regime: RegimeState) -> pd.DataFrame:
        """
        Generate final stock rankings
        
        Methodology:
        1. Normalize each model's scores to 0-100
        2. Apply regime-based weights
        3. Apply confidence adjustments
        4. Calculate model agreement score
        5. Generate final composite
        """
        
        normalized = self._normalize_scores(model_results)
        weighted = self._apply_weights(normalized, regime)
        
        # Model Agreement Score
        # How many models agree on direction?
        agreement = self._calculate_agreement(weighted)
        
        # Final composite with agreement boost
        composite = weighted.mean(axis=1) * (1 + 0.2 * agreement)
        
        return pd.DataFrame({
            "ticker": model_results.index,
            "composite_score": composite,
            "model_agreement": agreement,
            "confidence": self._calculate_confidence(composite, agreement),
            "signal": self._generate_signal(composite, agreement),
            "rank": composite.rank(ascending=False)
        })
    
    def _calculate_agreement(self, scores: pd.DataFrame) -> pd.Series:
        """
        Calculate % of models agreeing on direction
        
        Agreement = count(BUY signals) / total_models for longs
                  = count(AVOID signals) / total_models for shorts
        """
        buy_threshold = 70  # Score > 70 = BUY
        avoid_threshold = 30  # Score < 30 = AVOID
        
        buy_count = (scores > buy_threshold).sum(axis=1)
        avoid_count = (scores < avoid_threshold).sum(axis=1)
        total = scores.shape[1]
        
        # Agreement is max of buy or avoid agreement
        return pd.concat([buy_count, avoid_count], axis=1).max(axis=1) / total
```

---

## 📁 Project Directory Structure

```
quant-project-v2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Configuration management
│   │   │
│   │   ├── core/                      # Core orchestration logic
│   │   │   ├── __init__.py
│   │   │   ├── regime_engine.py       # Layer 1: Regime detection
│   │   │   ├── orchestrator.py        # Layer 2: Model orchestration
│   │   │   ├── ensemble.py            # Layer 4: Ranking engine
│   │   │   └── risk_manager.py        # Layer 5: Position sizing
│   │   │
│   │   ├── models/                    # Layer 3: All models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base model interface
│   │   │   ├── registry.py            # Model registry
│   │   │   │
│   │   │   ├── momentum/              # Momentum models (1-5)
│   │   │   │   ├── hqm_model.py
│   │   │   │   ├── clenow_momentum.py
│   │   │   │   ├── dual_momentum.py
│   │   │   │   ├── roc_multi.py
│   │   │   │   └── fifty_two_week.py
│   │   │   │
│   │   │   ├── trend/                 # Trend models (6-10)
│   │   │   │   ├── adx_trend.py
│   │   │   │   ├── multi_ema.py
│   │   │   │   ├── supertrend.py
│   │   │   │   ├── ichimoku.py
│   │   │   │   └── parabolic_sar.py
│   │   │   │
│   │   │   ├── fundamental/           # Fundamental models (11-15)
│   │   │   │   ├── magic_formula.py
│   │   │   │   ├── garp.py
│   │   │   │   ├── quality.py
│   │   │   │   ├── altman_z.py
│   │   │   │   └── dividend.py
│   │   │   │
│   │   │   └── quant/                 # Quantitative models (16-20)
│   │   │       ├── hmm_regime.py
│   │   │       ├── volatility_regime.py
│   │   │       ├── mean_reversion.py
│   │   │       ├── correlation_regime.py
│   │   │       └── rsi_divergence.py
│   │   │
│   │   ├── data/                      # Data layer
│   │   │   ├── __init__.py
│   │   │   ├── fetcher.py             # Market data fetching
│   │   │   ├── universe.py            # SET50/SET100 definitions
│   │   │   └── cache.py               # Data caching
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── models.py          # /api/models endpoints
│   │   │   │   ├── regime.py          # /api/regime endpoints
│   │   │   │   ├── screening.py       # /api/screen endpoints
│   │   │   │   └── reports.py         # /api/reports endpoints
│   │   │   └── schemas.py             # Pydantic schemas
│   │   │
│   │   └── reports/                   # Report generation
│   │       ├── __init__.py
│   │       └── pdf_generator.py       # Professional PDF output
│   │
│   ├── tests/                         # Unit tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RegimeIndicator.tsx    # Current regime display
│   │   │   ├── ModelWeights.tsx       # Active model weights
│   │   │   ├── StockRankings.tsx      # Top/Bottom stocks
│   │   │   ├── ModelAgreement.tsx     # Agreement heatmap
│   │   │   └── PositionSizer.tsx      # Position recommendations
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          # Main dashboard
│   │   │   ├── Screening.tsx          # Stock screening
│   │   │   └── Reports.tsx            # Report generation
│   │   └── hooks/
│   │       └── useRegime.ts           # Regime state hook
│   ├── package.json
│   └── next.config.js
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md                # This document
│   ├── MODEL_SPECIFICATIONS.md        # Detailed model docs
│   └── API_REFERENCE.md               # API documentation
│
└── scripts/
    ├── backtest.py                    # Backtesting framework
    └── data_quality.py                # Data validation
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure
- [ ] Implement base model interface
- [ ] Implement Regime Engine (HMM + Volatility)
- [ ] Implement 3 core models (HQM, ADX, Quality)
- [ ] Basic API endpoints
- [ ] Simple frontend dashboard

### Phase 2: Core Models (Week 3-4)
- [ ] Implement remaining 17 models
- [ ] Implement Model Orchestrator
- [ ] Implement Ensemble Engine
- [ ] Model weight matrix configuration
- [ ] Regime-conditional parameter adjustments

### Phase 3: Integration (Week 5-6)
- [ ] Full API integration
- [ ] Dashboard with all components
- [ ] PDF report generation
- [ ] Backtesting framework
- [ ] Performance tracking

### Phase 4: Production (Week 7-8)
- [ ] Data source integration (SETSMART API)
- [ ] Authentication & authorization
- [ ] Monitoring & alerting
- [ ] Performance optimization
- [ ] Documentation completion

---

## 📋 How to Use This Document

### When Starting a New Claude Code Session:

1. **Provide this document** as context
2. **Specify which component** you're working on
3. **Reference the specific model numbers** (e.g., "Implement Model 6: ADX Trend")

### Example Prompt for New Session:

```
I'm continuing work on my Renaissance-style quant project. 
Please read the attached ARCHITECTURE.md file.

Current status: 
- Phase 1 complete
- Working on Phase 2, Model 7 (Multi-EMA Matrix)

Next task: Implement the Multi-EMA Matrix model following the 
specification in the architecture document.
```

### Key Files to Track Progress:

1. `backend/app/models/registry.py` - Lists all implemented models
2. `backend/app/core/orchestrator.py` - Model weight matrix
3. `docs/IMPLEMENTATION_LOG.md` - Track what's been built

---

## 🎯 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Model Implementation | 20/20 models | Count of working models |
| Backtest Sharpe Ratio | > 1.5 | VectorBT backtest |
| Regime Detection Accuracy | > 70% | vs actual market behavior |
| Signal Win Rate | > 55% | Forward performance tracking |
| Model Agreement Correlation | > 0.3 | vs future returns |

---

## 📚 References

- **Renaissance Technologies**: Multi-model ensemble approach
- **AQR**: Factor-based investing
- **Two Sigma**: Machine learning + systematic trading
- **Cliff Asness**: Factor model research
- **Andreas Clenow**: "Stocks on the Move" momentum methodology

---

*Document Version: 1.0*  
*Last Updated: January 2026*  
*Next Review: After Phase 2 completion*

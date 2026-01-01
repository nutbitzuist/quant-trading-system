"""
Model Registry
Tracks all 20 quantitative models and their implementation status
"""

from typing import Dict, List, Type, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """Information about a registered model"""
    name: str
    class_name: str
    category: str
    description: str
    implemented: bool = False
    tested: bool = False
    module_path: str = ""


# Registry of all 20 models
MODEL_REGISTRY: Dict[str, ModelInfo] = {
    # Momentum Models (M1-M5)
    "hqm": ModelInfo(
        name="hqm",
        class_name="HQMModel",
        category="momentum",
        description="High-Quality Momentum: Multi-timeframe momentum percentile",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.momentum.hqm_model"
    ),
    "clenow": ModelInfo(
        name="clenow",
        class_name="ClenowMomentumModel",
        category="momentum",
        description="Clenow Momentum: Regression slope × R²",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.momentum.clenow_momentum"
    ),
    "dual_momentum": ModelInfo(
        name="dual_momentum",
        class_name="DualMomentumModel",
        category="momentum",
        description="Dual Momentum: Absolute + Relative momentum",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.momentum.dual_momentum"
    ),
    "roc_multi": ModelInfo(
        name="roc_multi",
        class_name="ROCMultiTimeframeModel",
        category="momentum",
        description="ROC Multi-Timeframe: Weighted rate of change",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.momentum.roc_multi"
    ),
    "52w_high": ModelInfo(
        name="52w_high",
        class_name="FiftyTwoWeekHighModel",
        category="momentum",
        description="52-Week High: Distance to 52-week high",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.momentum.fifty_two_week"
    ),
    
    # Trend Models (M6-M10)
    "adx": ModelInfo(
        name="adx",
        class_name="ADXTrendModel",
        category="trend",
        description="ADX Trend Strength: Trend strength 0-100",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.trend.adx_trend"
    ),
    "multi_ema": ModelInfo(
        name="multi_ema",
        class_name="MultiEMAModel",
        category="trend",
        description="Multi-EMA Matrix: EMA stack alignment",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.trend.multi_ema"
    ),
    "supertrend": ModelInfo(
        name="supertrend",
        class_name="SupertrendModel",
        category="trend",
        description="Supertrend: ATR-based trend with stops",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.trend.supertrend"
    ),
    "ichimoku": ModelInfo(
        name="ichimoku",
        class_name="IchimokuModel",
        category="trend",
        description="Ichimoku Cloud: Complete trend system",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.trend.ichimoku"
    ),
    "psar": ModelInfo(
        name="psar",
        class_name="ParabolicSARModel",
        category="trend",
        description="Parabolic SAR: Stop and reverse",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.trend.parabolic_sar"
    ),
    
    "magic_formula": ModelInfo(
        name="magic_formula",
        class_name="MagicFormulaModel",
        category="fundamental",
        description="Magic Formula: Greenblatt's EY + ROC rank",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.fundamental.magic_formula"
    ),
    "garp": ModelInfo(
        name="garp",
        class_name="GARPModel",
        category="fundamental",
        description="GARP: Growth at Reasonable Price (PEG)",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.fundamental.garp"
    ),
    "quality": ModelInfo(
        name="quality",
        class_name="QualityModel",
        category="fundamental",
        description="Quality Factor: ROE stability + earnings quality",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.fundamental.quality"
    ),
    "altman_z": ModelInfo(
        name="altman_z",
        class_name="AltmanZScoreModel",
        category="fundamental",
        description="Altman Z-Score: Financial distress prediction",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.fundamental.altman_z"
    ),
    "dividend": ModelInfo(
        name="dividend",
        class_name="DividendModel",
        category="fundamental",
        description="Dividend Quality: Yield + growth + sustainability",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.fundamental.dividend"
    ),
    
    # Quantitative Models (M16-M20)
    "hmm_regime": ModelInfo(
        name="hmm_regime",
        class_name="HMMRegimeModel",
        category="quant",
        description="HMM Regime: Hidden Markov Model regime detection",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.quant.hmm_regime"
    ),
    "vol_regime": ModelInfo(
        name="vol_regime",
        class_name="VolatilityRegimeModel",
        category="quant",
        description="Volatility Regime: Vol percentile classification",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.quant.volatility_regime"
    ),
    "mean_reversion": ModelInfo(
        name="mean_reversion",
        class_name="MeanReversionModel",
        category="quant",
        description="Mean Reversion: Bollinger z-score",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.quant.mean_reversion"
    ),
    "correlation": ModelInfo(
        name="correlation",
        class_name="CorrelationRegimeModel",
        category="quant",
        description="Correlation Regime: Beta classification",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.quant.correlation_regime"
    ),
    "rsi_divergence": ModelInfo(
        name="rsi_divergence",
        class_name="RSIDivergenceModel",
        category="quant",
        description="RSI Divergence: Price/RSI divergence detection",
        implemented=True,  # IMPLEMENTED
        module_path="app.models.quant.rsi_divergence"
    ),
}


def get_implemented_models() -> List[str]:
    """Return list of implemented model names"""
    return [name for name, info in MODEL_REGISTRY.items() if info.implemented]


def get_unimplemented_models() -> List[str]:
    """Return list of unimplemented model names"""
    return [name for name, info in MODEL_REGISTRY.items() if not info.implemented]


def get_models_by_category(category: str) -> List[str]:
    """Return list of model names in a category"""
    return [name for name, info in MODEL_REGISTRY.items() if info.category == category]


def get_model_info(model_name: str) -> Optional[ModelInfo]:
    """Get info for a specific model"""
    return MODEL_REGISTRY.get(model_name)


def mark_model_implemented(model_name: str) -> bool:
    """Mark a model as implemented"""
    if model_name in MODEL_REGISTRY:
        MODEL_REGISTRY[model_name].implemented = True
        return True
    return False


def mark_model_tested(model_name: str) -> bool:
    """Mark a model as tested"""
    if model_name in MODEL_REGISTRY:
        MODEL_REGISTRY[model_name].tested = True
        return True
    return False


def get_implementation_status() -> Dict[str, int]:
    """Get summary of implementation status"""
    total = len(MODEL_REGISTRY)
    implemented = len(get_implemented_models())
    tested = sum(1 for info in MODEL_REGISTRY.values() if info.tested)
    
    return {
        "total": total,
        "implemented": implemented,
        "tested": tested,
        "remaining": total - implemented
    }


# Categories for easy iteration
CATEGORIES = ["momentum", "trend", "fundamental", "quant"]

"""
Base Model Interface
All 20 models must implement this interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import pandas as pd


class Signal(Enum):
    """Trading signal types"""
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    AVOID = -1
    STRONG_AVOID = -2


class Regime(Enum):
    """Market regime types"""
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"
    NEUTRAL = "NEUTRAL"


class VolatilityRegime(Enum):
    """Volatility regime types"""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    SPIKE = "SPIKE"


@dataclass
class ModelResult:
    """
    Result from a single model for a single stock
    
    Attributes:
        ticker: Stock ticker symbol
        score: Normalized score 0-100
        signal: Trading signal (STRONG_BUY to STRONG_AVOID)
        confidence: Model's confidence in the signal (0-1)
        metadata: Additional model-specific data
    """
    ticker: str
    score: float  # 0-100 normalized
    signal: Signal
    confidence: float  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate score and confidence ranges"""
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be 0-100, got {self.score}")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")


@dataclass
class RegimeState:
    """
    Current market regime state
    
    Attributes:
        trend_regime: Current trend (BULL, BEAR, SIDEWAYS)
        volatility_regime: Current volatility (LOW, NORMAL, HIGH, SPIKE)
        confidence: Confidence in regime detection (0-1)
        active_models: List of model names to activate
        model_weights: Dict of model name -> weight multiplier
        position_size_multiplier: Position sizing multiplier (0.25-1.25)
    """
    trend_regime: Regime
    volatility_regime: VolatilityRegime
    confidence: float
    active_models: List[str]
    model_weights: Dict[str, float]
    position_size_multiplier: float = 1.0


class BaseModel(ABC):
    """
    Abstract base class for all quantitative models.
    
    All 20 models must inherit from this class and implement:
    - calculate(): Run the model and return results
    - get_regime_params(): Return regime-specific parameters
    
    Attributes:
        name: Unique model identifier (e.g., "hqm", "adx")
        category: Model category (momentum, trend, fundamental, quant)
        description: Brief description of the model
    """
    
    name: str = "base"
    category: str = "base"
    description: str = "Base model interface"
    
    def __init__(self):
        """Initialize the model"""
        pass
    
    @abstractmethod
    def calculate(
        self, 
        prices: pd.DataFrame, 
        fundamentals: Optional[Dict[str, Any]] = None,
        regime: str = "NEUTRAL"
    ) -> List[ModelResult]:
        """
        Run model calculations for all stocks in the universe.
        
        Args:
            prices: DataFrame with columns [open, high, low, close, volume]
                   and MultiIndex (ticker, date) or ticker as column
            fundamentals: Optional dict of fundamental data by ticker
            regime: Current market regime (BULL, BEAR, SIDEWAYS, NEUTRAL)
            
        Returns:
            List of ModelResult objects, one per ticker
        """
        pass
    
    @abstractmethod
    def get_regime_params(self, regime: str) -> Dict[str, Any]:
        """
        Return regime-specific parameters for this model.
        
        Different regimes may require different lookback periods,
        thresholds, or weights.
        
        Args:
            regime: Current market regime (BULL, BEAR, SIDEWAYS)
            
        Returns:
            Dict of parameter name -> value
        """
        pass
    
    def normalize_score(
        self, 
        raw_score: float, 
        min_val: float, 
        max_val: float
    ) -> float:
        """
        Normalize a raw score to 0-100 scale.
        
        Args:
            raw_score: The raw score to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            
        Returns:
            Normalized score between 0 and 100
        """
        if max_val == min_val:
            return 50.0
        normalized = (raw_score - min_val) / (max_val - min_val) * 100
        return max(0.0, min(100.0, normalized))
    
    def score_to_signal(self, score: float) -> Signal:
        """
        Convert normalized score to trading signal.
        
        Args:
            score: Normalized score (0-100)
            
        Returns:
            Signal enum value
        """
        if score >= 80:
            return Signal.STRONG_BUY
        elif score >= 60:
            return Signal.BUY
        elif score >= 40:
            return Signal.HOLD
        elif score >= 20:
            return Signal.AVOID
        else:
            return Signal.STRONG_AVOID
    
    def calculate_confidence(
        self, 
        score: float, 
        data_quality: float = 1.0
    ) -> float:
        """
        Calculate confidence based on score extremity and data quality.
        
        Confidence is higher when:
        - Score is more extreme (closer to 0 or 100)
        - Data quality is higher
        
        Args:
            score: Normalized score (0-100)
            data_quality: Data quality factor (0-1)
            
        Returns:
            Confidence value (0-1)
        """
        # Extremity: how far from 50 (neutral)
        extremity = abs(score - 50) / 50
        
        # Confidence is weighted combination
        confidence = 0.7 * extremity + 0.3 * data_quality
        
        return max(0.0, min(1.0, confidence))


# Weight matrix for regime-conditional model weighting
# Format: model_name -> [BULL_weight, BEAR_weight, SIDEWAYS_weight]
WEIGHT_MATRIX: Dict[str, List[float]] = {
    # Momentum models (favor BULL)
    "hqm":           [1.0, 0.3, 0.5],
    "clenow":        [1.0, 0.3, 0.5],
    "dual_momentum": [1.0, 0.5, 0.6],
    "roc_multi":     [0.9, 0.4, 0.7],
    "52w_high":      [1.0, 0.3, 0.5],
    
    # Trend models (moderate across regimes)
    "adx":           [0.8, 0.6, 0.8],
    "multi_ema":     [0.9, 0.5, 0.6],
    "supertrend":    [0.9, 0.6, 0.4],
    "ichimoku":      [0.8, 0.6, 0.5],
    "psar":          [0.7, 0.5, 0.4],
    
    # Fundamental models (favor BEAR)
    "magic_formula": [0.6, 0.8, 0.7],
    "garp":          [0.8, 0.6, 0.7],
    "quality":       [0.5, 1.0, 0.8],
    "altman_z":      [0.4, 1.0, 0.7],
    "dividend":      [0.3, 0.9, 0.8],
    
    # Quantitative models (mixed)
    "hmm_regime":    [0.5, 0.5, 0.5],  # Meta-model, constant weight
    "vol_regime":    [0.6, 0.8, 0.7],
    "mean_reversion":[0.2, 0.4, 1.0],  # Best in SIDEWAYS
    "correlation":   [0.6, 0.9, 0.6],
    "rsi_divergence":[0.4, 0.6, 0.9],
}


def get_model_weight(model_name: str, regime: str) -> float:
    """
    Get the weight multiplier for a model in a given regime.
    
    Args:
        model_name: Name of the model
        regime: Current market regime (BULL, BEAR, SIDEWAYS)
        
    Returns:
        Weight multiplier (0-1)
    """
    regime_index = {"BULL": 0, "BEAR": 1, "SIDEWAYS": 2}
    
    if model_name not in WEIGHT_MATRIX:
        return 0.5  # Default weight for unknown models
    
    idx = regime_index.get(regime, 2)  # Default to SIDEWAYS
    return WEIGHT_MATRIX[model_name][idx]

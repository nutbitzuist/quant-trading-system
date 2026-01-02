"""
Model Orchestrator (Layer 2)
Coordinates model execution based on current regime
"""

from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass

from app.models.base import (
    BaseModel, 
    ModelResult, 
    RegimeState, 
    Regime,
    WEIGHT_MATRIX,
    get_model_weight,
)
from app.models.registry import MODEL_REGISTRY, get_implemented_models


@dataclass
class OrchestrationResult:
    """Result from model orchestration."""
    ticker: str
    model_scores: Dict[str, float]
    model_signals: Dict[str, str]
    weighted_scores: Dict[str, float]
    composite_score: float
    model_agreement: float
    rank: int


class ModelOrchestrator:
    """
    Model Orchestrator (Layer 2)
    
    Coordinates execution of all active models based on current regime.
    
    Responsibilities:
    1. Load and instantiate active models
    2. Execute models with regime-specific parameters
    3. Apply regime-based weights to scores
    4. Collect and organize results
    """
    
    def __init__(self):
        """Initialize orchestrator with model instances."""
        self._models: Dict[str, BaseModel] = {}
        self._load_implemented_models()
    
    def _load_implemented_models(self):
        """Load all implemented models."""
        implemented = get_implemented_models()
        
        for model_name in implemented:
            try:
                model_class = self._get_model_class(model_name)
                if model_class:
                    self._models[model_name] = model_class()
            except Exception as e:
                print(f"Warning: Could not load model {model_name}: {e}")
    
    def _get_model_class(self, model_name: str) -> Optional[type]:
        """Get model class by name."""
        # Get info from registry
        model_info = MODEL_REGISTRY.get(model_name)
        if not model_info:
            return None
        
        if not model_info.implemented:
            # Check if file actually exists just in case registry is outdated
            # But normally we respect the flag. 
            # For now, we trust registry is source of truth.
            return None
        
        try:
            import importlib
            module = importlib.import_module(model_info.module_path)
            return getattr(module, model_info.class_name)
        except Exception as e:
            print(f"Could not import {model_name} from {model_info.module_path}: {e}")
            return None
    
    def execute_models(
        self,
        prices: pd.DataFrame,
        regime_state: RegimeState,
        fundamentals: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[OrchestrationResult]:
        """
        Execute all active models for the current regime.
        
        Args:
            prices: Price data for all stocks
            regime_state: Current regime state with active models and weights
            fundamentals: Optional fundamental data by ticker
            
        Returns:
            List of OrchestrationResult for each ticker
        """
        if fundamentals is None:
            fundamentals = {}
        
        regime_str = regime_state.trend_regime.value
        active_models = regime_state.active_models
        model_weights = regime_state.model_weights
        
        # Collect results from each model
        all_results: Dict[str, Dict[str, ModelResult]] = {}  # ticker -> model -> result
        
        for model_name in active_models:
            if model_name not in self._models:
                continue
                
            model = self._models[model_name]
            
            try:
                # Get regime-specific parameters
                params = model.get_regime_params(regime_str)
                
                # Execute model
                results = model.calculate(prices, fundamentals, regime_str)
                
                # Organize by ticker
                for result in results:
                    if result.ticker not in all_results:
                        all_results[result.ticker] = {}
                    all_results[result.ticker][model_name] = result
                    
            except Exception as e:
                print(f"Error executing {model_name}: {e}")
                continue
        
        # Calculate composite scores
        orchestration_results = []
        
        for ticker, model_results in all_results.items():
            result = self._calculate_composite(
                ticker, model_results, model_weights, regime_str
            )
            orchestration_results.append(result)
        
        # Sort by composite score and assign ranks
        orchestration_results.sort(key=lambda x: x.composite_score, reverse=True)
        for i, result in enumerate(orchestration_results):
            result.rank = i + 1
        
        return orchestration_results
    
    def _calculate_composite(
        self,
        ticker: str,
        model_results: Dict[str, ModelResult],
        model_weights: Dict[str, float],
        regime: str,
    ) -> OrchestrationResult:
        """
        Calculate composite score for a ticker.
        
        Applies regime-based weights and calculates model agreement.
        """
        model_scores = {}
        model_signals = {}
        weighted_scores = {}
        
        total_weight = 0
        weighted_sum = 0
        
        # Buy signals count (for agreement)
        buy_count = 0
        avoid_count = 0
        total_models = len(model_results)
        
        for model_name, result in model_results.items():
            score = result.score
            signal = result.signal.name
            
            model_scores[model_name] = score
            model_signals[model_name] = signal
            
            # Get weight
            weight = model_weights.get(model_name, get_model_weight(model_name, regime))
            weighted_score = score * weight
            weighted_scores[model_name] = weighted_score
            
            total_weight += weight
            weighted_sum += weighted_score
            
            # Count signals
            if signal in ["STRONG_BUY", "BUY"]:
                buy_count += 1
            elif signal in ["STRONG_AVOID", "AVOID"]:
                avoid_count += 1
        
        # Composite score
        composite = weighted_sum / total_weight if total_weight > 0 else 50
        
        # Model agreement (% of models agreeing on direction)
        if total_models > 0:
            agreement = max(buy_count, avoid_count) / total_models
        else:
            agreement = 0
        
        # Agreement bonus/penalty
        if agreement > 0.75:
            composite = min(100, composite * 1.1)  # +10% bonus
        elif agreement < 0.4:
            composite = composite * 0.9  # -10% penalty
        
        return OrchestrationResult(
            ticker=ticker,
            model_scores=model_scores,
            model_signals=model_signals,
            weighted_scores=weighted_scores,
            composite_score=round(composite, 2),
            model_agreement=round(agreement, 2),
            rank=0,  # Will be set after sorting
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of loaded models."""
        return list(self._models.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get info about a specific model."""
        if model_name in self._models:
            model = self._models[model_name]
            return {
                "name": model.name,
                "category": model.category,
                "description": model.description,
            }
        return None

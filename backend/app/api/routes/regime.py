"""
Regime API Routes
Endpoints for market regime detection
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

from app.core.regime_engine import RegimeEngine
from app.models.base import Regime, VolatilityRegime

router = APIRouter()


class RegimeResponse(BaseModel):
    """Response model for regime detection."""
    trend_regime: str
    volatility_regime: str
    confidence: float
    active_models: List[str]
    model_weights: Dict[str, float]
    position_size_multiplier: float
    timestamp: str


class RegimeHistoryResponse(BaseModel):
    """Response model for regime history."""
    regimes: List[RegimeResponse]


@router.get("/current", response_model=RegimeResponse)
async def get_current_regime():
    """
    Get current market regime.
    
    Returns the detected trend and volatility regime along with
    which models are active and their weights.
    """
    # TODO: Fetch real market data
    # For now, return mock data
    return RegimeResponse(
        trend_regime="BULL",
        volatility_regime="NORMAL",
        confidence=0.75,
        active_models=[
            "hqm", "clenow", "dual_momentum", "roc_multi", "52w_high",
            "adx", "multi_ema", "supertrend", "ichimoku", "psar",
            "garp", "magic_formula"
        ],
        model_weights={
            "hqm": 1.0,
            "clenow": 1.0,
            "dual_momentum": 1.0,
            "roc_multi": 0.9,
            "52w_high": 1.0,
            "adx": 0.8,
            "multi_ema": 0.9,
            "supertrend": 0.9,
            "ichimoku": 0.8,
            "psar": 0.7,
            "garp": 0.8,
            "magic_formula": 0.6,
        },
        position_size_multiplier=1.0,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/weights", response_model=Dict[str, Dict[str, float]])
async def get_regime_weights():
    """
    Get weight matrix for all models across regimes.
    
    Returns the weight multiplier for each model in each regime.
    """
    from app.models.base import WEIGHT_MATRIX
    
    # Convert to regime-keyed format
    regimes = ["BULL", "BEAR", "SIDEWAYS"]
    result = {regime: {} for regime in regimes}
    
    for model, weights in WEIGHT_MATRIX.items():
        for i, regime in enumerate(regimes):
            result[regime][model] = weights[i]
    
    return result


@router.get("/activation")
async def get_model_activation():
    """
    Get which models activate in each regime.
    """
    engine = RegimeEngine()
    return {
        "BULL": engine.MODEL_ACTIVATION[Regime.BULL],
        "BEAR": engine.MODEL_ACTIVATION[Regime.BEAR],
        "SIDEWAYS": engine.MODEL_ACTIVATION[Regime.SIDEWAYS],
    }

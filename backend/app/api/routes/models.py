"""
Models API Routes
Endpoints for model information and status
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

from app.models.registry import (
    MODEL_REGISTRY,
    get_implemented_models,
    get_unimplemented_models,
    get_models_by_category,
    get_implementation_status,
    CATEGORIES,
)

router = APIRouter()


class ModelInfo(BaseModel):
    """Model information."""
    name: str
    class_name: str
    category: str
    description: str
    implemented: bool
    tested: bool


class ImplementationStatus(BaseModel):
    """Implementation status summary."""
    total: int
    implemented: int
    tested: int
    remaining: int


@router.get("/")
async def list_all_models() -> Dict[str, ModelInfo]:
    """
    List all 20 models with their status.
    """
    return {
        name: ModelInfo(
            name=info.name,
            class_name=info.class_name,
            category=info.category,
            description=info.description,
            implemented=info.implemented,
            tested=info.tested,
        )
        for name, info in MODEL_REGISTRY.items()
    }


@router.get("/status", response_model=ImplementationStatus)
async def get_status():
    """
    Get implementation status summary.
    """
    status = get_implementation_status()
    return ImplementationStatus(**status)


@router.get("/implemented", response_model=List[str])
async def list_implemented():
    """
    List implemented models.
    """
    return get_implemented_models()


@router.get("/unimplemented", response_model=List[str])
async def list_unimplemented():
    """
    List unimplemented models.
    """
    return get_unimplemented_models()


@router.get("/category/{category}", response_model=List[str])
async def list_by_category(category: str):
    """
    List models in a specific category.
    
    Categories: momentum, trend, fundamental, quant
    """
    if category not in CATEGORIES:
        return {"error": f"Invalid category. Valid: {CATEGORIES}"}
    return get_models_by_category(category)


@router.get("/categories", response_model=List[str])
async def list_categories():
    """
    List all model categories.
    """
    return CATEGORIES

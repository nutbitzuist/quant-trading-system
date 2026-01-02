"""
Diagnostics API - System Health and Pipeline Status
Provides visibility into what's working and what's failing
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import traceback

from app.config import settings
from app.db.base import get_db
from app.db.models import PipelineLog, ScreeningResult, StockScore

router = APIRouter()


class ModelStatus(BaseModel):
    name: str
    category: str
    status: str  # "active", "error", "not_implemented"
    last_run: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    error_message: Optional[str] = None


class DataSourceStatus(BaseModel):
    name: str
    status: str  # "connected", "fallback", "error"
    last_check: datetime
    error_message: Optional[str] = None
    using_mock_data: bool = False


class PipelineStatus(BaseModel):
    status: str  # "idle", "running", "completed", "failed"
    last_run: Optional[datetime] = None
    stocks_attempted: int = 0
    stocks_successful: int = 0
    stocks_failed: int = 0
    current_regime: Optional[str] = None
    errors: List[str] = []
    duration_seconds: Optional[float] = None


class SystemHealth(BaseModel):
    overall_status: str  # "healthy", "degraded", "error"
    timestamp: datetime
    data_source: DataSourceStatus
    pipeline: PipelineStatus
    models: Dict[str, ModelStatus]
    recommendations: List[str] = []


# Track runtime state (in production, use Redis)
_runtime_state = {
    "pipeline_logs": [],
    "model_errors": {},
    "data_source_status": "unknown",
    "last_api_check": None,
    "using_mock_data": True,
    "stocks_processed": {},
}


def log_event(event_type: str, message: str, details: Optional[Dict] = None):
    """Log diagnostic event"""
    _runtime_state["pipeline_logs"].append({
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "message": message,
        "details": details or {}
    })
    # Keep only last 100 logs
    if len(_runtime_state["pipeline_logs"]) > 100:
        _runtime_state["pipeline_logs"] = _runtime_state["pipeline_logs"][-100:]


def log_model_error(model_name: str, error: str):
    """Log model-specific error"""
    if model_name not in _runtime_state["model_errors"]:
        _runtime_state["model_errors"][model_name] = []
    _runtime_state["model_errors"][model_name].append({
        "timestamp": datetime.now().isoformat(),
        "error": error
    })


def log_stock_result(ticker: str, success: bool, error: Optional[str] = None):
    """Log per-stock processing result"""
    _runtime_state["stocks_processed"][ticker] = {
        "success": success,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }


def set_data_source_status(status: str, using_mock: bool = False):
    """Update data source status"""
    _runtime_state["data_source_status"] = status
    _runtime_state["using_mock_data"] = using_mock
    _runtime_state["last_api_check"] = datetime.now()


# All 20 models from architecture
ALL_MODELS = {
    # Momentum (5)
    "hqm": {"name": "High-Quality Momentum", "category": "momentum", "implemented": True},
    "clenow": {"name": "Clenow Momentum", "category": "momentum", "implemented": False},
    "dual_momentum": {"name": "Dual Momentum", "category": "momentum", "implemented": False},
    "roc_multi": {"name": "ROC Multi-Timeframe", "category": "momentum", "implemented": False},
    "52w_high": {"name": "52-Week High", "category": "momentum", "implemented": False},
    # Trend (5)
    "adx": {"name": "ADX Trend", "category": "trend", "implemented": True},
    "multi_ema": {"name": "Multi-EMA Matrix", "category": "trend", "implemented": False},
    "supertrend": {"name": "Supertrend", "category": "trend", "implemented": False},
    "ichimoku": {"name": "Ichimoku Cloud", "category": "trend", "implemented": False},
    "psar": {"name": "Parabolic SAR", "category": "trend", "implemented": False},
    # Fundamental (5)
    "magic_formula": {"name": "Magic Formula", "category": "fundamental", "implemented": False},
    "garp": {"name": "GARP", "category": "fundamental", "implemented": False},
    "quality": {"name": "Quality Factor", "category": "fundamental", "implemented": True},
    "altman_z": {"name": "Altman Z-Score", "category": "fundamental", "implemented": False},
    "dividend": {"name": "Dividend Quality", "category": "fundamental", "implemented": False},
    # Quant (5)
    "hmm_regime": {"name": "HMM Regime", "category": "quant", "implemented": False},
    "vol_regime": {"name": "Volatility Regime", "category": "quant", "implemented": False},
    "mean_reversion": {"name": "Mean Reversion", "category": "quant", "implemented": False},
    "correlation": {"name": "Correlation Regime", "category": "quant", "implemented": False},
    "rsi_divergence": {"name": "RSI Divergence", "category": "quant", "implemented": False},
}


@router.get("/status", response_model=SystemHealth)
async def get_system_health(db: Session = Depends(get_db)):
    """
    Get comprehensive system health status.
    Shows what's working, what's failing, and why.
    """
    # Get latest pipeline log
    latest_log = db.query(PipelineLog).order_by(PipelineLog.started_at.desc()).first()
    
    # Get latest screening result
    latest_screening = db.query(ScreeningResult).order_by(ScreeningResult.created_at.desc()).first()
    
    # Count stocks in latest screening
    stocks_count = 0
    if latest_screening:
        stocks_count = db.query(StockScore).filter(
            StockScore.screening_id == latest_screening.id
        ).count()
    
    # Build pipeline status
    pipeline_status = PipelineStatus(
        status=latest_log.status if latest_log else "never_run",
        last_run=latest_log.started_at if latest_log else None,
        stocks_attempted=100,  # SET100
        stocks_successful=stocks_count,
        stocks_failed=100 - stocks_count,
        current_regime=latest_screening.market_regime if latest_screening else None,
        errors=[latest_log.error_message] if latest_log and latest_log.error_message else [],
        duration_seconds=(latest_log.completed_at - latest_log.started_at).total_seconds() 
            if latest_log and latest_log.completed_at else None
    )
    
    # Build data source status
    data_source = DataSourceStatus(
        name="SET Smart API",
        status=_runtime_state.get("data_source_status", "unknown"),
        last_check=_runtime_state.get("last_api_check") or datetime.now(),
        using_mock_data=_runtime_state.get("using_mock_data", True),
        error_message="Using mock OHLCV data - SET Smart API not responding" 
            if _runtime_state.get("using_mock_data") else None
    )
    
    # Build models status
    models = {}
    for model_id, model_info in ALL_MODELS.items():
        errors = _runtime_state.get("model_errors", {}).get(model_id, [])
        models[model_id] = ModelStatus(
            name=model_info["name"],
            category=model_info["category"],
            status="active" if model_info["implemented"] else "not_implemented",
            error_count=len(errors),
            error_message=errors[-1]["error"] if errors else None
        )
    
    # Determine overall health
    implemented_count = sum(1 for m in ALL_MODELS.values() if m["implemented"])
    
    if pipeline_status.status == "FAILED" or data_source.status == "error":
        overall = "error"
    elif data_source.using_mock_data or implemented_count < 10:
        overall = "degraded"
    else:
        overall = "healthy"
    
    # Build recommendations
    recommendations = []
    if data_source.using_mock_data:
        recommendations.append("Configure SET Smart API key for real market data")
    if implemented_count < 20:
        recommendations.append(f"Only {implemented_count}/20 models implemented - {20-implemented_count} models pending")
    if pipeline_status.stocks_failed > 0:
        recommendations.append(f"{pipeline_status.stocks_failed} stocks failed to process - check logs")
    if pipeline_status.status == "never_run":
        recommendations.append("Run 'Global Screening' to generate stock rankings")
    
    return SystemHealth(
        overall_status=overall,
        timestamp=datetime.now(),
        data_source=data_source,
        pipeline=pipeline_status,
        models=models,
        recommendations=recommendations
    )


@router.get("/logs")
async def get_pipeline_logs(limit: int = 50):
    """
    Get recent pipeline execution logs.
    Shows errors, warnings, and processing details.
    """
    logs = _runtime_state.get("pipeline_logs", [])[-limit:]
    
    # Group by type
    errors = [l for l in logs if l["type"] == "error"]
    warnings = [l for l in logs if l["type"] == "warning"]
    info = [l for l in logs if l["type"] == "info"]
    
    return {
        "total_logs": len(logs),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "logs": logs[::-1],  # Most recent first
        "summary": {
            "errors": errors[-5:],
            "warnings": warnings[-5:]
        }
    }


@router.get("/models")
async def get_models_status():
    """
    Get detailed status of all 20 models.
    Shows which are implemented, active, or failing.
    """
    result = {
        "total_models": 20,
        "implemented": 0,
        "pending": 0,
        "by_category": {},
        "models": []
    }
    
    for model_id, model_info in ALL_MODELS.items():
        status = "implemented" if model_info["implemented"] else "pending"
        if status == "implemented":
            result["implemented"] += 1
        else:
            result["pending"] += 1
        
        category = model_info["category"]
        if category not in result["by_category"]:
            result["by_category"][category] = {"implemented": 0, "pending": 0}
        result["by_category"][category][status] += 1
        
        errors = _runtime_state.get("model_errors", {}).get(model_id, [])
        result["models"].append({
            "id": model_id,
            "name": model_info["name"],
            "category": category,
            "status": status,
            "error_count": len(errors),
            "last_error": errors[-1] if errors else None
        })
    
    return result


@router.get("/stocks")
async def get_stocks_processing_status():
    """
    Get per-stock processing status from last run.
    Shows which stocks succeeded, failed, and why.
    """
    stocks = _runtime_state.get("stocks_processed", {})
    
    successful = [t for t, s in stocks.items() if s.get("success")]
    failed = [t for t, s in stocks.items() if not s.get("success")]
    
    return {
        "total_attempted": len(stocks),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": f"{len(successful)/max(len(stocks),1)*100:.1f}%",
        "failed_stocks": [
            {"ticker": t, "error": stocks[t].get("error")} 
            for t in failed[:20]  # Limit to first 20
        ],
        "all_tickers": list(stocks.keys())
    }


@router.post("/test-connection")
async def test_data_source_connection():
    """Test connection to SET Smart API"""
    from app.data.setsmart_client import SetSmartClient
    
    try:
        client = SetSmartClient()
        # Try to get stock list
        stocks = await client.get_set100()
        await client.close()
        
        if stocks and len(stocks) > 0:
            set_data_source_status("connected", using_mock=False)
            return {
                "status": "connected",
                "stocks_found": len(stocks),
                "sample": stocks[:5]
            }
        else:
            set_data_source_status("fallback", using_mock=True)
            return {
                "status": "fallback",
                "message": "API returned empty, using hardcoded SET100 list",
                "stocks_found": 100
            }
    except Exception as e:
        set_data_source_status("error", using_mock=True)
        return {
            "status": "error",
            "error": str(e),
            "message": "Using mock data as fallback"
        }

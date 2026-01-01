"""
Screening API Routes
Endpoints for stock screening and rankings
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.base import get_db
from app.db.models import ScreeningResult, StockScore as DBStockScore, PipelineLog
from app.pipeline.engine import PipelineEngine

router = APIRouter()
pipeline_engine = PipelineEngine()


class StockScore(BaseModel):
    """Score for a single stock."""
    ticker: str
    composite_score: float
    signal: str
    confidence: float = 0.8
    model_agreement: float
    rank: int
    model_scores: Dict[str, Any] = {}


class ScreeningResponse(BaseModel):
    """Result from full screening."""
    id: int
    regime: str
    timestamp: datetime
    status: str
    stocks_count: int


class PipelineStatus(BaseModel):
    """Status of pipeline."""
    status: str
    stocks_processed: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@router.post("/run", response_model=PipelineStatus)
async def run_screening(
    background_tasks: BackgroundTasks, 
    user_id: Optional[int] = None
):
    """
    Trigger full stock screening pipeline in background.
    """
    # Check if already running
    # (Simple check, ideally check DB or Redis lock)
    
    # Add to background tasks
    background_tasks.add_task(pipeline_engine.run_pipeline, user_id)
    
    return PipelineStatus(
        status="STARTED",
        stocks_processed=0,
        started_at=datetime.now()
    )


@router.get("/status", response_model=PipelineStatus)
async def get_pipeline_status(db: Session = Depends(get_db)):
    """Get status of latest pipeline run."""
    log = db.query(PipelineLog).order_by(desc(PipelineLog.started_at)).first()
    
    if not log:
        return PipelineStatus(
            status="IDLE",
            stocks_processed=0,
            started_at=datetime.now()
        )
        
    return PipelineStatus(
        status=log.status,
        stocks_processed=log.stocks_processed,
        started_at=log.started_at,
        completed_at=log.completed_at,
        error=log.error_message
    )


@router.get("/rankings", response_model=List[StockScore])
async def get_rankings(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get current stock rankings from latest successful screening.
    """
    # Get latest screening
    latest_screening = db.query(ScreeningResult).order_by(desc(ScreeningResult.run_date)).first()
    
    if not latest_screening:
        # If no DB results, return empty (or demo data if preferred)
        return []
        
    # Get top stocks
    stocks = db.query(DBStockScore)\
        .filter(DBStockScore.screening_id == latest_screening.id)\
        .order_by(desc(DBStockScore.composite_score))\
        .limit(limit)\
        .all()
        
    results = []
    for i, stock in enumerate(stocks):
        results.append(StockScore(
            ticker=stock.ticker,
            composite_score=stock.composite_score,
            signal=stock.signal,
            confidence=0.8, # Placeholder
            model_agreement=stock.model_agreement,
            rank=i + 1,
            model_scores=stock.details or {}
        ))
        
    return results


@router.get("/stock/{ticker}", response_model=StockScore)
async def get_stock_analysis(ticker: str, db: Session = Depends(get_db)):
    """
    Get detailed analysis for a specific stock.
    """
    # Get latest score for this ticker
    latest_screening = db.query(ScreeningResult).order_by(desc(ScreeningResult.run_date)).first()
    
    if not latest_screening:
         raise HTTPException(status_code=404, detail="No screening data found")
         
    stock = db.query(DBStockScore)\
        .filter(
            DBStockScore.screening_id == latest_screening.id,
            DBStockScore.ticker == ticker
        ).first()
        
    if not stock:
         raise HTTPException(status_code=404, detail="Stock not found in latest screening")
         
    return StockScore(
        ticker=stock.ticker,
        composite_score=stock.composite_score,
        signal=stock.signal,
        confidence=0.8,
        model_agreement=stock.model_agreement,
        rank=0, # Not calculated here
        model_scores=stock.details or {}
    )

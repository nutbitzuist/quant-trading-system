"""
Backtest API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import BacktestResult as DBBacktestResult
from app.backtest.engine import BacktestEngine

router = APIRouter()
backtest_engine = BacktestEngine()


class BacktestRequest(BaseModel):
    ticker: str
    start_date: str # ISO format
    end_date: str # ISO format
    initial_capital: float = 100000.0
    strategy: str = "long_only"


class BacktestResponse(BaseModel):
    id: int
    ticker: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    trades_count: int
    equity_curve: List[Dict[str, Any]]


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run backtest execution.
    """
    try:
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        
        result_id = await backtest_engine.run_backtest(
            ticker=request.ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=request.initial_capital,
            strategy=request.strategy
        )
        
        # Fetch result
        # Note: Ideally we'd return from engine directly, but engine returns ID
        # Wait, I need a DB session here to fetch it back
        # For simplicity MVP, I should modify engine to return result object? 
        # Or just use ID to query here.
        
        # Re-open session to fetch
        from app.db.base import SessionLocal
        db = SessionLocal()
        result = db.query(DBBacktestResult).get(result_id)
        db.close()
        
        if not result:
             raise HTTPException(status_code=500, detail="Backtest failed to save")
             
        return BacktestResponse(
            id=result.id,
            ticker=result.ticker,
            total_return=result.total_return,
            sharpe_ratio=result.sharpe_ratio,
            max_drawdown=result.max_drawdown,
            trades_count=result.trades_count,
            equity_curve=result.equity_curve
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

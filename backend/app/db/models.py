"""
Database Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    """User for authentication and settings"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user")
    screenings = relationship("ScreeningResult", back_populates="user")


class APIKey(Base):
    """API Keys for external access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="api_keys")


class ScreeningResult(Base):
    """Top-level screening runs"""
    __tablename__ = "screening_results"
    
    id = Column(Integer, primary_key=True, index=True)
    run_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    market_regime = Column(String, nullable=True)  # BULL, BEAR, etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for system runs
    
    scores = relationship("StockScore", back_populates="screening")
    
    user = relationship("User", back_populates="screenings")


class StockScore(Base):
    """Individual stock results from a screening"""
    __tablename__ = "stock_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    screening_id = Column(Integer, ForeignKey("screening_results.id"))
    ticker = Column(String, index=True)
    composite_score = Column(Float)
    signal = Column(String) # BUY, SELL, HOLD
    model_agreement = Column(Float)
    
    # Store detailed model breakdown as JSON
    # e.g. {"hqm": 90, "adx": 80, ...}
    details = Column(JSON, nullable=True)
    
    screening = relationship("ScreeningResult", back_populates="scores")


class BacktestResult(Base):
    """Backtest execution results"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String)
    ticker = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_capital = Column(Float)
    final_capital = Column(Float)
    total_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    trades_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Store equity curve and trades as JSON
    equity_curve = Column(JSON)
    trades = Column(JSON)


class PipelineLog(Base):
    """Log of pipeline execution runs"""
    __tablename__ = "pipeline_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String) # RUNNING, COMPLETED, FAILED
    stocks_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

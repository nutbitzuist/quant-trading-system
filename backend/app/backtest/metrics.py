"""
Backtest Metrics Calculator
"""

import pandas as pd
import numpy as np
from typing import Dict

def calculate_metrics(equity_curve: pd.Series, risk_free_rate: float = 0.02) -> Dict[str, float]:
    """
    Calculate performance metrics from equity curve.
    
    Args:
        equity_curve: Series of portfolio value over time
        risk_free_rate: Annualized risk-free rate
        
    Returns:
        Dict with metrics
    """
    if equity_curve.empty:
        return {}
        
    start_value = equity_curve.iloc[0]
    end_value = equity_curve.iloc[-1]
    
    # Returns
    returns = equity_curve.pct_change().dropna()
    total_return = (end_value - start_value) / start_value
    
    # CAGR (assuming daily data)
    days = (equity_curve.index[-1] - equity_curve.index[0]).days
    if days > 0:
        cagr = (end_value / start_value) ** (365 / days) - 1
    else:
        cagr = 0
        
    # Volatility (Annualized)
    volatility = returns.std() * np.sqrt(252)
    
    # Sharpe Ratio
    if volatility > 0:
        sharpe = (cagr - risk_free_rate) / volatility
    else:
        sharpe = 0
        
    # Max Drawdown
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    return {
        "total_return": round(total_return, 4),
        "cagr": round(cagr, 4),
        "volatility": round(volatility, 4),
        "sharpe_ratio": round(sharpe, 4),
        "max_drawdown": round(max_drawdown, 4)
    }

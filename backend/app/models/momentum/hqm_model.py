"""
High-Quality Momentum (HQM) Model
Model M1 - Momentum Category

Multi-timeframe momentum ranking using percentile scores
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class HQMModel(BaseModel):
    """
    High-Quality Momentum Score
    
    Combines multiple momentum timeframes with quality adjustment.
    
    Formula:
        HQM_Score = weighted_avg(
            percentile_rank(return_1m),
            percentile_rank(return_3m),
            percentile_rank(return_6m),
            percentile_rank(return_12m)
        )
    
    Regime Adjustments:
        BULL: [0.20, 0.25, 0.30, 0.25] - Favor recent momentum
        BEAR: [0.10, 0.20, 0.30, 0.40] - Favor sustained momentum
        SIDEWAYS: [0.25, 0.25, 0.25, 0.25] - Equal weight
    """
    
    name = "hqm"
    category = "momentum"
    description = "High-Quality Momentum: Multi-timeframe momentum percentile"
    
    # Regime-specific weights for [1m, 3m, 6m, 12m]
    REGIME_WEIGHTS = {
        "BULL": [0.20, 0.25, 0.30, 0.25],
        "BEAR": [0.10, 0.20, 0.30, 0.40],
        "SIDEWAYS": [0.25, 0.25, 0.25, 0.25],
        "NEUTRAL": [0.25, 0.25, 0.25, 0.25],
    }
    
    # Periods in trading days
    PERIODS = {
        "1m": 21,
        "3m": 63,
        "6m": 126,
        "12m": 252,
    }
    
    def __init__(self):
        """Initialize HQM model."""
        super().__init__()
    
    def get_regime_params(self, regime: str) -> Dict[str, Any]:
        """Get regime-specific parameters."""
        weights = self.REGIME_WEIGHTS.get(regime, self.REGIME_WEIGHTS["NEUTRAL"])
        return {
            "weights": weights,
            "periods": self.PERIODS,
        }
    
    def calculate(
        self,
        prices: pd.DataFrame,
        fundamentals: Optional[Dict[str, Any]] = None,
        regime: str = "NEUTRAL"
    ) -> List[ModelResult]:
        """
        Calculate HQM score for all stocks.
        
        Args:
            prices: DataFrame with MultiIndex (ticker, date) or 
                   columns as tickers, rows as dates
            fundamentals: Not used for HQM
            regime: Current market regime
            
        Returns:
            List of ModelResult for each ticker
        """
        params = self.get_regime_params(regime)
        weights = params["weights"]
        periods = params["periods"]
        
        results = []
        
        # Handle different DataFrame formats
        if isinstance(prices.index, pd.MultiIndex):
            # MultiIndex format (ticker, date)
            tickers = prices.index.get_level_values(0).unique()
            returns_by_period = self._calculate_returns_multiindex(prices, periods)
        else:
            # Columns as tickers format
            tickers = prices.columns if 'close' not in prices.columns else self._get_tickers(prices)
            returns_by_period = self._calculate_returns_columns(prices, periods)
        
        # Calculate percentile ranks for each period
        percentiles = {}
        for period_name, returns in returns_by_period.items():
            percentiles[period_name] = returns.rank(pct=True) * 100
        
        # Calculate HQM score for each ticker
        for ticker in tickers:
            try:
                # Get percentile for each timeframe
                pct_1m = percentiles["1m"].get(ticker, 50)
                pct_3m = percentiles["3m"].get(ticker, 50)
                pct_6m = percentiles["6m"].get(ticker, 50)
                pct_12m = percentiles["12m"].get(ticker, 50)
                
                # Weighted average
                hqm_score = (
                    weights[0] * pct_1m +
                    weights[1] * pct_3m +
                    weights[2] * pct_6m +
                    weights[3] * pct_12m
                )
                
                # Handle NaN
                if pd.isna(hqm_score):
                    hqm_score = 50
                
                # Generate signal and confidence
                signal = self.score_to_signal(hqm_score)
                confidence = self.calculate_confidence(hqm_score)
                
                results.append(ModelResult(
                    ticker=ticker,
                    score=round(hqm_score, 2),
                    signal=signal,
                    confidence=round(confidence, 2),
                    metadata={
                        "pct_1m": round(pct_1m, 1) if not pd.isna(pct_1m) else None,
                        "pct_3m": round(pct_3m, 1) if not pd.isna(pct_3m) else None,
                        "pct_6m": round(pct_6m, 1) if not pd.isna(pct_6m) else None,
                        "pct_12m": round(pct_12m, 1) if not pd.isna(pct_12m) else None,
                        "regime": regime,
                    }
                ))
            except Exception as e:
                # Handle errors gracefully
                results.append(ModelResult(
                    ticker=ticker,
                    score=50,
                    signal=Signal.HOLD,
                    confidence=0.0,
                    metadata={"error": str(e)}
                ))
        
        return results
    
    def _calculate_returns_multiindex(
        self, 
        prices: pd.DataFrame, 
        periods: Dict[str, int]
    ) -> Dict[str, pd.Series]:
        """Calculate returns for MultiIndex DataFrame."""
        returns = {}
        
        # Pivot to have tickers as columns
        close = prices['close'].unstack(level=0)
        
        for period_name, days in periods.items():
            if len(close) >= days:
                period_return = close.iloc[-1] / close.iloc[-days] - 1
                returns[period_name] = period_return * 100  # As percentage
            else:
                returns[period_name] = pd.Series(dtype=float)
        
        return returns
    
    def _calculate_returns_columns(
        self, 
        prices: pd.DataFrame, 
        periods: Dict[str, int]
    ) -> Dict[str, pd.Series]:
        """Calculate returns for columns-as-tickers DataFrame."""
        returns = {}
        
        # Assume 'close' column or direct price columns
        if 'close' in prices.columns:
            close = prices['close']
        else:
            close = prices
        
        for period_name, days in periods.items():
            if len(close) >= days:
                if isinstance(close, pd.Series):
                    # Single stock
                    period_return = (close.iloc[-1] / close.iloc[-days] - 1) * 100
                    returns[period_name] = pd.Series({close.name: period_return})
                else:
                    # Multiple stocks as columns
                    period_return = (close.iloc[-1] / close.iloc[-days] - 1) * 100
                    returns[period_name] = period_return
            else:
                returns[period_name] = pd.Series(dtype=float)
        
        return returns
    
    def _get_tickers(self, prices: pd.DataFrame) -> List[str]:
        """Extract ticker list from DataFrame."""
        if 'ticker' in prices.columns:
            return prices['ticker'].unique().tolist()
        elif isinstance(prices.index, pd.MultiIndex):
            return prices.index.get_level_values(0).unique().tolist()
        elif hasattr(prices, 'name') and prices.name:
            # Single-stock OHLCV DataFrame with name attribute set
            return [prices.name]
        elif 'close' in prices.columns:
            # Single-stock OHLCV format - use 'close' column name property
            close_series = prices['close']
            if hasattr(close_series, 'name') and close_series.name and close_series.name != 'close':
                return [close_series.name]
            # Fallback: This is a single unnamed stock
            return ['UNKNOWN']
        else:
            return list(prices.columns)

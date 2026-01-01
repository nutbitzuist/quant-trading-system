"""
Correlation Regime Model
Model M19 - Quantitative Category

Beta and correlation-based classification
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class CorrelationRegimeModel(BaseModel):
    """
    Correlation Regime Model
    
    Analyzes beta and correlation vs market index.
    
    Metrics:
        - Beta: Systematic risk relative to market
        - Correlation: How closely stock moves with market
        - Decoupling: When correlation drops (regime change signal)
    
    Regime Applications:
        BULL: Prefer high-beta for leverage
        BEAR: Prefer low-beta for defense
        SIDEWAYS: Prefer low-correlation for diversification
    """
    
    name = "correlation"
    category = "quant"
    description = "Correlation Regime: Beta and correlation analysis"
    
    REGIME_PARAMS = {
        "BULL": {"preferred_beta": "HIGH", "lookback": 60},
        "BEAR": {"preferred_beta": "LOW", "lookback": 60},
        "SIDEWAYS": {"preferred_beta": "LOW_CORR", "lookback": 60},
        "NEUTRAL": {"preferred_beta": "NEUTRAL", "lookback": 60},
    }
    
    def __init__(self):
        super().__init__()
        self._market_returns = None
    
    def set_market_data(self, market_close: pd.Series):
        """Set market index data for beta calculation."""
        self._market_returns = market_close.pct_change()
    
    def get_regime_params(self, regime: str) -> Dict[str, Any]:
        return self.REGIME_PARAMS.get(regime, self.REGIME_PARAMS["NEUTRAL"])
    
    def calculate(
        self,
        prices: pd.DataFrame,
        fundamentals: Optional[Dict[str, Any]] = None,
        regime: str = "NEUTRAL"
    ) -> List[ModelResult]:
        params = self.get_regime_params(regime)
        lookback = params["lookback"]
        preferred_beta = params["preferred_beta"]
        results = []
        
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(
                    ticker, ticker_data['close'], lookback, preferred_beta, regime
                )
                results.append(result)
        else:
            if 'close' in prices.columns:
                result = self._calculate_single(
                    "STOCK", prices['close'], lookback, preferred_beta, regime
                )
                results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        close: pd.Series,
        lookback: int,
        preferred_beta: str,
        regime: str
    ) -> ModelResult:
        try:
            if len(close) < lookback:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            stock_returns = close.pct_change().iloc[-lookback:]
            
            # If market data available, calculate beta
            if self._market_returns is not None and len(self._market_returns) >= lookback:
                market_returns = self._market_returns.iloc[-lookback:]
                
                # Align indices
                aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
                if len(aligned) > 10:
                    stock_ret = aligned.iloc[:, 0]
                    market_ret = aligned.iloc[:, 1]
                    
                    covariance = np.cov(stock_ret, market_ret)[0, 1]
                    variance = np.var(market_ret)
                    
                    beta = covariance / variance if variance > 0 else 1.0
                    correlation = np.corrcoef(stock_ret, market_ret)[0, 1]
                else:
                    beta = 1.0
                    correlation = 0.5
            else:
                # Estimate beta from volatility proxy
                stock_vol = stock_returns.std() * np.sqrt(252)
                beta = stock_vol / 0.20  # Assume market vol ~20%
                correlation = 0.6  # Assume moderate correlation
            
            # Beta classification
            if beta > 1.3:
                beta_class = "HIGH"
            elif beta > 0.7:
                beta_class = "NEUTRAL"
            else:
                beta_class = "LOW"
            
            # Calculate score based on preference
            if preferred_beta == "HIGH":
                if beta > 1.3:
                    score = 80 + min(20, (beta - 1.3) * 20)
                elif beta > 1.0:
                    score = 60 + (beta - 1.0) * 60
                else:
                    score = 30 + beta * 30
                    
            elif preferred_beta == "LOW":
                if beta < 0.7:
                    score = 80 + min(20, (0.7 - beta) * 40)
                elif beta < 1.0:
                    score = 60 + (1.0 - beta) * 60
                else:
                    score = 60 - (beta - 1.0) * 30
                    
            elif preferred_beta == "LOW_CORR":
                # Prefer low correlation for diversification
                if correlation < 0.3:
                    score = 90
                elif correlation < 0.5:
                    score = 70
                elif correlation < 0.7:
                    score = 50
                else:
                    score = 30
            else:
                # Neutral: prefer beta around 1
                score = 100 - abs(beta - 1.0) * 40
            
            score = max(0, min(100, score))
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "beta": round(beta, 2),
                    "correlation": round(correlation, 2),
                    "beta_class": beta_class,
                    "preferred_beta": preferred_beta,
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

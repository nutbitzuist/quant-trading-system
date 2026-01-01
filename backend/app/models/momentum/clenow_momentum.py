"""
Clenow Momentum Model
Model M2 - Momentum Category

Andreas Clenow's Exponential Regression Momentum
Quality-adjusted momentum using regression slope and R²
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from scipy import stats

from app.models.base import BaseModel, ModelResult, Signal


class ClenowMomentumModel(BaseModel):
    """
    Clenow Momentum Model
    
    Based on Andreas Clenow's methodology from "Stocks on the Move".
    Uses exponential regression to find stocks with smooth, quality momentum.
    
    Formula:
        1. Fit exponential regression to last N days: ln(price) = a + b*t
        2. annualized_slope = (1 + daily_slope)^252 - 1
        3. momentum_score = annualized_slope × R²
    
    The R² adjustment penalizes "noisy" momentum.
    High R² = smooth trend, Low R² = choppy movement.
    
    Regime Adjustments:
        BULL: lookback = 60 days, min_r² = 0.6 (catch faster trends)
        BEAR: lookback = 120 days, min_r² = 0.8 (require strong conviction)
        SIDEWAYS: lookback = 90 days, min_r² = 0.7
    """
    
    name = "clenow"
    category = "momentum"
    description = "Clenow Momentum: Regression slope × R² for quality momentum"
    
    REGIME_PARAMS = {
        "BULL": {"lookback": 60, "min_r_squared": 0.6},
        "BEAR": {"lookback": 120, "min_r_squared": 0.8},
        "SIDEWAYS": {"lookback": 90, "min_r_squared": 0.7},
        "NEUTRAL": {"lookback": 90, "min_r_squared": 0.7},
    }
    
    def __init__(self):
        super().__init__()
    
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
        min_r_squared = params["min_r_squared"]
        
        results = []
        
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(
                    ticker, ticker_data['close'], lookback, min_r_squared, regime
                )
                results.append(result)
        else:
            if 'close' in prices.columns:
                result = self._calculate_single(
                    "STOCK", prices['close'], lookback, min_r_squared, regime
                )
                results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        close: pd.Series,
        lookback: int,
        min_r_squared: float,
        regime: str
    ) -> ModelResult:
        try:
            if len(close) < lookback:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            # Get last N days
            prices = close.iloc[-lookback:].dropna()
            if len(prices) < lookback * 0.8:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Too many missing values"}
                )
            
            # Log prices for exponential regression
            log_prices = np.log(prices.values)
            x = np.arange(len(log_prices))
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_prices)
            r_squared = r_value ** 2
            
            # Annualize slope
            annualized_return = (np.exp(slope) ** 252 - 1) * 100  # As percentage
            
            # Quality-adjusted momentum
            momentum_score = annualized_return * r_squared
            
            # Normalize to 0-100
            # Typical range: -50% to +100% annualized
            score = self.normalize_score(momentum_score, -50, 100)
            
            # Penalize low R²
            if r_squared < min_r_squared:
                score = score * (r_squared / min_r_squared)
            
            signal = self.score_to_signal(score)
            
            # Confidence based on R² and momentum magnitude
            confidence = min(1.0, r_squared * (abs(annualized_return) / 50))
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "annualized_return": round(annualized_return, 2),
                    "r_squared": round(r_squared, 3),
                    "daily_slope": round(slope, 6),
                    "quality_adjusted_score": round(momentum_score, 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

"""
Ensemble Engine (Layer 4)
Combines all model outputs into unified stock rankings
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

from app.models.base import (
    ModelResult,
    Signal,
    RegimeState,
    WEIGHT_MATRIX,
    get_model_weight,
)


@dataclass
class StockRanking:
    """Final ranking for a single stock."""
    ticker: str
    composite_score: float
    signal: Signal
    confidence: float
    model_agreement: float
    rank: int
    model_scores: Dict[str, float] = field(default_factory=dict)
    model_signals: Dict[str, str] = field(default_factory=dict)
    position_size_pct: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnsembleResult:
    """Result from full ensemble calculation."""
    regime: str
    volatility_regime: str
    timestamp: str
    top_buy: List[StockRanking]
    top_avoid: List[StockRanking]
    all_rankings: List[StockRanking]
    total_screened: int
    active_models: List[str]
    model_weights: Dict[str, float]


class EnsembleEngine:
    """
    Ensemble Engine (Layer 4)
    
    Combines outputs from all active models into unified stock rankings.
    
    Process:
    1. Collect scores from all models
    2. Normalize scores to common scale
    3. Apply regime-based weights
    4. Calculate model agreement
    5. Apply agreement bonus/penalty
    6. Generate final composite scores
    7. Rank and output Top N Buy / Top N Avoid
    """
    
    def __init__(
        self,
        top_n: int = 20,
        agreement_bonus: float = 0.10,
        agreement_penalty: float = 0.10,
        min_models_for_ranking: int = 3,
    ):
        """
        Initialize ensemble engine.
        
        Args:
            top_n: Number of stocks for top buy/avoid lists
            agreement_bonus: Score boost when models agree (e.g., 0.10 = +10%)
            agreement_penalty: Score reduction when models disagree
            min_models_for_ranking: Minimum models required to rank a stock
        """
        self.top_n = top_n
        self.agreement_bonus = agreement_bonus
        self.agreement_penalty = agreement_penalty
        self.min_models_for_ranking = min_models_for_ranking
    
    def calculate_rankings(
        self,
        model_results: Dict[str, List[ModelResult]],
        regime_state: RegimeState,
        fundamentals: Optional[Dict[str, Dict]] = None,
    ) -> EnsembleResult:
        """
        Calculate unified stock rankings from all model outputs.
        
        Args:
            model_results: Dict of model_name -> List[ModelResult]
            regime_state: Current market regime
            fundamentals: Optional fundamental data for position sizing
            
        Returns:
            EnsembleResult with top buy/avoid lists and all rankings
        """
        from datetime import datetime
        
        # Organize results by ticker
        ticker_scores: Dict[str, Dict[str, ModelResult]] = {}
        
        for model_name, results in model_results.items():
            for result in results:
                if result.ticker not in ticker_scores:
                    ticker_scores[result.ticker] = {}
                ticker_scores[result.ticker][model_name] = result
        
        # Calculate composite score for each ticker
        rankings = []
        
        for ticker, scores in ticker_scores.items():
            if len(scores) < self.min_models_for_ranking:
                continue
            
            ranking = self._calculate_composite(
                ticker, scores, regime_state
            )
            rankings.append(ranking)
        
        # Sort by composite score
        rankings.sort(key=lambda x: x.composite_score, reverse=True)
        
        # Assign ranks
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1
        
        # Calculate position sizes
        self._calculate_position_sizes(rankings, regime_state)
        
        # Split into buy/avoid
        top_buy = [r for r in rankings[:self.top_n] if r.signal in [Signal.STRONG_BUY, Signal.BUY]]
        
        # Avoid list: lowest scores
        avoid_candidates = sorted(rankings, key=lambda x: x.composite_score)
        top_avoid = [r for r in avoid_candidates[:self.top_n] if r.signal in [Signal.STRONG_AVOID, Signal.AVOID]]
        
        return EnsembleResult(
            regime=regime_state.trend_regime.value,
            volatility_regime=regime_state.volatility_regime.value,
            timestamp=datetime.now().isoformat(),
            top_buy=top_buy,
            top_avoid=top_avoid,
            all_rankings=rankings,
            total_screened=len(rankings),
            active_models=regime_state.active_models,
            model_weights=regime_state.model_weights,
        )
    
    def _calculate_composite(
        self,
        ticker: str,
        model_scores: Dict[str, ModelResult],
        regime_state: RegimeState,
    ) -> StockRanking:
        """Calculate composite score for a single ticker."""
        
        scores = {}
        signals = {}
        weighted_scores = {}
        confidences = []
        
        total_weight = 0
        weighted_sum = 0
        
        buy_count = 0
        avoid_count = 0
        
        for model_name, result in model_scores.items():
            score = result.score
            signal = result.signal
            confidence = result.confidence
            
            scores[model_name] = score
            signals[model_name] = signal.name
            confidences.append(confidence)
            
            # Get weight from regime state or default
            weight = regime_state.model_weights.get(
                model_name, 
                get_model_weight(model_name, regime_state.trend_regime.value)
            )
            
            weighted_score = score * weight
            weighted_scores[model_name] = weighted_score
            
            total_weight += weight
            weighted_sum += weighted_score
            
            # Count signal direction
            if signal in [Signal.STRONG_BUY, Signal.BUY]:
                buy_count += 1
            elif signal in [Signal.STRONG_AVOID, Signal.AVOID]:
                avoid_count += 1
        
        # Base composite score
        composite = weighted_sum / total_weight if total_weight > 0 else 50
        
        # Calculate agreement
        total_models = len(model_scores)
        if total_models > 0:
            agreement = max(buy_count, avoid_count) / total_models
        else:
            agreement = 0
        
        # Apply agreement bonus/penalty
        if agreement >= 0.75:
            composite = min(100, composite * (1 + self.agreement_bonus))
        elif agreement < 0.4:
            # Low agreement: reduce confidence in the score
            if composite > 50:
                composite = composite * (1 - self.agreement_penalty)
            else:
                composite = composite * (1 + self.agreement_penalty)
        
        # Clamp to 0-100
        composite = max(0, min(100, composite))
        
        # Determine final signal
        if composite >= 80:
            final_signal = Signal.STRONG_BUY
        elif composite >= 60:
            final_signal = Signal.BUY
        elif composite <= 20:
            final_signal = Signal.STRONG_AVOID
        elif composite <= 40:
            final_signal = Signal.AVOID
        else:
            final_signal = Signal.HOLD
        
        # Average confidence
        avg_confidence = np.mean(confidences) if confidences else 0.5
        
        # Boost confidence with agreement
        final_confidence = min(1.0, avg_confidence * (0.8 + agreement * 0.4))
        
        return StockRanking(
            ticker=ticker,
            composite_score=round(composite, 2),
            signal=final_signal,
            confidence=round(final_confidence, 2),
            model_agreement=round(agreement, 2),
            rank=0,  # Will be set after sorting
            model_scores=scores,
            model_signals=signals,
            metadata={
                "weighted_scores": weighted_scores,
                "buy_count": buy_count,
                "avoid_count": avoid_count,
                "total_models": total_models,
            }
        )
    
    def _calculate_position_sizes(
        self,
        rankings: List[StockRanking],
        regime_state: RegimeState,
        max_position_pct: float = 10.0,
        min_position_pct: float = 1.0,
    ):
        """
        Calculate position sizes based on:
        1. Composite score
        2. Confidence
        3. Model agreement
        4. Regime volatility multiplier
        """
        vol_multiplier = regime_state.position_size_multiplier
        
        for ranking in rankings:
            if ranking.signal not in [Signal.STRONG_BUY, Signal.BUY]:
                ranking.position_size_pct = 0.0
                continue
            
            # Base position on score (scaled 0-max)
            score_factor = ranking.composite_score / 100
            
            # Confidence adjustment
            confidence_factor = ranking.confidence
            
            # Agreement adjustment
            agreement_factor = 0.5 + ranking.model_agreement * 0.5
            
            # Calculate position
            raw_position = (
                max_position_pct *
                score_factor *
                confidence_factor *
                agreement_factor *
                vol_multiplier
            )
            
            # Clamp
            position = max(min_position_pct, min(max_position_pct, raw_position))
            
            ranking.position_size_pct = round(position, 2)
    
    def get_summary(self, result: EnsembleResult) -> Dict[str, Any]:
        """Get a summary of ensemble results."""
        return {
            "regime": result.regime,
            "volatility": result.volatility_regime,
            "total_screened": result.total_screened,
            "active_models": len(result.active_models),
            "top_buy_count": len(result.top_buy),
            "top_avoid_count": len(result.top_avoid),
            "top_buy_tickers": [r.ticker for r in result.top_buy[:5]],
            "top_avoid_tickers": [r.ticker for r in result.top_avoid[:5]],
        }

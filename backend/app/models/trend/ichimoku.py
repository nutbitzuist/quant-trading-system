"""
Ichimoku Cloud Model
Model M9 - Trend Category

Complete Ichimoku Kinko Hyo system
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from app.models.base import BaseModel, ModelResult, Signal


class IchimokuModel(BaseModel):
    """
    Ichimoku Cloud Model
    
    Complete trend following system with multiple components.
    
    Components:
        tenkan_sen = (highest_9 + lowest_9) / 2 (Conversion Line)
        kijun_sen = (highest_26 + lowest_26) / 2 (Base Line)
        senkou_span_a = (tenkan + kijun) / 2, shifted 26 forward
        senkou_span_b = (highest_52 + lowest_52) / 2, shifted 26 forward
        chikou_span = close, shifted 26 backward
    
    Signals:
        STRONG_BUY: Price above cloud, tenkan > kijun, chikou > price_26_ago
        BUY: Price above cloud
        NEUTRAL: Price in cloud
        AVOID: Price below cloud
    """
    
    name = "ichimoku"
    category = "trend"
    description = "Ichimoku Cloud: Complete trend system with cloud analysis"
    
    REGIME_PARAMS = {
        "BULL": {"tenkan": 9, "kijun": 26, "senkou_b": 52},
        "BEAR": {"tenkan": 9, "kijun": 26, "senkou_b": 52},
        "SIDEWAYS": {"tenkan": 9, "kijun": 26, "senkou_b": 52},
        "NEUTRAL": {"tenkan": 9, "kijun": 26, "senkou_b": 52},
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
        results = []
        
        if isinstance(prices.index, pd.MultiIndex):
            tickers = prices.index.get_level_values(0).unique()
            for ticker in tickers:
                ticker_data = prices.loc[ticker]
                result = self._calculate_single(ticker, ticker_data, params, regime)
                results.append(result)
        else:
            result = self._calculate_single("STOCK", prices, params, regime)
            results.append(result)
        
        return results
    
    def _calculate_single(
        self,
        ticker: str,
        data: pd.DataFrame,
        params: Dict[str, Any],
        regime: str
    ) -> ModelResult:
        try:
            tenkan_period = params["tenkan"]
            kijun_period = params["kijun"]
            senkou_b_period = params["senkou_b"]
            
            if len(data) < senkou_b_period + 26:
                return ModelResult(
                    ticker=ticker, score=50, signal=Signal.HOLD,
                    confidence=0.0, metadata={"error": "Insufficient data"}
                )
            
            high = data['high']
            low = data['low']
            close = data['close']
            
            # Tenkan-sen (Conversion Line)
            tenkan = (high.rolling(tenkan_period).max() + low.rolling(tenkan_period).min()) / 2
            
            # Kijun-sen (Base Line)
            kijun = (high.rolling(kijun_period).max() + low.rolling(kijun_period).min()) / 2
            
            # Senkou Span A (Leading Span A)
            senkou_a = ((tenkan + kijun) / 2).shift(26)
            
            # Senkou Span B (Leading Span B)
            senkou_b = ((high.rolling(senkou_b_period).max() + 
                        low.rolling(senkou_b_period).min()) / 2).shift(26)
            
            # Chikou Span (Lagging Span)
            chikou = close.shift(-26)
            
            # Current values
            current_price = close.iloc[-1]
            current_tenkan = tenkan.iloc[-1]
            current_kijun = kijun.iloc[-1]
            current_senkou_a = senkou_a.iloc[-1]
            current_senkou_b = senkou_b.iloc[-1]
            
            # Cloud boundaries
            cloud_top = max(current_senkou_a, current_senkou_b)
            cloud_bottom = min(current_senkou_a, current_senkou_b)
            
            # Position relative to cloud
            if current_price > cloud_top:
                cloud_position = "ABOVE"
                position_score = 70
            elif current_price < cloud_bottom:
                cloud_position = "BELOW"
                position_score = 30
            else:
                cloud_position = "INSIDE"
                position_score = 50
            
            # TK Cross
            tk_bullish = current_tenkan > current_kijun
            
            # Chikou vs price 26 days ago
            price_26_ago = close.iloc[-26] if len(close) >= 26 else current_price
            chikou_bullish = close.iloc[-1] > price_26_ago
            
            # Cloud color (future)
            future_senkou_a = (tenkan.iloc[-1] + kijun.iloc[-1]) / 2
            future_senkou_b = (high.iloc[-senkou_b_period:].max() + 
                              low.iloc[-senkou_b_period:].min()) / 2
            cloud_bullish = future_senkou_a > future_senkou_b
            
            # Calculate score
            score = position_score
            
            if tk_bullish:
                score += 10
            else:
                score -= 10
            
            if chikou_bullish:
                score += 10
            else:
                score -= 10
            
            if cloud_bullish:
                score += 5
            else:
                score -= 5
            
            score = max(0, min(100, score))
            
            # Determine signal strength
            bullish_signals = sum([
                cloud_position == "ABOVE",
                tk_bullish,
                chikou_bullish,
                cloud_bullish
            ])
            
            if bullish_signals >= 4:
                signal_strength = "STRONG_BULLISH"
            elif bullish_signals >= 3:
                signal_strength = "BULLISH"
            elif bullish_signals <= 1:
                signal_strength = "BEARISH"
            else:
                signal_strength = "NEUTRAL"
            
            signal = self.score_to_signal(score)
            confidence = self.calculate_confidence(score)
            
            return ModelResult(
                ticker=ticker,
                score=round(score, 2),
                signal=signal,
                confidence=round(confidence, 2),
                metadata={
                    "cloud_position": cloud_position,
                    "tk_bullish": tk_bullish,
                    "chikou_bullish": chikou_bullish,
                    "cloud_bullish": cloud_bullish,
                    "signal_strength": signal_strength,
                    "tenkan": round(current_tenkan, 2),
                    "kijun": round(current_kijun, 2),
                    "regime": regime,
                }
            )
            
        except Exception as e:
            return ModelResult(
                ticker=ticker, score=50, signal=Signal.HOLD,
                confidence=0.0, metadata={"error": str(e)}
            )

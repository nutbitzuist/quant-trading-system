"""
Pipeline Engine
Orchestrates the full data->model->db pipeline
"""

import asyncio
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db.models import ScreeningResult, StockScore, PipelineLog, User
from app.data.setsmart_client import SetSmartClient
from app.core.regime_engine import RegimeEngine
from app.core.orchestrator import ModelOrchestrator
from app.config import settings

class PipelineEngine:
    """
    Core engine for the screening pipeline.
    """
    
    def __init__(self):
        self.data_client = SetSmartClient()
        self.regime_engine = RegimeEngine()
        self.orchestrator = ModelOrchestrator()
    
    async def run_pipeline(self, user_id: Optional[int] = None) -> int:
        """
        Run the full screening pipeline.
        
        Args:
            user_id: ID of user triggering the run (None for system)
            
        Returns:
            ID of the created ScreeningResult
        """
        # Create DB session
        db = SessionLocal()
        
        # Log start
        log = PipelineLog(status="RUNNING", stocks_processed=0)
        db.add(log)
        db.commit()
        db.refresh(log)
        
        try:
            # Import diagnostic logging
            from app.api.routes.diagnostics import log_event, log_stock_result, set_data_source_status
            
            log_event("info", "Pipeline started", {"user_id": user_id})
            
            # 1. Fetch Universe (SET100)
            tickers = await self.data_client.get_set100()
            if not tickers:
                # Fallback to hardcoded list if API fails
                log_event("warning", "SET100 API failed, using hardcoded list")
                set_data_source_status("fallback", using_mock=True)
                tickers = [
                    "ADVANC", "AOT", "AWC", "BANPU", "BBL", "BDMS", "BEM", "BGRIM", "BH", "BTS",
                    "CBG", "CENTEL", "CHG", "CK", "CKP", "COM7", "CPALL", "CPF", "CPN", "CRC",
                    "DELTA", "DOHOME", "EA", "EGCO", "EPG", "GLOBAL", "GPSC", "GULF", "HMPRO", "INTUCH",
                    "IVL", "JMT", "JMART", "KBANK", "KCE", "KKP", "KTB", "KTC", "LH", "MAJOR",
                    "MEGA", "MINT", "MTC", "NRF", "OR", "ORI", "OSP", "PLANB", "PRM", "PTG",
                    "PTT", "PTTEP", "PTTGC", "QH", "RATCH", "RS", "SAWAD", "SCB", "SCC", "SCGP",
                    "SINGER", "SPALI", "SPRC", "STA", "STEC", "SUPER", "TASCO", "TCAP", "THAI", "THANI",
                    "TISCO", "TKN", "TMB", "TOP", "TRUE", "TTB", "TTW", "TU", "TVO", "VGI",
                    "WHA", "WHAUP", "AAV", "AIMIRT", "BCH", "BCPG", "BLA", "BROOK", "BTG", "HUMAN",
                    "IRPC", "JAS", "MC", "MFEC", "MK", "NER", "NEUTRAL", "PR9", "PSL", "PJW"
                ]
            else:
                log_event("info", f"Fetched {len(tickers)} tickers from API")
                set_data_source_status("connected", using_mock=False)
            
            # 2. Determine Regime
            # Fetch SET Index history - client now has Yahoo fallback
            set_history = await self.data_client.get_index_history("SET", days=365)
            if set_history.empty or 'close' not in set_history.columns:
                # Client couldn't get data from ANY source (SET Smart + Yahoo)
                log_event("error", "Could not fetch SET Index from any source")
                set_data_source_status("error", using_mock=True)
                # Use a default regime since we can't detect
                from app.models.base import Regime, VolatilityRegime, RegimeState
                regime_state = RegimeState(
                    trend_regime=Regime.SIDEWAYS,
                    volatility_regime=VolatilityRegime.NORMAL,
                    confidence=0.0,
                    active_models=[],
                    model_weights={},
                    position_size_multiplier=0.5
                )
            else:
                set_data_source_status("connected", using_mock=False)
                regime_state = self.regime_engine.detect_regime(set_history)
            
            log_event("info", f"Regime detected: {regime_state.trend_regime.value}", {
                "confidence": regime_state.confidence,
                "volatility": regime_state.volatility_regime.value
            })
            
            # 3. Create Screening Result entry
            screening = ScreeningResult(
                market_regime=regime_state.trend_regime.value,
                user_id=user_id
            )
            db.add(screening)
            db.commit()
            db.refresh(screening)
            
            # 4. Loop stocks and run models
            processed_count = 0
            failed_count = 0
            
            # Use chunks to avoid hitting API limits too hard
            chunk_size = 10  # Increased for faster processing
            for i in range(0, len(tickers), chunk_size):
                chunk = tickers[i:i+chunk_size]
                
                tasks = []
                for ticker in chunk:
                    tasks.append(self._process_stock(ticker, regime_state))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Save results
                for idx, res in enumerate(results):
                    ticker = chunk[idx]
                    if isinstance(res, Exception):
                        log_stock_result(ticker, success=False, error=str(res))
                        log_event("error", f"Failed to process {ticker}", {"error": str(res)})
                        failed_count += 1
                    elif res:
                        score_entry = StockScore(
                            screening_id=screening.id,
                            ticker=res.ticker,
                            composite_score=res.composite_score,
                            signal=res.model_signals.get("composite", "HOLD"),
                            model_agreement=res.model_agreement,
                            details=res.model_scores
                        )
                        db.add(score_entry)
                        processed_count += 1
                        log_stock_result(ticker, success=True)
                    else:
                        log_stock_result(ticker, success=False, error="No result returned")
                        failed_count += 1
                
                db.commit()
                
                # Update log
                log.stocks_processed = processed_count
                db.commit()
                
                # Progress log
                log_event("info", f"Progress: {processed_count}/{len(tickers)} processed, {failed_count} failed")
                
                # Tiny sleep to be nice to API
                await asyncio.sleep(0.2)
            
            # Complete log
            log.status = "COMPLETED"
            log.completed_at = datetime.utcnow()
            db.commit()
            
            log_event("info", f"Pipeline completed: {processed_count} stocks processed, {failed_count} failed")
            
            return screening.id
            
        except Exception as e:
            # Log error
            log.status = "FAILED"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            db.commit()
            print(f"Pipeline failed: {e}")
            try:
                from app.api.routes.diagnostics import log_event
                log_event("error", f"Pipeline failed: {str(e)}")
            except:
                pass
            raise e
        finally:
            db.close()
    
    def _generate_mock_ohlcv(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """Generate realistic mock OHLCV data for a stock."""
        import numpy as np
        
        # Seed based on ticker for consistent results
        np.random.seed(hash(ticker) % 2**32)
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate realistic price series with trend and volatility
        base_price = 50 + np.random.uniform(0, 150)  # Random starting price
        returns = np.random.normal(0.0005, 0.02, days)  # Daily returns
        
        prices = [base_price]
        for r in returns[1:]:
            prices.append(prices[-1] * (1 + r))
        prices = np.array(prices)
        
        # Generate OHLCV
        high = prices * (1 + np.abs(np.random.normal(0, 0.01, days)))
        low = prices * (1 - np.abs(np.random.normal(0, 0.01, days)))
        open_prices = low + (high - low) * np.random.uniform(0.2, 0.8, days)
        
        volume = np.random.uniform(100000, 10000000, days).astype(int)
        
        df = pd.DataFrame({
            'open': open_prices,
            'high': high,
            'low': low,
            'close': prices,
            'volume': volume
        }, index=dates)
        
        # Set the name for model identification
        df.name = ticker
        
        return df
            
    async def _process_stock(self, ticker: str, regime_state):
        """Process a single stock: fetch data -> run orchestrator."""
        try:
            # Fetch history from API (client has Yahoo fallback built-in)
            history = await self.data_client.get_stock_history(ticker, days=365)
            
            # If ALL sources failed (SET Smart + Yahoo), skip this stock
            if history.empty or 'close' not in history.columns:
                print(f"Skipping {ticker}: No data from any source")
                return None
                
            # Run Orchestrator
            results = self.orchestrator.execute_models(
                prices=history,
                regime_state=regime_state
            )
            
            if results:
                result = results[0]
                result.ticker = ticker
                return result
            return None
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            return None


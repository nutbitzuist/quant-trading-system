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
            # 1. Fetch Universe (SET100)
            tickers = await self.data_client.get_set100()
            if not tickers:
                # Fallback to hardcoded list if API fails
                tickers = ["DELTA", "PTT", "AOT", "KBANK", "SCB", "ADVANC", "GULF", "CPALL", "BDMS", "SCC"]
            
            # 2. Determine Regime (using dummy index data for now or fetch real)
            # Fetch SET Index history
            set_history = await self.data_client.get_index_history("SET", days=365)
            if set_history.empty:
                 # Fallback mock history if API fails
                 regime_state = self.regime_engine.detect_regime(pd.DataFrame()) 
            else:
                 regime_state = self.regime_engine.detect_regime(set_history)
            
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
            
            # Use chunks to avoid hitting API limits too hard
            chunk_size = 5
            for i in range(0, len(tickers), chunk_size):
                chunk = tickers[i:i+chunk_size]
                
                tasks = []
                for ticker in chunk:
                    tasks.append(self._process_stock(ticker, regime_state))
                
                results = await asyncio.gather(*tasks)
                
                # Save results
                for res in results:
                    if res:
                        score_entry = StockScore(
                            screening_id=screening.id,
                            ticker=res.ticker,
                            composite_score=res.composite_score,
                            signal=res.model_signals.get("composite", "HOLD"), # Use composite signal logic
                            model_agreement=res.model_agreement,
                            details=res.model_scores # Store raw scores as JSON
                        )
                        db.add(score_entry)
                        processed_count += 1
                
                db.commit()
                
                # Update log
                log.stocks_processed = processed_count
                db.commit()
                
                # Tiny sleep to be nice to API
                await asyncio.sleep(0.5)
            
            # Complete log
            log.status = "COMPLETED"
            log.completed_at = datetime.utcnow()
            db.commit()
            
            return screening.id
            
        except Exception as e:
            # Log error
            log.status = "FAILED"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            db.commit()
            print(f"Pipeline failed: {e}")
            raise e
        finally:
            db.close()
            
    async def _process_stock(self, ticker: str, regime_state):
        """Process a single stock: fetch data -> run orchestrator."""
        try:
            # Fetch history
            history = await self.data_client.get_stock_history(ticker, days=365)
            if history.empty:
                return None
                
            # Run Orchestrator
            results = self.orchestrator.execute_models(
                prices=history,
                regime_state=regime_state
            )
            
            if results:
                return results[0] # Should be only one result for one ticker
            return None
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            return None

"""
Sector Rotation API Routes
Endpoints for sector analysis and rotation signals
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.data.setsmart_client import get_setsmart_client

router = APIRouter()

# Sector Mappings (SET Code -> Yahoo Ticker)
SECTOR_MAP = {
    "FINCIAL": "^SETFIN.BK",
    "TECH": "^SETTECH.BK",
    "RESOURC": "^SETRES.BK",
    "PROPCON": "^SETPROP.BK",
    "INDUS": "^SETINDUS.BK",
    "SERVICE": "^SETSERV.BK",
    "CONSUMP": "^SETCONS.BK",
    "AGRO": "^SETAGRI.BK",
}

class RRGPointResponse(BaseModel):
    """RRG point data."""
    sector: str
    rs_ratio: float
    rs_momentum: float
    quadrant: str
    rotation_direction: str


class SectorRotationResponse(BaseModel):
    """Sector rotation analysis."""
    timestamp: str
    rrg_data: List[RRGPointResponse]
    sector_recommendations: Dict[str, str]
    top_sectors: List[str]
    bottom_sectors: List[str]
    cycle_phase: Optional[str] = None


class SectorMomentumResponse(BaseModel):
    """Sector momentum data."""
    sector: str
    momentum_1w: float
    momentum_1m: float
    momentum_3m: float
    momentum_6m: float
    composite_score: float
    trend: str
    rank: int


async def _get_rrg_metrics(sector_df: pd.DataFrame, benchmark_df: pd.DataFrame):
    """Calculate simplified RRG metrics."""
    # Align dates
    common_idx = sector_df.index.intersection(benchmark_df.index)
    if len(common_idx) < 20:
        return 100.0, 100.0
        
    s_close = sector_df.loc[common_idx]['close']
    b_close = benchmark_df.loc[common_idx]['close']
    
    # Relative Strength
    rs = (s_close / b_close) * 100
    
    # RS-Ratio (Trend of RS) - approximated by current vs MA
    rs_ma = rs.rolling(10).mean()
    rs_ratio = (rs.iloc[-1] / rs_ma.iloc[-1]) * 100
    
    # RS-Momentum (Rate of change of RS-Ratio)
    rs_ratio_series = rs / rs.rolling(10).mean() * 100
    rs_mom_ma = rs_ratio_series.rolling(10).mean()
    rs_momentum = (rs_ratio_series.iloc[-1] / rs_mom_ma.iloc[-1]) * 100
    
    return round(rs_ratio, 2), round(rs_momentum, 2)


def _get_quadrant(ratio: float, mom: float) -> str:
    if ratio > 100 and mom > 100: return "LEADING"
    if ratio < 100 and mom > 100: return "IMPROVING"
    if ratio < 100 and mom < 100: return "LAGGING"
    return "WEAKENING"


@router.get("/rrg", response_model=SectorRotationResponse)
async def get_sector_rrg():
    """Get Relative Rotation Graph data using real market data."""
    client = get_setsmart_client()
    
    # Fetch Benchmark (SET Index)
    benchmark = await client.get_index_history("SET", days=365)
    if benchmark.empty:
        # Fallback if totally failed
        return SectorRotationResponse(
            timestamp=datetime.now().isoformat(),
            rrg_data=[],
            sector_recommendations={},
            top_sectors=[],
            bottom_sectors=[],
            cycle_phase="UNKNOWN"
        )

    rrg_data = []
    
    for sector_code, ticker in SECTOR_MAP.items():
        # Yahoo Ticker is mapped, get_index_history will use it via fallback
        # Passing ticker as "index" name is a bit hacky for client, but works with my updated client
        # Wait, client.get_index_history prepends '^' if not using fallback.
        # My updated get_index_history calls get_price_history(index) WITHOUT prepending caret
        # Wait, I changed line 249 to `return await self.get_price_history(index, period=period)` 
        # So I should pass the exact ticker I want.
        
        # But get_price_history uses the logic: if ticker="SET" -> ^SET.BK.
        # So I can pass raw ticker here.
        
        # Actually my client fallback logic handles raw tickers ending in .BK
        
        sector_df = await client.get_price_history(ticker, days=365)
        
        if sector_df.empty:
            continue
            
        rs_ratio, rs_mom = await _get_rrg_metrics(sector_df, benchmark)
        quadrant = _get_quadrant(rs_ratio, rs_mom)
        
        rrg_data.append(RRGPointResponse(
            sector=sector_code,
            rs_ratio=rs_ratio,
            rs_momentum=rs_mom,
            quadrant=quadrant,
            rotation_direction="CLOCKWISE" # Simplified assumption
        ))
    
    # Sort for recommendations
    rrg_data.sort(key=lambda x: x.rs_ratio, reverse=True)
    
    recs = {}
    for item in rrg_data:
        if item.quadrant == "LEADING": recs[item.sector] = "OVERWEIGHT"
        elif item.quadrant == "WEAKENING": recs[item.sector] = "NEUTRAL"
        elif item.quadrant == "IMPROVING": recs[item.sector] = "NEUTRAL"
        else: recs[item.sector] = "UNDERWEIGHT"
        
    top = [x.sector for x in rrg_data[:2]]
    bottom = [x.sector for x in rrg_data[-2:]]
    
    return SectorRotationResponse(
        timestamp=datetime.now().isoformat(),
        rrg_data=rrg_data,
        sector_recommendations=recs,
        top_sectors=top,
        bottom_sectors=bottom,
        cycle_phase="DATA_DRIVEN"
    )

@router.get("/momentum", response_model=List[SectorMomentumResponse])
async def get_sector_momentum():
    """Get sector momentum rankings using real data."""
    client = get_setsmart_client()
    results = []
    
    for sector_code, ticker in SECTOR_MAP.items():
        df = await client.get_price_history(ticker, days=200)
        if df.empty or len(df) < 130:
            continue
            
        current = df['close'].iloc[-1]
        
        def get_ret(days):
            if len(df) > days:
                return ((current / df['close'].iloc[-days]) - 1) * 100
            return 0.0
            
        m1w = get_ret(5)
        m1m = get_ret(20)
        m3m = get_ret(60)
        m6m = get_ret(120)
        
        score = (m1w * 0.1) + (m1m * 0.2) + (m3m * 0.3) + (m6m * 0.4)
        
        results.append(SectorMomentumResponse(
            sector=sector_code,
            momentum_1w=round(m1w, 2),
            momentum_1m=round(m1m, 2),
            momentum_3m=round(m3m, 2),
            momentum_6m=round(m6m, 2),
            composite_score=round(score, 2),
            trend="UP" if score > 0 else "DOWN",
            rank=0
        ))
        
    results.sort(key=lambda x: x.composite_score, reverse=True)
    for i, res in enumerate(results):
        res.rank = i + 1
        
    return results


@router.get("/cycle")
async def get_business_cycle():
    """Get current business cycle (Placeholder for Macro Data)."""
    # Macro data is harder to get from basic stock APIs. 
    # Keeping simplistic logic for now.
    return {
        "phase": "MID_EXPANSION",
        "confidence": 0.5,
        "indicators": {
            "gdp_growth": 3.0, # Placeholder
            "inflation": 2.0,
        },
        "sector_recommendations": {},
        "next_phase_probability": {"stay": 0.8}
    }


@router.get("/recommendations")
async def get_sector_recommendations():
    """Get consolidated sector recommendations."""
    # Reuse computations
    rrg = await get_sector_rrg()
    mom = await get_sector_momentum()
    
    mom_map = {m.sector: m for m in mom}
    
    recs = []
    for r in rrg.rrg_data:
        m = mom_map.get(r.sector)
        rank = m.rank if m else 99
        
        recs.append({
            "sector": r.sector,
            "overall": rrg.sector_recommendations.get(r.sector, "NEUTRAL"),
            "rrg_signal": r.quadrant,
            "cycle_signal": "NEUTRAL",
            "momentum_rank": rank,
            "confidence": 0.8 if r.quadrant == "LEADING" else 0.5
        })
        
    return {
        "timestamp": datetime.now().isoformat(),
        "recommendations": recs,
        "rotation_alert": None
    }

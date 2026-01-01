"""
Data API Routes
Endpoints for fetching real market data from SET Smart
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import os

router = APIRouter()

# SET Smart API Key (from environment or hardcoded for now)
SETSMART_API_KEY = os.getenv("SETSMART_API_KEY", "93001366-5f83-4b52-b96b-3550980d1b38")


@router.get("/stocks")
async def get_stock_list(market: str = Query("SET100", description="Market index")):
    """
    Get list of stocks in a market index.
    """
    from app.data.setsmart_client import get_setsmart_client
    
    try:
        client = get_setsmart_client(SETSMART_API_KEY)
        stocks = await client.get_stock_list(market)
        return {"market": market, "count": len(stocks), "symbols": stocks}
    except Exception as e:
        # Return mock data if API fails
        return {
            "market": market,
            "count": 100,
            "symbols": [
                "ADVANC", "AOT", "AWC", "BANPU", "BBL", "BDMS", "BEM", "BGRIM",
                "BH", "BJC", "BTS", "CBG", "CENTEL", "CHG", "CK", "CPALL", "CPF",
                "CPN", "CRC", "DELTA", "DOHOME", "EA", "EGCO", "GLOBAL", "GPSC",
                "GULF", "HMPRO", "INTUCH", "IRPC", "IVL", "JAS", "KBANK", "KCE",
                "KKP", "KTB", "KTC", "LH", "MAJOR", "MBK", "MEGA", "MINT", "MTC",
                "OR", "ORI", "OSP", "PLANB", "PRM", "PSL", "PTG", "PTT", "PTTEP",
                "PTTGC", "QH", "RATCH", "RBF", "RS", "SAWAD", "SCB", "SCC", "SCGP",
                "SINGER", "SPALI", "SPRC", "STA", "STEC", "SUPER", "TASCO", "TCAP",
                "THAI", "THANI", "TISCO", "TKN", "TOA", "TOP", "TPIPP", "TRUE",
                "TTA", "TTB", "TU", "UV", "VGI", "WHA", "WHAUP",
            ],
            "source": "mock"
        }


@router.get("/prices/{ticker}")
async def get_stock_prices(
    ticker: str,
    period: str = Query("1y", description="Time period: 1m, 3m, 6m, 1y, 2y"),
):
    """
    Get historical price data for a stock.
    """
    from app.data.setsmart_client import get_setsmart_client
    
    try:
        client = get_setsmart_client(SETSMART_API_KEY)
        df = await client.get_price_history(ticker, period=period)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")
        
        # Convert to list of dicts
        df_reset = df.reset_index()
        df_reset["date"] = df_reset["date"].dt.strftime("%Y-%m-%d")
        
        return {
            "ticker": ticker,
            "period": period,
            "count": len(df),
            "data": df_reset.to_dict(orient="records"),
        }
    except HTTPException:
        raise
    except Exception as e:
        # Return mock data
        import random
        base = 100
        data = []
        for i in range(252):  # 1 year of trading days
            date = datetime(2025, 1, 1) + timedelta(days=i)
            if date.weekday() < 5:  # Weekdays only
                change = random.uniform(-0.03, 0.03)
                base *= (1 + change)
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(base * 0.99, 2),
                    "high": round(base * 1.02, 2),
                    "low": round(base * 0.98, 2),
                    "close": round(base, 2),
                    "volume": random.randint(1000000, 10000000),
                })
        
        return {
            "ticker": ticker,
            "period": period,
            "count": len(data),
            "data": data,
            "source": "mock"
        }


from datetime import timedelta

@router.get("/fundamentals/{ticker}")
async def get_stock_fundamentals(ticker: str):
    """
    Get fundamental data for a stock.
    """
    from app.data.setsmart_client import get_setsmart_client
    
    try:
        client = get_setsmart_client(SETSMART_API_KEY)
        data = await client.get_fundamentals(ticker)
        
        return {
            "ticker": ticker,
            "pe_ratio": data.pe_ratio,
            "pb_ratio": data.pb_ratio,
            "dividend_yield": data.dividend_yield,
            "roe": data.roe,
            "roa": data.roa,
            "market_cap": data.market_cap,
            "eps": data.eps,
            "debt_to_equity": data.debt_to_equity,
            "profit_margin": data.profit_margin,
            "revenue_growth": data.revenue_growth,
            "earnings_growth": data.earnings_growth,
        }
    except Exception as e:
        # Return mock data
        import random
        return {
            "ticker": ticker,
            "pe_ratio": round(random.uniform(8, 25), 2),
            "pb_ratio": round(random.uniform(0.8, 3.5), 2),
            "dividend_yield": round(random.uniform(1, 6), 2),
            "roe": round(random.uniform(5, 25), 2),
            "roa": round(random.uniform(2, 15), 2),
            "market_cap": round(random.uniform(10, 500) * 1e9, 0),
            "eps": round(random.uniform(1, 20), 2),
            "debt_to_equity": round(random.uniform(0.1, 2.5), 2),
            "profit_margin": round(random.uniform(5, 25), 2),
            "revenue_growth": round(random.uniform(-10, 30), 2),
            "earnings_growth": round(random.uniform(-15, 40), 2),
            "source": "mock"
        }


@router.get("/index/{index_name}")
async def get_index_data(
    index_name: str = "SET",
    period: str = Query("1y", description="Time period"),
):
    """
    Get index historical data.
    """
    from app.data.setsmart_client import get_setsmart_client
    
    try:
        client = get_setsmart_client(SETSMART_API_KEY)
        df = await client.get_index_data(index_name, period)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data for {index_name}")
        
        df_reset = df.reset_index()
        df_reset["date"] = df_reset["date"].dt.strftime("%Y-%m-%d")
        
        return {
            "index": index_name,
            "period": period,
            "data": df_reset.to_dict(orient="records"),
        }
    except HTTPException:
        raise
    except Exception as e:
        # Mock SET index data
        import random
        base = 1400
        data = []
        for i in range(252):
            date = datetime(2025, 1, 1) + timedelta(days=i)
            if date.weekday() < 5:
                change = random.uniform(-0.015, 0.015)
                base *= (1 + change)
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "close": round(base, 2),
                })
        
        return {
            "index": index_name,
            "period": period,
            "data": data,
            "source": "mock"
        }


@router.get("/status")
async def get_data_status():
    """
    Check SET Smart API connection status.
    """
    api_key = SETSMART_API_KEY
    has_key = bool(api_key and len(api_key) > 10)
    
    return {
        "api_configured": has_key,
        "api_key_preview": f"{api_key[:8]}..." if has_key else "Not configured",
        "status": "ready" if has_key else "mock_mode",
        "message": "SET Smart API configured" if has_key else "Using mock data",
    }

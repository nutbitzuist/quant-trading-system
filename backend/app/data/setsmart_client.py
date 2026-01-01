"""
SET Smart API Client
Integration with SET Smart for Thai market data
"""

import os
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd


@dataclass
class SetSmartConfig:
    """Configuration for SET Smart API."""
    api_key: str = ""
    base_url: str = "https://api.setsmart.com"
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> "SetSmartConfig":
        """Load config from environment."""
        return cls(
            api_key=os.getenv("SETSMART_API_KEY", ""),
            base_url=os.getenv("SETSMART_BASE_URL", "https://api.setsmart.com"),
        )


@dataclass
class StockData:
    """Stock price and volume data."""
    ticker: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    value: float = 0.0


@dataclass
class FundamentalData:
    """Fundamental data for a stock."""
    ticker: str
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    dividend_yield: float = 0.0
    roe: float = 0.0
    roa: float = 0.0
    market_cap: float = 0.0
    eps: float = 0.0
    book_value: float = 0.0
    debt_to_equity: float = 0.0
    current_ratio: float = 0.0
    profit_margin: float = 0.0
    revenue_growth: float = 0.0
    earnings_growth: float = 0.0


class SetSmartClient:
    """
    Client for SET Smart API.
    
    API Documentation: https://www.setsmart.com/api
    
    Endpoints used:
    - /stock/price - Historical price data
    - /stock/info - Stock information
    - /stock/financial - Financial ratios
    - /market/index - Index data (SET, SET50, SET100)
    """
    
    def __init__(self, config: Optional[SetSmartConfig] = None):
        """
        Initialize client.
        
        Args:
            config: API configuration. If None, loads from environment.
        """
        self.config = config or SetSmartConfig.from_env()
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
        )
        
        # Cache for reducing API calls
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._cache_timestamps: Dict[str, datetime] = {}
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        use_cache: bool = True,
    ) -> Dict:
        """Make API request with caching."""
        cache_key = f"{method}:{endpoint}:{str(params)}"
        
        # Check cache
        if use_cache and cache_key in self._cache:
            cached_at = self._cache_timestamps.get(cache_key, datetime.min)
            if datetime.now() - cached_at < self._cache_ttl:
                return self._cache[cache_key]
        
        # Make request
        try:
            if method == "GET":
                response = await self._client.get(endpoint, params=params)
            else:
                response = await self._client.post(endpoint, json=params)
            
            response.raise_for_status()
            data = response.json()
            
            # Cache response
            self._cache[cache_key] = data
            self._cache_timestamps[cache_key] = datetime.now()
            
            return data
            
        except httpx.HTTPError as e:
            print(f"SET Smart API error: {e}")
            return {}
    
    async def get_stock_list(self, market: str = "SET100") -> List[str]:
        """
        Get list of stocks in a market index.
        
        Args:
            market: Index name (SET, SET50, SET100)
            
        Returns:
            List of ticker symbols
        """
        data = await self._request("GET", f"/market/{market}/stocks")
        return data.get("symbols", [])
    
    async def get_price_history(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1y",
    ) -> pd.DataFrame:
        """
        Get historical price data.
        
        Args:
            ticker: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Alternative to dates (1m, 3m, 6m, 1y, 2y, 5y)
            
        Returns:
            DataFrame with OHLCV data
        """
        params = {"symbol": ticker}
        
        if start_date and end_date:
            params["startDate"] = start_date
            params["endDate"] = end_date
        else:
            params["period"] = period
        
        data = await self._request("GET", "/stock/price/history", params)
        
        if not data.get("data"):
            return pd.DataFrame()
        
        df = pd.DataFrame(data["data"])
        
        # Standardize column names
        column_mapping = {
            "date": "date",
            "open": "open",
            "high": "high", 
            "low": "low",
            "close": "close",
            "volume": "volume",
            "value": "value",
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            df = df.set_index("date")
        
        return df
    
    async def get_fundamentals(self, ticker: str) -> FundamentalData:
        """
        Get fundamental data for a stock.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            FundamentalData object
        """
        data = await self._request("GET", "/stock/financial", {"symbol": ticker})
        
        if not data.get("data"):
            return FundamentalData(ticker=ticker)
        
        d = data["data"]
        
        return FundamentalData(
            ticker=ticker,
            pe_ratio=d.get("peRatio", 0),
            pb_ratio=d.get("pbRatio", 0),
            dividend_yield=d.get("dividendYield", 0),
            roe=d.get("roe", 0),
            roa=d.get("roa", 0),
            market_cap=d.get("marketCap", 0),
            eps=d.get("eps", 0),
            book_value=d.get("bookValue", 0),
            debt_to_equity=d.get("debtToEquity", 0),
            current_ratio=d.get("currentRatio", 0),
            profit_margin=d.get("profitMargin", 0),
            revenue_growth=d.get("revenueGrowth", 0),
            earnings_growth=d.get("earningsGrowth", 0),
        )
    
    async def get_index_data(
        self, 
        index: str = "SET",
        period: str = "1y",
    ) -> pd.DataFrame:
        """
        Get index price history.
        
        Args:
            index: Index name (SET, SET50, SET100)
            period: Time period
            
        Returns:
            DataFrame with index OHLCV
        """
        return await self.get_price_history(f"^{index}", period=period)
    
    async def get_sector_data(self, sector: str) -> Dict:
        """
        Get sector index data.
        
        Args:
            sector: Sector code (FINCIAL, TECH, etc.)
            
        Returns:
            Sector data including performance
        """
        data = await self._request("GET", "/sector/info", {"sector": sector})
        return data.get("data", {})
    
    async def get_realtime_quote(self, ticker: str) -> Dict:
        """
        Get real-time quote for a stock.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Real-time quote data
        """
        data = await self._request("GET", "/stock/quote", {"symbol": ticker}, use_cache=False)
        return data.get("data", {})
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()


# Singleton instance with configured API key
_client: Optional[SetSmartClient] = None


def get_setsmart_client(api_key: Optional[str] = None) -> SetSmartClient:
    """
    Get or create SET Smart client instance.
    
    Args:
        api_key: Optional API key override
        
    Returns:
        SetSmartClient instance
    """
    global _client
    
    if _client is None or api_key:
        config = SetSmartConfig(
            api_key=api_key or os.getenv("SETSMART_API_KEY", "")
        )
        _client = SetSmartClient(config)
    
    return _client

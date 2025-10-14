# backend/fetcher.py
import yfinance as yf
import pandas as pd
from pathlib import Path
from typing import List, Dict

CACHE_DIR = Path(__file__).resolve().parents[1] / "data"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_stock_history(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical data for a single ticker.
    Returns pandas DataFrame (empty if not found).
    """
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
    except Exception:
        df = pd.DataFrame()
    if df is None:
        df = pd.DataFrame()
    if not df.empty:
        # ensure consistent column names and index
        df = df.reset_index()
        df.rename(columns={"Date": "Datetime"}, inplace=True)
        # save a cache copy
        df.to_csv(CACHE_DIR / f"{symbol}_{period}_{interval}.csv", index=False)
    return df

def fetch_stock_data(symbols: List[str], period: str = "1mo", interval: str = "1d") -> Dict[str, pd.DataFrame]:
    out = {}
    for s in symbols:
        s = str(s).strip()
        if s == "":
            continue
        df = fetch_stock_history(s, period=period, interval=interval)
        out[s] = df
    return out

def get_latest_close(symbol: str) -> float:
    df = fetch_stock_history(symbol, period="5d", interval="1m")
    if df.empty or 'Close' not in df.columns:
        return None
    # last non-null close
    vals = df['Close'].dropna()
    return float(vals.iloc[-1]) if not vals.empty else None


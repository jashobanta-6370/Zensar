# backend/summarizer.py
import pandas as pd
from statistics import mean

def simple_moving_avg_prediction(df: pd.DataFrame, window_short: int = 3, window_long: int = 7) -> dict:
    """
    Very simple rule-based 'prediction' using moving averages:
    - Use 'Close' column. Returns direction, short_ma, long_ma
    """
    result = {"direction": "unknown", "short_ma": None, "long_ma": None}
    if df.empty or 'Close' not in df.columns:
        return result
    close = df['Close'].dropna().astype(float)
    if len(close) < 2:
        return result
    short_ma = float(close.tail(window_short).mean()) if len(close) >= window_short else float(close.mean())
    long_ma = float(close.tail(window_long).mean()) if len(close) >= window_long else float(close.mean())
    direction = "bullish" if short_ma > long_ma else "bearish" if short_ma < long_ma else "neutral"
    result.update({"direction": direction, "short_ma": round(short_ma, 4), "long_ma": round(long_ma, 4)})
    # simple expected pct change (very naive)
    last = float(close.iloc[-1])
    expected = (short_ma - last) / last * 100
    result["expected_pct_change"] = round(expected, 3)
    return result

def make_text_summary(ticker: str, hist_df: pd.DataFrame, rule_result: dict) -> str:
    if hist_df.empty:
        return f"No historical data available for {ticker}."
    last_close = hist_df['Close'].dropna().astype(float).iloc[-1]
    s = f"{ticker}: Last close {last_close:.2f}. Short MA={rule_result.get('short_ma')}, Long MA={rule_result.get('long_ma')}."
    s += f" Direction: {rule_result.get('direction')}. Expected (naive) change: {rule_result.get('expected_pct_change')}%."
    return s

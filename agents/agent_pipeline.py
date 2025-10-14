# agents/agent_pipeline.py
from backend.fetcher import fetch_stock_data
from backend.summarizer import simple_moving_avg_prediction, make_text_summary
from agents.llm_client import query_llm
from agents.vision_agent import analyze_image_for_report
from typing import List, Dict

def analyze_ticker_pipeline(ticker: str) -> Dict:
    """
    Full pipeline for a single ticker:
    - fetch data
    - compute simple rule prediction
    - prepare prompt and call LLM for a human-readable insight
    """
    out = {"ticker": ticker, "history": None, "rule": None, "llm": None}
    data = fetch_stock_data([ticker], period="1mo", interval="1d").get(ticker)
    if data is None or data.empty:
        out["llm"] = f"No data available for {ticker}."
        return out
    out["history"] = data
    rule = simple_moving_avg_prediction(data)
    out["rule"] = rule

    # Create a compact prompt for LLM
    recent = list(data['Close'].dropna().astype(float).tail(7))
    prompt = (
        f"You are a concise market analyst.\n"
        f"Ticker: {ticker}\n"
        f"Recent closes (last {len(recent)}): {recent}\n"
        f"Short MA: {rule.get('short_ma')}, Long MA: {rule.get('long_ma')}\n"
        f"Naive expected pct change: {rule.get('expected_pct_change')}%\n"
        f"Produce a 2-3 sentence insight (no legal/advice language) and a one-line recommendation: Buy/Hold/Sell with confidence score 0-100.\n"
    )
    llm_resp = query_llm(prompt)
    out["llm"] = llm_resp
    return out

def analyze_portfolio(tickers: List[str]):
    results = []
    for t in tickers:
        results.append(analyze_ticker_pipeline(t))
    return results

def analyze_image_and_data(image_bytes: bytes, ticker: str = None) -> str:
    text_from_image = analyze_image_for_report(image_bytes)
    if ticker:
        # Combine with ticker quick fetch
        pipeline = analyze_ticker_pipeline(ticker)
        combined_prompt = (
            f"Image summary: {text_from_image}\n\n"
            f"Ticker analysis (short): {pipeline['llm']}\n\n"
            "Provide a short combined insight."
        )
        return query_llm(combined_prompt)
    else:
        return query_llm(f"Image summary: {text_from_image}\nProvide a short insight.")

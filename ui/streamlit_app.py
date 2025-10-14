import sys, os
# make project root importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from io import BytesIO
from agents.agent_pipeline import analyze_ticker_pipeline, analyze_portfolio, analyze_image_and_data
import requests

# -------------------------------
# Ollama server check
# -------------------------------
def ollama_running():
    try:
        r = requests.get("http://127.0.0.1:11434/v1/models", timeout=5)
        return r.status_code == 200
    except Exception as e:
        st.warning(f"Ollama check error: {e}")
        return False

# Try a few times in case server is slow
LLM_ENABLED = False
for _ in range(5):
    if ollama_running():
        LLM_ENABLED = True
        break

if not LLM_ENABLED:
    st.warning("⚠️ Ollama server not reachable. Start it with: ollama serve")

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Finsight", layout="wide")
st.title("📊 Finsight AI — Smart Stock Insight Assistant")

st.markdown(
    "Upload a CSV of stock symbols (column name: `Symbol`) and optionally a chart image. "
    "Then click **Analyze**."
)

# Layout: Left for uploads, right for results
left, right = st.columns([1, 2])

with left:
    uploaded_file = st.file_uploader("Upload CSV with stock symbols (Symbol column)", type=["csv"])
    image_file = st.file_uploader("Upload stock chart / screenshot (optional)", type=["png", "jpg", "jpeg"])
    period = st.selectbox("History period", options=["7d", "1mo", "3mo"], index=1)
    interval = st.selectbox("Interval", options=["1d", "1h"], index=0)
    analyze_button = st.button("Analyze")

with right:
    result_area = st.empty()

# -------------------------------
# Helper: read symbols from CSV
# -------------------------------
def read_symbols_from_file(uploaded) -> list:
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Unable to read CSV: {e}")
        return []
    cols = [c.strip().lower() for c in df.columns]
    if 'symbol' in cols:
        symbol_col = df.columns[cols.index('symbol')]
        symbols = df[symbol_col].dropna().astype(str).str.strip().tolist()
        return symbols
    # fallback to first column
    symbols = df.iloc[:,0].dropna().astype(str).str.strip().tolist()
    return symbols

# -------------------------------
# Main analysis
# -------------------------------
if analyze_button:
    symbols = []
    if uploaded_file:
        symbols = read_symbols_from_file(uploaded_file)
        if not symbols:
            st.warning("No symbols found in CSV.")
    else:
        st.warning("Please upload a CSV with stock symbols (or refresh and try).")

    image_summary = None
    if image_file:
        image_bytes = image_file.read()
        # Pass first symbol if available for combined insight
        image_summary = analyze_image_and_data(image_bytes, ticker=symbols[0] if symbols else None)

    if symbols:
        with st.spinner("Fetching data and running analysis..."):
            results = analyze_portfolio(symbols)
            for res in results:
                t = res.get("ticker")
                st.subheader(f"{t}")

                # Chart
                df = res.get("history")
                if df is not None and not df.empty and 'Close' in df.columns:
                    df_chart = df.rename(columns={'Datetime':'ds'})
                    df_chart['ds'] = pd.to_datetime(df_chart['ds'])
                    df_chart = df_chart.set_index('ds')
                    st.line_chart(df_chart['Close'])

                # Rule summary
                rule = res.get("rule") or {}
                st.markdown(
                    f"**Rule verdict:** {rule.get('direction','-')} — "
                    f"ShortMA: {rule.get('short_ma')} , LongMA: {rule.get('long_ma')}"
                )

                # LLM explanation
                st.markdown("**AI explanation:**")
                if LLM_ENABLED:
                    st.text(res.get("llm","No explanation"))
                else:
                    st.text("⚠️ Ollama server not reachable — AI explanation disabled.")

                st.write("---")

            # Show image summary if present
            if image_summary:
                st.subheader("Image summary & ViT trend")
                st.text(image_summary)
    else:
        st.info("No symbols to analyze. Upload CSV and click Analyze.")

st.markdown("---")
st.write("Demo prepared by Finsight. This tool is for educational/demo purpose only — not financial advice.")

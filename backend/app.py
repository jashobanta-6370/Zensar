from fastapi import FastAPI, UploadFile, File
from backend.fetcher import fetch_stock_data
from backend.image_analyzer import analyze_image

app = FastAPI()

@app.get("/mcp/fetch_stock")
def mcp_fetch(symbol: str):
    return fetch_stock_data([symbol])

@app.post("/mcp/analyze_chart")
async def mcp_analyze_chart(file: UploadFile = File(...)):
    contents = await file.read()          # ✅ read file bytes
    trend = analyze_image(contents)       # ✅ pass bytes to analyzer
    return {"trend": trend}


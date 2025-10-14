# agents/vision_agent.py
from backend.image_analyzer import analyze_image_bytes

def analyze_image_for_report(image_bytes: bytes) -> str:
    summary = analyze_image_bytes(image_bytes)
    if "error" in summary:
        return f"Image analysis error: {summary['error']}"
    desc = (
    f"Image {summary['width']}x{summary['height']}, Dominant color: {summary['dominant_color']}. "
    f"ViT trend prediction: {summary.get('vit_trend','Unknown')}. "
    f"{summary.get('note','')}"
)
    return desc

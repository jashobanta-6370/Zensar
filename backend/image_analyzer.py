from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import torch
from PIL import Image
import io
from collections import Counter

MODEL_NAME = "google/vit-base-patch16-224-in21k"
vit_model_cache = None

def load_vit_model():
    global vit_model_cache
    if vit_model_cache:
        return vit_model_cache
    feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
    model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
    vit_model_cache = {"model": model, "extractor": feature_extractor}
    return vit_model_cache

def predict_chart_trend(image: Image.Image):
    vit_model = load_vit_model()
    inputs = vit_model["extractor"](images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = vit_model["model"](**inputs)
    predicted_class = outputs.logits.argmax(-1).item()
    return "Uptrend" if predicted_class % 2 == 0 else "Downtrend"


def analyze_image_bytes(image_bytes: bytes):
    """Return image summary + ViT trend"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {"error": f"unable to open image: {e}"}

    w, h = img.size
    pixels = list(img.getdata())
    sample = pixels if len(pixels) < 20000 else pixels[:: max(1, len(pixels)//20000)]
    def round_color(c, step=32):
        return tuple((x//step)*step for x in c)
    rounded = [round_color(px) for px in sample]
    most_common = Counter(rounded).most_common(3)
    dominant = most_common[0][0] if most_common else (0,0,0)
    
    trend = predict_chart_trend(img)

    return {
        "width": w,
        "height": h,
        "mode": img.mode,
        "dominant_color": dominant,
        "top_colors": [c for c,_ in most_common[:3]],
        "vit_trend": trend,
        "note": "ViT trend prediction included"
    }

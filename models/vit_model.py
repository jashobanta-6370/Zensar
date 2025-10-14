from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import torch
from PIL import Image

MODEL_NAME = "google/vit-base-patch16-224-in21k"

def load_vit_model():
    feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
    model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
    return {"model": model, "extractor": feature_extractor}

def predict_chart_trend(vit_model, image: Image.Image):
    extractor = vit_model["extractor"]
    model = vit_model["model"]
    inputs = extractor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_class = outputs.logits.argmax(-1).item()
    return "Uptrend" if predicted_class % 2 == 0 else "Downtrend"

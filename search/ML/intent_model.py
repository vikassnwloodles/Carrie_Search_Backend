import os
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# Load classifier
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
clf = joblib.load(os.path.join(BASE_DIR, "intent_classifier.pkl"))

# Load embedding model from Hugging Face
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def classify_intent(query, threshold=0.6):
    embedding = embedding_model.encode([query])
    probs = clf.predict_proba(embedding)[0]
    label = clf.classes_[np.argmax(probs)]
    confidence = np.max(probs)

    if confidence < threshold:
        return "unsure", confidence
    return label, confidence

def map_intent_to_model(intent: str) -> str:
    intent_model_map = {
        "factual": "sonar-pro",
        "deep-research": "sonar-deep-research",
        "reasoning": "sonar-reasoning-pro",
        "creative": "r1-1776",
        "unsure": "sonar-pro"
    }
    return intent_model_map.get(intent, "sonar-pro")

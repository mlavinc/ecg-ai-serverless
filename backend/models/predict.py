import joblib
import pandas as pd

from backend.constants import CLASS_NAMES
from backend.features.ecg_features import extract_features
from backend.models.train import FEATURE_COLUMNS
from backend.services.ecg_service import load_ecg


def load_model(model_path):
    return joblib.load(model_path)


def predict(model, features):

    df = pd.DataFrame([features])

    df = df[FEATURE_COLUMNS]

    prediction = model.predict(df)[0]

    probabilities = model.predict_proba(df)[0]

    confidence = float(max(probabilities))

    return {
        "class_id": int(prediction),
        "class_name": CLASS_NAMES[prediction],
        "confidence": confidence
    }


def predict_ecg(model, record_path):

    signal = load_ecg(record_path)

    features = extract_features(signal)

    return predict(model, features)
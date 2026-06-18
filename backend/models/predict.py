import joblib
import numpy as np

from backend.constants import CLASS_NAMES
from backend.constants import FEATURE_COLUMNS
from backend.features.ecg_features import extract_features
from backend.services.ecg_service import load_ecg


def load_model(model_path):
    return joblib.load(model_path)


def _features_to_vector(features):
    """Build the model input row (numpy) in the canonical feature order.

    Using a plain ndarray (instead of a pandas DataFrame) keeps pandas out
    of the Lambda runtime dependencies. The model is trained the same way,
    so there is no feature-name mismatch warning.
    """
    return np.array(
        [[features[col] for col in FEATURE_COLUMNS]],
        dtype=np.float64,
    )


def predict(model, features):

    x = _features_to_vector(features)

    prediction = int(model.predict(x)[0])

    probabilities = model.predict_proba(x)[0]

    confidence = float(max(probabilities))

    return {
        "class_id": prediction,
        "class_name": CLASS_NAMES[prediction],
        "confidence": confidence
    }


def predict_ecg(model, record_path):

    signal = load_ecg(record_path)

    features = extract_features(signal)

    return predict(model, features)

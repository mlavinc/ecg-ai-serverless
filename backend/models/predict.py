import joblib
import numpy as np

from backend.constants import CLASS_NAMES
from backend.constants import FEATURE_COLUMNS
from backend.features.ecg_features import extract_features
from backend.services.ecg_service import load_ecg
from backend.services.ecg_service import load_ecg_from_bytes


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

    raw_probabilities = model.predict_proba(x)[0]

    # model.classes_ carries the label ordering learned during training;
    # map it back to class_id -> probability so the output does not depend
    # on sklearn's internal class ordering.
    probabilities = {
        CLASS_NAMES[int(class_id)]: float(prob)
        for class_id, prob in zip(model.classes_, raw_probabilities)
    }

    confidence = float(max(raw_probabilities))

    return {
        "class_id": prediction,
        "class_name": CLASS_NAMES[prediction],
        "confidence": confidence,
        "probabilities": probabilities,
    }


def predict_ecg(model, record_path):
    """Run inference on a WFDB record already present on disk (local/dev use)."""
    signal = load_ecg(record_path)
    features = extract_features(signal)
    return {
        "prediction": predict(model, features),
        "features": features,
        "signal": signal,
    }


def predict_ecg_bytes(model, header_bytes, signal_bytes):
    """Run inference on ECG file contents received over the wire."""
    signal = load_ecg_from_bytes(header_bytes, signal_bytes)
    features = extract_features(signal)
    return {
        "prediction": predict(model, features),
        "features": features,
        "signal": signal,
    }

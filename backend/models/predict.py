import joblib
import pandas as pd
import wfdb

from backend.features.ecg_features import extract_features
from backend.models.train import FEATURE_COLUMNS
from backend.services.ecg_service import load_ecg


CLASS_NAMES = {
    0: "Dangerous_VFL_VF",
    1: "Special_Form_VTTdP",
    2: "Threatening_VT",
    3: "Potential_Dangerous",
    4: "Supraventricular",
    5: "Sinus_rhythm",
}


def load_model(model_path):
    return joblib.load(model_path)


def predict(model, features):

    df = pd.DataFrame([features])

    df = df[FEATURE_COLUMNS]

    prediction = model.predict(df)[0]

    return {
        "class_id": int(prediction),
        "class_name": CLASS_NAMES[prediction]
    }


def predict_ecg(model, record_path):
    """
    Predict directly from a WFDB ECG record.
    """

    record = wfdb.rdrecord(record_path)

    signal = record.p_signal

    features = extract_features(signal)

    return predict(model, features)
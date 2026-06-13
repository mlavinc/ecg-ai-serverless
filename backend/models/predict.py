import joblib
import pandas as pd


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

    prediction = model.predict(df)[0]

    return {
        "class_id": int(prediction),
        "class_name": CLASS_NAMES[prediction]
    }
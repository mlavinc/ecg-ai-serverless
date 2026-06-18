from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "models"
    / "random_forest_final.joblib"
)


CLASS_MAPPING = {
    "1_Dangerous_VFL_VF": 0,
    "2_Special_Form_VTTdP": 1,
    "3_Threatening_VT": 2,
    "4_Potential_Dangerous": 3,
    "5_Supraventricular": 4,
    "6_Sinus_rhythm": 5,
}


CLASS_NAMES = {
    0: "Dangerous_VFL_VF",
    1: "Special_Form_VTTdP",
    2: "Threatening_VT",
    3: "Potential_Dangerous",
    4: "Supraventricular",
    5: "Sinus_rhythm",
}
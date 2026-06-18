from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "models"
    / "random_forest_final.joblib"
)


# S3 location of the trained model (used by the Lambda runtime).
# Values can be overridden through environment variables so the same
# code works locally and on AWS without edits.
S3_BUCKET_NAME = "ecg-ai-models-mlavinc"
S3_MODEL_KEY = "random_forest_final.joblib"
S3_REGION = "sa-east-1"


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


# Order of the feature vector expected by the trained model.
# This is the single source of truth shared by training and inference.
FEATURE_COLUMNS = [
    "mean",
    "median",
    "std",
    "variance",
    "min",
    "max",
    "range",
    "rms",
    "energy",
    "peak_to_peak",
    "waveform_length",

    "mean_rr",
    "std_rr",
    "rmssd",

    "min_rr",
    "max_rr",
    "rr_range",

    "skewness",
    "kurtosis",

    "dominant_frequency",
    "spectral_energy",
    "spectral_entropy",
]

import os
import joblib
import boto3

MODEL_PATH_LOCAL = "/tmp/random_forest_final.joblib"

BUCKET_NAME = "ecg-ai-models-mlavinc"
MODEL_KEY = "random_forest_final.joblib"

_s3 = boto3.client("s3")

_MODEL = None


def get_model():

    global _MODEL

    if _MODEL is not None:
        return _MODEL

    # si ya existe en /tmp, no descargar
    if not os.path.exists(MODEL_PATH_LOCAL):

        _s3.download_file(
            BUCKET_NAME,
            MODEL_KEY,
            MODEL_PATH_LOCAL
        )

    _MODEL = joblib.load(MODEL_PATH_LOCAL)

    return _MODEL
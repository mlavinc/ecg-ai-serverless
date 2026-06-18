import json

from backend.constants import MODEL_PATH
from backend.models.predict import load_model, predict_ecg


MODEL = load_model(MODEL_PATH)


def lambda_handler(event, context):

    record_path = event["record_path"]

    result = predict_ecg(
        MODEL,
        record_path
    )

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
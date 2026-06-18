import json

from backend.services.model_loader import get_model
from backend.models.predict import predict_ecg


def lambda_handler(event, context):

    record_path = event["record_path"]

    model = get_model()

    result = predict_ecg(
        model,
        record_path
    )

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
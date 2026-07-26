"""Local end-to-end test for the ECG Lambda HTTP router.

Builds the same Lambda Function URL ("payload format 2.0") events that API
Gateway/Function URLs send in production, and runs them through the local
``backend`` source tree. By default it exercises /health, /metrics and
/predict (with a synthetic ECG record) so the full pipeline can be checked
without any real dataset or AWS credentials.

Usage:
    python test_lambda.py                 # health + metrics + predict (synthetic ECG)
    python test_lambda.py path/to/record  # predict using a real WFDB record (no extension)
"""

import base64
import os
import sys

from backend.services.lambda_handler import lambda_handler
from backend.utils.mock_ecg import ensure_mock_record


def _http_event(method, path, body=None):
    return {
        "requestContext": {"http": {"method": method}},
        "rawPath": path,
        "isBase64Encoded": False,
        "body": body,
    }


def _predict_event(record_path):
    with open(record_path + ".hea", "rb") as fh:
        header_b64 = base64.b64encode(fh.read()).decode("ascii")
    with open(record_path + ".dat", "rb") as fh:
        signal_b64 = base64.b64encode(fh.read()).decode("ascii")

    import json

    return _http_event(
        "POST",
        "/predict",
        body=json.dumps({"header": header_b64, "signal": signal_b64}),
    )


def main():
    default_model = os.path.join("data", "models", "random_forest_final.joblib")
    if "MODEL_LOCAL_PATH" not in os.environ and os.path.exists(default_model):
        os.environ["MODEL_LOCAL_PATH"] = default_model

    print("GET /health ->", lambda_handler(_http_event("GET", "/health"), None))
    print("GET /metrics ->", lambda_handler(_http_event("GET", "/metrics"), None))

    if len(sys.argv) > 1:
        record_path = sys.argv[1]
    else:
        record_path = ensure_mock_record(os.path.join("data", "mock"))
        print(f"Using synthetic ECG record: {record_path}")

    result = lambda_handler(_predict_event(record_path), None)
    print("POST /predict ->", result)


if __name__ == "__main__":
    main()

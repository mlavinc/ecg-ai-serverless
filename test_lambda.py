"""Local end-to-end test for the ECG Lambda pipeline.

Runs the exact same handler that AWS Lambda will run, but importing from
the local ``backend`` source tree. By default it generates a synthetic
ECG record so the full pipeline works without the real ECG_DB dataset.

Usage:
    python test_lambda.py                 # synthetic ECG
    python test_lambda.py path/to/record  # real WFDB record (no extension)

For inference to succeed a model must be available. Either:
    * place it at data/models/random_forest_final.joblib, or
    * set MODEL_LOCAL_PATH to its location, or
    * have valid AWS credentials so it can be downloaded from S3.
"""

import os
import sys

from backend.services.lambda_handler import lambda_handler
from backend.utils.mock_ecg import ensure_mock_record


def build_event():
    # Allow passing a real WFDB record base path as an argument.
    if len(sys.argv) > 1:
        return {"record_path": sys.argv[1]}

    # Otherwise generate a synthetic ECG record on the fly.
    # Base path "data/mock" -> data/mock.hea + data/mock.dat. This is the same
    # record bundled into the Lambda ZIP, so record_path="data/mock" behaves
    # identically locally and on AWS.
    mock_path = os.path.join("data", "mock")
    record_path = ensure_mock_record(mock_path)
    print(f"Using synthetic ECG record: {record_path}")
    return {"record_path": record_path}


def main():
    event = build_event()

    # Prefer a local model file when present so the test runs without AWS.
    default_model = os.path.join(
        "data", "models", "random_forest_final.joblib"
    )
    if "MODEL_LOCAL_PATH" not in os.environ and os.path.exists(default_model):
        os.environ["MODEL_LOCAL_PATH"] = default_model

    response = lambda_handler(event, None)
    print(response)


if __name__ == "__main__":
    main()

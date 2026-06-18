import os
import tempfile

import joblib

from backend.constants import (
    S3_BUCKET_NAME,
    S3_MODEL_KEY,
    S3_REGION,
)


_MODEL = None


def _config():
    """Resolve configuration at call time so env vars set by the caller
    (or by the Lambda runtime) are always honoured."""
    bucket = os.environ.get("MODEL_BUCKET", S3_BUCKET_NAME)
    key = os.environ.get("MODEL_KEY", S3_MODEL_KEY)
    region = os.environ.get("AWS_REGION", S3_REGION)
    local_path = os.environ.get("MODEL_LOCAL_PATH")
    # Cross-platform writable cache (/tmp on Lambda, %TEMP% on Windows).
    cache_path = os.path.join(tempfile.gettempdir(), key)
    return bucket, key, region, local_path, cache_path


def _download_from_s3(bucket, key, region, destination):
    """Download the model from S3 using the AWS-provided boto3 runtime."""
    import boto3

    s3 = boto3.client("s3", region_name=region)
    s3.download_file(bucket, key, destination)


def _resolve_model_path():
    """Return a local filesystem path to the model, downloading if needed."""
    bucket, key, region, local_path, cache_path = _config()

    # 1. Explicit local override (used for local testing, no AWS needed).
    if local_path and os.path.exists(local_path):
        return local_path

    # 2. Cached copy from a previous (warm) invocation.
    if os.path.exists(cache_path):
        return cache_path

    # 3. Download from S3 into the writable cache directory.
    try:
        _download_from_s3(bucket, key, region, cache_path)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Could not load model from S3 (s3://{bucket}/{key}): {exc}"
        ) from exc

    return cache_path


def get_model():
    """Return the cached model, loading it from disk/S3 on first use."""
    global _MODEL

    if _MODEL is not None:
        return _MODEL

    model_path = _resolve_model_path()
    _MODEL = joblib.load(model_path)

    return _MODEL

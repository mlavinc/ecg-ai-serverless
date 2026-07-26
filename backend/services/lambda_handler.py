"""HTTP router for the ECG classification Lambda.

Invoked directly through a Lambda Function URL (no API Gateway), which uses
the same "payload format 2.0" event shape as an API Gateway HTTP API:

    event["requestContext"]["http"]["method"]
    event["rawPath"]
    event["body"]              # possibly base64-encoded
    event["isBase64Encoded"]

Routes:
    GET  /health    -> liveness + model-loaded check
    GET  /metrics    -> static model evaluation metrics
    POST /predict    -> run inference on an uploaded ECG record

CORS is not required for the deployed architecture (CloudFront serves the
frontend and proxies /api/* to this same function, so requests are
same-origin). The headers below are added anyway as a safe default for
direct testing against the raw Function URL.
"""

import base64
import json
import time
import traceback

from backend.constants import CLASS_NAMES
from backend.constants import MODEL_VERSION
from backend.models.predict import predict_ecg_bytes
from backend.services.metrics_service import get_model_metrics
from backend.services.model_loader import get_model


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

# Cap the number of points sent back for charting; the frontend only needs
# enough resolution to render the waveform smoothly, not every raw sample.
MAX_SIGNAL_POINTS = 3000


class ApiError(Exception):
    """A handled error that maps to a specific HTTP status code."""

    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", **CORS_HEADERS},
        "body": json.dumps(body),
    }


def _downsample(values, max_points):
    n = len(values)
    if n <= max_points:
        return values
    step = n / max_points
    return [values[int(i * step)] for i in range(max_points)]


def _handle_health(_event):
    try:
        get_model()
        model_loaded = True
    except Exception:  # noqa: BLE001
        model_loaded = False

    return _response(200, {"status": "ok", "model_loaded": model_loaded})


def _handle_metrics(_event):
    return _response(200, get_model_metrics())


def _parse_body(event):
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body)
    else:
        body = body.encode("utf-8")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ApiError(400, "Request body must be valid JSON.") from exc

    header_b64 = payload.get("header")
    signal_b64 = payload.get("signal")
    if not header_b64 or not signal_b64:
        raise ApiError(
            400,
            "Request body must include base64-encoded 'header' (.hea) and "
            "'signal' (.dat) fields.",
        )

    try:
        header_bytes = base64.b64decode(header_b64)
        signal_bytes = base64.b64decode(signal_b64)
    except (ValueError, TypeError) as exc:
        raise ApiError(400, "'header' and 'signal' must be valid base64.") from exc

    return header_bytes, signal_bytes


def _handle_predict(event):
    header_bytes, signal_bytes = _parse_body(event)

    start = time.perf_counter()
    try:
        model = get_model()
        result = predict_ecg_bytes(model, header_bytes, signal_bytes)
    except ValueError as exc:
        raise ApiError(400, f"Could not process ECG record: {exc}") from exc
    inference_time_ms = round((time.perf_counter() - start) * 1000, 2)

    signal_values = result["signal"].flatten().tolist()

    return _response(
        200,
        {
            "prediction": result["prediction"],
            "features": result["features"],
            "signal": {
                "sampling_rate": 250,
                "values": [
                    round(v, 5)
                    for v in _downsample(signal_values, MAX_SIGNAL_POINTS)
                ],
                "total_samples": len(signal_values),
            },
            "meta": {
                "inference_time_ms": inference_time_ms,
                "model_version": MODEL_VERSION,
                "class_names": list(CLASS_NAMES.values()),
            },
        },
    )


ROUTES = {
    ("GET", "/health"): _handle_health,
    ("GET", "/metrics"): _handle_metrics,
    ("POST", "/predict"): _handle_predict,
}


def _route_key(event):
    """Extract (method, path) from a Function URL / HTTP API v2 event.

    Strips a leading "/api" prefix so the same handler works whether it is
    invoked directly (Function URL root) or via CloudFront's /api/* origin,
    and normalizes a trailing slash.
    """
    http_ctx = event.get("requestContext", {}).get("http", {})
    method = http_ctx.get("method", "GET").upper()
    path = event.get("rawPath") or "/"

    if path.startswith("/api"):
        path = path[len("/api"):] or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    return method, path


def lambda_handler(event, context):
    method, path = _route_key(event)

    if method == "OPTIONS":
        return {"statusCode": 204, "headers": CORS_HEADERS, "body": ""}

    handler = ROUTES.get((method, path))
    if handler is None:
        return _response(404, {"error": f"No route for {method} {path}"})

    try:
        return handler(event)
    except ApiError as exc:
        return _response(exc.status_code, {"error": exc.message})
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return _response(500, {"error": "Internal server error."})

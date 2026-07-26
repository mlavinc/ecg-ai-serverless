import json

from backend.constants import METRICS_RELATIVE_PATH


def get_model_metrics():
    """Load the static evaluation metrics produced by backend/models/train.py.

    Returns an empty-ish dict with an explanatory note instead of raising if
    the file is missing, so the /metrics endpoint degrades gracefully rather
    than returning a 500 for a non-critical, informational route.
    """
    try:
        with open(METRICS_RELATIVE_PATH, "r") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "available": False,
            "note": (
                "Model metrics have not been generated yet. Run "
                "`python scripts/train_model.py` with the dataset present."
            ),
        }

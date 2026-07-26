import json

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix
)

import joblib
from pathlib import Path

from backend.constants import CLASS_NAMES, FEATURE_COLUMNS, MODEL_VERSION


def train_model(X_train, y_train):

    model = RandomForestClassifier(
        n_estimators = 1000,
        max_depth = 25,
        min_samples_leaf = 1,
        class_weight = "balanced",
        random_state = 42,
        n_jobs = -1
    )

    model.fit(X_train, y_train)

    return model


def save_metrics(accuracy, balanced_accuracy, report_dict, confusion, labels_sorted, df):
    """Persist evaluation metrics consumed by the /metrics API route.

    Writes data/models/model_metadata.json: the single source of truth for
    both this training script and the ``/metrics`` Lambda route (see
    backend/services/metrics_service.py).
    """
    class_names_sorted = [CLASS_NAMES[label] for label in labels_sorted]

    per_class = {
        CLASS_NAMES[label]: {
            "precision": round(report_dict[str(label)]["precision"], 4),
            "recall": round(report_dict[str(label)]["recall"], 4),
            "f1_score": round(report_dict[str(label)]["f1-score"], 4),
            "support": int(report_dict[str(label)]["support"]),
        }
        for label in labels_sorted
    }

    class_distribution = (
        df["class_name"].value_counts().sort_index().to_dict()
    )

    metrics = {
        "model": "RandomForestClassifier",
        "model_version": MODEL_VERSION,
        "dataset": "PhysioNet ECG Fragment Database for Dangerous Arrhythmia (2022)",
        "dataset_size": int(len(df)),
        "num_classes": len(CLASS_NAMES),
        "num_features": len(FEATURE_COLUMNS),
        "random_state": 42,
        "accuracy": round(float(accuracy), 4),
        "balanced_accuracy": round(float(balanced_accuracy), 4),
        "macro_precision": round(report_dict["macro avg"]["precision"], 4),
        "macro_recall": round(report_dict["macro avg"]["recall"], 4),
        "macro_f1_score": round(report_dict["macro avg"]["f1-score"], 4),
        "per_class": per_class,
        "class_distribution": class_distribution,
        "confusion_matrix": {
            "labels": class_names_sorted,
            "matrix": confusion.tolist(),
        },
    }

    output_path = Path("data/models/model_metadata.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as fh:
        json.dump(metrics, fh, indent=2)

    print(f"\nMetrics saved to: {output_path}")


def main():

    print("\nLoading dataset...")

    df = pd.read_csv(
        "data/processed/dataset.csv"
    )

    # Train on plain numpy arrays so the saved model carries no feature-name
    # metadata. Inference then feeds numpy arrays too (no pandas at runtime).
    X = df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = df["label"].to_numpy()

    print(f"Dataset shape: {df.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples : {len(X_test)}")

    print("\nTraining model...")

    model = train_model(
        X_train,
        y_train
    )

    model_dir = Path("data/models")
    model_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        model_dir /
        "random_forest_final.joblib"
    )

    joblib.dump(
        model,
        model_path
    )

    print(
        f"\nModel saved to: {model_path}"
    )

    y_pred = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    balanced_accuracy = (
        balanced_accuracy_score(
            y_test,
            y_pred
        )
    )

    print("\n===================================")
    print("MODEL EVALUATION")
    print("===================================\n")

    print(
        f"Accuracy          : {accuracy:.4f}"
    )

    print(
        f"Balanced Accuracy : {balanced_accuracy:.4f}"
    )

    report_dict = classification_report(
        y_test,
        y_pred,
        digits=4,
        output_dict=True,
        zero_division=0,
    )

    print("\nClassification Report\n")

    print(
        classification_report(
            y_test,
            y_pred,
            digits=4
        )
    )

    print("\nConfusion Matrix\n")

    labels_sorted = sorted(CLASS_NAMES.keys())
    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=labels_sorted,
    )

    print(cm)

    save_metrics(
        accuracy=accuracy,
        balanced_accuracy=balanced_accuracy,
        report_dict=report_dict,
        confusion=cm,
        labels_sorted=labels_sorted,
        df=df,
    )

    feature_importance = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "importance": model.feature_importances_
    })

    feature_importance = (
        feature_importance
        .sort_values(
            by="importance",
            ascending=False
        )
    )

    print("\n===================================")
    print("FEATURE IMPORTANCE")
    print("===================================\n")

    print(
        feature_importance.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
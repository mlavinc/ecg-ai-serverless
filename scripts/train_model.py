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


# =====================================
# Main
# =====================================

def main():

    print("\nLoading dataset...")

    df = pd.read_csv("data/processed/dataset.csv")

    feature_columns = [
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
        "signal_length",
        "waveform_length",
        "dominant_frequency",
        "spectral_energy",
        "spectral_entropy",
    ]

    X = df[feature_columns]
    y = df["label"]

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

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )

    print("\nTraining model...")

    model.fit(X_train, y_train)

    # Save model

    model_dir = Path("data/models")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "random_forest.joblib"

    joblib.dump(model, model_path)

    print(f"\nModel saved to: {model_path}")

    # Predictions

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    balanced_accuracy = balanced_accuracy_score(
        y_test,
        y_pred
    )

    print("\n===================================")
    print("MODEL EVALUATION")
    print("===================================\n")

    print(f"Accuracy          : {accuracy:.4f}")
    print(f"Balanced Accuracy : {balanced_accuracy:.4f}")

    print("\nClassification Report\n")

    print(
        classification_report(
            y_test,
            y_pred,
            digits=4
        )
    )

    print("\nConfusion Matrix\n")

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print(cm)


if __name__ == "__main__":
    main()
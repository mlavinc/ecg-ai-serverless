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

from backend.constants import FEATURE_COLUMNS


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
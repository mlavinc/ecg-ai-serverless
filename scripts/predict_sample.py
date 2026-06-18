from pathlib import Path

from backend.models.predict import (
    load_model,
    predict_ecg
)

DATA_PATH = Path("ECG_DB")


def main():

    model = load_model(
        "data/models/random_forest_final.joblib"
    )

    records = list(
        DATA_PATH.rglob("*.hea")
    )

    if not records:
        print("No ECG files found.")
        return

    sample_record = records[0]

    print(
        f"\nTesting record: "
        f"{sample_record.name}"
    )

    result = predict_ecg(
        model,
        str(sample_record.with_suffix(""))
    )

    print("\nPrediction\n")
    print(result)


if __name__ == "__main__":
    main()
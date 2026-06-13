import pandas as pd

from backend.models.predict import (
    load_model,
    predict
)


MODEL_PATH = "data/models/random_forest.joblib"


def main():

    df = pd.read_csv(
        "data/processed/dataset.csv"
    )

    sample = (
        df
        .drop(columns=["label", "class_name"])
        .iloc[0]
        .to_dict()
    )

    model = load_model(MODEL_PATH)

    result = predict(
        model,
        sample
    )

    print("\nPrediction Result\n")

    print(result)


if __name__ == "__main__":
    main()
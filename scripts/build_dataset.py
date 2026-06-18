import pandas as pd
from pathlib import Path

from backend.constants import CLASS_MAPPING
from backend.features.ecg_features import extract_features
from backend.services.ecg_service import load_ecg


# =====================================
# Configuration
# =====================================

DATA_PATH = Path(__file__).resolve().parent.parent / "ECG_DB"


# =====================================
# Label Mapping
# =====================================

def get_label(class_folder):
    return CLASS_MAPPING[class_folder]


# =====================================
# Main
# =====================================

def main():

    records = list(DATA_PATH.rglob("*.hea"))

    if not records:
        print(f"ERROR: No .hea files found in {DATA_PATH}")
        return

    features_list = []
    labels = []
    class_names = []

    unknown_classes = set()

    total_records = len(records)

    print(f"\nRecords found: {total_records}\n")

    for idx, hea_file in enumerate(records, start=1):

        try:

            # Example:
            # ECG_DB/3_Threatening_VT/frag/record.hea
            class_folder = hea_file.parent.parent.name

            if class_folder not in CLASS_MAPPING:
                unknown_classes.add(class_folder)
                continue

            record_path = hea_file.with_suffix("")

            signal = load_ecg(record_path)

            features = extract_features(signal)

            features_list.append(features)
            labels.append(get_label(class_folder))
            class_names.append(class_folder)

            if idx % 200 == 0:
                print(f"Processed {idx}/{total_records}")

        except Exception as e:
            print(f"ERROR processing {hea_file}: {e}")

    df = pd.DataFrame(features_list)

    df["label"] = labels
    df["class_name"] = class_names

    output_path = Path("data/processed")
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / "dataset.csv"

    df.to_csv(output_file, index=False)

    print("\nDataset generated successfully")
    print(f"Output file: {output_file}")
    print(f"Dataset shape: {df.shape}")

    if unknown_classes:
        print("\nUnknown classes found:")

        for class_name in sorted(unknown_classes):
            print(f" - {class_name}")

    print("\nClass distribution:\n")

    print(
        df["class_name"]
        .value_counts()
        .sort_index()
    )


if __name__ == "__main__":
    main()
# ECG AI Serverless

ECG arrhythmia classification system using Machine Learning and AWS Serverless architecture.

## Overview

This project detects and classifies potentially dangerous cardiac arrhythmias from ECG recordings.

The system extracts statistical, frequency-domain, and heart rate variability (HRV) features from ECG signals and uses a Random Forest classifier to predict one of six arrhythmia classes.

Deployment architecture:

ECG record → Feature Extraction → Random Forest Model → AWS Lambda (ZIP) → JSON Response

The model is stored in Amazon S3 and loaded into the Lambda `/tmp` cache at
runtime. An API Gateway front door is planned.

---

## Dataset

PhysioNet ECG Fragment Database for Dangerous Arrhythmia (2022)

Classes:

* Dangerous_VFL_VF
* Special_Form_VTTdP
* Threatening_VT
* Potential_Dangerous
* Supraventricular
* Sinus_rhythm

Dataset size:

* Total ECG fragments: 1016

Class distribution:

| Class               | Samples |
| ------------------- | ------: |
| Dangerous_VFL_VF    |     337 |
| Special_Form_VTTdP  |      72 |
| Threatening_VT      |     169 |
| Potential_Dangerous |     132 |
| Supraventricular    |     106 |
| Sinus_rhythm        |     200 |

---

## Technology Stack

* Python 3.11
* NumPy
* SciPy (stats, FFT, and signal-based R-peak detection)
* Scikit-Learn (RandomForest)
* Pandas (development / training only)
* AWS Lambda (ZIP deployment)
* Amazon S3 (model storage)
* API Gateway (planned)

Removed to fit the 250 MB ZIP limit: `wfdb` (replaced by a minimal numpy
format-16 reader) and `neurokit2` + `matplotlib` (HRV peaks now via scipy).

---

## Feature Engineering

### Statistical Features

* mean
* median
* std
* variance
* min
* max
* range
* rms
* energy
* peak_to_peak
* waveform_length

### HRV Features

* mean_rr
* std_rr
* rmssd
* min_rr
* max_rr
* rr_range

### Signal Shape Features

* skewness
* kurtosis

### Frequency Domain Features

* dominant_frequency
* spectral_energy
* spectral_entropy

Total features: 22

---

## Model

Algorithm:

* RandomForestClassifier

Configuration:

* class_weight="balanced"
* random_state=42

---

## Current Results

Accuracy: **77.5%**

Balanced Accuracy: **71.5%**

The model is trained on six ECG rhythm classes and evaluated using a stratified
train-test split. These numbers reflect the lightweight, dependency-free feature
pipeline (see "Deployment strategy" below); they are intentionally a small
trade-off against the original neurokit2-based pipeline (75.6% balanced) in
exchange for a much smaller, simpler Lambda ZIP.

---

## Architecture: two clearly separated environments

This project keeps **development source** and the **Lambda deployment artifact**
strictly separate.

### 1. `backend/` — source code (development)

All clean Python lives here and uses package-style imports:

```python
from backend.services.model_loader import get_model
```

### 2. Deployment artifact

The artifact is **generated** from `backend/` (never edited by hand):

* `package/` — flat artifact staged by `scripts/build_package.py`. Inside it,
  imports are rewritten to the flat Lambda style:

```python
from model_loader import get_model
```

The same script also bundles the synthetic test record at `package/data/` and
zips everything into `lambda.zip` with forward-slash paths (correct for Linux/
Lambda). The artifact does not vendor `boto3`/`botocore`; the runtime provides
them.

### 3. `test_lambda.py` — local end-to-end test

Imports from `backend`, generates a synthetic ECG (so no real dataset is
required) and runs the full Lambda handler locally:

```bash
pip install -r requirements.txt
python test_lambda.py
# -> {'statusCode': 200, 'body': '{"class_id": 5, "class_name": "Sinus_rhythm", ...}'}
```

It loads the model from `data/models/` when present (no AWS credentials needed).

## Project Structure

```
ECG_AI_Serverless/
├── backend/                  # SOURCE (development)
│   ├── __init__.py
│   ├── constants.py          # CLASS_NAMES, FEATURE_COLUMNS, S3 config
│   ├── features/
│   │   └── ecg_features.py
│   ├── models/
│   │   ├── train.py
│   │   └── predict.py
│   ├── services/
│   │   ├── ecg_service.py
│   │   ├── lambda_handler.py
│   │   └── model_loader.py   # cross-platform /tmp cache + S3 download
│   └── utils/
│       └── mock_ecg.py       # synthetic ECG generator for testing
│
├── data/
│   ├── models/
│   │   ├── random_forest_final.joblib   # trained model (uploaded to S3)
│   │   └── model_metadata.json
│   ├── mock.hea / mock.dat   # tiny synthetic test record (bundled into the ZIP)
│   └── processed/dataset.csv # extracted feature dataset (gitignored)
│
├── scripts/
│   ├── build_dataset.py      # re-extract features from ECG_DB
│   ├── train_model.py
│   ├── predict_sample.py
│   └── build_package.py      # builds package/ + lambda.zip from backend/
│
├── package/                  # GENERATED staging dir (gitignored)
├── lambda.zip                # GENERATED deploy artifact (gitignored)
├── test_lambda.py            # local end-to-end test
├── requirements.txt          # dev deps (pandas + boto3 for training/upload)
├── requirements-lambda.txt   # runtime deps (numpy/scipy/scikit-learn/joblib)
└── .gitignore
```

---

## Deployment strategy (why this fits a ZIP)

A naive vendoring of the scientific stack was **~290 MB unzipped** — over the
250 MB hard limit for `.zip` Lambda. The size came almost entirely from two
optional dependencies:

* `neurokit2` (HRV R-peak detection) → pulls in **matplotlib** (~70 MB).
* `wfdb` (record reader) → pulls in matplotlib + aiohttp/requests/fsspec.

This project removes both **without changing the model's role**:

* R-peak detection now uses a small **Pan-Tompkins-style detector built on
  `scipy.signal`** (`backend/features/ecg_features.py`). scipy is already a
  scikit-learn dependency, so this adds nothing to the package.
* ECG files are read by a **minimal numpy WFDB format-16 reader**
  (`backend/services/ecg_service.py`) — byte-identical to `wfdb` on this dataset.
* Inference feeds the model **numpy arrays**, so `pandas` is not packaged.

The model is **retrained** on these features so the training and inference
pipelines stay coherent (Python 3.11 / scikit-learn 1.7.2 stack).

Resulting runtime dependencies: `numpy`, `scipy`, `scikit-learn`, `joblib`.

| Artifact | Size |
| --- | --- |
| Unzipped package | **~183 MB** (limit 250 MB) |
| Zipped `lambda.zip` | **~57 MB** |

## Deployment (ZIP, Python 3.11)

### 1. Build the artifact

```bash
python scripts/build_package.py
```

This single command builds `package/` (Linux cp311 wheels), bundles the test
record at `package/data/mock.{hea,dat}`, and writes `lambda.zip` directly.

> The zip is created in Python with forward-slash paths on purpose. Do **not**
> use PowerShell 5.1 `Compress-Archive` — it writes backslash paths that AWS
> Lambda (Linux) treats as literal filenames, breaking the package.

Handler: `lambda_handler.lambda_handler`  •  Runtime: `python3.11`

The demo invocation works with no external files because the record is inside
the ZIP (AWS Lambda's working directory is the function root `/var/task`):

```json
{ "record_path": "data/mock" }
```

### 2. Upload the model to S3 (once, and after every retrain)

The ~35 MB model is **not** in the ZIP; it is downloaded to `/tmp` at runtime.

```bash
aws s3 cp data/models/random_forest_final.joblib \
    s3://ecg-ai-models-mlavinc/random_forest_final.joblib --region sa-east-1
```

### 3. Create the function

The zipped artifact (~57 MB) exceeds the 50 MB **direct** upload limit, so
upload it through S3:

```bash
aws s3 cp lambda.zip s3://<your-deploy-bucket>/lambda.zip --region sa-east-1

aws lambda create-function \
  --function-name ecg-ai \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --role <EXECUTION_ROLE_ARN> \
  --code S3Bucket=<your-deploy-bucket>,S3Key=lambda.zip \
  --timeout 30 --memory-size 1024 \
  --region sa-east-1
```

The execution role needs `s3:GetObject` on the model bucket plus the basic
Lambda logging permissions. Updates: `aws lambda update-function-code
--function-name ecg-ai --s3-bucket <bucket> --s3-key lambda.zip`.

### Free Tier notes

* `python3.11` ZIP (no container, no ECR) → no ECR storage cost.
* 1024 MB memory + warm-start model caching in `/tmp` and in-process keeps each
  invocation well within the Lambda free tier for personal use.

---

## Current Status

Completed:

* Dataset generation pipeline
* ECG feature extraction
* HRV feature extraction
* Random Forest training pipeline
* ECG prediction from real .hea/.dat files
* Model evaluation
* Feature importance analysis

* Dependency-light feature pipeline (scipy-only HRV, numpy WFDB reader)
* AWS Lambda ZIP packaging under 250 MB (~183 MB unzipped)
* S3 model loading with /tmp caching

Next:

* API Gateway endpoint
* CI for automated package builds

---

## License

Educational and research purposes.

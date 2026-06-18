# ECG AI Serverless

ECG arrhythmia classification system using Machine Learning and AWS Serverless architecture.

## Overview

This project detects and classifies potentially dangerous cardiac arrhythmias from ECG recordings.

The system extracts statistical, frequency-domain, and heart rate variability (HRV) features from ECG signals and uses a Random Forest classifier to predict one of six arrhythmia classes.

Planned deployment architecture:

ECG File → Feature Extraction → Random Forest Model → AWS Lambda → API Gateway → JSON Response

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
* Pandas
* SciPy
* WFDB
* NeuroKit2
* Scikit-Learn
* AWS Lambda (planned)
* API Gateway (planned)
* Amazon S3 (planned)

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

Accuracy:

76.96%

Balanced Accuracy:

75.60%

The model is trained on six ECG rhythm classes and evaluated using a stratified train-test split.

---

## Project Structure

ECG_AI_Serverless/

├── backend/
│   ├── constants.py
│   ├── features/
│   │   └── ecg_features.py
│   ├── models/
│   │   ├── train.py
│   │   └── predict.py
│   └── services/
│
├── data/
│   ├── processed/
│   │   └── dataset.csv
│   └── models/
│       ├── random_forest_final.joblib
│       └── model_metadata.json
│
├── scripts/
│   ├── build_dataset.py
│   ├── train_model.py
│   └── predict_sample.py
│
├── requirements.txt
├── requirements-lambda.txt
├── README.md
└── .gitignore

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

Next:

* AWS Lambda integration
* API Gateway endpoint
* S3 model storage
* End-to-end serverless deployment

---

## License

Educational and research purposes.

# ECG AI Serverless

End-to-end ECG arrhythmia classification: a Random Forest model runs inference on short single-lead fragments and returns class probabilities through a serverless HTTP API.

Built as a portfolio project covering applied ML, a React frontend, and a cost-aware AWS backend with no always-on compute. Not a medical device.

## Features

- Classifies ECG fragments into 6 rhythm classes (VF/VFL, VT/TdP variants, supraventricular, sinus)
- Extracts 22 statistical, HRV, and frequency-domain features before inference
- Serverless backend on AWS Lambda with a Function URL (no API Gateway)
- React SPA for upload, sample playback, waveform charts, and model metrics
- Terraform + one-command deploy/destroy scripts for the AWS side
- Local end-to-end test of `/health`, `/metrics`, and `/predict` without AWS

## Architecture

```text
Browser → Vercel (React / Vite)
              │
              ▼
        Lambda Function URL
              │
              ├── feature extraction (NumPy / SciPy)
              └── Random Forest (joblib model from S3, cached in /tmp)
```

Terraform manages the artifacts bucket, Lambda, Function URL, IAM, and CloudWatch Logs. The trained model lives in a separate S3 bucket that Terraform does not create or destroy. The frontend is hosted on Vercel and calls the Function URL via `VITE_API_URL`.

API routes on the Function URL:

| Route | Method | Role |
| --- | --- | --- |
| `/health` | GET | Liveness + model-loaded check |
| `/metrics` | GET | Static evaluation metadata |
| `/predict` | POST | Inference on base64-encoded `.hea` / `.dat` |

## Technical Highlights

- **ZIP-sized scientific stack.** A naive NumPy/SciPy/sklearn package exceeded Lambda’s 250 MB unzipped limit. `wfdb` and `neurokit2` were dropped; the runtime uses a minimal format-16 WFDB reader and a Pan-Tompkins-style R-peak detector on `scipy.signal`. Result: ~183 MB unzipped / ~57 MB zipped.
- **Lambda Function URL instead of API Gateway.** Direct HTTPS endpoint with CORS configured in Terraform; keeps the demo stack free of API Gateway’s 12-month free-tier cliff.
- **Model loading.** On cold start the joblib artifact is downloaded from S3 into `/tmp` and reused on warm invocations (`MODEL_BUCKET` / `MODEL_KEY`).
- **Shared feature contract.** `FEATURE_COLUMNS` in `backend/constants.py` is the single source of truth for training and inference.
- **IaC + operational scripts.** `scripts/deploy.*` builds Linux x86_64 wheels, stages the ZIP in S3 (needed because it exceeds the ~50 MB direct upload limit), applies Terraform, and health-checks the Function URL.

Model (from `data/models/model_metadata.json`): RandomForestClassifier, 76.96% accuracy / 75.6% balanced accuracy on the PhysioNet ECG Fragment Database for Dangerous Arrhythmia (2022), 1,016 fragments, 6 classes.

## Tech Stack

**Backend / ML**
Python 3.11 · NumPy · SciPy · scikit-learn · joblib · AWS Lambda · Amazon S3

**Frontend**
React 19 · TypeScript · Vite · Tailwind CSS · shadcn/ui · TanStack Query · Axios · Zod · uPlot · Recharts

**Infrastructure**
Terraform · Lambda Function URL · IAM · CloudWatch Logs · Vercel (frontend hosting)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js (for the Vite frontend)
- (Optional deploy) AWS CLI, Terraform ≥ 1.6, and an existing S3 bucket for the model object

### Backend

```bash
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python test_lambda.py
```

`test_lambda.py` exercises `/health`, `/metrics`, and `/predict` with a synthetic ECG. No dataset or AWS credentials required when `data/models/random_forest_final.joblib` is present (it sets `MODEL_LOCAL_PATH` automatically).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Copy `frontend/.env.example` to `frontend/.env.local` and set `VITE_API_URL` to a deployed Function URL when you are not using a local backend. With `npm run dev`, `/api/*` is proxied to `http://localhost:9000` by default (`vite.config.ts`).

### Deploy (AWS backend)

```powershell
.\scripts\deploy.ps1
.\scripts\destroy.ps1 -Yes
```

```bash
./scripts/deploy.sh
./scripts/destroy.sh --yes
```

Full runbook: [`DEPLOY.md`](DEPLOY.md). Infra details: [`infra/README.md`](infra/README.md).

## Limitations

Portfolio / research demo only — not for clinical use. Trained on a small public dataset. Frontend “Try a sample” signals are synthetic illustrations, not patient recordings. Per-class metrics and the confusion matrix in `/metrics` stay `null` until training is re-run with the raw PhysioNet data (`ECG_DB/`, not bundled in the repo).

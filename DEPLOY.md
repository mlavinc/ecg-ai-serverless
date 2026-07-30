# Deploy & destroy (AWS backend)

One-command lifecycle for the serverless **inference backend** on AWS.
The React frontend is hosted on **Vercel** and talks to the Lambda Function
URL via `VITE_API_URL`. Infrastructure is defined only in [`infra/`](infra/).

```
Vercel (React frontend)
        |
        v
AWS Lambda Function URL
        |
        +-- code ZIP staged in artifacts S3
        v
Random Forest model in S3 (external bucket)
```

## Prerequisites

| Tool | Purpose |
| --- | --- |
| AWS CLI | credentials configured (`aws configure` or env vars) |
| Terraform >= 1.6 | infrastructure |
| Python 3.11+ | `scripts/build_package.py` |
| Local model file | `data/models/random_forest_final.joblib` |
| External model bucket | must already exist (`model_bucket_name`) |

Optional: copy [`infra/terraform.tfvars.example`](infra/terraform.tfvars.example)
to `infra/terraform.tfvars`.

## Deploy (one command)

```powershell
.\scripts\deploy.ps1
```

```bash
chmod +x scripts/deploy.sh scripts/destroy.sh   # once
./scripts/deploy.sh
```

The script is **idempotent**: safe to re-run after a partial failure. It will:

1. Build `lambda.zip`
2. Verify the external model bucket exists; upload the model object if missing
3. `terraform init` + `terraform apply` (stages ZIP in artifacts S3, creates/updates Lambda)
4. Health-check `GET {function_url}/health`
5. Print the Lambda Function URL (use as `VITE_API_URL` on Vercel)

## Vercel frontend

In the Vercel project settings (or `frontend/.env.local` for local builds):

```
VITE_API_URL=https://<id>.lambda-url.<region>.on.aws
```

Do not include a trailing slash. See [`frontend/.env.example`](frontend/.env.example).

## Destroy (one command)

```powershell
.\scripts\destroy.ps1 -Yes
```

```bash
./scripts/destroy.sh --yes
```

Removes the artifacts bucket (`force_destroy`), Lambda + Function URL, and IAM.
The external model bucket and the Vercel deployment are left intact.

## Deployment audit notes

| Issue | Resolution |
| --- | --- |
| ZIP > 50 MB direct upload | Stage via artifacts S3 (`s3_bucket` / `s3_key`) |
| Reserved concurrency vs account floor | Not set (needs ≥10 unreserved) |
| Function URL CORS `OPTIONS` | Invalid (method string length ≤ 6); use `GET`/`POST` only |
| Public Function URL 403 | Both `InvokeFunctionUrl` (AuthType NONE) and `InvokeFunction` (`InvokedViaFunctionUrl`) |
| Multipart S3 ETag churn | Use `source_hash = filemd5(...)` instead of `etag` |
| Package arch | Lambda `architectures = ["x86_64"]` matches build wheels |

## Cost awareness

- No API Gateway, no CloudFront, no always-on compute, no custom domain
- Tear down with destroy between demos
- Frontend bandwidth is billed by Vercel (hobby tier for portfolio demos)

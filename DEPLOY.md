# Deploy & destroy (portfolio demo)

One-command lifecycle for a fully serverless demo on AWS. Infrastructure is
defined only in [`infra/`](infra/) (Terraform). Application code (ML pipeline,
REST API, React UI) is **not** modified by these scripts.

```
CloudFront
├── /*      → S3 (private, OAC)           Frontend
└── /api/*  → Lambda Function URL          Backend
                    ↑ code ZIP staged in artifacts S3
                    ↓
              Model object in S3 (external bucket)
```

## Prerequisites

| Tool | Purpose |
| --- | --- |
| AWS CLI | credentials configured (`aws configure` or env vars) |
| Terraform >= 1.6 | infrastructure |
| Python 3.11+ | `scripts/build_package.py` |
| Node.js + npm | frontend build |
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
3. `terraform init` + `terraform apply` (stages ZIP in artifacts S3, creates Lambda from S3)
4. Wait for CloudFront to finish deploying
5. Build + sync the frontend, invalidate the CDN
6. Health-check `GET {cloudfront}/api/health`
7. Print the CloudFront URL and API endpoints

## Destroy (one command)

```powershell
.\scripts\destroy.ps1 -Yes
```

```bash
./scripts/destroy.sh --yes
```

Removes CloudFront, frontend/artifacts buckets (`force_destroy`), Lambda +
Function URL, and IAM. The external model bucket is left intact.

## Deployment audit notes (production readiness)

Fixes applied so a clean / resumed `terraform apply` succeeds without manual
console work:

| Issue | Resolution |
| --- | --- |
| ZIP > 50 MB direct upload | Stage via artifacts S3 (`s3_bucket` / `s3_key`) |
| Reserved concurrency vs account floor | Not set (needs ≥10 unreserved) |
| Function URL CORS `OPTIONS` | Invalid (method string length ≤ 6); use `GET`/`POST` only |
| Public Function URL 403 | Explicit `aws_lambda_permission` for `lambda:InvokeFunctionUrl` |
| Multipart S3 ETag churn | Use `source_hash = filemd5(...)` instead of `etag` |
| SPA `404 → index.html` rewrote API errors | Only map S3 `403 → index.html` |
| Cold starts / CDN races | Wait for distribution deployed; longer health retries |
| Package arch | Lambda `architectures = ["x86_64"]` matches build wheels |

## Cost awareness

- No API Gateway, no always-on compute, no custom domain / Route 53 / ACM
- CloudFront `PriceClass_100`
- Tear down with destroy between demos

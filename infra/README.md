# Infrastructure (Terraform)

Fully serverless, cost-aware stack. Nothing here runs (or bills) while the
infrastructure is destroyed; it is meant to be brought up on demand for demos
and torn down afterwards.

```
CloudFront
├── /*      → S3 (private, via Origin Access Control)   [Frontend]
└── /api/*  → Lambda Function URL                        [Backend]
                    ↑ code from artifacts S3 bucket (ZIP staged here)
                    ↓
              Random Forest Model (S3-cached in /tmp)
```

The Lambda ZIP (~57 MB) exceeds the ~50 MB **direct** upload limit for
`CreateFunction`, so Terraform stages it in a managed artifacts bucket and
creates the function with `s3_bucket` / `s3_key` (same approach as the
original CLI deploy: `aws s3 cp lambda.zip ...` then create-function from S3).

No API Gateway, no Route 53 hosted zone, no ACM certificate, no NAT gateway,
no always-on compute.

**Preferred path for demos:** use the one-command scripts documented in
[`../DEPLOY.md`](../DEPLOY.md) (`scripts/deploy.*` / `scripts/destroy.*`).
This directory remains the single source of truth for infrastructure.

## Prerequisites

* Terraform >= 1.6
* AWS credentials with permission to manage S3, CloudFront, Lambda and IAM
* Optional: `terraform.tfvars` copied from `terraform.tfvars.example`

The Lambda ZIP and frontend sync are normally produced by the deploy scripts.
If applying manually:

```bash
python scripts/build_package.py   # from repo root → ../lambda.zip
```

The trained model lives in an **existing** S3 bucket referenced by
`var.model_bucket_name`. Terraform does **not** create or destroy that bucket.

## Manual usage

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars   # optional
terraform init
terraform plan
terraform apply
```

Then sync the frontend and invalidate (or use `scripts/deploy.*` which does this):

```bash
cd ../frontend
npm run build
aws s3 sync dist/ "s3://$(terraform -chdir=../infra output -raw frontend_bucket_name)" --delete
aws cloudfront create-invalidation \
  --distribution-id "$(terraform -chdir=../infra output -raw cloudfront_distribution_id)" \
  --paths "/*"
```

Open the app:

```bash
terraform output cloudfront_domain_name
# Health: $(terraform output -raw cloudfront_domain_name)/api/health
```

## Tearing down

Prefer:

```bash
../scripts/destroy.sh --yes    # or .\scripts\destroy.ps1 -Yes
```

Or manually:

```bash
cd infra
terraform destroy
```

The frontend bucket has `force_destroy = true` so destroy succeeds even when
build artifacts are present. The external model bucket is untouched.

## Variables

See `variables.tf` and `terraform.tfvars.example`. Notable knobs:

| Variable | Purpose |
| --- | --- |
| `project_name` | Prefix for resource names |
| `aws_region` | Lambda + frontend bucket region |
| `model_bucket_name` / `model_key` | External model object |
| `cloudfront_price_class` | Default `PriceClass_100` |
| `lambda_timeout` | Lambda + CloudFront origin read timeout (max 60) |

## Notes

* **CloudFront propagation**: first creation often takes 3–10 minutes; deploy
  scripts retry `/api/health` for this reason.
* **Cold starts**: first invocation after idle downloads the model into `/tmp`.
* **Custom domain**: not configured (keeps cost at $0). A `us_east_1` provider
  alias is declared in `versions.tf` if you add ACM later.

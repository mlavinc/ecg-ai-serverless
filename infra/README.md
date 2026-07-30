# Infrastructure (Terraform)

Serverless **inference backend** only. The React frontend is hosted on Vercel
and calls the Lambda Function URL directly (`VITE_API_URL`).

```
Vercel (React)
      |
      v
Lambda Function URL  ← ZIP staged in artifacts S3
      |
      v
Random Forest model (external S3 bucket, cached in /tmp)
```

The Lambda ZIP (~57 MB) exceeds the ~50 MB **direct** upload limit for
`CreateFunction`, so Terraform stages it in a managed artifacts bucket and
creates the function with `s3_bucket` / `s3_key`.

No CloudFront, no frontend S3 bucket, no API Gateway, no Route 53, no ACM,
no always-on compute.

**Preferred path:** [`../DEPLOY.md`](../DEPLOY.md) (`scripts/deploy.*` /
`scripts/destroy.*`).

## Prerequisites

* Terraform >= 1.6
* AWS credentials with permission to manage S3, Lambda, and IAM
* Optional: `terraform.tfvars` copied from `terraform.tfvars.example`

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
terraform output lambda_function_url
```

Set that URL as `VITE_API_URL` in Vercel.

## Tearing down

```bash
../scripts/destroy.sh --yes    # or .\scripts\destroy.ps1 -Yes
# or: terraform destroy
```

The external model bucket is untouched.

## Variables

See `variables.tf` and `terraform.tfvars.example`.

| Variable | Purpose |
| --- | --- |
| `project_name` | Prefix for resource names |
| `aws_region` | Lambda + artifacts bucket region |
| `model_bucket_name` / `model_key` | External model object |
| `lambda_timeout` | Inference timeout (seconds) |

## Notes

* **Function URL auth NONE** requires both resource-based permissions:
  `lambda:InvokeFunctionUrl` (+ `FunctionUrlAuthType=NONE`) and
  `lambda:InvokeFunction` (+ `InvokedViaFunctionUrl=true`).
* **Cold starts**: first invocation after idle downloads the model into `/tmp`.
* **CORS**: Function URL allows browser origins (`*`) for the Vercel frontend.

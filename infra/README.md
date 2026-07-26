# Infrastructure (Terraform)

Fully serverless, cost-aware stack. Nothing here runs (or bills) while the
infrastructure is destroyed; it is meant to be brought up on demand for demos
and torn down afterwards.

```
CloudFront
├── /*      → S3 (private, via Origin Access Control)   [Frontend]
└── /api/*  → Lambda Function URL                        [Backend]
                    ↓
              Random Forest Model (S3-cached in /tmp)
```

No API Gateway, no Route 53 hosted zone, no ACM certificate, no NAT gateway,
no always-on compute. See the root README for the cost analysis behind these
choices.

## Prerequisites

* Terraform >= 1.6
* AWS credentials with permission to manage S3, CloudFront, Lambda and IAM
  (`aws configure` or environment variables)
* The Lambda deployment artifact built once via:

  ```bash
  python scripts/build_package.py
  ```

  This produces `../lambda.zip` (relative to this directory), which
  `lambda.tf` packages as the function code. Re-run it whenever
  `backend/` changes, before `terraform apply`.

* The model already uploaded to the **existing** S3 bucket referenced by
  `var.model_bucket_name` (see root README, "Deployment"). Terraform does
  **not** create or manage this bucket -- it was provisioned manually and is
  only referenced as a read-only data dependency (least-privilege IAM).

## Usage

```bash
cd infra
terraform init
terraform plan
terraform apply
```

After `apply`, sync the built frontend into the new bucket and invalidate
the CDN cache:

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
```

## Tearing down

```bash
cd infra
terraform destroy
```

This removes the S3 bucket, CloudFront distribution, Lambda function/Function
URL, and IAM role -- everything Terraform created. The existing model bucket
(`var.model_bucket_name`) is untouched, since Terraform never took ownership
of it.

## Notes

* **CloudFront propagation**: distribution edits (including first creation)
  typically take 3-10 minutes to fully propagate globally.
* **Cold starts**: the first `/api/*` request after `apply` (or after a Lambda
  has been idle) downloads the model from S3 into `/tmp`, adding a few
  hundred ms; subsequent warm invocations reuse the cached model.
* **Custom domain**: intentionally not configured, to keep this at a strict
  $0. Re-introducing one only requires adding an `aws_acm_certificate` (in
  the `us_east_1` provider alias already declared in `versions.tf`) and a
  `viewer_certificate.acm_certificate_arn` on the distribution.

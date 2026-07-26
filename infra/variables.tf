variable "aws_region" {
  description = "AWS region to deploy the Lambda function and frontend bucket in."
  type        = string
  default     = "sa-east-1"
}

variable "project_name" {
  description = "Short name used to prefix/tag created resources."
  type        = string
  default     = "ecg-ai"
}

variable "model_bucket_name" {
  description = <<-EOT
    Name of the EXISTING S3 bucket holding the trained model artifact
    (random_forest_final.joblib). Created outside of Terraform (see
    README.md "Deployment"), so it is only referenced here via a data
    source, never managed/destroyed by this configuration.
  EOT
  type        = string
  default     = "ecg-ai-models-mlavinc"
}

variable "model_key" {
  description = "Object key of the trained model inside model_bucket_name."
  type        = string
  default     = "random_forest_final.joblib"
}

variable "lambda_zip_path" {
  description = "Path to the built Lambda deployment artifact (see scripts/build_package.py)."
  type        = string
  default     = "../lambda.zip"
}

variable "lambda_memory_size" {
  description = "Memory (MB) allocated to the inference Lambda."
  type        = number
  default     = 1024
}

variable "lambda_timeout" {
  description = "Timeout (seconds) for the inference Lambda."
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention for the Lambda function."
  type        = number
  default     = 14
}

variable "cloudfront_price_class" {
  description = <<-EOT
    Limits which CloudFront edge locations serve this distribution.
    PriceClass_100 (US/Canada/Europe) keeps a personal portfolio demo
    comfortably within the CloudFront always-free tier while covering the
    audience (recruiters, reviewers) most likely to visit it.
  EOT
  type        = string
  default     = "PriceClass_100"
}

variable "frontend_bucket_suffix" {
  description = <<-EOT
    Optional fixed suffix for the frontend bucket name, for reproducible
    plans across `terraform apply`/`destroy` cycles. If empty, a random
    suffix is generated once and persisted in state.
  EOT
  type        = string
  default     = ""
}

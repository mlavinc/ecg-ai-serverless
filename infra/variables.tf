variable "aws_region" {
  description = "AWS region for the Lambda function and artifacts bucket."
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

variable "lambda_s3_key" {
  description = "Object key for the Lambda ZIP inside the Terraform-managed artifacts bucket."
  type        = string
  default     = "lambda/lambda.zip"
}

variable "artifacts_bucket_suffix" {
  description = <<-EOT
    Optional fixed suffix for the Lambda artifacts bucket name. If empty, a
    random suffix is generated once and persisted in state.
  EOT
  type        = string
  default     = ""
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

  validation {
    condition     = var.lambda_timeout >= 3 && var.lambda_timeout <= 900
    error_message = "lambda_timeout must be between 3 and 900 seconds."
  }
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention for the Lambda function."
  type        = number
  default     = 14
}

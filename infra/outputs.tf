output "cloudfront_domain_name" {
  description = "Public URL of the app (frontend + /api/*)."
  value       = "https://${aws_cloudfront_distribution.this.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "Used to invalidate the cache after deploying a new frontend build."
  value       = aws_cloudfront_distribution.this.id
}

output "frontend_bucket_name" {
  description = "Private S3 bucket to sync the Vite build output into."
  value       = aws_s3_bucket.frontend.bucket
}

output "lambda_function_url" {
  description = "Direct Function URL (bypasses CloudFront; useful for debugging only)."
  value       = aws_lambda_function_url.inference.function_url
}

output "lambda_function_name" {
  value = aws_lambda_function.inference.function_name
}

output "artifacts_bucket_name" {
  description = "S3 bucket that stages the Lambda ZIP (used because the ZIP exceeds the direct-upload limit)."
  value       = aws_s3_bucket.artifacts.bucket
}

output "lambda_s3_key" {
  description = "Object key of the staged Lambda ZIP."
  value       = aws_s3_object.lambda_zip.key
}

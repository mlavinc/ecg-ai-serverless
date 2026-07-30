output "lambda_function_url" {
  description = "Public Lambda Function URL for the inference API (set as VITE_API_URL on Vercel)."
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

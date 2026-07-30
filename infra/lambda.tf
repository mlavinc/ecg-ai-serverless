# Inference function, exposed via a Lambda Function URL (no API Gateway).
# The React frontend is hosted on Vercel and calls this URL directly
# (VITE_API_URL). CORS is enabled on the Function URL for browser clients.
#
# Code packaging: the ZIP is staged in S3 (see s3_artifacts.tf) because it
# exceeds the ~50 MB direct-upload limit for CreateFunction.

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.project_name}-inference"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "inference" {
  function_name = "${var.project_name}-inference"
  role          = aws_iam_role.lambda_exec.arn

  s3_bucket = aws_s3_bucket.artifacts.id
  s3_key    = aws_s3_object.lambda_zip.key
  # Hash the local ZIP so Terraform updates the function when package contents change.
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  handler = "lambda_handler.lambda_handler"
  runtime = "python3.11"
  # Match scripts/build_package.py (manylinux x86_64 wheels).
  architectures = ["x86_64"]

  memory_size = var.lambda_memory_size
  timeout     = var.lambda_timeout

  # Do not set reserved_concurrent_executions: this account requires at least
  # 10 unreserved concurrent executions. The Lambda runtime injects AWS_REGION.

  environment {
    variables = {
      MODEL_BUCKET = var.model_bucket_name
      MODEL_KEY    = var.model_key
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_model_read,
    aws_s3_object.lambda_zip,
  ]
}

# CORS AllowMethods must be GET/POST/DELETE or "*" — not "OPTIONS".
# AWS validates each method string length <= 6; "OPTIONS" is 7 characters and
# fails CreateFunctionUrlConfig (see CreateFunctionUrlConfig / CORS docs).
# Preflight OPTIONS is handled by the Function URL CORS config automatically.
resource "aws_lambda_function_url" "inference" {
  function_name      = aws_lambda_function.inference.function_name
  authorization_type = "NONE"
  invoke_mode        = "BUFFERED"

  cors {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST"]
    allow_headers = ["content-type"]
    max_age       = 300
  }
}

# AuthType NONE requires BOTH permissions (AWS docs, Oct 2025+):
#   1) lambda:InvokeFunctionUrl + FunctionUrlAuthType=NONE
#   2) lambda:InvokeFunction   + InvokedViaFunctionUrl=true
# Missing (2) returns HTTP 403 before the function is invoked (no CloudWatch logs).
# https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html#urls-auth-none
resource "aws_lambda_permission" "function_url_public" {
  statement_id           = "FunctionURLAllowPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.inference.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "function_url_invoke" {
  statement_id             = "FunctionURLInvokeAllowPublicAccess"
  action                   = "lambda:InvokeFunction"
  function_name            = aws_lambda_function.inference.function_name
  principal                = "*"
  invoked_via_function_url = true
}

# Inference function, exposed directly via a Lambda Function URL -- no API
# Gateway. CloudFront (see cloudfront.tf) fronts this URL under /api/* so
# the browser only ever talks to one HTTPS domain, and no CORS handling is
# required for the deployed app. CORS is still configured on the Function
# URL itself purely as a convenience for testing it directly.

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.project_name}-inference"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "inference" {
  function_name = "${var.project_name}-inference"
  role          = aws_iam_role.lambda_exec.arn

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  handler = "lambda_handler.lambda_handler"
  runtime = "python3.11"

  memory_size = var.lambda_memory_size
  timeout     = var.lambda_timeout

  environment {
    variables = {
      MODEL_BUCKET = var.model_bucket_name
      MODEL_KEY    = var.model_key
      AWS_REGION   = var.aws_region
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}

resource "aws_lambda_function_url" "inference" {
  function_name      = aws_lambda_function.inference.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["content-type"]
    max_age       = 300
  }
}

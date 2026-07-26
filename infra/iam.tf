# Minimal IAM: basic Lambda execution (CloudWatch Logs) plus read-only
# access to the single object holding the trained model. No wildcard
# permissions, no access to any other AWS resource.

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "${var.project_name}-lambda-exec"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "lambda_model_read" {
  statement {
    sid       = "ReadTrainedModel"
    actions   = ["s3:GetObject"]
    resources = ["arn:aws:s3:::${var.model_bucket_name}/${var.model_key}"]
  }

  statement {
    sid       = "AllowBucketLocation"
    actions   = ["s3:GetBucketLocation"]
    resources = ["arn:aws:s3:::${var.model_bucket_name}"]
  }
}

resource "aws_iam_role_policy" "lambda_model_read" {
  name   = "${var.project_name}-model-read"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.lambda_model_read.json
}

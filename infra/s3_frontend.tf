# Private bucket serving the built React app. No static website hosting,
# no public access -- CloudFront is the only reader, via the Origin Access
# Control defined in cloudfront.tf.

resource "random_id" "frontend_bucket_suffix" {
  count       = var.frontend_bucket_suffix == "" ? 1 : 0
  byte_length = 4
}

locals {
  frontend_bucket_suffix = var.frontend_bucket_suffix != "" ? var.frontend_bucket_suffix : random_id.frontend_bucket_suffix[0].hex
  frontend_bucket_name   = "${var.project_name}-frontend-${local.frontend_bucket_suffix}"
}

resource "aws_s3_bucket" "frontend" {
  bucket = local.frontend_bucket_name
  # Portfolio demos create/destroy often; allow terraform destroy even when
  # the Vite build has been synced into the bucket.
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Grants CloudFront (identified by this specific distribution, via OAC) read
# access. No principal other than the CloudFront service can read objects.
data "aws_iam_policy_document" "frontend_bucket_policy" {
  statement {
    sid       = "AllowCloudFrontOAC"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.frontend.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.this.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = data.aws_iam_policy_document.frontend_bucket_policy.json
}

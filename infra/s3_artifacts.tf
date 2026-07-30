# Private bucket for the Lambda deployment ZIP.
#
# The artifact (~57 MB) exceeds the 50 MB direct-upload limit for
# CreateFunction / UpdateFunctionCode, so the ZIP must be staged in S3 first
# (same strategy documented historically for this project). Terraform uploads
# the local lambda.zip here; the Lambda resource then references s3_bucket /
# s3_key instead of filename.

resource "random_id" "artifacts_bucket_suffix" {
  count       = var.artifacts_bucket_suffix == "" ? 1 : 0
  byte_length = 4
}

locals {
  artifacts_bucket_suffix = (
    var.artifacts_bucket_suffix != ""
    ? var.artifacts_bucket_suffix
    : random_id.artifacts_bucket_suffix[0].hex
  )
  artifacts_bucket_name = "${var.project_name}-artifacts-${local.artifacts_bucket_suffix}"
  lambda_s3_key         = var.lambda_s3_key
}

resource "aws_s3_bucket" "artifacts" {
  bucket        = local.artifacts_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_object" "lambda_zip" {
  bucket = aws_s3_bucket.artifacts.id
  key    = local.lambda_s3_key
  source = var.lambda_zip_path

  # Large ZIPs use multipart upload; the S3 ETag becomes "<md5>-<parts>" and
  # must NOT be compared to filemd5() (that caused perpetual plan diffs and
  # unnecessary Lambda replacements). source_hash tracks the local file only.
  source_hash = filemd5(var.lambda_zip_path)
}

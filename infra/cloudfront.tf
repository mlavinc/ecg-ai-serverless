# Single CloudFront distribution fronting both the static frontend (S3, via
# OAC) and the backend (the Lambda Function URL, as a second origin behind
# /api/*). This keeps frontend and API same-origin (no CORS needed in the
# deployed app) and avoids API Gateway entirely.

locals {
  s3_origin_id     = "frontend-s3"
  lambda_origin_id = "inference-lambda"

  # Function URL comes back as "https://<id>.lambda-url.<region>.on.aws/";
  # CloudFront custom origins need a bare domain name (no scheme, no
  # trailing slash).
  lambda_function_url_domain = trimsuffix(
    replace(aws_lambda_function_url.inference.function_url, "https://", ""),
    "/"
  )
}

resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${var.project_name}-frontend-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# AWS-managed policies, referenced by name instead of hardcoding their IDs.
data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_origin_request_policy" "all_viewer_except_host" {
  name = "Managed-AllViewerExceptHostHeader"
}

resource "aws_cloudfront_distribution" "this" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = var.cloudfront_price_class
  comment             = "${var.project_name} frontend + API"

  # Ensure the Function URL is publicly invokable before CF starts proxying.
  depends_on = [aws_lambda_permission.function_url_public]

  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = local.s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  origin {
    domain_name = local.lambda_function_url_domain
    origin_id   = local.lambda_origin_id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
      # Match Lambda timeout so long cold-start + inference are not cut by CF.
      origin_read_timeout      = var.lambda_timeout
      origin_keepalive_timeout = 5
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = local.s3_origin_id
    viewer_protocol_policy = "redirect-to-https"
    cache_policy_id        = data.aws_cloudfront_cache_policy.caching_optimized.id
    compress               = true
  }

  ordered_cache_behavior {
    path_pattern             = "/api/*"
    allowed_methods          = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods           = ["GET", "HEAD"]
    target_origin_id         = local.lambda_origin_id
    viewer_protocol_policy   = "https-only"
    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id
    compress                 = true
  }

  # SPA routing for the S3 origin: OAC missing-object responses are typically
  # 403, not 404. Map 403 -> index.html for client-side routes.
  # Do NOT map 404 globally: custom error responses are distribution-wide and
  # would rewrite legitimate Lambda /api/* 404 JSON into HTML.
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # Default *.cloudfront.net certificate: no ACM certificate, no Route53
  # hosted zone, no custom domain -- keeps this at $0 (see infra/README.md).
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

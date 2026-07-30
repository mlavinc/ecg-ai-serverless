terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      # 6.28.0+ required for aws_lambda_permission.invoked_via_function_url
      # (Function URL AuthType NONE second permission, AWS docs Oct 2025+)
      version = ">= 6.28.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = var.project_name
      ManagedBy = "terraform"
    }
  }
}

# CloudFront-related ACM certificates must live in us-east-1. Not used today
# (the default *.cloudfront.net certificate is used to keep this at $0 -- no
# Route53 hosted zone, no ACM certificate), but kept available for a future
# custom domain without restructuring providers.
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project   = var.project_name
      ManagedBy = "terraform"
    }
  }
}

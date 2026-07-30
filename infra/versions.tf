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

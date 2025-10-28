terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
  
  default_tags {
    tags = {
      Project     = "fraud-detection-system"
      Environment = "development"
      ManagedBy   = "terraform"
      CreatedBy   = "verafin-inspired-project"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
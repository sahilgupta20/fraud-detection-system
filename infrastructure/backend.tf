terraform {
  backend "s3" {
    bucket  = "fraud-tfstate-sahil-2024" 
    key     = "fraud-detection/terraform.tfstate"
    region  = "ap-south-1"
    encrypt = true
  }
}
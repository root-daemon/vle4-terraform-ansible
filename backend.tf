terraform {
  backend "s3" {
    bucket       = "vle4-terraform-state-071292884790-us-east-1"
    key          = "vle4/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}

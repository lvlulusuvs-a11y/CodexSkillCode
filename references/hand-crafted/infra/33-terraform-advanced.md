# Terraform Advanced Patterns

Beyond basic infrastructure management.

## Workspaces for Environments

terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

terraform workspace select dev
terraform apply

Use workspace name in resource naming:

resource "aws_instance" "app" {
  tags = {
    Name = "app-${terraform.workspace}"
  }
}

## Remote State

terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

DynamoDB prevents concurrent changes.
S3 stores state with versioning for rollback.

## Modules

modules/vpc/main.tf:
variable "environment" {}
variable "cidr" {}
resource "aws_vpc" "main" {
  cidr_block = var.cidr
  tags = { Name = "vpc-${var.environment}" }
}

Usage:
module "vpc" {
  source      = "./modules/vpc"
  environment = "prod"
  cidr        = "10.0.0.0/16"
}

## Data Sources

Read existing resources:

data "aws_vpc" "existing" {
  tags = { Name = "production-vpc" }
}

resource "aws_subnet" "app" {
  vpc_id     = data.aws_vpc.existing.id
  cidr_block = "10.0.1.0/24"
}

## Lifecycle Rules

Prevent accidental deletion:

resource "aws_db_instance" "main" {
  lifecycle {
    prevent_destroy = true
  }
}

Ignore changes made outside Terraform:

resource "aws_instance" "app" {
  lifecycle {
    ignore_changes = [ami, user_data]
  }
}


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.

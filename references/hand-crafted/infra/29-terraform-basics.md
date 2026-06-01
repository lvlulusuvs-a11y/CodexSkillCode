# Terraform: Infrastructure as Code

Manage cloud resources with code. Reproducible, reviewable, versioned.

## Basic Configuration

terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

## Resource Example

resource "aws_ecs_service" "app" {
  name            = "my-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.app.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8080
  }
}

## Variables

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod"
  }
}

variable "instance_count" {
  description = "Number of instances"
  type        = number
  default     = 2
}

## Outputs

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "database_url" {
  description = "Database connection URL"
  value       = aws_rds_cluster.main.endpoint
  sensitive   = true
}

## Modules

module "networking" {
  source = "./modules/networking"
  vpc_cidr = "10.0.0.0/16"
  environment = var.environment
}

module "database" {
  source = "./modules/database"
  vpc_id     = module.networking.vpc_id
  subnet_ids = module.networking.private_subnet_ids
}

## State Management

terraform {
  backend "s3" {
    bucket         = "myapp-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

DynamoDB table for state locking prevents concurrent modifications.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.

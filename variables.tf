variable "aws_region" {
  description = "AWS Region used for the lab"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR range for the VPC"
  type        = string
  default     = "10.44.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR range for the internet-facing subnet"
  type        = string
  default     = "10.44.1.0/24"
}

variable "admin_cidr" {
  description = "Operator public IPv4 CIDR permitted to SSH to the lab hosts"
  type        = string
}

variable "key_name" {
  description = "EC2 key pair name managed by this lab"
  type        = string
  default     = "vle4-terraform-ansible-20260921"
}

variable "public_key_path" {
  description = "Path to the public half of the dedicated lab SSH key, relative to this project"
  type        = string
}

variable "instance_type" {
  description = "Instance type for both VLE 4 web nodes"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "Pinned Amazon Linux 2023 AMI in us-east-1; changing it would replace both lab servers"
  type        = string
  default     = "ami-0fef201115eefe936"
}

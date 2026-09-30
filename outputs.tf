output "vpc_id" {
  value = aws_vpc.lab.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "security_group_id" {
  value = aws_security_group.web.id
}

output "instance_ids" {
  value = aws_instance.web[*].id
}

output "public_ips" {
  value = aws_instance.web[*].public_ip
}

output "public_dns" {
  value = aws_instance.web[*].public_dns
}

output "ssm_instance_profile" {
  value = aws_iam_instance_profile.web_ssm.name
}

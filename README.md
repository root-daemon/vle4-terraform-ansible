# VLE 4 Terraform and Ansible Lab

The public repository excludes the lab SSH key, Terraform state and plan files, the operator-specific `terraform.tfvars`, and browser evidence. Copy `terraform.tfvars.example` to `terraform.tfvars`, set your current public IPv4 CIDR, and generate your own SSH key before adapting this project for another AWS account.

This project provisions a dedicated VPC, public subnet, internet gateway, route table, security group, and two Amazon Linux 2023 EC2 instances. The Ansible playbook installs Docker and starts an Nginx container on each host so the configuration can be verified over HTTP.

Terraform runs in AWS CodeBuild in `us-east-1`. Its state is stored remotely in the private, versioned S3 backend `vle4-terraform-state-071292884790-us-east-1`, under `vle4/terraform.tfstate`. This deployment uses AWS account `071292884790` through the `vishal-test` CLI profile; the CodeBuild job itself uses its IAM role, not a local credential or access key.

## AWS-only deployment (verified 2026-09-29)

The `vle4-terraform-cloud-deploy` CodeBuild project reads the private S3 source archive `artifacts/vle4-cloud-redo.zip`. Its `buildspec-cloud-deploy.yml` installs Terraform, runs `terraform init`, `validate`, `plan`, and `apply`, then uses Systems Manager Run Command to execute `ansible/configure_web.yml` on both EC2 hosts. Each host installs Docker, runs Nginx, and is checked over HTTP from its own loopback interface. An SSM instance profile was attached to both hosts; no operator SSH session is needed for the cloud deployment.

The AMI is pinned to the image already running on the two hosts. A plan guard rejects any delete or replacement before `terraform apply`, preventing a moving "latest AMI" pointer from unexpectedly rebuilding the lab servers.

The latest successful build ID is `vle4-terraform-cloud-deploy:88be3104-5457-4bbe-a0b2-1fb028e6a83c`. It was started from AWS CloudShell. Google Chrome screenshots of the CloudShell build status, both SSM Ansible recaps, and both HTTP 200 checks are in `evidence/`. To rerun the same AWS-hosted workflow:

```bash
aws codebuild start-build --project-name vle4-terraform-cloud-deploy --profile vishal-test --region us-east-1
```

Check the resulting build and its CloudWatch logs before considering a rerun complete. Updating the local source files alone does not update the private S3 source archive used by CodeBuild.

## CloudShell run

1. Open CloudShell in `us-east-1`.
2. Download the project archive from the lab artifact bucket and extract it in `$HOME`.
3. Run `./cloudshell-run.sh`.

The script uses CloudShell's temporary IAM credentials, verifies the AWS account and region, runs `terraform init`, and creates a no-change plan against the remote state. It does not embed AWS access keys or a local profile.

## AWS-hosted validation-only run

The separate `vle4-terraform-cloud-plan` project uses `buildspec-cloud-validate.yml` to run Terraform init, validation, and plan without applying changes. Both projects use dedicated IAM roles and the same remote S3 state backend. Neither workflow runs `terraform destroy`.

SSH is restricted to the operator CIDR defined in `terraform.tfvars`; HTTP is public solely for the lab validation page.

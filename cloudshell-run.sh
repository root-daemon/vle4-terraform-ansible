#!/usr/bin/env bash
set -euo pipefail

expected_account="071292884790"
expected_region="us-east-1"
terraform_version="1.16.3"

if ! command -v terraform >/dev/null 2>&1; then
  install_dir="${HOME}/.local/bin"
  mkdir -p "${install_dir}"
  curl --fail --silent --show-error --location \
    "https://releases.hashicorp.com/terraform/${terraform_version}/terraform_${terraform_version}_linux_amd64.zip" \
    --output "/tmp/terraform_${terraform_version}.zip"
  unzip -o "/tmp/terraform_${terraform_version}.zip" -d "${install_dir}"
  export PATH="${install_dir}:${PATH}"
fi

actual_account="$(aws sts get-caller-identity --query Account --output text)"
actual_region="$(aws configure get region || true)"

if [[ "${actual_account}" != "${expected_account}" ]]; then
  echo "Refusing to run: expected AWS account ${expected_account}, found ${actual_account}." >&2
  exit 1
fi

if [[ "${actual_region}" != "${expected_region}" ]]; then
  export AWS_DEFAULT_REGION="${expected_region}"
fi

terraform init -input=false
terraform validate
terraform plan -input=false -out=cloudshell.tfplan
terraform show -no-color cloudshell.tfplan

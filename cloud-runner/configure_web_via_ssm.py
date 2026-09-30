"""Run the VLE 4 Ansible playbook on each AWS EC2 host through Systems Manager."""

import base64
import json
import subprocess
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


ROOT = Path(__file__).resolve().parents[1]
playbook = ROOT.joinpath("ansible/configure_web.yml").read_bytes()
encoded_playbook = base64.b64encode(playbook).decode("ascii")
instance_ids = json.loads(
    subprocess.check_output(
        ["terraform", "output", "-json", "instance_ids"], cwd=ROOT, text=True
    )
)
ssm = boto3.client("ssm", region_name="us-east-1")

for index, instance_id in enumerate(instance_ids, start=1):
    host_name = f"vle4-web-{index}"
    for _ in range(90):
        managed = ssm.describe_instance_information(
            Filters=[{"Key": "InstanceIds", "Values": [instance_id]}]
        )["InstanceInformationList"]
        if managed and managed[0]["PingStatus"] == "Online":
            break
        time.sleep(10)
    else:
        raise SystemExit(f"{host_name}: SSM agent did not register within 15 minutes")

    commands = [
        "set -eu",
        "dnf install -y ansible-core",
        f"printf '%s' '{encoded_playbook}' | base64 -d > /tmp/vle4-configure-web.yml",
        f"printf '[servers]\\n{host_name} ansible_connection=local\\n' > /tmp/vle4-inventory.ini",
        "ansible-playbook -i /tmp/vle4-inventory.ini /tmp/vle4-configure-web.yml",
        "curl --fail --silent --show-error http://127.0.0.1/",
    ]
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands, "executionTimeout": ["1800"]},
        Comment=f"VLE 4 Ansible cloud configuration for {host_name}",
        TimeoutSeconds=1800,
    )
    command_id = response["Command"]["CommandId"]
    print(f"{host_name}: SSM command {command_id} started on {instance_id}", flush=True)

    for _ in range(360):
        time.sleep(5)
        try:
            invocation = ssm.get_command_invocation(
                CommandId=command_id, InstanceId=instance_id
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "InvocationDoesNotExist":
                continue
            raise
        status = invocation["Status"]
        if status in {"Success", "Failed", "Cancelled", "TimedOut", "Cancelling"}:
            print(invocation.get("StandardOutputContent", ""), flush=True)
            if invocation.get("StandardErrorContent"):
                print(invocation["StandardErrorContent"], flush=True)
            if status != "Success":
                raise SystemExit(f"{host_name}: SSM/Ansible ended with {status}")
            break
    else:
        raise SystemExit(f"{host_name}: timed out waiting for Ansible")

print("VLE 4: Terraform apply and Ansible configuration completed in AWS.")

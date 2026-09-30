"""Stop the lab's cloud deployment before Terraform deletes or replaces resources."""

import json
import sys


plan = json.load(sys.stdin)
destructive = []
for item in plan.get("resource_changes", []):
    actions = item.get("change", {}).get("actions", [])
    if "delete" in actions:
        destructive.append((item.get("address", "<unknown>"), actions))

if destructive:
    for address, actions in destructive:
        print(f"Blocked destructive Terraform change: {address} {actions}", file=sys.stderr)
    raise SystemExit(1)

print("Terraform safety check passed: no deletes or replacements")

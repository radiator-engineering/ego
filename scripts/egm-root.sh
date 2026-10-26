#!/bin/sh
# Prints the install root of the enabled EGM plugin, or fails with a message.
# EGO reads EGM's skills, personas and rubrics from this root.
claude plugin list --json 2>/dev/null | python3 -c '
import json, sys
data = json.load(sys.stdin)
plugins = data if isinstance(data, list) else data.get("plugins", [])
roots = [p["installPath"] for p in plugins
         if p.get("id", "").split("@")[0] == "egm" and p.get("enabled")]
if not roots:
    sys.exit("EGO needs EGM: claude plugin marketplace add google/elephant-goldfish-model && claude plugin install egm@egm")
print(roots[0])
'

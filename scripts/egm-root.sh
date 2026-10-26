#!/bin/sh
# Prints the install root of the EGM plugin, or fails with a message.
# EGO reads EGM's skills, personas and rubrics from this root.
# Checks Claude Code first, then Codex. Other harnesses: see docs/harnesses.md.
{
  command -v claude >/dev/null 2>&1 && claude plugin list --json 2>/dev/null
  echo '<<codex>>'
  command -v codex >/dev/null 2>&1 && codex plugin list 2>/dev/null
} | python3 -c '
import json, os, sys
claude, _, codex = sys.stdin.read().partition("<<codex>>")
roots = []
try:
    data = json.loads(claude)
    plugins = data if isinstance(data, list) else data.get("plugins", [])
    roots += [p["installPath"] for p in plugins
              if p.get("id", "").split("@")[0] == "egm" and p.get("enabled")]
except ValueError:
    pass
for line in codex.splitlines():
    cols = line.split()
    if cols and cols[0].split("@")[0] == "egm" and "installed" in line:
        roots.append(cols[-1])
roots = [r for r in roots if os.path.isfile(os.path.join(r, "skills/egm_review/SKILL.md"))]
if not roots:
    sys.exit("EGO needs EGM installed in this harness. See https://github.com/google/elephant-goldfish-model/blob/main/docs/harnesses.md")
print(roots[0])
'

#!/bin/sh
# Approves Read, Grep and Glob inside EGO's own skills/, agents/ and docs/.
# Background subagents cannot ask for permission, so without this they cannot
# read EGO's instructions. Any input containing ".." or an absolute Glob
# pattern falls through to the normal permission rules.
input=$(cat)
case "$input" in *..*) exit 0 ;; esac
root=${CLAUDE_PLUGIN_ROOT%/}
[ -n "$root" ] || exit 0
if printf '%s' "$input" | grep -Eq '"tool_name"[[:space:]]*:[[:space:]]*"Glob"' &&
  printf '%s' "$input" | grep -Eq '"pattern"[[:space:]]*:[[:space:]]*"[/~]'; then
  exit 0
fi
path=$(printf '%s' "$input" | sed -nE 's/.*"(file_path|path)"[[:space:]]*:[[:space:]]*"([^"\\]*)".*/\2/p' | head -n 1)
case "$path" in
  "$root"/agents | "$root"/agents/* | "$root"/docs | "$root"/docs/* | \
  "$root"/skills | "$root"/skills/*)
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"EGO plugin file"}}'
    ;;
esac
exit 0

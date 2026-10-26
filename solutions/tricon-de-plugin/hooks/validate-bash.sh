#!/bin/bash
# PreToolUse hook: block dbt commands that target production.
# Reads the hook context JSON on stdin; exit 2 blocks and stderr becomes the reason.
INPUT=$(cat)
CMD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)

if printf '%s' "$CMD" | grep -Eq '(^|[^[:alnum:]_])dbt[[:space:]].*--target([[:space:]]+|=)prod([^[:alnum:]_]|$)'; then
  echo "Blocked: direct production dbt runs are not allowed from CoCo. Open a PR and let the CI/CD pipeline deploy to prod." >&2
  exit 2
fi
exit 0

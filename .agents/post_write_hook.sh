#!/usr/bin/env bash
# PostToolUse hook: auto-update art_manifest.json when a new algorithm .py is written.
# Invoked by Claude Code after every Write tool call; tool input arrives on stdin as JSON.
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null || true)

# Only act on .py files under src/logic_lab/ (skip __init__.py)
if [[ "$FILE_PATH" != *"src/logic_lab/"* ]] || [[ "$FILE_PATH" != *.py ]]; then
    exit 0
fi
if [[ "$(basename "$FILE_PATH")" == "__init__.py" ]]; then
    exit 0
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "[manifest] New algorithm detected: $FILE_PATH"
cd "$REPO_ROOT"
python3 .agents/update_art_manifest.py --write 2>&1 | tail -5

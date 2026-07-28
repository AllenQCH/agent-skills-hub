#!/usr/bin/env bash
set -euo pipefail

TOOL_DIR="/Users/heytea/Documents/new_tools/dbauto_export_tool"

if [ ! -x "$TOOL_DIR/start-agent.sh" ]; then
  echo "dbauto export launcher not found: $TOOL_DIR/start-agent.sh" >&2
  exit 1
fi

exec "$TOOL_DIR/start-agent.sh" "$@"

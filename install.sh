#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.agents/skills/goal-architect"
DEST_DIR="$HOME/.agents/skills/goal-architect"

mkdir -p "$(dirname "$DEST_DIR")"
rm -rf "$DEST_DIR"
cp -R "$SRC_DIR" "$DEST_DIR"

echo "Installed Goal Architect skill to $DEST_DIR"
echo "Restart Codex if the skill does not appear immediately."

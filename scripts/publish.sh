#!/usr/bin/env bash
# One command: create a GitHub repo from this folder and push it.
# Needs git and the GitHub CLI (https://cli.github.com), signed in once with `gh auth login`.
# Usage: scripts/publish.sh [repo-name] [--private|--public]
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="${1:-milk-carton}"
VISIBILITY="${2:---private}"

command -v git >/dev/null || { echo "git is not installed."; exit 1; }
command -v gh  >/dev/null || { echo "Install the GitHub CLI first: https://cli.github.com"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Run 'gh auth login' once, then run this script again."; exit 1; }

[ -d .git ] || git init -b main
git add -A
git diff --cached --quiet || git commit -m "Update milk carton schematics and notes"

if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin main
else
  gh repo create "$NAME" "$VISIBILITY" --source=. --remote=origin --push
fi

echo "Done: $(gh repo view --json url -q .url)"

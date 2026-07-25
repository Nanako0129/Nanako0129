#!/bin/sh
# Local half of the README sync: refreshes the usage panel from tokscale, which
# CI cannot see, and pushes. Run by launchd (see com.nanako.readme-sync.plist).
set -e
cd "$(dirname "$0")/.."
git pull --rebase --quiet
python3 scripts/update_readme.py
git add -A
git diff --cached --quiet || {
  git commit -q -m "chore(readme): local usage sync"
  git push -q
}

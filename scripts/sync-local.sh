#!/bin/sh
# Local half of the README sync: refreshes the usage panel from tokscale, which
# CI cannot see, and pushes. Run by launchd (see com.nanako.readme-sync.plist).
set -e
cd "$(dirname "$0")/.."
# launchd hands over PATH=/usr/bin:/bin:/usr/sbin:/sbin, which has neither gh nor
# tokscale. Without this the run succeeds and silently changes nothing, because
# every renderer treats a missing tool as "leave that block alone".
PATH="/opt/homebrew/bin:$HOME/.bun/bin:$PATH"
export PATH
# BIRTH_DATE lives here, outside the repo, so it is never committed. CI gets the
# same value from the BIRTH_DATE repository secret. Without it the Uptime row is
# omitted, which would make the two environments disagree — keep both supplied.
[ -f "$HOME/.config/nanako-readme.env" ] && . "$HOME/.config/nanako-readme.env"
git pull --rebase --quiet
python3 scripts/update_readme.py
git add -A
git diff --cached --quiet || {
  git commit -q -m "chore(readme): local usage sync"
  git push -q
}

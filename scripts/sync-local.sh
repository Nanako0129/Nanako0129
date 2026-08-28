#!/bin/sh
# Local README sync (launchd — see com.nanako.readme-sync.plist).
#
# Two halves, deliberately independent so one path dying does not kill the other:
#   1. workflow_dispatch → same job as the GitHub schedule (HTTPS, no git SSH).
#      Forces the remote runner to refresh NEOFETCH / PROJECTS / NOW even when
#      schedule is late or git://github.com is unreachable from this Mac.
#   2. local update_readme.py + push → same blocks via `gh`, plus USAGE from
#      tokscale (CI has no tokscale, so only this half can fill that panel).
set -e
cd "$(dirname "$0")/.."
# launchd hands over PATH=/usr/bin:/bin:/usr/sbin:/sbin, which has neither gh nor
# tokscale. Without this the run succeeds and silently changes nothing, because
# every renderer treats a missing tool as "leave that block alone".
PATH="/opt/homebrew/bin:$HOME/.bun/bin:$PATH"
export PATH
# Secrets / LAN endpoints live here, outside the repo, so they are never
# committed. CI gets BIRTH_DATE from a repository secret. HOMELAB_SSH (user@host
# for the Proxmox uptime probe) is Mac-only and must not appear in git.
[ -f "$HOME/.config/nanako-readme.env" ] && . "$HOME/.config/nanako-readme.env"
# Every renderer treats a missing input as "leave that block alone", which is
# right for CI and silent everywhere else: HOMELAB_SSH was set in that file but
# never exported, so the Proxmox probe saw nothing and the README kept copying
# the same uptime forward for 19 days without one line of complaint. The
# fallback stays; what it lacked was a way to notice it had engaged.
for v in HOMELAB_SSH HA_URL HA_TOKEN CF_API_TOKEN CF_ACCOUNT_ID; do
  eval "[ -n \"\$$v\" ]" || echo "sync-local: $v unset (must be exported); that homelab number will keep its last value" >&2
done

# A rebase already in flight is a human's, not ours: this script is the only
# other writer here and it never leaves one behind (see pull_rebase). Touching
# it would throw away a conflict resolution someone is in the middle of, so
# stop instead — the sync is six hours from running again.
git_dir=$(git rev-parse --git-dir)
if [ -d "$git_dir/rebase-merge" ] || [ -d "$git_dir/rebase-apply" ]; then
  echo "sync-local: a rebase is already in progress; leaving the repo alone" >&2
  exit 1
fi

# `git pull --rebase` does not clean up after itself when it conflicts: it stops
# on a detached HEAD with conflict markers in README.md, and `set -e` then kills
# this script mid-surgery. The repo stays that way until someone opens it by
# hand — which, running --quiet under launchd, is how a broken tree sat there
# unnoticed. Nothing in the conflict is worth resolving here: every block this
# script writes is derived data that the next run regenerates. So abort, keep
# whatever commits are already local, and fail loudly.
pull_rebase() {
  git pull --rebase --quiet && return 0
  git rebase --abort 2>/dev/null || true
  echo "sync-local: pull --rebase conflicted; aborted, tree left clean at HEAD" >&2
  return 1
}

# --- 1. Force the remote CI job (same workflow the cron would run) ---
# schedule is best-effort; workflow_dispatch is on-demand. Failure here must not
# skip the local half — and the other way around — so each step is soft-failed
# only where independence matters.
dispatch_ok=0
if command -v gh >/dev/null 2>&1; then
  if gh workflow run readme.yml; then
    dispatch_ok=1
  else
    echo "sync-local: gh workflow run readme.yml failed" >&2
  fi
else
  echo "sync-local: gh not on PATH; skipped workflow_dispatch" >&2
fi

# --- 2. Local half (usage panel + same API blocks + push as bot) ---
pull_rebase
python3 scripts/update_readme.py
git add -A
git diff --cached --quiet || {
  # Commit as the bot, not as me. GitHub credits the contribution graph by the
  # commit author's email, so four automated commits a day under my own address
  # would fill the graph with a cron job's work. Scoped with -c rather than
  # written into the repo config, so commits I actually make stay mine.
  git -c user.name="github-actions[bot]" \
      -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
      commit -q -m "chore(readme): local usage sync"
  if ! git push -q; then
    # The dispatched workflow may have pushed after our initial pull. If that
    # rebase conflicts, pull_rebase aborts it and this exits non-zero with the
    # commit still sitting in the local branch, ready for the next run.
    pull_rebase
    git push -q
  fi
}

# Non-zero only if the remote force failed *and* we never got a local commit
# path that at least ran the script successfully. Local pull/push errors still
# abort earlier via set -e (expected: fix SSH / network).
if [ "$dispatch_ok" -ne 1 ]; then
  echo "sync-local: remote workflow_dispatch did not succeed (local half ran)" >&2
fi


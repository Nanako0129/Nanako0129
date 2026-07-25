#!/usr/bin/env python3
"""Regenerate the auto-updated blocks in README.md.

Runs in two places with the same code:
  - GitHub Actions (daily)   -> fills NEOFETCH / PROJECTS / NOW from the GitHub API
  - the Mac (launchd, daily) -> additionally fills USAGE from local `tokscale`

Blocks it does not have data for are left untouched, so a CI run never wipes
the usage panel and a local run never needs network beyond `gh`.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

USER = "Nanako0129"
FEATURED = [
    ("pilotfish", "Multi-model orchestration for Claude Code"),
    ("coralline", "Powerlevel10k-inspired statusline for Claude Code"),
    ("TokenBar", "Native macOS menu-bar monitor for AI token usage"),
    ("remora-cc", "Session-scoped GPT-5.6 agent routing"),
    ("SocksBypass", "SOCKS5 proxy for iOS, built to defeat tethering limits"),
    ("postmortem-prose", "zh-TW tech longform in a postmortem voice"),
]
BAR_WIDTH = 22

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


def gh(path):
    if not shutil.which("gh"):
        return None
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def replace_block(text, name, body):
    pat = re.compile(rf"<!-- {name}:START -->.*?<!-- {name}:END -->", re.S)
    new, n = pat.subn(lambda _: f"<!-- {name}:START -->\n{body}\n<!-- {name}:END -->", text)
    if n != 1:
        sys.exit(f"marker {name} not found in README.md")
    return new


def human(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def ago(iso):
    d = (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if d == 0:
        return "today"
    if d < 30:
        return f"{d}d ago"
    return f"{d//30}mo ago"


def bar(frac):
    filled = round(frac * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def render_projects():
    rows = []
    for name, blurb in FEATURED:
        repo = gh(f"repos/{USER}/{name}")
        if not repo:
            continue
        releases = gh(f"repos/{USER}/{name}/releases?per_page=100") or []
        dl = sum(a["download_count"] for r in releases for a in r.get("assets", []))
        tag = releases[0]["tag_name"] if releases else "—"
        rows.append(
            f"| **[{name}](https://github.com/{USER}/{name})** | {blurb} | "
            f"★ {repo['stargazers_count']} | `{tag}` | "
            f"{human(dl) if dl else '—'} | {ago(repo['pushed_at'])} |"
        )
    if not rows:
        return None
    head = (
        "| Project | What it is | Stars | Latest | Downloads | Updated |\n"
        "| :-- | :-- | --: | :-- | --: | :-- |"
    )
    return head + "\n" + "\n".join(rows)


def render_now():
    events = gh(f"users/{USER}/events/public?per_page=100") or []
    lines = []
    for e in events:
        repo = e["repo"]["name"].split("/")[-1]
        if e["type"] == "PushEvent":
            commits = e["payload"].get("commits") or []
            if not commits:
                continue
            msg = commits[-1]["message"].splitlines()[0]
        elif e["type"] == "ReleaseEvent":
            msg = f"released {e['payload']['release']['tag_name']}"
        else:
            continue
        date = e["created_at"][:10]
        lines.append(f"{date}  {repo:<18.18}  {msg[:58]}")
        if len(lines) == 5:
            break
    return "```console\n" + "\n".join(lines) + "\n```" if lines else None


def render_usage():
    """Weekly token usage per client. Local-only: CI has no tokscale, so on a CI
    run this returns None and the block keeps whatever the Mac last pushed.
    Only the aggregate lands in the README — the raw export (which carries
    per-model cost) never leaves the machine."""
    if not shutil.which("tokscale"):
        return None
    r = subprocess.run(
        ["tokscale", "models", "--json", "--week", "--group-by", "client,model", "--no-spinner"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    data = json.loads(r.stdout)

    by_client = {}
    for e in data["entries"]:
        tok = e["input"] + e["output"] + e["cacheRead"] + e["cacheWrite"]
        by_client[e["client"]] = by_client.get(e["client"], 0) + tok
    top = sorted(by_client.items(), key=lambda kv: -kv[1])[:6]
    total = sum(by_client.values()) or 1

    lines = [f"last 7 days · {total/1e9:.1f}B tokens · {data['totalMessages']:,} messages", ""]
    for client, tok in top:
        lines.append(f"  {client:<10}  {bar(tok/total)}  {tok/total*100:4.1f}%  {tok/1e6:>7.0f}M")
    return "```console\n" + "\n".join(lines) + "\n```"


JOINED = "2018-11-04"

# Never hardcoded: a full date of birth is an identity-verification field, and
# this repository is public. CI reads it from the BIRTH_DATE secret, the Mac
# from ~/.config/nanako-readme.env (outside the repo, see scripts/sync-local.sh).
# Without it the Uptime row is simply left out — both environments have the
# value, so the rendered page does not flip back and forth.
BIRTH = os.environ.get("BIRTH_DATE")

# Traced from the reference plush photo: luminance mapped onto a density ramp,
# background speckle floored to spaces. Deliberately ASCII and nothing else.
# An earlier braille version looked better but had to sit above the info block
# rather than beside it: braille renders at one cell in GitHub's code font and
# about 1.1 in some editors, and whole spaces cannot pay a fractional cell, so
# the two columns could never agree. ASCII is exactly one cell everywhere,
# which is what buys back the side-by-side neofetch layout. cell_width() fails
# the build if anything wider sneaks in.
CAT = r"""
       J@8m]            .X*Bb
      >$@$$$p(|uzUJUzx)Y%$$@$t
      u@W#o*WBBBBBBBBB%Woa*W@C
     'dM*MW&8&WW&&&&&&888W*o#b
    n%8&&&W&&%%%%%%%%B88888&&&&t
   /%oo#8vjO)m@BBBB%B%zfm(ZB#**%[
   dMah*8WW88%BBBB%BBB888W&8aaoWZ
   vB*Wh#%8%%%%%%%%%%%%%8%%h*MaBf
    nWoo%88%%%%%%%%%%8%%888&kMBu
     ;#WW&&&88888888888&&8&&&M8d
     f8&%%%%%%%%888%%%%%BBBBBW@W
     :&&8%%%88&%$@@B8%%%%%8W&Wh!
      x$$$$@BB$@$$$$$$$@@@$$p!
       ;YbMWWoL<;><!jd*MMaO(
""".strip("\n").splitlines()


FRAME = "─│╭╮╰╯"


def cell_width(s):
    """Frame padding assumes one rendered column per character.

    ASCII is the only thing that reliably holds to that across every font a
    reader might have. CJK ragged the border on github.com by falling back to a
    proportional face; braille was fine there but ran about 1.1 cells wide in an
    editor, and a fractional cell cannot be paid for with whole spaces. Since
    the art now shares a line with the info column, anything but ASCII breaks
    the layout somewhere — so fail the build instead. Chinese belongs in the
    prose below, which needs no alignment at all.
    """
    bad = [c for c in s if not (c.isascii() or c in FRAME)]
    if bad:
        sys.exit(f"non-monospace glyph in the neofetch block: {bad!r} in {s!r}")
    return len(s)


def render_neofetch():
    all_repos = gh(f"users/{USER}/repos?per_page=100&type=owner") or []
    sources = [r for r in all_repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in sources)
    if not stars:
        return None

    now = datetime.now(timezone.utc).date()
    title = "nanako@taiwan"

    uptime = []
    if BIRTH:
        born = datetime.fromisoformat(BIRTH).date()
        age = now.year - born.year - ((now.month, now.day) < (born.month, born.day))
        uptime = [f"Uptime: {age} years"]

    info = [
        title,
        "─" * len(title),
        "Name: Nanako, or Nyanako",
        "Pronouns: she / her",
        "OS: macOS 26.5.2 arm64",
        "Host: MacBook Air (M5, 2026), 32GB / 1TB",
        "Kernel: SRE, platform & DevSecOps",
        *uptime,
        f"Install Date: {JOINED} (github.com)",
        f"Packages: {len(sources)} sources (git), {stars:,} stars",
        "Shell: zsh + powerlevel10k",
        "DE: coralline (Claude Code statusline)",
        "Homelab: Proxmox, 182d up, 0 open ports",
        "CPU: Rust, Swift, Python, Ansible, K8s",
        "Locale: zh_TW.UTF-8 (English via translator)",
        "",
        "Now: no roadmap. What I ship, I maintain.",
    ]

    gutter = max(len(line) for line in CAT) + 3
    body = []
    for i in range(max(len(CAT), len(info)) + 2):
        art = CAT[i - 1] if 0 < i <= len(CAT) else ""
        text = info[i - 2] if 1 < i <= len(info) + 1 else ""
        body.append(art.ljust(gutter) + text)

    inner = max(cell_width(line) for line in body) + 2
    head = f"╭─ {title} " + "─" * (inner - cell_width(title) - 3) + "╮"
    out = [head]
    out += [f"│ {line}" + " " * (inner - cell_width(line) - 1) + "│" for line in body]
    out.append("╰" + "─" * inner + "╯")
    return "```console\n" + "\n".join(out) + "\n```"


def main():
    text = README.read_text()
    for name, body in (
        ("NEOFETCH", render_neofetch()),
        ("PROJECTS", render_projects()),
        ("NOW", render_now()),
        ("USAGE", render_usage()),
    ):
        if body:
            text = replace_block(text, name, body)
    text = re.sub(
        r"(last sync: )[\d-]+", lambda m: m.group(1) + datetime.now(timezone.utc).strftime("%Y-%m-%d"), text
    )
    README.write_text(text)


if __name__ == "__main__":
    main()

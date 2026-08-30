#!/usr/bin/env python3
"""Regenerate the auto-updated blocks in README.md.

Runs in two places with the same code:
  - GitHub Actions (every 6h)   -> fills NEOFETCH / PROJECTS / NOW from the GitHub API
  - the Mac (launchd, every 6h) -> additionally fills USAGE from local `tokscale`
    and Proxmox uptime over LAN SSH (CI cannot reach the homelab)

Blocks it does not have data for are left untouched, so a CI run never wipes
the usage panel / last-known Proxmox uptime and a local run never needs
network beyond `gh` (plus optional LAN SSH for the homelab line).
"""

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = "Nanako0129"
# Which repos appear in the table, and how each is described. NOT the order:
# the heading above the table says --sort=stars, so render_projects() sorts by
# star count and this list only decides membership.
FEATURED = [
    ("pilotfish", "Multi-model orchestration for Claude Code"),
    ("coralline", "Powerlevel10k-inspired statusline for Claude Code"),
    ("TokenBar", "Native macOS menu-bar monitor for AI token usage"),
    ("sepia", "De-AI writing skill for coding agents"),
    ("remora-cc", "Session-scoped GPT-5.6 agent routing"),
    ("SocksBypass", "SOCKS5 proxy for iOS and Android, built to defeat tethering limits"),
    ("postmortem-prose", "zh-TW tech longform in a postmortem voice"),
]
BAR_WIDTH = 22

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


def gh(path, paginate=False):
    if not shutil.which("gh"):
        return None
    cmd = ["gh", "api"]
    if paginate:
        cmd.append("--paginate")
    cmd.append(path)
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


# download_count on a release asset is not an install. Sparkle (and the old
# updater) polls latest.json on every check; those hits are not people who
# fetched the app. TokenBar's badge already sums only installer archives
# (\.(tar.gz|dmg|zip|pkg)$) and drops the metadata. This table used to add
# every asset, so TokenBar's cell was the badge plus the feed traffic.
# checksums.txt is the same class. apk is included because SocksBypass ships
# one, and TokenBar's allow-list would zero it.
INSTALL_ASSET = re.compile(
    r"\.(tar\.gz|tgz|dmg|zip|pkg|apk|ipa|exe|msi|appimage|deb|rpm)$",
    re.I,
)


def installer_downloads(releases):
    return sum(
        a["download_count"]
        for r in releases
        for a in r.get("assets", [])
        if INSTALL_ASSET.search(a.get("name") or "")
    )


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
        releases = gh(f"repos/{USER}/{name}/releases?per_page=100", paginate=True) or []
        dl = installer_downloads(releases)
        tag = releases[0]["tag_name"] if releases else "—"
        rows.append((
            repo["stargazers_count"],
            f"| **[{name}](https://github.com/{USER}/{name})** | {blurb} | "
            f"★ {repo['stargazers_count']} | `{tag}` | "
            f"{human(dl) if dl else '—'} | {ago(repo['pushed_at'])} |",
        ))
    if not rows:
        return None
    rows.sort(key=lambda r: -r[0])
    head = (
        "| Project | What it is | Stars | Latest | Downloads | Updated |\n"
        "| :-- | :-- | --: | :-- | --: | :-- |"
    )
    return head + "\n" + "\n".join(row for _, row in rows)


def render_now():
    """Latest commits across the repos pushed to most recently.

    Not from /users/{user}/events/public: that endpoint no longer carries
    commit details at all — a PushEvent payload is down to before, head,
    push_id, ref and repository_id, with `commits` null — so anything wanting a
    commit message from it silently gets nothing. Asking each repository
    directly costs a handful of calls and actually returns messages.

    This repo is skipped. Its history is mostly the scheduled sync rewriting this
    very block, which would leave the section reporting on itself.
    """
    repos = gh(f"users/{USER}/repos?per_page=100&type=owner") or []
    active = [
        r["name"]
        for r in sorted(repos, key=lambda r: r["pushed_at"], reverse=True)
        if not r["fork"] and r["name"] != USER
    ][:6]

    commits = []
    for name in active:
        for c in gh(f"repos/{USER}/{name}/commits?per_page=8&author={USER}") or []:
            msg = c["commit"]["message"].splitlines()[0]
            if msg.startswith(("Merge pull request", "Merge branch", "Merge remote")):
                continue  # says who pressed the button, not what changed
            commits.append((c["commit"]["author"]["date"], name, msg))
    if not commits:
        return None

    commits.sort(reverse=True)
    lines = [f"{d[:10]}  {r:<18.18}  {m[:58]}" for d, r, m in commits[:5]]
    return "```console\n" + "\n".join(lines) + "\n```"


def render_usage():
    """Weekly token usage per model.

    Grouped by model, not by client, because the client says almost nothing
    here: Claude Code is wired to GPT models, so a "claude" row would be mostly
    OpenAI tokens. The model is the thing that is actually true.

    Local-only: CI has no tokscale, so there this returns None and the block
    keeps whatever the Mac last pushed. Only the aggregate lands in the README;
    the raw export, which carries per-model spend, never leaves the machine.
    """
    if not shutil.which("tokscale"):
        return None
    r = subprocess.run(
        ["tokscale", "models", "--json", "--week", "--group-by", "model", "--no-spinner"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    data = json.loads(r.stdout)

    by_model = {}
    for e in data["entries"]:
        tok = e["input"] + e["output"] + e["cacheRead"] + e["cacheWrite"]
        by_model[e["model"]] = by_model.get(e["model"], 0) + tok
    total = sum(by_model.values()) or 1
    top = sorted(by_model.items(), key=lambda kv: -kv[1])[:6]

    lines = [f"last 7 days · {total/1e9:.1f}B tokens · {data['totalMessages']:,} messages", ""]
    for model, tok in top:
        lines.append(f"  {model:<18.18}  {bar(tok/total)}  {tok/total*100:4.1f}%  {tok/1e6:>7.0f}M")
    return "```console\n" + "\n".join(lines) + "\n```"


JOINED = "2018-11-04"

# Never hardcoded: a full date of birth is an identity-verification field, and
# this repository is public. CI reads it from the BIRTH_DATE secret, the Mac
# from ~/.config/nanako-readme.env (outside the repo, see scripts/sync-local.sh).
# Without it the Uptime row is simply left out — both environments have the
# value, so the rendered page does not flip back and forth.
BIRTH = os.environ.get("BIRTH_DATE")


def fetch_proxmox_uptime_days():
    """Days since boot on the Proxmox host, via SSH to /proc/uptime.

    Local-only. Target comes only from HOMELAB_SSH (set in
    ~/.config/nanako-readme.env by sync-local.sh) — never hardcoded in the
    public repo. CI has no route to the LAN and no env, so this returns None
    and the caller keeps the last value already in README.md (same contract
    as USAGE / tokscale).
    """
    host = os.environ.get("HOMELAB_SSH")
    if not host or not shutil.which("ssh"):
        return None
    r = subprocess.run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=5",
            "-o",
            "StrictHostKeyChecking=accept-new",
            host,
            "cat /proc/uptime",
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return None
    try:
        seconds = float(r.stdout.split()[0])
    except (IndexError, ValueError):
        return None
    return int(seconds // 86400)


def http(url, headers, body=None, timeout=15):
    """Small GET/POST helper. Returns decoded text, or None on any failure.

    Every homelab reader below is best-effort by design: CI has no route to the
    LAN and no tokens, and a Mac run with the VPN down should leave the page
    alone rather than publish a zero. Callers turn None into "keep whatever
    README.md already says".
    """
    req = urllib.request.Request(
        url,
        data=body.encode() if body else None,
        headers=headers,
        method="POST" if body else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode()
    except (urllib.error.URLError, OSError, TimeoutError):
        return None


# One render pass returns both counts, so the 377-entity state dump is not
# downloaded merely to call len() on it.
HA_TEMPLATE = (
    "{{ states|count }}|"
    "{{ states|map(attribute='entity_id')|map('device_id')|reject('none')|unique|list|count }}"
)


def fetch_homeassistant_counts():
    """(integrations, entities, devices) from Home Assistant, or None.

    The three numbers were hand-typed and nobody wrote down what they counted,
    which is how 141/369/53 sat there while the instance moved on. Pinned here:

    integrations  top-level names in /api/config `components`. That list also
                  carries platform rows (cast.media_player, backup.sensor);
                  they are not integrations, so anything with a dot is dropped.
    entities      everything in the state machine.
    devices       distinct devices reachable from an entity. The device
                  registry is WebSocket-only — /api/config/device_registry/list
                  is a 404 — and one number on a profile page does not justify
                  hand-rolling an RFC 6455 client, so this counts device_id
                  across all entities via the template API instead. A device
                  with no entities at all would be missed; on this instance the
                  two definitions agree exactly (53).
    """
    url, token = os.environ.get("HA_URL"), os.environ.get("HA_TOKEN")
    if not url or not token:
        return None
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    cfg = http(f"{url.rstrip('/')}/api/config", auth)
    rendered = http(
        f"{url.rstrip('/')}/api/template", auth, json.dumps({"template": HA_TEMPLATE})
    )
    if not cfg or not rendered or "|" not in rendered:
        return None
    try:
        components = json.loads(cfg)["components"]
        entities, devices = (int(x) for x in rendered.split("|", 1))
    except (ValueError, KeyError, TypeError):
        return None
    return len([c for c in components if "." not in c]), entities, devices


def fetch_cloudflare_counts():
    """(tunnels, ztna_apps) from the Cloudflare API, or None.

    Same archaeology as above — both numbers turned out to be right, but only
    because they encoded a definition that lived nowhere:

    tunnels   healthy ones only. A down or inactive tunnel is a retired
              machine, not a route into the homelab, and counting it would
              overstate what is actually reachable.
    apps      Access applications minus app_launcher and warp. The launcher is
              the index page listing the others, warp is the device enrolment
              policy; neither is an application anyone opens.
    """
    token, account = os.environ.get("CF_API_TOKEN"), os.environ.get("CF_ACCOUNT_ID")
    if not token or not account:
        return None
    base = f"https://api.cloudflare.com/client/v4/accounts/{account}"
    auth = {"Authorization": f"Bearer {token}"}

    def result(path):
        raw = http(f"{base}/{path}", auth)
        if not raw:
            return None
        try:
            payload = json.loads(raw)
        except ValueError:
            return None
        return payload["result"] if payload.get("success") else None

    tunnels = result("cfd_tunnel?is_deleted=false&per_page=100")
    apps = result("access/apps?per_page=100")
    if tunnels is None or apps is None:
        return None
    return (
        sum(t.get("status") == "healthy" for t in tunnels),
        sum(a.get("type") not in ("app_launcher", "warp") for a in apps),
    )


def substitute(text, pattern, replacement, what):
    """Rewrite exactly one line, or fail the build.

    A silent no-op here is the failure mode that already cost 19 days of stale
    uptime: the renderer ran, matched nothing, wrote the file back unchanged
    and exited 0.
    """
    text, n = re.subn(pattern, replacement, text, count=1)
    if n != 1:
        sys.exit(f"{what}: no line matched {pattern!r} in README.md")
    return text


def resolve_os_line(readme_text):
    """The `OS:` row, read off the running Mac — or kept as-is.

    render_neofetch() also runs on the CI runner, where platform.mac_ver() is
    empty and platform.machine() answers x86_64, so deriving this
    unconditionally would let ubuntu overwrite the row with its own identity
    every six hours. Same contract as USAGE and the Proxmox uptime: only the
    environment that can actually observe a value may write it, everywhere
    else the last observed one stands. Matched up to the box border, since the
    row is padded out to the frame.
    """
    if sys.platform == "darwin":
        ver = platform.mac_ver()[0]
        if ver:
            return f"OS: macOS {ver} {platform.machine()}"
    m = re.search(r"(OS: \S[^│]*?)\s*│", readme_text)
    return m.group(1) if m else None


def resolve_proxmox_uptime_days(readme_text):
    """Live days from the host, else the last number already rendered."""
    live = fetch_proxmox_uptime_days()
    if live is not None:
        return live
    # Prefer the neofetch line; fall back to the homelab section.
    for pat in (
        r"Homelab: Proxmox, (\d+)d up",
        r"Proxmox VE\s+(\d+)d uptime",
    ):
        m = re.search(pat, readme_text)
        if m:
            return int(m.group(1))
    return None

# Traced from the reference plush photo. The silhouette comes from a flood fill
# of the white background, so light features *inside* the cat are kept rather
# than mistaken for background; each cell then takes the 82nd percentile of its
# pixels rather than the mean, which is what makes the eyes legible — they are
# bright yellow (luminance ~225) against near-black fur, and averaging buried
# them. The whiskers are the three `-` strokes on each cheek and they are drawn
# by hand: a few pixels of white stitching inside a 28-pixel cell cannot move
# that cell's statistic far enough to change a glyph, so no sampling parameter
# recovers them. Placed one column inside the silhouette on each side so the
# outline stays closed, and mirrored about column 21.5.
# Deliberately ASCII and nothing else.
# An earlier braille version looked better but had to sit above the info block
# rather than beside it: braille renders at one cell in GitHub's code font and
# about 1.1 in some editors, and whole spaces cannot pay a fractional cell, so
# the two columns could never agree. ASCII is exactly one cell everywhere,
# which is what buys back the side-by-side neofetch layout. cell_width() fails
# the build if anything wider sneaks in.
CAT = r"""
         w*aw                   kok
        m8BB8Mk              Za8BB%*
        *%B@@#akwwqpdbkkbqwmdh*@@@B&
        8%*ooo#MWWWWWWWWWWMM#oahaaB%Z
       Za*##MWWWWWW&&&&88&&&&WW#*oaaw
      q*MWWWW&&88888888888%8888&WMMMop
     oW&8WWM/M/)&%%%%%%%%%%*)&rC&888WMa
    h---*W&<>|<<(%B%%%%%%%8+<|+<(8W#---k
    #----M&&&88%%%%%%%%%%%%%%%8888M----*
    h---8bW&&&&888%%%%%%%%%888888*&8---h
     oW&fW&8&888888888888888888&&&oM8&o
      daM&&&888888888888888888888&&M#op
       h**MMW&&&&8&8&888&8&&&&&&WM#M&8M
      mhM8%%BB%%88&88&&&888%BBBBB%8%h8#
       dW88%%%88&&&8$$$$W8%88%%88&M*h&
       mM&8%BB%8&W&&$@$MW8BBB%B88&Mk
        b*&8%%%8%%8  $$BM&8888%88Ma
           M88%%%         &88%%8
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


def render_neofetch(proxmox_days=None, os_line=None):
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

    if proxmox_days is not None:
        homelab = f"Homelab: Proxmox, {proxmox_days}d up, 0 open ports"
    else:
        # No live read and nothing preserved — still true without a fake number.
        homelab = "Homelab: Proxmox, 0 open ports"

    info = [
        title,
        "─" * len(title),
        "Name: Nanako, or Nyanako",
        "Pronouns: she / her",
        *([os_line] if os_line else []),
        "Host: MacBook Air (M5, 2026), 32GB / 1TB",
        "Kernel: SRE, platform & DevSecOps",
        *uptime,
        f"Install Date: {JOINED} (github.com)",
        f"Packages: {len(sources)} sources (git), {stars:,} stars",
        "Shell: zsh + powerlevel10k",
        "DE: coralline (Claude Code statusline)",
        homelab,
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
    proxmox_days = resolve_proxmox_uptime_days(text)
    os_line = resolve_os_line(text)
    for name, body in (
        ("NEOFETCH", render_neofetch(proxmox_days, os_line)),
        ("PROJECTS", render_projects()),
        ("NOW", render_now()),
        ("USAGE", render_usage()),
    ):
        if body:
            text = replace_block(text, name, body)
    # The homelab panel stays prose in README.md and only its numbers are
    # rewritten here. Generating the whole block would drag the curated service
    # lists into this file, where they are harder to read and to edit.
    if proxmox_days is not None:
        text = substitute(
            text,
            r"(Proxmox VE\s+)\d+d uptime",
            rf"\g<1>{proxmox_days}d uptime",
            "Proxmox uptime",
        )
    ha = fetch_homeassistant_counts()
    if ha:
        text = substitute(
            text,
            r"(Home Assistant\s+)\d+ integrations · \d+ entities · \d+ devices",
            rf"\g<1>{ha[0]} integrations · {ha[1]} entities · {ha[2]} devices",
            "Home Assistant counts",
        )
    cf = fetch_cloudflare_counts()
    if cf:
        text = substitute(
            text,
            r"(Cloudflare Tunnel \+ Access · )\d+ tunnels · \d+ ZTNA apps",
            rf"\g<1>{cf[0]} tunnels · {cf[1]} ZTNA apps",
            "Cloudflare counts",
        )
    text = re.sub(
        r"(last sync: )[\d-]+", lambda m: m.group(1) + datetime.now(timezone.utc).strftime("%Y-%m-%d"), text
    )
    README.write_text(text)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render the README project-lineage diagram as a themed SVG.

GitHub strips <style> and style="" from README HTML, but not from an SVG it
shows as an image, so the layout and the light/dark palette live in here.
Edit NODES/EDGES and rerun; the output is committed, not built in CI.
"""
from html import escape
from pathlib import Path
import sys

# id: (name, sub, col, row, kind)   kind: flag | ext | gone | ""
NODES = {
    "ts":   ("tokscale", "junhoyeo · upstream", 0, 0, "ext"),
    "tc":   ("tokscale-core", "shared Rust core", 1, 0, ""),
    "sy":   ("Syrtis", "Swift shell, ex-TokenBar", 2, 1, "flag"),
    "tt":   ("TokenBar-Tauri", "Tauri 2 · retired", 1, 2, "gone"),
    "sa":   ("Syrtis-Agent", "remote usage contracts", 2, 0, ""),
    "sw":   ("Syrtis-Windows", "WinUI 3 shell", 3, 0, ""),
    "sf":   ("syrtis-film", "intro film, all code", 3, 1, ""),
    "ht":   ("homebrew-tap", "", 3, 2, ""),
    "hk":   ("homebrew-tokenbar", "archived", 2, 2, "gone"),

    "pf":   ("pilotfish", "orchestration layer", 0, 4.5, "flag"),
    "pg":   ("pilotfish-grok", "", 1, 3.5, ""),
    "pc":   ("pilotfish-codex", "", 1, 4.5, ""),
    "rm":   ("remora-cc", "GPT-5.6 agent routing", 1, 5.5, ""),
    "cc":   ("calico-claude", "after patch-claude-code", 2, 5.5, ""),
    "lz":   ("lorenzini", "PR-reviewer gates", 1, 6.5, ""),
    "sr":   ("stingray", "Stop hook for half-done", 1, 7.5, ""),

    "jv":   ("TypeSafe Jev", "System One · jev-1.13.0", 0, 8.5, "ext"),
    "nc":   ("NyanCogs", "Red Discord bot cogs", 0, 10, ""),
    "mw":   ("MessageWatch", "scam & hostility reports", 1, 8.5, ""),
    "cs":   ("ChannelSummary", "LLM channel summaries", 1, 9.5, ""),
    "ef":   ("EmbedFixer", "provider-fixed links", 1, 10.5, ""),
    "sp":   ("SpotifyPlaylist", "playlists in Audio", 1, 11.5, ""),
    "le":   ("Learning", "catch-up notes", 2, 9.5, ""),
    "cu":   ("computer-use-fast", "macOS GUI in 1-2 turns", 0, 11, ""),
    "sj":   ("shanjie", "Zhuyin IME · WIP", 0, 12, ""),

    "ss":   ("StoryScope", "Russell et al. · arXiv", 2, 7.5, "ext"),
    "se":   ("sepia", "de-AI writing", 3, 7.5, "flag"),
    "pp":   ("postmortem-prose", "zh-TW postmortem voice", 2, 8.5, ""),
    "md":   ("md-style", "", 3, 8.5, ""),
    "co":   ("coralline", "Claude Code statusline", 2, 10.5, "flag"),
    "sb":   ("SocksBypass", "SOCKS5 for iOS & Android", 3, 10.5, ""),
    "cr":   ("Cryptocentrus", "goal guardian · Codex", 2, 11.5, ""),
    "na":   ("nacre", "OpenWrt LuCI theme", 3, 11.5, ""),
    "st":   ("SyncTray", "menu-bar sync · upstream", 2, 12.5, "ext"),
    "li":   ("limpet", "rclone menu-bar mirror", 3, 12.5, ""),
}
EDGES = [
    ("ts", "tc"), ("tc", "sy"), ("tt", "sy"), ("sy", "sw"), ("sa", "sw"),
    ("sy", "ht"), ("hk", "ht"), ("sy", "sf"),
    ("pf", "pg"), ("pf", "pc"), ("pf", "rm"), ("rm", "cc"), ("pf", "lz"), ("pf", "sr"),
    ("jv", "lz"), ("jv", "sr"), ("jv", "mw"),
    ("nc", "mw"), ("nc", "cs"), ("nc", "ef"), ("nc", "sp"), ("cs", "le"),
    ("ss", "se"), ("pp", "md"), ("co", "na"), ("st", "li"),
]

W, H, COL, ROW, PAD = 184, 40, 214, 50, 12


def box(c, r):
    return PAD + c * COL, PAD + r * ROW


def render():
    cols = max(n[2] for n in NODES.values()) + 1
    rows = max(n[3] for n in NODES.values()) + 1
    width = PAD * 2 + (cols - 1) * COL + W
    height = PAD * 2 + (rows - 1) * ROW + H + 24
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height:g}" '
        f'viewBox="0 0 {width} {height:g}" role="img" aria-label="Project lineage">',
        """<style>
  text { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #1f2328; }
  .n rect { fill: #ffffff; stroke: #d0d7de; stroke-width: 1; }
  .n .s { font-size: 11px; fill: #59636e; }
  .n .t { font-size: 13px; font-weight: 600; }
  .flag rect { fill: #2f81f7; stroke: #2f81f7; }
  .flag text, .flag .s { fill: #ffffff; }
  .ext rect { stroke-dasharray: 4 3; stroke: #8c959f; }
  .gone { opacity: .55; }
  .e { fill: none; stroke: #8c959f; stroke-width: 1.2; }
  .ah { fill: #8c959f; }
  .lg { font-size: 11px; fill: #59636e; }
  @media (prefers-color-scheme: dark) {
    text { fill: #f0f6fc; }
    .n rect { fill: #151b23; stroke: #3d444d; }
    .n .s, .lg { fill: #9198a1; }
    .flag rect { fill: #2f81f7; stroke: #2f81f7; }
    .flag text, .flag .s { fill: #ffffff; }
    .ext rect { stroke: #656c76; }
    .e { stroke: #656c76; }
    .ah { fill: #656c76; }
  }
</style>
<defs><marker id="a" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
<path class="ah" d="M0,0 L8,4 L0,8 z"/></marker></defs>""",
    ]
    for s, t in EDGES:
        x1, y1 = box(NODES[s][2], NODES[s][3])
        x2, y2 = box(NODES[t][2], NODES[t][3])
        x1, y1, y2 = x1 + W, y1 + H / 2, y2 + H / 2
        xm = (x1 + x2) / 2
        out.append(f'<path class="e" marker-end="url(#a)" '
                   f'd="M{x1:g},{y1:g} C{xm:g},{y1:g} {xm:g},{y2:g} {x2 - 1:g},{y2:g}"/>')
    for name, sub, c, r, kind in NODES.values():
        x, y = box(c, r)
        ty = y + (16 if sub else 25)
        out.append(f'<g class="n {kind}"><rect x="{x}" y="{y:g}" width="{W}" height="{H}" rx="6"/>'
                   f'<text class="t" x="{x + 10}" y="{ty:g}">{escape(name)}</text>'
                   + (f'<text class="s" x="{x + 10}" y="{y + 32:g}">{escape(sub)}</text>' if sub else "")
                   + "</g>")
    out.append(f'<text class="lg" x="{PAD}" y="{height - 8:g}">'
               "filled = flagship · dashed = someone else's · faded = retired</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "assets" / "lineage.svg"
    out.write_text(render())

#!/usr/bin/env python3
"""Social preview for Nanako0129/Nanako0129: 1280x640, dark terminal window.

Run: python3 scripts/og_image.py  ->  assets/og.png

GitHub has no API for a repository's social preview, as far as anyone here has
checked, so the PNG is uploaded by hand: Settings > General > Social preview.
Styled after coralline's preview so the two read as a set. The cat and its
colours come from update_readme.py, so the image matches the README. There
are no live numbers in it, because the uploaded image never updates.
"""
import subprocess
import tempfile
from html import escape
from pathlib import Path

import update_readme as u

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = Path(__file__).resolve().parent.parent / "assets" / "og.png"

W, H = 1280, 640
BG, WIN, BD = "#010409", "#0d1117", "#30363d"
FG, MUTE = "#f0f6fc", "#9198a1"
ACC = u.ACCENT[1]

FLAGSHIPS = [
    ("Syrtis", "AI token usage in the macOS menu bar"),
    ("pilotfish", "multi-model orchestration for Claude Code"),
    ("coralline", "Powerlevel10k-style Claude Code statusline"),
    ("sepia", "de-AI writing skill for coding agents"),
]


def svg():
    fs, lh = 17, 23
    cw = fs * 0.61
    ax, ay = 70, 150
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f"""<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: {FG}; white-space: pre; }}
  .eye {{ fill: {u.EYE[1]}; font-weight: 700; }} .fur {{ fill: {u.FUR[1]}; }} .wh {{ fill: {u.WHISKER[1]}; }}
  .m {{ fill: {MUTE}; }} .a {{ fill: {ACC}; font-weight: 700; }}
</style>""",
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="14" fill="{WIN}" stroke="{BD}"/>',
        '<circle cx="52" cy="52" r="8" fill="#ff5f57"/><circle cx="78" cy="52" r="8" fill="#febc2e"/>'
        '<circle cx="104" cy="52" r="8" fill="#28c840"/>',
        f'<text class="m" x="{W / 2}" y="58" text-anchor="middle" font-size="18">nanako@taiwan — ~</text>',
        f'<line x1="20" y1="84" x2="{W - 20}" y2="84" stroke="{BD}"/>',
    ]
    for i, line in enumerate(u.CAT):
        out.append(f'<text x="{ax}" y="{ay + i * lh}" font-size="{fs}" xml:space="preserve">{u._cat_row(line)}</text>')
    tx = ax + max(len(l) for l in u.CAT) * cw + 60
    out += [
        f'<text x="{tx:g}" y="190" font-size="58" font-weight="700">Nanako</text>',
        f'<text class="m" x="{tx:g}" y="232" font-size="22">SRE · Taiwan · github.com/Nanako0129</text>',
        f'<text x="{tx:g}" y="296" font-size="24">UX has frontend engineers. <tspan class="a">DX has SRE.</tspan></text>',
    ]
    for i, (name, blurb) in enumerate(FLAGSHIPS):
        y = 370 + i * 48
        out.append(f'<text x="{tx:g}" y="{y}" font-size="22"><tspan class="a">{escape(name)}</tspan></text>')
        out.append(f'<text class="m" x="{tx + 150:g}" y="{y}" font-size="19">{escape(blurb)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "og.html"
        (Path(d) / "og.svg").write_text(svg())
        page.write_text('<html><body style="margin:0"><img src="og.svg"></body></html>')
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={W},{H}", f"--screenshot={OUT}", page.as_uri()],
                       check=True, capture_output=True)
    print(OUT)

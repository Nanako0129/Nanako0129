#!/usr/bin/env python3
"""Self-check for the two-environment branches. Run: python3 scripts/test_update_readme.py

Only covers what running the real script on the Mac cannot show: the CI path.
Everything else is observable by just running update_readme.py and reading the
diff, and a test that repeats that would only be a second place to update.
"""

import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_readme as u  # noqa: E402

BOX = "│     h---8bW&&&&888*&8---h   OS: macOS 26.5.2 arm64                       │"


def test_os_line():
    # On the Mac: derived from the running system, not from the file.
    with mock.patch.object(sys, "platform", "darwin"), \
         mock.patch.object(u.platform, "mac_ver", return_value=("15.9.9", "", "")), \
         mock.patch.object(u.platform, "machine", return_value="arm64"):
        assert u.resolve_os_line(BOX) == "OS: macOS 15.9.9 arm64"

    # On the CI runner: the row already in README.md wins. The failure this
    # guards is not an exception, it is ubuntu quietly publishing "OS: Linux"
    # to a public page four times a day.
    with mock.patch.object(sys, "platform", "linux"), \
         mock.patch.object(u.platform, "mac_ver", return_value=("", "", "")), \
         mock.patch.object(u.platform, "machine", return_value="x86_64"):
        assert u.resolve_os_line(BOX) == "OS: macOS 26.5.2 arm64"

    # Padding must not survive into the row, or every CI run re-widens the box.
    assert not u.resolve_os_line(BOX).endswith(" ")


def test_readme_row_is_matchable():
    # The regex reads the live README, so a layout change that breaks it has to
    # fail here rather than silently drop the row out of the neofetch block.
    text = (Path(__file__).resolve().parent.parent / "README.md").read_text()
    with mock.patch.object(sys, "platform", "linux"), \
         mock.patch.object(u.platform, "mac_ver", return_value=("", "", "")):
        assert (u.resolve_os_line(text) or "").startswith("OS: macOS")


def test_homelab_readers_stay_out_of_ci():
    # No tokens means no opinion. The failure being guarded is a CI run
    # publishing "0 tunnels · 0 ZTNA apps" over numbers it cannot see.
    with mock.patch.dict("os.environ", {}, clear=True):
        assert u.fetch_homeassistant_counts() is None
        assert u.fetch_cloudflare_counts() is None


def test_installer_downloads_drop_updater_metadata():
    # The failure this guards is TokenBar's latest.json (Sparkle poll traffic)
    # inflating the table to look like GitHub's raw download total. checksums
    # are the same class; an .apk is a real artefact and has to survive.
    releases = [
        {
            "assets": [
                {"name": "TokenBar.app.tar.gz", "download_count": 3980},
                {"name": "latest.json", "download_count": 2321},
            ]
        },
        {"assets": [{"name": "TokenBar-Beta.app.tar.gz", "download_count": 43}]},
        {
            "assets": [
                {"name": "remora-cc-0.1.22.tar.gz", "download_count": 5},
                {"name": "checksums.txt", "download_count": 61},
            ]
        },
        {"assets": [{"name": "app-debug.apk", "download_count": 30}]},
        {"assets": []},
        {},
    ]
    assert u.installer_downloads(releases) == 3980 + 43 + 5 + 30


def test_homelab_patterns_still_match():
    # substitute() exits non-zero on a miss, but only on a run that reached the
    # API. Reword the panel and this fails now instead of at 05:30.
    import re

    text = (Path(__file__).resolve().parent.parent / "README.md").read_text()
    for pattern in (
        r"(Home Assistant\s+)\d+ integrations · \d+ entities · \d+ devices",
        r"(Cloudflare Tunnel \+ Access · )\d+ tunnels · \d+ ZTNA apps",
        r"(Proxmox VE\s+)\d+d uptime",
    ):
        assert len(re.findall(pattern, text)) == 1, pattern


if __name__ == "__main__":
    test_os_line()
    test_readme_row_is_matchable()
    test_homelab_readers_stay_out_of_ci()
    test_installer_downloads_drop_updater_metadata()
    test_homelab_patterns_still_match()
    print("ok")

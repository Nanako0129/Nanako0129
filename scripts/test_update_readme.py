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
_README = (Path(__file__).resolve().parent.parent / "README.md").read_text()


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


def test_blurb_drift_is_reported_not_repaired():
    # The failure this guards is the one that actually happened: SocksBypass
    # shipped an Android client, its GitHub description said so, and the blurb
    # went on saying "for iOS" because nothing compared the two.
    repos = {
        "repos/Nanako0129/only": {
            "description": "now mentions Android",
            "stargazers_count": 1,
            "pushed_at": "2026-08-31T00:00:00Z",
        }
    }
    featured = [("only", "a blurb about iOS", "was iOS only")]
    with mock.patch.object(u, "FEATURED", featured), \
         mock.patch.object(u, "gh", lambda p, paginate=False: repos.get(p, [])):
        body, drift = u.render_projects()
    assert len(drift) == 1, drift
    # The report has to carry all three strings, or it cannot be acted on.
    assert "a blurb about iOS" in drift[0]
    assert "was iOS only" in drift[0]
    assert "now mentions Android" in drift[0]
    # And the table is still rendered: drift never blocks the page.
    assert "a blurb about iOS" in body

    # Matching description, no report — the common case must stay silent.
    featured = [("only", "a blurb about iOS", "now mentions Android")]
    with mock.patch.object(u, "FEATURED", featured), \
         mock.patch.object(u, "gh", lambda p, paginate=False: repos.get(p, [])):
        _, drift = u.render_projects()
    assert drift == [], drift


def test_cadence_reads_both_real_schedules():
    # Not a fixture: the live workflow and plist. If either schedule is edited
    # into a shape these parsers cannot read, that surfaces here rather than as
    # a silently unchecked claim at 05:30.
    ci, agent = u.ci_interval_hours(), u.agent_interval_hours()
    assert ci == agent, f"CI every {ci}h vs launchd every {agent}h"
    assert ci in u.NUMBER_WORDS, ci
    # Both cron spellings must give the same answer, or swapping one for the
    # other would raise a false alarm on a legitimate edit.
    for cron, expected in (("23 2,8,14,20 * * *", 6), ("23 */6 * * *", 6), ("0 * * * *", 1)):
        assert u.ci_interval_hours(f'    - cron: "{cron}"\n') == expected, cron
    # An unparseable schedule must return None, so cadence_report says the claim
    # is unchecked instead of quietly passing it.
    assert u.ci_interval_hours("no cron here") is None
    assert u.agent_interval_hours("<plist></plist>") is None


def _plist(entries):
    body = "".join(
        f"<dict><key>Hour</key><integer>{h}</integer>"
        f"<key>Minute</key><integer>{m}</integer></dict>"
        for h, m in entries
    )
    return (
        '<?xml version="1.0"?><plist version="1.0"><dict>'
        f"<key>StartCalendarInterval</key><array>{body}</array></dict></plist>"
    )


def test_launchd_minutes_are_part_of_the_schedule():
    # 05:30, 11:00, 17:30, 23:30 has evenly spaced *hours* and gaps of 5h30,
    # 6h30, 6h, 6h. Reading only <key>Hour</key> certified it as six-hourly.
    assert u.agent_interval_hours(_plist([(5, 30), (11, 30), (17, 30), (23, 30)])) == 6
    assert u.agent_interval_hours(_plist([(5, 30), (11, 0), (17, 30), (23, 30)])) is None
    # A Minute of 0 may be omitted entirely, and a lone entry is daily.
    assert u.agent_interval_hours(_plist([(0, 0), (12, 0)])) == 12
    assert u.agent_interval_hours(_plist([(9, 0)])) == 24
    assert u.agent_interval_hours("<plist></plist>") is None
    assert u.agent_interval_hours("not a plist at all") is None


def test_launchd_calendar_restrictions_are_unchecked():
    # A StartCalendarInterval entry may carry Weekday, Day or Month. Weekday=1
    # makes these four entries a Monday-only schedule while their hours go on
    # reading as six-hourly — the launchd mirror of the day-restricted cron, and
    # refused the same way rather than approximated.
    def with_key(key, value):
        return _plist([(5, 30), (11, 30), (17, 30), (23, 30)]).replace(
            "<key>Hour</key><integer>5</integer>",
            f"<key>{key}</key><integer>{value}</integer><key>Hour</key><integer>5</integer>",
            1,
        )

    assert u.agent_interval_hours(with_key("Weekday", 1)) is None
    assert u.agent_interval_hours(with_key("Day", 1)) is None
    assert u.agent_interval_hours(with_key("Month", 6)) is None
    # An entry with no Hour is hourly to launchd; unmeasured here, so unchecked.
    assert u.agent_interval_hours(
        '<?xml version="1.0"?><plist version="1.0"><dict>'
        "<key>StartCalendarInterval</key><array>"
        "<dict><key>Minute</key><integer>30</integer></dict>"
        "</array></dict></plist>"
    ) is None
    # The unrestricted schedule is still read.
    assert u.agent_interval_hours(_plist([(5, 30), (11, 30), (17, 30), (23, 30)])) == 6


def test_every_cron_trigger_counts():
    # A workflow may carry several schedules; their union is the real one.
    six = '    - cron: "23 2,8,14,20 * * *"\n'
    assert u.ci_interval_hours(six) == 6
    # Adding a lone daily trigger makes the real gaps uneven. Reading only the
    # first entry went on answering 6.
    assert u.ci_interval_hours(six + '    - cron: "23 5 * * *"\n') is None
    # Two triggers that together are six-hourly must still read as six-hourly.
    assert u.ci_interval_hours('    - cron: "0 0,12 * * *"\n    - cron: "0 6,18 * * *"\n') == 6
    # The minute field is part of the time: 00:00 and 00:30 are not 12h apart.
    assert u.ci_interval_hours('    - cron: "0,30 */12 * * *"\n') is None
    # One unreadable entry makes the whole schedule unchecked, not partly checked.
    assert u.ci_interval_hours(six + '    - cron: "23 JAN * * *"\n') is None


def test_a_wrapped_claim_is_still_a_claim():
    """Reflowing prose must not change what the check sees.

    Both directions failed before: with every claim wrapped the run reported
    correct prose as missing, and with one claim wrapped and wrong it read
    straight past it. The README wraps near ninety columns and the usage
    sentence sits in a blockquote, so this is an ordinary edit, not an exotic one.
    """
    quote = "> Real usage, pushed here every six hours by a cron job on my Mac."
    assert quote in _README

    # Wrapped inside a blockquote — the continuation line starts with "> ".
    wrapped = _README.replace(
        quote, "> Real usage, pushed here every six\n> hours by a cron job on my Mac."
    )
    assert u.cadence_report(wrapped) == []
    # Wrapped and wrong is still caught.
    bad = _README.replace(
        quote, "> Real usage, pushed here every three\n> hours by a cron job on my Mac."
    )
    assert "'every three hours'" in u.cadence_report(bad)[0], u.cadence_report(bad)

    # Every claim wrapped at once: the backstop must not fire on true prose.
    every = wrapped.replace(
        "Most of this page rebuilds itself every six hours:",
        "Most of this page rebuilds itself every six\n  │  hours:",
    ).replace(
        "This page rebuilds itself every six hours ·",
        "This page rebuilds itself every six\nhours ·",
    )
    assert u.cadence_report(every) == []

    # A blank line is a paragraph break, not a wrap, and flatten must not join
    # across one — otherwise two unrelated paragraphs could be spliced into a
    # phrase neither of them contains.
    assert u.flatten("pushed here every six\n> hours by a cron job") == (
        "pushed here every six hours by a cron job"
    )
    assert "\n" not in u.flatten("a\n  │  b  │\n> c")


def test_both_schedulers_refuse_the_same_things():
    """The two parsers are one contract in two implementations.

    Three of the review findings on this work were the same defect discovered
    once per side: the minute ignored, then the day fields ignored, then the
    launchd calendar keys ignored. Each was fixed where it was found. This
    asserts the symmetry directly, so the next gap fails here instead of being
    found a fourth time.
    """
    def cron(expr):
        return u.ci_interval_hours(f'    - cron: "{expr}"\n')

    def agent(entry_xml):
        return u.agent_interval_hours(
            '<?xml version="1.0"?><plist version="1.0"><dict>'
            f"<key>StartCalendarInterval</key><array>{entry_xml}</array></dict></plist>"
        )

    hhmm = "<key>Hour</key><integer>{}</integer><key>Minute</key><integer>{}</integer>"

    # Both accept the same real schedule and agree on it.
    assert cron("30 5,11,17,23 * * *") == 6
    assert agent("".join(f"<dict>{hhmm.format(h, 30)}</dict>" for h in (5, 11, 17, 23))) == 6

    # Both refuse an hour outside 0-23.
    assert cron("30 25 * * *") is None
    assert agent(f"<dict>{hhmm.format(25, 30)}</dict>") is None

    # Both refuse a minute outside 0-59.
    assert cron("90 5 * * *") is None
    assert agent(f"<dict>{hhmm.format(5, 90)}</dict>") is None
    # Four entries at :90 used to come back as a tidy six-hourly schedule.
    assert agent("".join(f"<dict>{hhmm.format(h, 90)}</dict>" for h in (5, 11, 17, 23))) is None

    # Both refuse a restriction that makes the schedule not-every-day.
    assert cron("30 5,11,17,23 * * 1-5") is None
    assert agent(
        "<dict><key>Weekday</key><integer>1</integer>"
        + hhmm.format(5, 30)
        + "</dict>"
    ) is None

    # Both refuse an uneven schedule rather than averaging it.
    assert cron("30 5,9,13,17 * * *") is None
    assert agent("".join(f"<dict>{hhmm.format(h, 30)}</dict>" for h in (5, 9, 13, 17))) is None


def test_the_workflow_comment_is_checked_too():
    # readme.yml states the cadence in words two lines from the cron. It was
    # left unscanned at first; it is free to include, since the file carries no
    # prose beyond its schedule comments.
    # Clean today: the live workflow agrees with the live schedule.
    assert u.cadence_report(_README) == []
    stale = u.WORKFLOW.read_text().replace("Every six hours", "Every three hours", 1)
    assert stale != u.WORKFLOW.read_text()
    with mock.patch.object(
        u, "_read", lambda p: stale if p is u.WORKFLOW else u.PLIST.read_text()
    ):
        report = u.cadence_report(_README)
    assert report and u.WORKFLOW.name in report[0], report


def test_day_restricted_cron_is_unchecked():
    # `23 2,8,14,20 * * 1-5` is six-hourly inside a weekday and 54 hours from
    # Friday 20:23 to Monday 02:23. An interval cannot describe it, so it must
    # not be given one. Same mistake as reading the hour and calling it the time.
    for expr in (
        "23 2,8,14,20 * * 1-5",   # weekdays only
        "23 2,8,14,20 1 * *",     # first of the month
        "23 2,8,14,20 * 6 *",     # June only
        "23 2,8,14,20 * *",       # too few fields
        "23 2,8,14,20 * * * *",   # too many
    ):
        assert u.ci_interval_hours(f'    - cron: "{expr}"\n') is None, expr
    assert u.ci_interval_hours('    - cron: "23 2,8,14,20 * * *"\n') == 6


def test_a_daily_schedule_may_be_called_daily():
    # If both schedulers move to once a day, "rebuilds daily" is true prose and
    # must not fail the run. cadence_phrases(24) used to accept only the
    # arithmetic spelling.
    assert u.ci_interval_hours('    - cron: "0 5 * * *"\n') == 24
    with mock.patch.object(u, "ci_interval_hours", lambda *a, **k: 24), \
         mock.patch.object(u, "agent_interval_hours", lambda *a, **k: 24), \
         mock.patch.object(u, "_read", lambda p: ""):
        assert u.cadence_report("This page rebuilds itself daily.") == []
        assert u.cadence_report("This page is regenerated every day.") == []
        assert u.cadence_report("This page rebuilds itself every six hours.")


def test_accepted_phrases_are_all_matchable():
    # cadence_phrases() and CADENCE_CLAIM are two statements of one contract.
    # If the accepted set grows a phrase the matcher cannot find, cadence_claims()
    # returns nothing for it and the backstop reports true prose as missing.
    for hours in (1, 2, 3, 4, 6, 8, 12, 24):
        for phrase in u.cadence_phrases(hours):
            assert u.CADENCE_CLAIM.fullmatch(phrase), (hours, phrase)


def test_generated_blocks_are_not_prose():
    # render_now() copies commit subjects out of other repositories verbatim.
    # Someone else committing "daily backup schedule" must not fail this sync.
    polluted = _README.replace(
        "<!-- NOW:START -->",
        "<!-- NOW:START -->\n2026-08-31  otherrepo  chore: daily backup schedule",
        1,
    )
    assert u.cadence_report(polluted) == []
    # The hand-written half is still read.
    assert u.cadence_report(_README.replace("rebuilds itself every six hours",
                                            "rebuilds itself daily", 1))


def test_every_spelling_of_one_schedule_agrees():
    # A fresh reviewer found `0-23/6` answering 24 instead of 6, which would have
    # failed the run over a cron that was correct. Every spelling of six-hourly
    # must land on 6, or rewriting the cron becomes a trap.
    # Driven through the public entry point rather than the field parser, so the
    # test keeps holding when the internals move.
    def ci(hour_field):
        return u.ci_interval_hours(f'    - cron: "23 {hour_field} * * *"\n')

    for field in ("2,8,14,20", "*/6", "0-23/6", "2-20/6", "0-23/6,0-23/6"):
        assert ci(field) == 6, field
    for field, expected in (("*", 1), ("0-23", 1), ("0,12", 12), ("3", 24)):
        assert ci(field) == expected, field
    # Unrecognised shapes must be None — "unchecked" beats a confident wrong number.
    for field in ("*/0", "*/x", "JAN", "0-99", "20-2", "0/6"):
        assert ci(field) is None, field
    assert u.ci_interval_hours("no cron here at all") is None
    # Uneven schedules have no single interval and must not be given one. */7
    # fires four times a day, which naive arithmetic called "every six hours"
    # while the real gaps were 7,7,7,3.
    for field in ("*/7", "5-17/4", "1-3/2", "*/13", "1-5,9", "0,1"):
        assert ci(field) is None, field


def test_cadence_ignores_prose_that_is_not_about_rebuilding():
    # "daily driver" is not a claim about the schedule. A guard that fails the
    # run over it gets deleted rather than obeyed.
    for innocent in (
        "TokenBar is my daily driver.",
        "I read every one.\n\nA daily standup, nightly builds elsewhere.",
    ):
        assert u.cadence_report(_README + "\n\n" + innocent) == [], innocent
    # The numeric spelling of the true cadence is correct English and must pass.
    assert u.cadence_report(_README.replace("every six hours", "every 6 hours")) == []
    # But the same words inside a rebuild sentence still fail.
    assert u.cadence_report(_README + "\n\nThis page rebuilds itself daily.")


def test_unreadable_repo_is_reported_not_skipped():
    # Exiting 0 has to mean the blurbs were compared. A renamed or 404 repo used
    # to drop out silently, taking its blurb out of the check with it.
    live = {
        "repos/Nanako0129/ok": {
            "description": "d", "stargazers_count": 1, "pushed_at": "2026-08-31T00:00:00Z",
        }
    }
    featured = [("ok", "b", "d"), ("gone", "b", "d")]
    with mock.patch.object(u, "FEATURED", featured), \
         mock.patch.object(u, "gh", lambda p, paginate=False: live.get(p, [])):
        _, drift = u.render_projects()
    assert any("gone" in d and "not checked" in d for d in drift), drift

    # With no `gh` on the machine at all, nothing is readable *by design* and the
    # script must stay a silent no-op — CI without a token, a Mac mid-upgrade.
    with mock.patch.object(u, "FEATURED", featured), \
         mock.patch.object(u, "gh", lambda p, paginate=False: None), \
         mock.patch.object(u.shutil, "which", lambda _: None):
        body, drift = u.render_projects()
    assert body is None and drift == [], drift

    # But `gh` installed and answering for nothing is a different thing — an
    # expired token, a rate limit — and used to be indistinguishable from the
    # line above. It has to say so instead of exiting 0 as if all was checked.
    with mock.patch.object(u, "FEATURED", featured), \
         mock.patch.object(u, "gh", lambda p, paginate=False: None), \
         mock.patch.object(u.shutil, "which", lambda _: "/opt/homebrew/bin/gh"):
        body, drift = u.render_projects()
    assert body is None and any("not checked" in d for d in drift), drift


def test_cadence_catches_a_stale_claim():
    # "nightly" is the exact word that sat on the page for weeks, so the message
    # has to name it. Asserting merely that the report is non-empty let a mutant
    # that deleted \bnightly\b from the pattern survive: the run still failed,
    # but via the "no longer states how often it rebuilds" backstop instead.
    assert "'nightly'" in u.cadence_report("This page rebuilds itself nightly.")[0]
    assert "'every three hours'" in u.cadence_report("pushed here every three hours by cron")[0]
    # A reworded verb must not walk past the paragraph filter.
    assert "'nightly'" in u.cadence_report("This page is refreshed nightly.")[0]
    # The live README must agree with the live schedules.
    assert u.cadence_report(_README) == []


def test_cadence_notices_the_claim_disappearing_entirely():
    # The backstop had no test at all: deleting the whole branch passed the suite.
    # A page that stopped saying how often it rebuilds is not a page that passed.
    silent = _README.replace("every six hours", "on a schedule")
    report = u.cadence_report(silent)
    assert report and "no longer states" in report[0], report


if __name__ == "__main__":
    test_os_line()
    test_readme_row_is_matchable()
    test_homelab_readers_stay_out_of_ci()
    test_installer_downloads_drop_updater_metadata()
    test_homelab_patterns_still_match()
    test_blurb_drift_is_reported_not_repaired()
    test_cadence_reads_both_real_schedules()
    test_launchd_minutes_are_part_of_the_schedule()
    test_launchd_calendar_restrictions_are_unchecked()
    test_every_cron_trigger_counts()
    test_a_wrapped_claim_is_still_a_claim()
    test_both_schedulers_refuse_the_same_things()
    test_the_workflow_comment_is_checked_too()
    test_day_restricted_cron_is_unchecked()
    test_a_daily_schedule_may_be_called_daily()
    test_accepted_phrases_are_all_matchable()
    test_generated_blocks_are_not_prose()
    test_every_spelling_of_one_schedule_agrees()
    test_cadence_ignores_prose_that_is_not_about_rebuilding()
    test_unreadable_repo_is_reported_not_skipped()
    test_cadence_catches_a_stale_claim()
    test_cadence_notices_the_claim_disappearing_entirely()
    print("ok")

<!--
  ╭─ hey, you opened the raw file ─────────────────────────────╮
  │  Most of this page rebuilds itself every six hours:        │
  │  scripts/update_readme.py + .github/workflows/readme.yml   │
  │  The numbers below are not decoration. They are the build. │
  ╰────────────────────────────────────────────────────────────╯
-->

<!-- NEOFETCH:START -->
```console
╭─ nanako@taiwan ─────────────────────────────────────────────────────────────────────────╮
│                                                                                         │
│          w*aw                   kok                                                     │
│         m8BB8Mk              Za8BB%*       nanako@taiwan                                │
│         *%B@@#akwwqpdbkkbqwmdh*@@@B&       ─────────────                                │
│         8%*ooo#MWWWWWWWWWWMM#oahaaB%Z      Name: Nanako, or Nyanako                     │
│        Za*##MWWWWWW&&&&88&&&&WW#*oaaw      Pronouns: she / her                          │
│       q*MWWWW&&88888888888%8888&WMMMop     OS: macOS 27.0 arm64                         │
│      oW&8WWM/M/)&%%%%%%%%%%*)&rC&888WMa    Host: MacBook Air (M5, 2026), 32GB / 1TB     │
│     h---*W&<>|<<(%B%%%%%%%8+<|+<(8W#---k   Kernel: SRE, platform & DevSecOps            │
│     #----M&&&88%%%%%%%%%%%%%%%8888M----*   Uptime: 27 years                             │
│     h---8bW&&&&888%%%%%%%%%888888*&8---h   Install Date: 2018-11-04 (github.com)        │
│      oW&fW&8&888888888888888888&&&oM8&o    Packages: 31 sources (git), 4,682 stars      │
│       daM&&&888888888888888888888&&M#op    Shell: zsh + powerlevel10k                   │
│        h**MMW&&&&8&8&888&8&&&&&&WM#M&8M    DE: coralline (Claude Code statusline)       │
│       mhM8%%BB%%88&88&&&888%BBBBB%8%h8#    Homelab: Proxmox, 23d up, 0 open ports       │
│        dW88%%%88&&&8$$$$W8%88%%88&M*h&     CPU: Rust, Swift, Python, Ansible, K8s       │
│        mM&8%BB%8&W&&$@$MW8BBB%B88&Mk       Locale: zh_TW.UTF-8 (English via translator) │
│         b*&8%%%8%%8  $$BM&8888%88Ma                                                     │
│            M88%%%         &88%%8           Now: no roadmap. What I ship, I maintain.    │
│                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```
<!-- NEOFETCH:END -->

```console
~ ❯ cat about.md
```

Nanako (菜菜子), or Nyanako (喵菜子) if you know me from Discord. I'm an SRE. Keeping
systems reliable is the day job — the projects here are the same instinct pointed
somewhere else.

**UX has frontend engineers. DX has SRE.**

Every one of these started because I needed it. Syrtis (formerly TokenBar) exists
because I wanted to know what a session actually cost without opening a dashboard.
coralline exists because I've used Powerlevel10k in zsh for years and wanted the same
thing in my Claude Code statusline — I only packaged it up because people kept asking
how I'd done it.

I share it because sharing is the good part, and once it's public I maintain it properly.
What comes next is genuinely unknown — whatever I hit while learning, whatever annoys me
enough to open a new repo.

> The full story of the TokenBar rewrite (now Syrtis) — Rust core, Swift shell, and the
> FFI seam between them — is written up here (zh-TW):
> **[Rust 的引擎，Swift 的外殼](https://hackmd.io/@Nyanako0129/tokenbar-rust-swift-ffi-zh)**

```console
~ ❯ ls -l ~/projects --sort=stars
```

<!-- PROJECTS:START -->
| Project | What it is | Stars | Latest | Downloads | Updated |
| :-- | :-- | --: | :-- | --: | :-- |
| **[sepia](https://github.com/Nanako0129/sepia)** | De-AI writing skill for coding agents | ★ 2881 | `v0.12.2` | — | 3d ago |
| **[pilotfish](https://github.com/Nanako0129/pilotfish)** | Multi-model orchestration for Claude Code | ★ 698 | `v1.4.2` | — | 1d ago |
| **[coralline](https://github.com/Nanako0129/coralline)** | Powerlevel10k-inspired statusline for Claude Code | ★ 541 | `v0.18.1` | — | 2d ago |
| **[Syrtis](https://github.com/Nanako0129/Syrtis)** | Native macOS menu-bar monitor for AI token usage | ★ 375 | `v2.0.1` | 6.9k | today |
| **[SocksBypass](https://github.com/Nanako0129/SocksBypass)** | SOCKS5 proxy for iOS and Android, built to defeat tethering limits | ★ 79 | `—` | — | 20d ago |
| **[remora-cc](https://github.com/Nanako0129/remora-cc)** | Session-scoped GPT-5.6 agent routing | ★ 26 | `v0.1.23` | 70 | 8d ago |
| **[lorenzini](https://github.com/Nanako0129/lorenzini)** | PR-reviewer gates that decide whether a verdict means pass | ★ 17 | `v0.2.3` | — | 1d ago |
| **[postmortem-prose](https://github.com/Nanako0129/postmortem-prose)** | zh-TW tech longform in a postmortem voice | ★ 4 | `—` | — | 2mo ago |
<!-- PROJECTS:END -->

```console
~ ❯ tokscale models --week --group-by model
```

> Real usage, pushed here every six hours by a cron job on my Mac. The numbers come from
> [tokscale](https://github.com/junhoyeo/tokscale) — junhoyeo's Rust engine for reading
> agent session data, and the engine [Syrtis](https://github.com/Nanako0129/syrtis)
> runs on. I send fixes upstream when I trip over them; the Swift shell around it is my
> part. Grouped by model rather than by client, because the client would lie: I drive
> GPT models through Claude Code.

<!-- USAGE:START -->
```console
last 7 days · 8.5B tokens · 22,141 messages

  claude-opus-5-5     ████████████░░░░░░░░░░  52.5%     4450M
  claude-opus-5       ███████░░░░░░░░░░░░░░░  33.0%     2795M
  claude-sonnet-5     ██░░░░░░░░░░░░░░░░░░░░  11.4%      962M
  claude-fable-5-1    ░░░░░░░░░░░░░░░░░░░░░░   1.9%      165M
  grok-4.6            ░░░░░░░░░░░░░░░░░░░░░░   0.4%       37M
  gemini-3.8-flash    ░░░░░░░░░░░░░░░░░░░░░░   0.3%       29M
```
<!-- USAGE:END -->

```console
~ ❯ git log --oneline --author=nanako -5
```

<!-- NOW:START -->
```console
2026-09-27  syrtis              docs(verification): show --locked on the CI cargo commands
2026-09-27  syrtis              docs(verification): separate what --all-targets does in th
2026-09-27  syrtis              ci: run the Rust unit tests and Clippy wherever CI builds 
2026-09-27  syrtis              docs(release): the CI gate stops the release, not the tag
2026-09-27  syrtis              ci: refuse a release tag unless both CI runs are green
```
<!-- NOW:END -->

```console
~ ❯ tree ~/projects --lineage
```

<p align="center"><img src="assets/lineage.svg" alt="Project lineage: tokscale to tokscale-core to Syrtis, which feeds Syrtis-Windows and homebrew-tap; pilotfish to pilotfish-grok, pilotfish-codex, remora-cc (then calico-claude), lorenzini and stingray; TypeSafe Jev to lorenzini, stingray and MessageWatch; NyanCogs to ChannelSummary, MessageWatch, EmbedFixer and SpotifyPlaylist; StoryScope to sepia; postmortem-prose to md-style; plus coralline, SocksBypass and Cryptocentrus" width="100%"></p>

```console
~ ❯ ssh homelab -- uptime
```

The same discipline, off the clock — everything below runs at home:

```console
Proxmox VE      23d uptime · every service in Compose, every service healthchecked
Zero trust      Cloudflare Tunnel + Access · 6 tunnels · 20 ZTNA apps · 0 inbound ports
Home Assistant  140 integrations · 409 entities · 56 devices · one Lovelace panel
Self-hosted     Immich · Nextcloud AIO · LiteLLM · Open-WebUI · n8n · TrueNAS
```

```console
~ ❯ ssh nyanko.home
```

### 卯咪卯的窩 · a Chinese-speaking dev community

[![Discord](https://img.shields.io/discord/1523004250152501341?label=%E5%8D%AF%E5%92%AA%E5%8D%AF%E7%9A%84%E7%AA%A9&logo=discord&logoColor=white&color=5865F2&style=for-the-badge)](https://discord.gg/C6NRm5jHMt)

我一直想要一個地方：能認真聊技術，也能放心做自己。找不到，那就自己開一個。

- 💻 **技術控** — agentic coding、熱門 AI 應用、開源工具、軟體開發、DevOps／SRE。想深聊、想求救、想炫專案都可以。
- 💬 **只想交朋友、放鬆閒聊** — 完全歡迎，不用很懂技術。
- 🏳️‍⚧️ **秘密專區** — 我自己是跨女，所以特別開了一區給跨性別、偽娘／男娘：安心做自己、和姐妹聊女裝、交朋友、談談心事。

不管你是哪一種（或同時是好幾種），這裡都有你的位置。

**[→ 進來坐](https://discord.gg/C6NRm5jHMt)**

```console
~ ❯ cat .offline
```

```console
Coffee      Sunbeam Barista Max + Option-O Lagom Casa
            nutty / chocolate base, with the occasional fruit bomb
Hamsters    once shared my life with two hamsters — 877 and 907 days, respectively.
Headphones  Sony IER-M9 · MDR-MV1 · MDR-M1 · iFi xDSD Gryphon
```

```console
~ ❯ patreon --thanks
```

If any of this saved you time or money, a membership keeps the cron jobs running.

[![Patreon](https://img.shields.io/badge/Support%20on-Patreon-FF424D?logo=patreon&logoColor=white&style=for-the-badge)](https://www.patreon.com/cw/Nanako0129/membership)

```console
~ ❯ contact
```

**Something broken, or an idea for a feature** → open an issue on that repo. That's what
issues are for, and the answer helps the next person too. If a tool just made your day
easier and you want to say so there, that's welcome as well — I read every one.

**Anything formal** → email me at **nanakotsai@nyanako.com**.

**Anything casual** → the Discord above, DM me there, or find me on
[Threads](https://www.threads.com/@nyanako0129) and [X](https://x.com/Nyanako0129).

A note on language: I'm a native Traditional Chinese speaker and my English isn't fluent —
some of my replies go through a translator. Chinese is very welcome, and please bear with
me in English.

```console
~ ❯ exit
```

<sub>This page rebuilds itself every six hours · last sync: 2026-09-27 · <a href="https://github.com/Nanako0129/Nanako0129/blob/main/scripts/update_readme.py">how</a></sub>

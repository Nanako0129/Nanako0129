<!--
  ╭─ hey, you opened the raw file ─────────────────────────────╮
  │  Most of this page rebuilds itself every six hours:        │
  │  scripts/update_readme.py + .github/workflows/readme.yml   │
  │  The numbers below are not decoration. They are the build. │
  ╰────────────────────────────────────────────────────────────╯
-->

<!-- NEOFETCH:START -->
<p align="center"><img src="assets/neofetch.svg" alt="nanako@taiwan · Name: Nanako, or Nyanako · Pronouns: she / her · OS: macOS 27.0 arm64 · Host: MacBook Air (M5, 2026), 32GB / 1TB · Kernel: SRE, platform &amp; DevSecOps · Uptime: 27 years · Install Date: 2018-11-04 (github.com) · Packages: 35 sources (git), 4,786 stars · Shell: zsh + powerlevel10k · DE: coralline (Claude Code statusline) · Homelab: Proxmox, 28d up, 0 open ports · CPU: Rust, Swift, Python, Ansible, K8s · Locale: zh_TW.UTF-8 (English via translator) · Now: no roadmap. What I ship, I maintain." width="100%"></p>
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
| **[sepia](https://github.com/Nanako0129/sepia)** | De-AI writing skill for coding agents | ★ 2936 | `v0.12.2` | — | 9d ago |
| **[pilotfish](https://github.com/Nanako0129/pilotfish)** | Multi-model orchestration for Claude Code | ★ 699 | `v1.4.2` | — | 7d ago |
| **[coralline](https://github.com/Nanako0129/coralline)** | Powerlevel10k-inspired statusline for Claude Code | ★ 546 | `v0.19.0` | — | today |
| **[Syrtis](https://github.com/Nanako0129/Syrtis)** | Native macOS menu-bar monitor for AI token usage | ★ 399 | `v2.3.0` | 7.5k | today |
| **[SocksBypass](https://github.com/Nanako0129/SocksBypass)** | SOCKS5 proxy for iOS and Android, built to defeat tethering limits | ★ 79 | `—` | — | 25d ago |
| **[remora-cc](https://github.com/Nanako0129/remora-cc)** | Session-scoped GPT-5.6 agent routing | ★ 26 | `v0.1.23` | 72 | 14d ago |
| **[lorenzini](https://github.com/Nanako0129/lorenzini)** | PR-reviewer gates that decide whether a verdict means pass | ★ 17 | `v0.2.3` | — | 7d ago |
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
last 7 days · 8.8B tokens · 25,048 messages

  claude-opus-5-5     ██████████████████░░░░  80.4%     7045M
  claude-sonnet-5     ███░░░░░░░░░░░░░░░░░░░  15.2%     1330M
  claude-opus-5       ░░░░░░░░░░░░░░░░░░░░░░   2.3%      198M
  grok-4.7            ░░░░░░░░░░░░░░░░░░░░░░   1.7%      153M
  claude-sonnet-5-5   ░░░░░░░░░░░░░░░░░░░░░░   0.1%       13M
  claude-haiku-4-5    ░░░░░░░░░░░░░░░░░░░░░░   0.1%       12M
```
<!-- USAGE:END -->

```console
~ ❯ git log --oneline --author=nanako -5
```

<!-- NOW:START -->
```console
2026-10-03  Syrtis-Windows      fix(onboarding): disambiguate Grid in the setup-card view
2026-10-03  Syrtis-Windows      feat(onboarding): the pace card and the icon pickers inclu
2026-10-03  Syrtis-Windows      refactor(onboarding): one tray icon style list for both pi
2026-10-03  Syrtis-Windows      test(onboarding): the Agents card folds CLI aliases into o
2026-10-03  Syrtis-Windows      refactor(discord): retire the launch-time intro window
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
Proxmox VE      28d uptime · every service in Compose, every service healthchecked
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

<sub>This page rebuilds itself every six hours · last sync: 2026-10-03 · <a href="https://github.com/Nanako0129/Nanako0129/blob/main/scripts/update_readme.py">how</a></sub>

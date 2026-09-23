# claude-config

Smitty's portable Claude Code (and, eventually, Codex) user configuration —
personal instructions, hooks, and skills that apply across machines.

## What's here

| File/Dir | Installs to | Purpose |
|----------|-------------|---------|
| `CLAUDE.md` | `$CLAUDE_CONFIG_DIR/CLAUDE.md` | Shared global instructions — installed to every profile |
| `CLAUDE.work.md` | appended after `CLAUDE.md`, work profile only | Delta on top of the shared rules for things that are genuinely work-specific |
| `settings.json` | deep-merged into `$CLAUDE_CONFIG_DIR/settings.json` | Shared permissions/hooks; repo keys win, local-only keys are preserved |
| `settings.work.json` | merged on top, work profile only | Work-specific permissions/MCP servers — not yet populated |
| `hooks/` | `$CLAUDE_CONFIG_DIR/hooks/` | Lifecycle scripts — `check-config-sync.sh` (SessionStart auto-pull + reinstall) |
| `skills/` | `$CLAUDE_CONFIG_DIR/skills/` | Slash-command skills — empty so far |
| `hooks-work/` | `$CLAUDE_CONFIG_DIR/hooks/`, work profile only | `pre-akka-push.sh` — enforces the push-review gate below |
| `skills-work/` | `$CLAUDE_CONFIG_DIR/skills/`, work profile only | `akka-pr-review` — independent pre-push review |
| `templates/` | copy into a project root as needed | Per-project scaffolding |
| `codex/` | `~/.codex` and project roots | Portable Codex config — not yet built |
| `akka-mcp-gateway` (registered by `install.sh`, work profile only) | user-scope MCP registration | Company gateway at `https://mcp.akka.services/mcp` — Slack, Gmail, Calendar, Drive, HubSpot, Okta, Groundcover. Auth is per-machine: run `/mcp` and sign in via Okta. |

One repo, two install targets: `~/.claude-personal` and `~/.claude-work` (kept
isolated for auth, usage tracking, and session history by the
`claude-personal`/`claude-work` shell functions in
[dotfiles](https://github.com/smittyweygant/dotfiles)) share the same base
rules in `CLAUDE.md`, so discipline doesn't drift between the two. `install.sh`
infers the profile from the target directory name (or `$CLAUDE_PROFILE`) and
layers `CLAUDE.work.md`/`settings.work.json` on top only for the work profile.
Those overlay files start empty and get filled in as work-specific needs
(org MCP servers, a push-review gate, etc.) come up — see `CLAUDE.work.md`.

## Install

```bash
git clone https://github.com/smittyweygant/claude-config
cd claude-config
bash install.sh                              # → ~/.claude-personal
CLAUDE_CONFIG_DIR=~/.claude-work bash install.sh   # → ~/.claude-work, with the work overlay
```

Restart Claude Code after installing. Safe to re-run.

Also wired into a fresh-machine bootstrap via
[dotfiles](https://github.com/smittyweygant/dotfiles) — see that repo for the
automated path.

## Update

```bash
cd claude-config
git pull
bash install.sh
```

## Inspired by

Structured after [Tyler Jewell's `claude-user-config`](https://github.com/TylerJewell/claude-user-config)
— the repo → `install.sh` → deep-merged `settings.json` pattern, and the
hooks/skills split, are borrowed from there. This isn't a fork: the content
is personal rather than Akka/company-specific, so it diverges from the start.
The "LLM Discipline" section of `CLAUDE.md` traces further back to
[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills).

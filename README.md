# claude-config

Smitty's portable Claude Code (and, eventually, Codex) user configuration —
personal instructions, hooks, and skills that apply across machines.

## What's here

| File/Dir | Installs to | Purpose |
|----------|-------------|---------|
| `CLAUDE.md` | `$CLAUDE_SHARED_DIR/CLAUDE.md` | Global instructions, shared by every profile. Work-specific guidance (the "Work-Specific Additions" section) is self-gating on repo content — e.g. an akka-org remote — not on which profile is running |
| `settings.json` | deep-merged into `$CLAUDE_SHARED_DIR/settings.json` | Shared permissions/hooks; repo keys win, local-only keys are preserved |
| `hooks/` | `$CLAUDE_SHARED_DIR/hooks/` | Lifecycle scripts — `check-config-sync.sh` (SessionStart auto-pull + reinstall), `pre-akka-push.sh` (push-review gate, self-gates on akka-org remote) |
| `skills/` | `$CLAUDE_SHARED_DIR/skills/` | Slash-command skills — `akka-pr-review` (independent pre-push review, self-gates on akka-org remote) |
| `templates/` | copy into a project root as needed | Per-project scaffolding |
| `codex/` | `~/.codex` and project roots | Portable Codex config — not yet built |
| `akka-mcp-gateway` (registered by `install.sh`, work profile only) | user-scope MCP registration in `$CLAUDE_CONFIG_DIR/.claude.json`, per profile | Company gateway at `https://mcp.akka.services/mcp` — Slack, Gmail, Calendar, Drive, HubSpot, Okta, Groundcover. Auth is per-machine: run `/mcp` and sign in via Okta. |

One repo, two profile directories — `~/.claude-personal` and `~/.claude-work`
— but a single shared config/history tree at `~/.claude-shared` (default;
override with `$CLAUDE_SHARED_DIR`). `install.sh` populates the shared tree
and symlinks `CLAUDE.md`, `settings.json`, `hooks/`, `skills/`, and
`projects/` (session history) from each profile directory into it, so both
profiles see identical config and identical thread history. Only the two
things Claude Code itself keys to `$CLAUDE_CONFIG_DIR` — auth credentials and
the `akka-mcp-gateway` MCP registration, both living in that directory's own
`.claude.json` — stay separate per profile. That split is the whole point:
`claude-personal`/`claude-work` (the shell functions in
[dotfiles](https://github.com/smittyweygant/dotfiles)) toggle which Anthropic
account — and which plan's quota — a session draws against, independent of
which project or content you're working on.

Work-specific rules used to live in overlay files (`CLAUDE.work.md`,
`settings.work.json`, `hooks-work/`, `skills-work/`) installed only into the
work profile. Those are gone now that history isn't split by profile either —
each piece of work-only content gates itself on the repo it's running in
(an akka-org git remote) rather than on which directory installed it.

## Install

```bash
git clone https://github.com/smittyweygant/claude-config
cd claude-config
bash install.sh                                    # → ~/.claude-personal
CLAUDE_CONFIG_DIR=~/.claude-work bash install.sh    # → ~/.claude-work
```

Both commands populate the same `~/.claude-shared`. Restart Claude Code after
installing. Safe to re-run.

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

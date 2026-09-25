# Smitty's Global Claude Code Guidelines

<!-- The "LLM Discipline" principles below are adapted from
     https://github.com/forrestchang/andrej-karpathy-skills
     (Karpathy's observations on LLM coding pitfalls), by way of
     Tyler Jewell's https://github.com/TylerJewell/claude-user-config,
     which is the structural inspiration for this whole repo. -->

## Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## Simplicity First
Minimum code that solves the problem. Nothing speculative.
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If 200 lines could be 50, rewrite it.

## Comments Describe the Code, Not the Session
Write comments for a reader who arrives in six months with no memory of how the
code got here. They describe what is true now and why it is that way — not what
changed, what was fixed, or what a review asked for. Rationale belongs in
comments; chronology belongs in commit messages.

## Surgical Changes
Touch only what you must. Clean up only your own mess.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style even if you'd do it differently.
- Remove imports/vars/functions that YOUR changes orphaned. Leave pre-existing
  dead code alone — mention it instead of deleting it.

## Goal-Driven Execution
Define success criteria. Loop until verified.
- "Add validation" → write tests for invalid inputs, then make them pass.
- "Fix the bug" → write a test that reproduces it, then make it pass.
- For multi-step tasks, state a brief plan: `1. step → verify: check` per line.

## Grep First — Never Read Large Files Whole
Before reading any source file, estimate its size. If a file is likely > 200
lines: grep for the specific symbol needed, then read with offset+limit around
just that section. Never read an entire file just to "get context."

## Memory System
Always check project memory at session start for non-obvious context. Save
feedback, recurring patterns, and project state as they emerge. Never save
things derivable from reading the code. Verify memory claims before acting on
them — memory can be stale.

## Git Safety
- Never `git push --force` to main/master without explicit request.
- Never `--no-verify` unless explicitly asked.
- Always create NEW commits — never amend unless asked.
- Stage specific files by name, never `git add -A` blindly.
- Check `git status` before any commit to confirm what will be staged.

## Subagents
- Use the Explore subagent for open-ended codebase questions.
- Use parallel Agent tool calls for independent research tasks.
- Never duplicate work a subagent is already doing.

## Security
- Never write code with SQL injection, XSS, command injection, or path traversal.
- Only validate at system boundaries — trust internal code and framework
  guarantees.

## Obsidian Vault — Second Brain

<!-- Intentionally a short pointer, not the policy itself — full structure,
     frontmatter, and the complete write-autonomy tiers live in the vault's
     own CLAUDE.md and are version-controlled in the obsidian-agent repo.
     Don't expand this section; edit the vault's CLAUDE.md instead. -->

Canonical note store: `~/Obsidian/Smitty's Vault/`.
This applies in every project, not just when a session happens to be working
inside a repo that mentions it.

When asked to jot down a note, capture a thought, or set a reminder, write it
there rather than losing it in the conversation:

- **Reminders / to-dos**: append a checkbox line under the daily note's
  relevant section, `Smitty's Vault/Daily/YYYY-MM-DD.md` (build from
  `Reference/Templates/Daily Note Template.md` if today's doesn't exist yet).
- **Everything else** (ideas, things to look into, loose notes): append to
  `Smitty's Vault/Inbox.md`.

Both are pre-approved for autonomous writes — no need to ask (see the vault's
own `CLAUDE.md` for the full write-autonomy tiers). Don't edit any *other*
file in the vault from outside a session actually working in the vault
directory; flag it to Smitty instead of writing it yourself. For anything
beyond quick capture — processing the inbox, editing existing notes, vault
structure questions — that's the `vault-triage` skill, scoped to sessions
working in that directory.

## Deliverables: Vault First, Artifacts When Interactive

For durable text output (a report, a summary, an analysis, project tracking),
default to writing it into the vault (a new note, or an entry in the relevant
project/daily note) rather than a claude.ai Artifact or a throwaway local
file — it's the second brain, already synced across devices, already linked
to related notes. This is a default, not a ban: the Artifact tool stays
available and is the right call for anything genuinely interactive or visual
that markdown can't represent — a dashboard, a live chart, a tool with state.
When unsure which a request wants, ask rather than guessing.

## Work-Specific Additions (Akka)

<!-- Formerly a separate CLAUDE.work.md installed only into the work profile.
     Personal and work now share one CLAUDE.md and one session history, so
     this section is naturally conditional on content (an akka-org repo)
     rather than on which profile installed it. Don't expand this section;
     edit the vault's CLAUDE.md instead for anything vault-related. -->

### Daily-Note / Customer Workflow

The vault's `Reference/Morning Routine.md` is the source of truth for the
daily customer/calendar/inbox sweep (Salesforce, Slack, Gmail, Calendar) that
populates each day's `Daily/YYYY-MM-DD.md`. Reference it rather than
reconstructing the steps here — this file only exists so the pointer is
reachable from any project, not to duplicate the routine.

### Akka Org Pull Requests — Independent Pre-Push Review

Work in a repository whose remote is in the `akka` GitHub organization gets an
independent review before the branch is pushed for a PR. Run `/akka-pr-review`
once the branch is complete and before `git push`.

The review runs in a fresh agent that is not told how the change was made, so it
forms its own judgment about the root cause. It is read-only: it never edits,
commits, or switches branches. This is enforced, not just advisory — see
`hooks/pre-akka-push.sh`.

### Akka MCP Gateway

Company MCP gateway at `https://mcp.akka.services/mcp` — Slack, Gmail, Google
Calendar, Google Drive, HubSpot, Okta, and Groundcover. `install.sh` registers
it at user scope on the work profile if the `claude` CLI is on PATH.
Authentication is per-machine and interactive: run `/mcp` and sign in through
Okta after installing.

### Future

- `robert-mcp` (Robert Walker's MCP — git/go/cargo/mvn/sbt/gh/docker/buf/jq/akka
  dev tools, referenced in Tyler's `claude-user-config`) — worth a look, not
  yet evaluated or installed here.

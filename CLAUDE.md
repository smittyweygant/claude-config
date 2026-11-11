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

## Voice: Plain and Spare

Write prose the way Hemingway would. Say the thing, then stop.
- Short, declarative sentences. Vary the length so it doesn't drone.
- Concrete nouns, active verbs. The subject acts.
- Plain words over fancy ones. "Use," not "utilize."
- Few adjectives. Almost no adverbs. If a word adds no weight, cut it.
- No preamble, no recap, no cheerleading, no hedging filler. Lead with the answer.
- Stay level. State facts and let them carry the feeling.

Limits:
- Omit surface detail, never substance. Assumptions, uncertainty, risks, and
  tradeoffs get stated plainly even when brevity tempts you to drop them.
- Code, commands, error text, and commit/PR messages follow their own
  conventions. This voice governs the prose around them.
- When a user asks for another register (formal email, customer-facing copy),
  use theirs. For a full rewrite in this style, use the `hemingway` skill.

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

## Token Estimates: Before and After

Estimate before you start. Measure after. Record the gap.

Applies to every issue or task, in any project.

- **Baseline first.** Before anything else, run
  `python3 -I ~/development/claude-config/scripts/usage.py <session>.jsonl` on the
  current session transcript (`~/.claude-personal/projects/<project-dir>/<session-id>.jsonl`;
  the work profile's root may differ). Note calls and all_total.
- **Estimate before work.** State processed tokens (all_total), fresh tokens and
  output, each with a range. all_total is roughly calls x average context. Average
  context starts at the size of the system prompt and tools (55k in the finances
  project) and grows about 1.2k per call. Budget calls by decisions, not lines of
  code: about 6 per PR (branch, commit, push, create, review, comment). Widen the
  range for an unknown cause. Budget design work at 1.6x the first pass for the
  review round. A `/code-review low` subagent costs about 41k, and it is not in the
  main transcript. Take its figure from the task notification.
- **Post the estimate on the issue before branching.** If the work has no issue,
  state it in the session instead.
- **After the PR, measure.** Run `usage.py` again and subtract the baseline. Add
  subagent tokens. Comment the estimate and the actual on the issue: calls,
  all_total, fresh, output, and one line on why they differed.
- **Log it.** Add a dated entry to the vault note
  `Projects/Coding Agent Orchestration/Agent Work Estimation.md`. It is the one note
  outside the quick-capture rule that Claude writes to from any project.
- Do not skip the up-front estimate because the task looks small.

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

## Project Workflow: Issues, PRs, Deploy

Applies to Smitty's own repos (`github.com/smittyweygant/*`) and any repo with no
workflow of its own. A project's `CLAUDE.md` and docs win on specifics. Repos
in the `akka` org follow the company's conventions plus the pre-push review
below.

- **Start from an issue.** Run `gh issue list` at session start. If the work has
  no issue, create one first: what, why, and checkable "Done when" boxes.
- **Branch per issue**, named `<issue#>-<slug>`, off an up-to-date default branch.
- **Never push to the default branch.** Open a PR with `Closes #N`: what and
  why, how it was verified, deploy notes. Smitty merges (squash). Run
  `/code-review` before asking for review. One issue per PR.
- **Status lives on the issue and the board,** not in docs or journals.
  Findings go in issue comments. Design goes in a plan doc linked from the issue.
- **Bugs start with a test** that reproduces them.
- **A merge may deploy.** If a deploy workflow runs on the default branch, a
  merge is a release: watch the run (`gh run watch --exit-status`), check the
  live system, then report. Never deploy around CI. Done means verified live.
- **Changing production data:** a named dump first, a dry run that shows the
  diff, apply only on Smitty's go-ahead, and a record of what was replaced.
- **New repo, or a repo missing the scaffolding:** adopt
  `templates/project-workflow/` from claude-config (issue forms, PR template,
  labels, workflow doc, project `CLAUDE.md`) instead of inventing a variant.

## Chezmoi Dotfiles Repos
In a chezmoi source repo, read its `CLAUDE.md` before editing any managed file.
Edit the source, not the live file, and check `chezmoi diff` before and after.
Keep personal data (hosts, key names, IPs, account IDs) out of public repos;
it belongs in the gitignored `.local` files the repo's `CLAUDE.md` names.

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

- **Reminders / to-dos**: capture each new action once as a checkbox with a
  creation date (`➕ YYYY-MM-DD`) under the daily note's
  relevant section, `Smitty's Vault/Daily/YYYY-MM-DD.md` (build from
  `Reference/Templates/Daily Note Template.md` if today's doesn't exist yet).
- **Everything else** (ideas, things to look into, loose notes): append to
  `Smitty's Vault/Inbox.md`.

Both are pre-approved for autonomous writes — no need to ask (see the vault's
own `CLAUDE.md` for the full write-autonomy tiers). A third target is
pre-approved too: token-estimate log entries, appended to
`Smitty's Vault/Projects/Coding Agent Orchestration/Agent Work Estimation.md`
(see "Token Estimates: Before and After"). Don't edit any *other*
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
When unsure which a request wants, ask rather than guessing. Token-estimate
entries go to `Projects/Coding Agent Orchestration/Agent Work Estimation.md`.

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

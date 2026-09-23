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

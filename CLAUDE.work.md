<!-- Work-profile overlay: appended after the shared CLAUDE.md when installing
     into a *-work profile (see install.sh). Only things that genuinely need
     to differ at work belong here — everything else stays in the shared
     CLAUDE.md so personal and work don't drift apart on general discipline. -->

# Work-Specific Additions

## Daily-Note / Customer Workflow

The vault's `Reference/Morning Routine.md` is the source of truth for the
daily customer/calendar/inbox sweep (Salesforce, Slack, Gmail, Calendar) that
populates each day's `Daily/YYYY-MM-DD.md`. Reference it rather than
reconstructing the steps here — this file only exists so the pointer is
reachable from any project, not to duplicate the routine.

## Akka Org Pull Requests — Independent Pre-Push Review

Work in a repository whose remote is in the `akka` GitHub organization gets an
independent review before the branch is pushed for a PR. Run `/akka-pr-review`
once the branch is complete and before `git push`.

The review runs in a fresh agent that is not told how the change was made, so it
forms its own judgment about the root cause. It is read-only: it never edits,
commits, or switches branches. This is enforced, not just advisory — see
`hooks-work/pre-akka-push.sh`.

## Akka MCP Gateway

Company MCP gateway at `https://mcp.akka.services/mcp` — Slack, Gmail, Google
Calendar, Google Drive, HubSpot, Okta, and Groundcover. `install.sh` registers
it at user scope on the work profile if the `claude` CLI is on PATH.
Authentication is per-machine and interactive: run `/mcp` and sign in through
Okta after installing.

## Future

- `robert-mcp` (Robert Walker's MCP — git/go/cargo/mvn/sbt/gh/docker/buf/jq/akka
  dev tools, referenced in Tyler's `claude-user-config`) — worth a look, not
  yet evaluated or installed here.

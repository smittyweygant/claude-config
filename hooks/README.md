# hooks/

Lifecycle scripts, installed to `$CLAUDE_CONFIG_DIR/hooks/` and wired up via
the `hooks` key in `settings.json`.

- `check-config-sync.sh` — `SessionStart`: auto-pulls this repo and re-runs
  `install.sh` when it's behind origin.
- `pre-akka-push.sh` — `PreToolUse`: blocks `git push` of an akka-org feature
  branch until an `/akka-pr-review` report exists for it. Self-gates on the
  repo's git remote, so it's a no-op outside akka-org repos regardless of
  which profile is running it.

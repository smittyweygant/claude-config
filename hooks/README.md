# hooks/

Lifecycle scripts, installed to `$CLAUDE_CONFIG_DIR/hooks/` and wired up via
the `hooks` key in `settings.json`. Empty for now — add scripts here as
recurring friction shows up (see Tyler's `claude-user-config` for the pattern:
a `SessionStart` self-sync hook, and `PreToolUse` hooks that turn an advisory
rule into an enforced one).

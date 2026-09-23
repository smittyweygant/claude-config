#!/bin/bash
# Adapted from Tyler Jewell's claude-user-config (hooks/check-config-sync.sh).
#
# Fires on SessionStart. If ~/development/claude-config is behind origin and
# the working tree is clean, auto-pull and re-run install.sh (which respects
# whatever CLAUDE_CONFIG_DIR this session inherited — personal or work), then
# remind the user to restart Claude Code so the new config is picked up.
#
# Exits silently when there is nothing to do so a normal session start
# produces no noise.

REPO="$HOME/development/claude-config"
[ -d "$REPO/.git" ] || exit 0

cd "$REPO" || exit 0

# Short-timeout fetch so a network hiccup doesn't block session start.
if command -v timeout >/dev/null 2>&1; then
    timeout 5 git fetch --quiet 2>/dev/null || exit 0
else
    git fetch --quiet 2>/dev/null || exit 0
fi

# How many commits are we behind upstream?
BEHIND=$(git rev-list --count HEAD..@{u} 2>/dev/null)
[ "${BEHIND:-0}" -eq 0 ] && exit 0

# Don't auto-pull if there are local uncommitted changes.
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠ claude-config: $BEHIND commits behind origin, but the checkout has uncommitted changes. Skipping auto-pull." >&2
    echo "  Resolve manually: cd $REPO && git status" >&2
    exit 0
fi

# Safe to pull.
if ! git pull --ff-only --quiet 2>/dev/null; then
    echo "⚠ claude-config: git pull failed. Investigate '$REPO' manually." >&2
    exit 0
fi

# Redeploy to the current profile. install.sh is itself a no-op when nothing
# changed for that profile.
if ! bash "$REPO/install.sh" >/dev/null 2>&1; then
    echo "⚠ claude-config: pulled successfully but install.sh failed. Run it manually." >&2
    exit 0
fi

echo "✓ claude-config updated ($BEHIND new commits) and re-installed." >&2
echo "  Restart Claude Code to load the new configuration." >&2
exit 0

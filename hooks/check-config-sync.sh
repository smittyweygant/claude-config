#!/bin/bash
# Adapted from Tyler Jewell's claude-user-config (hooks/check-config-sync.sh).
#
# Fires on SessionStart. If ~/development/claude-config is behind origin and
# the working tree is clean, auto-pull. Then, if HEAD differs from the commit
# install.sh last deployed (recorded in $SHARED_DIR/.installed-commit), re-run
# install.sh (which respects whatever CLAUDE_CONFIG_DIR this session inherited
# — personal or work) and remind the user to restart Claude Code. Comparing
# against the deployed commit means local commits deploy too, not only pulls.
#
# Exits silently when there is nothing to do so a normal session start
# produces no noise.

REPO="$HOME/development/claude-config"
SHARED_DIR="${CLAUDE_SHARED_DIR:-$HOME/.claude-shared}"
[ -d "$REPO/.git" ] || exit 0

cd "$REPO" || exit 0

DIRTY=$(git status --porcelain)

# Short-timeout fetch so a network hiccup doesn't block session start. A
# failed fetch still falls through to the local deploy check below.
if command -v timeout >/dev/null 2>&1; then
    timeout 5 git fetch --quiet 2>/dev/null
else
    git fetch --quiet 2>/dev/null
fi

# How many commits are we behind upstream?
BEHIND=$(git rev-list --count HEAD..@{u} 2>/dev/null)
if [ "${BEHIND:-0}" -gt 0 ]; then
    # Don't auto-pull if there are local uncommitted changes.
    if [ -n "$DIRTY" ]; then
        echo "⚠ claude-config: $BEHIND commits behind origin, but the checkout has uncommitted changes. Skipping auto-pull." >&2
        echo "  Resolve manually: cd $REPO && git status" >&2
        exit 0
    fi
    if ! git pull --ff-only --quiet 2>/dev/null; then
        echo "⚠ claude-config: git pull failed. Investigate '$REPO' manually." >&2
        exit 0
    fi
fi

# Deploy only committed state: an uncommitted edit is work in progress.
[ -n "$DIRTY" ] && exit 0

HEAD_COMMIT=$(git rev-parse HEAD)
INSTALLED_COMMIT=$(cat "$SHARED_DIR/.installed-commit" 2>/dev/null)
[ "$HEAD_COMMIT" = "$INSTALLED_COMMIT" ] && exit 0

# Redeploy to the current profile.
if ! bash "$REPO/install.sh" >/dev/null 2>&1; then
    echo "⚠ claude-config: install.sh failed. Run it manually." >&2
    exit 0
fi

echo "✓ claude-config re-installed at $(git rev-parse --short HEAD)." >&2
echo "  Restart Claude Code to load the new configuration." >&2
exit 0

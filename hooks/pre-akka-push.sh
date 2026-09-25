#!/bin/bash
# Adapted from Tyler Jewell's claude-user-config (hooks/pre-akka-push.sh) —
# generic to the "akka" GitHub org convention, no changes needed beyond the
# report path below.
#
# Fires before Bash/PowerShell tool calls. Blocks `git push` of a feature
# branch in an akka-org repo until an /akka-pr-review report exists for that
# branch and is newer than the branch tip.
#
# A review written before the last few commits describes code that is no
# longer being pushed, so staleness is treated the same as absence.
#
# Escape hatch: prefix the command with AKKA_PR_REVIEW_SKIP=1.
#
# Exits silently for everything that isn't such a push.

FIELDS=$(python3 -c "
import json, sys
d = json.load(sys.stdin)
print((d.get('tool_input') or {}).get('command', '').replace(chr(10), ' '))
print(d.get('cwd') or '')
" 2>/dev/null) || exit 0

COMMAND=$(printf '%s\n' "$FIELDS" | sed -n 1p)
CWD=$(printf '%s\n' "$FIELDS" | sed -n 2p)

case "$COMMAND" in
    *AKKA_PR_REVIEW_SKIP=1*) exit 0 ;;
    *"git push"*) ;;
    *) exit 0 ;;
esac

[ -n "$CWD" ] && cd "$CWD" 2>/dev/null

REMOTE=$(git remote get-url origin 2>/dev/null) || exit 0
case "$REMOTE" in
    *github.com/akka/*|*github.com:akka/*) ;;
    *) exit 0 ;;
esac

BRANCH=$(git branch --show-current 2>/dev/null)
[ -z "$BRANCH" ] && exit 0

# Pushing an integration branch isn't opening a PR, so there is nothing to review.
# main/master count as integration branches even when origin/HEAD is unset.
DEFAULT=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
case "$BRANCH" in
    main|master|"${DEFAULT#origin/}") exit 0 ;;
esac

REPO=$(basename -s .git "$REMOTE")
# This hook is installed at $CLAUDE_CONFIG_DIR/hooks/pre-akka-push.sh, so
# derive the profile dir from its own location rather than hardcoding one —
# this repo installs into both ~/.claude-personal and ~/.claude-work.
CONFIG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$CONFIG_DIR/reviews/$REPO-${BRANCH//\//-}-review.md"

block() {
    echo "BLOCKED: $1" >&2
    echo "Run /akka-pr-review on this branch, then push." >&2
    echo "  repo:   $REPO (akka org)" >&2
    echo "  branch: $BRANCH" >&2
    echo "  report: $REPORT" >&2
    echo "To push without a review: prefix the command with AKKA_PR_REVIEW_SKIP=1" >&2
    exit 2  # Blocking — denies the tool call
}

[ -f "$REPORT" ] || block "no independent review report for this branch."

TIP=$(git log -1 --format=%ct 2>/dev/null)
WRITTEN=$(stat -c %Y "$REPORT" 2>/dev/null || stat -f %m "$REPORT" 2>/dev/null)
if [ -n "$TIP" ] && [ -n "$WRITTEN" ] && [ "$WRITTEN" -lt "$TIP" ]; then
    block "the review report predates the branch tip — it reviewed different code."
fi

VERDICT=$(head -n 20 "$REPORT" | grep -m1 -oE 'READY TO PUSH|NEEDS WORK|NEEDS HUMAN DECISION')
if [ -n "$VERDICT" ] && [ "$VERDICT" != "READY TO PUSH" ]; then
    block "the review verdict is $VERDICT."
fi

exit 0

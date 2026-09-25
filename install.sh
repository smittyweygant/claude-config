#!/bin/bash
# install.sh — Install Smitty's Claude Code user configuration
# Run from the repo root: bash install.sh
#
# Targets $CLAUDE_CONFIG_DIR if set, otherwise ~/.claude-personal.
#
# CLAUDE.md, settings.json, hooks/, and skills/ are personal and work content
# now shared verbatim (work-only guidance is self-gating on repo content, not
# on which profile installed it — see hooks/README.md). They live in
# $CLAUDE_SHARED_DIR (default ~/.claude-shared) and each profile directory
# gets a symlink to them, so both profiles see identical config and session
# history. Only auth (credentials, keyed to $CLAUDE_CONFIG_DIR by Claude Code
# itself) and the akka-mcp-gateway MCP registration (which lives in
# $CLAUDE_CONFIG_DIR/.claude.json, also not shared) stay per-directory — that
# split is what lets `claude-personal`/`claude-work` toggle which account
# you're authenticated as without touching config or history.
#
# Safe to re-run. settings.json is deep-merged into the shared copy (repo
# wins on tracked keys, local-only keys preserved); CLAUDE.md/hooks/skills
# are overwritten in the shared copy. A profile dir whose target already
# exists as a REAL file/dir (not a symlink) is left untouched with a warning
# — that's pre-migration live data and this script won't silently absorb it.

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude-personal}"
SHARED_DIR="${CLAUDE_SHARED_DIR:-$HOME/.claude-shared}"

# Profile is inferred from the target dir name (e.g. ~/.claude-work) unless
# CLAUDE_PROFILE is set explicitly. Only used below to decide whether to
# register the company MCP gateway — shared content no longer branches on it.
PROFILE="${CLAUDE_PROFILE:-}"
if [ -z "$PROFILE" ]; then
    case "$(basename "$CLAUDE_DIR")" in
        *work*) PROFILE="work" ;;
        *) PROFILE="personal" ;;
    esac
fi

echo "Installing Claude user config from $REPO_DIR"
echo "  shared:  $SHARED_DIR"
echo "  profile: $CLAUDE_DIR (profile: $PROFILE)"
echo ""

mkdir -p "$SHARED_DIR/hooks"
mkdir -p "$SHARED_DIR/skills"
mkdir -p "$SHARED_DIR/projects"
mkdir -p "$CLAUDE_DIR"

# ── CLAUDE.md ─────────────────────────────────────────────────────────────
cp "$REPO_DIR/CLAUDE.md" "$SHARED_DIR/CLAUDE.md"
echo "✓ CLAUDE.md → $SHARED_DIR/CLAUDE.md"

# ── Hook scripts ─────────────────────────────────────────────────────────────
if compgen -G "$REPO_DIR/hooks/*.sh" > /dev/null; then
    cp "$REPO_DIR/hooks/"*.sh "$SHARED_DIR/hooks/"
    chmod +x "$SHARED_DIR/hooks/"*.sh
    echo "✓ hooks/*.sh → $SHARED_DIR/hooks/ (executable)"
else
    echo "= no hooks yet"
fi

# ── Skills ───────────────────────────────────────────────────────────────────
shopt -s nullglob
skill_dirs=("$REPO_DIR"/skills/*/)
shopt -u nullglob
if [ ${#skill_dirs[@]} -gt 0 ]; then
    for skill_dir in "${skill_dirs[@]}"; do
        skill_name=$(basename "$skill_dir")
        mkdir -p "$SHARED_DIR/skills/$skill_name"
        cp -r "$skill_dir"* "$SHARED_DIR/skills/$skill_name/"
        echo "✓ skills/$skill_name/ → $SHARED_DIR/skills/$skill_name/"
    done
else
    echo "= no skills yet"
fi

# ── settings.json (deep merge into the shared copy: repo wins on tracked keys) ──
SETTINGS_PATH="$SHARED_DIR/settings.json"
REPO_SETTINGS="$REPO_DIR/settings.json"

if [ ! -f "$SETTINGS_PATH" ]; then
    cp "$REPO_SETTINGS" "$SETTINGS_PATH"
    echo "✓ settings.json → $SETTINGS_PATH (new)"
else
    python3 - "$SETTINGS_PATH" "$REPO_SETTINGS" <<'PYEOF'
import sys, json, shutil, datetime

existing_path = sys.argv[1]
repo_path = sys.argv[2]

with open(existing_path, 'rb') as f:
    existing_raw = f.read()
with open(repo_path, 'rb') as f:
    repo_raw = f.read()

existing = json.loads(existing_raw)
repo = json.loads(repo_raw)


def deep_merge(local, upstream):
    """Repo wins on leaf conflicts. Local-only keys preserved. Lists overwrite."""
    if isinstance(upstream, dict) and isinstance(local, dict):
        result = dict(local)
        for k, v in upstream.items():
            if k in result:
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = v
        return result
    return upstream


def merge_hooks(local_hooks, repo_hooks):
    """Per-event entry union: a repo hook entry is appended to local hooks if an
    identical entry (by JSON serialization) isn't already present."""
    result = dict(local_hooks) if local_hooks else {}
    for event, repo_entries in (repo_hooks or {}).items():
        result.setdefault(event, [])
        existing_keys = {json.dumps(e, sort_keys=True) for e in result[event]}
        for entry in repo_entries:
            key = json.dumps(entry, sort_keys=True)
            label = entry.get("matcher") or event
            if key not in existing_keys:
                result[event].append(entry)
                existing_keys.add(key)
                print(f"  + Added hook: {label}")
            else:
                print(f"  ~ Skipped (already exists): {label}")
    return result


local_hooks = existing.pop("hooks", {})
repo_hooks = repo.pop("hooks", {})

merged = deep_merge(existing, repo)
merged["hooks"] = merge_hooks(local_hooks, repo_hooks)

merged_raw = (json.dumps(merged, indent=2) + "\n").encode("utf-8")

if merged_raw == existing_raw:
    print("  = settings.json already up to date")
else:
    backup = f"{existing_path}.bak.{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(existing_path, backup)
    with open(existing_path, 'wb') as f:
        f.write(merged_raw)
    print(f"  + settings.json updated (backup: {backup})")
PYEOF
    echo "✓ settings.json deep-merge complete"
fi

# ── Symlink the profile dir at $CLAUDE_DIR into the shared content ──────────
# Only ever creates/repairs a symlink. A real (non-symlink) file or dir at
# the target is left alone with a warning — that's either pre-migration live
# data or something unexpected, and this script won't guess which.
link() {
    local target="$1" link_path="$2"
    if [ -L "$link_path" ]; then
        [ "$(readlink "$link_path")" = "$target" ] || { rm "$link_path"; ln -s "$target" "$link_path"; }
        echo "✓ $link_path → $target"
    elif [ -e "$link_path" ]; then
        echo "⚠ $link_path exists and is not a symlink — leaving it alone. Migrate it into $SHARED_DIR manually, then re-run."
    else
        ln -s "$target" "$link_path"
        echo "✓ $link_path → $target (new)"
    fi
}

link "$SHARED_DIR/CLAUDE.md"    "$CLAUDE_DIR/CLAUDE.md"
link "$SHARED_DIR/settings.json" "$CLAUDE_DIR/settings.json"
link "$SHARED_DIR/hooks"        "$CLAUDE_DIR/hooks"
link "$SHARED_DIR/skills"       "$CLAUDE_DIR/skills"
link "$SHARED_DIR/projects"     "$CLAUDE_DIR/projects"

# ── akka-mcp-gateway (company MCP gateway, work profile only) ───────────────
# Registered at user scope in THIS profile's own (unshared) .claude.json —
# authentication and MCP registration stay per-directory on purpose, so the
# gateway is only available when authenticated as the work account.
# Authentication is per-machine and interactive — run /mcp and sign in
# through Okta. No credential belongs here.
if [ "$PROFILE" = "work" ]; then
    GATEWAY_NAME="akka-mcp-gateway"
    GATEWAY_URL="https://mcp.akka.services/mcp"
    if ! command -v claude >/dev/null 2>&1; then
        echo "⚠ claude not found on PATH — skipping $GATEWAY_NAME registration"
    elif CLAUDE_CONFIG_DIR="$CLAUDE_DIR" claude mcp get "$GATEWAY_NAME" 2>/dev/null | grep -q "User config"; then
        echo "✓ $GATEWAY_NAME already registered at user scope"
    else
        CLAUDE_CONFIG_DIR="$CLAUDE_DIR" claude mcp add --transport http --scope user "$GATEWAY_NAME" "$GATEWAY_URL" 2>&1 | sed 's/^/  /'
        echo "✓ $GATEWAY_NAME registered — run /mcp to authenticate"
    fi
fi

# ── Legacy ~/.claude → personal (defense against accidental bare `claude`) ──
# Claude Code falls back to ~/.claude whenever $CLAUDE_CONFIG_DIR is unset —
# a bare `claude` in a fresh shell, an IDE integration, a background job, or
# anything else that doesn't go through claude-personal/claude-work. Making
# that fallback literally BE the personal profile (auth included, not just
# config) means such a bypass can never silently authenticate as work.
LEGACY_DIR="$HOME/.claude"
PERSONAL_DIR="$HOME/.claude-personal"
if [ -L "$LEGACY_DIR" ]; then
    if [ "$(readlink "$LEGACY_DIR")" = "$PERSONAL_DIR" ]; then
        echo "✓ $LEGACY_DIR → $PERSONAL_DIR"
    else
        echo "⚠ $LEGACY_DIR is a symlink to something else — leaving it alone."
    fi
elif [ -e "$LEGACY_DIR" ]; then
    echo "⚠ $LEGACY_DIR exists and is a real directory — leaving it alone. Back it up, then 'ln -s $PERSONAL_DIR $LEGACY_DIR' manually to close the fallback gap."
elif [ -d "$PERSONAL_DIR" ]; then
    ln -s "$PERSONAL_DIR" "$LEGACY_DIR"
    echo "✓ $LEGACY_DIR → $PERSONAL_DIR (new)"
fi

echo ""
echo "Done! Restart Claude Code for changes to take effect."

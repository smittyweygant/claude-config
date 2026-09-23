#!/bin/bash
# install.sh — Install Smitty's Claude Code user configuration
# Run from the repo root: bash install.sh
#
# Targets $CLAUDE_CONFIG_DIR if set, otherwise ~/.claude-personal (this
# repo's config is personal-profile content; a work profile, if ever needed,
# is a separate — likely private — repo, same split as the dotfiles repo
# uses for public vs. private tooling).
#
# Safe to re-run: settings.json is deep-merged (repo wins on tracked keys,
# local-only keys are preserved); other files are overwritten.

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude-personal}"

# Profile is inferred from the target dir name (e.g. ~/.claude-work) unless
# CLAUDE_PROFILE is set explicitly. Only "work" triggers the overlay below.
PROFILE="${CLAUDE_PROFILE:-}"
if [ -z "$PROFILE" ]; then
    case "$(basename "$CLAUDE_DIR")" in
        *work*) PROFILE="work" ;;
        *) PROFILE="personal" ;;
    esac
fi

echo "Installing Claude user config from $REPO_DIR into $CLAUDE_DIR (profile: $PROFILE)..."
echo ""

mkdir -p "$CLAUDE_DIR/hooks"
mkdir -p "$CLAUDE_DIR/skills"

# ── CLAUDE.md (shared base + work overlay when profile=work) ────────────────
if [ "$PROFILE" = "work" ] && [ -f "$REPO_DIR/CLAUDE.work.md" ]; then
    cat "$REPO_DIR/CLAUDE.md" "$REPO_DIR/CLAUDE.work.md" > "$CLAUDE_DIR/CLAUDE.md"
    echo "✓ CLAUDE.md + CLAUDE.work.md → $CLAUDE_DIR/CLAUDE.md"
else
    cp "$REPO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    echo "✓ CLAUDE.md → $CLAUDE_DIR/CLAUDE.md"
fi

# ── Hook scripts ─────────────────────────────────────────────────────────────
if compgen -G "$REPO_DIR/hooks/*.sh" > /dev/null; then
    cp "$REPO_DIR/hooks/"*.sh "$CLAUDE_DIR/hooks/"
    chmod +x "$CLAUDE_DIR/hooks/"*.sh
    echo "✓ hooks/*.sh → $CLAUDE_DIR/hooks/ (executable)"
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
        mkdir -p "$CLAUDE_DIR/skills/$skill_name"
        cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
        echo "✓ skills/$skill_name/ → $CLAUDE_DIR/skills/$skill_name/"
    done
else
    echo "= no skills yet"
fi

# ── Work-only hooks/skills (profile=work only) ───────────────────────────────
if [ "$PROFILE" = "work" ]; then
    if compgen -G "$REPO_DIR/hooks-work/*.sh" > /dev/null; then
        cp "$REPO_DIR/hooks-work/"*.sh "$CLAUDE_DIR/hooks/"
        chmod +x "$CLAUDE_DIR/hooks/"*.sh
        echo "✓ hooks-work/*.sh → $CLAUDE_DIR/hooks/ (executable)"
    fi

    shopt -s nullglob
    work_skill_dirs=("$REPO_DIR"/skills-work/*/)
    shopt -u nullglob
    for skill_dir in "${work_skill_dirs[@]}"; do
        skill_name=$(basename "$skill_dir")
        mkdir -p "$CLAUDE_DIR/skills/$skill_name"
        cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
        echo "✓ skills-work/$skill_name/ → $CLAUDE_DIR/skills/$skill_name/"
    done
fi

# ── settings.json (deep merge: repo wins on tracked keys) ───────────────────
# On the work profile, settings.work.json (if present) is merged in as a
# second pass on top of the shared settings.json — same base+overlay split
# as CLAUDE.md above.
SETTINGS_PATH="$CLAUDE_DIR/settings.json"
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

if [ "$PROFILE" = "work" ] && [ -f "$REPO_DIR/settings.work.json" ]; then
    python3 - "$SETTINGS_PATH" "$REPO_DIR/settings.work.json" <<'PYEOF'
import sys, json
existing_path, overlay_path = sys.argv[1], sys.argv[2]
with open(existing_path) as f:
    existing = json.load(f)
with open(overlay_path) as f:
    overlay = json.load(f)

def deep_merge(local, upstream):
    if isinstance(upstream, dict) and isinstance(local, dict):
        result = dict(local)
        for k, v in upstream.items():
            result[k] = deep_merge(result[k], v) if k in result else v
        return result
    return upstream

merged = deep_merge(existing, overlay)
with open(existing_path, 'w') as f:
    json.dump(merged, f, indent=2)
    f.write("\n")
print("  + settings.work.json overlay merged")
PYEOF
fi

# ── akka-mcp-gateway (company MCP gateway, work profile only) ───────────────
# Registered at user scope. Authentication is per-machine and interactive —
# run /mcp in Claude Code and sign in through Okta. No credential belongs here.
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

echo ""
echo "Done! Restart Claude Code for changes to take effect."

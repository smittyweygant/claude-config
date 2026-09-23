#!/usr/bin/env python3
"""Read-only manifest of a Claude Code config dir's session transcripts.

Usage: manifest.py <claude-config-dir> > manifest.json

For each projects/*/*.jsonl file, records the session id, project dir name,
first-message timestamp, cwd, and (if cwd is still a live git repo) its
origin remote. Never modifies anything.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def git_remote(cwd: str) -> str | None:
    path = Path(cwd)
    if not (path / ".git").exists():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None


def first_user_meta(jsonl_path: Path) -> dict | None:
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") == "user" and "cwd" in d and "timestamp" in d:
                return {
                    "timestamp": d["timestamp"],
                    "cwd": d["cwd"],
                    "gitBranch": d.get("gitBranch"),
                }
    return None


def main():
    if len(sys.argv) != 2:
        print("usage: manifest.py <claude-config-dir>", file=sys.stderr)
        sys.exit(1)

    root = Path(sys.argv[1]) / "projects"
    if not root.is_dir():
        print(f"no projects dir under {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)

    remote_cache: dict[str, str | None] = {}
    entries = []
    for project_dir in sorted(root.iterdir()):
        if not project_dir.is_dir():
            continue
        for session_file in sorted(project_dir.glob("*.jsonl")):
            meta = first_user_meta(session_file)
            entry = {
                "session_id": session_file.stem,
                "project_dir": project_dir.name,
                "file": str(session_file),
            }
            if meta:
                cwd = meta["cwd"]
                if cwd not in remote_cache:
                    remote_cache[cwd] = git_remote(cwd)
                entry.update(meta)
                entry["remote"] = remote_cache[cwd]
            else:
                entry["error"] = "no first user message found"
            entries.append(entry)

    json.dump(entries, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()

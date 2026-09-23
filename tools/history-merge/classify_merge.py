#!/usr/bin/env python3
"""Classify manifest.py output as personal/work/flagged, and (unless --dry-run
is absent) merge session transcripts into the right profile's projects dir.

Rule:
  - cwd matches a --force-personal
    prefix (e.g. the interview demo
    app repo)                          -> personal, regardless of date
  - before --cutoff (ISO date)         -> personal
  - no first-user-message found        -> flagged: no_user_message
  - on/after cutoff, cwd is under a
    --work-path prefix (e.g. ~/akka/)  -> work
  - on/after cutoff, cwd is NOT under
    any --work-path prefix             -> flagged: not_under_work_path
                                           (confirm manually -- work can
                                           happen outside ~/akka/ too)

git remote (captured by manifest.py) is not used to decide the bucket -- an
"akka"-named repo can be an unrelated personal project (e.g. an interview
demo app), so only the ~/akka/ path signals real company work. Remote is
still shown in the flagged report as context for manual review.

Usage:
  classify_merge.py MANIFEST.json --staging DIR --cutoff 2026-09-14 \
      --work-path ~/akka --force-personal ~/development/akka-demo \
      --dest-personal ~/.claude-personal --dest-work ~/.claude-work [--apply]

Dry-run (no --apply) only prints the classification report; nothing is
copied. Existing destination files are never overwritten.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def classify(entry: dict, cutoff: str, work_paths: list[str], force_personal: list[str]) -> tuple[str, str]:
    cwd = entry.get("cwd")
    if cwd and cwd in force_personal:
        return "personal", "force_personal_path"

    if entry.get("error"):
        return "flagged", "no_user_message"

    ts = entry["timestamp"]
    if ts < cutoff:
        return "personal", "before_cutoff"

    if cwd and any(cwd == p or cwd.startswith(p.rstrip("/") + "/") for p in work_paths):
        return "work", f"under_work_path:{cwd}"

    return "flagged", "not_under_work_path"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--staging", required=True, help="root dir containing the source projects/ tree (paths in manifest 'file' entries)")
    ap.add_argument("--cutoff", required=True, help="ISO date/time; sessions before this are personal")
    ap.add_argument("--work-path", action="append", default=[], help="cwd path prefix that marks a session as work, e.g. ~/akka (repeatable)")
    ap.add_argument("--force-personal", action="append", default=[], help="cwd path prefix that's always personal regardless of date, e.g. an interview demo repo (repeatable)")
    ap.add_argument("--dest-personal", required=True)
    ap.add_argument("--dest-work", required=True)
    ap.add_argument("--apply", action="store_true", help="actually copy files; default is dry-run report only")
    args = ap.parse_args()

    with open(args.manifest) as f:
        entries = json.load(f)

    work_paths = [str(Path(p).expanduser()) for p in args.work_path]
    force_personal = [str(Path(p).expanduser()) for p in args.force_personal]

    dest = {"personal": Path(args.dest_personal), "work": Path(args.dest_work)}
    counts = {"personal": 0, "work": 0, "flagged": 0}
    flagged = []
    copied, skipped_existing = [], []

    for entry in entries:
        bucket, reason = classify(entry, args.cutoff, work_paths, force_personal)
        counts[bucket] += 1

        if bucket == "flagged":
            flagged.append({**entry, "reason": reason})
            continue

        src_file = Path(args.staging) / "projects" / entry["project_dir"] / f"{entry['session_id']}.jsonl"
        dest_file = dest[bucket] / "projects" / entry["project_dir"] / f"{entry['session_id']}.jsonl"
        if args.apply:
            if dest_file.exists():
                skipped_existing.append(str(dest_file))
                continue
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_file)
            copied.append(str(dest_file))
        else:
            copied.append(f"[dry-run] {src_file} -> {dest_file}")

    print(f"personal={counts['personal']}  work={counts['work']}  flagged={counts['flagged']}")
    print()
    if flagged:
        print(f"-- {len(flagged)} flagged for manual review --")
        for e in flagged:
            print(f"  {e['project_dir']}/{e['session_id']}.jsonl  cwd={e.get('cwd')}  reason={e['reason']}")
        print()
    if skipped_existing:
        print(f"-- {len(skipped_existing)} skipped, already present at destination --")
    if not args.apply:
        print(f"(dry-run: {len(copied)} would be copied; re-run with --apply to write)")
    else:
        print(f"{len(copied)} session files copied.")


if __name__ == "__main__":
    main()

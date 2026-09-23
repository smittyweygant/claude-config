# history-merge

Pulls Claude Code session history from a machine that's never had the
personal/work profile split (a single unprofiled `~/.claude`) and files it
into `~/.claude-personal` and `~/.claude-work` on the machine you run this
from.

Not installed by `install.sh` — this isn't portable config, it's a one-off
migration tool kept here for reuse/reference.

## Why the pull runs from here, not the other machine

If the other machine has a policy against inbound SSH/rsync connections
(e.g. CrowdStrike), it can't push files in — so this machine has to be the
SSH client, pulling instead of being pushed to. If your setup doesn't have
that constraint, a straightforward `rsync -e ssh` in either direction works
just as well; the two-script split below is about the classification logic,
not the transfer direction.

## Usage

1. **On the source machine** (read-only, never modifies anything):
   ```
   python3 manifest.py ~/.claude > manifest.json
   ```
   Scans `projects/*/*.jsonl`, and for each session records its id, project
   dir, first-message timestamp/cwd, and (if the cwd is still a live git
   repo) its `origin` remote.

2. **Pull the manifest and the referenced session files** to the machine
   doing the merge, e.g.:
   ```
   scp source-host:manifest.json .
   rsync -avz -e ssh source-host:.claude/projects/ ./staging/projects/
   ```

3. **Classify and merge** — dry-run first:
   ```
   python3 classify_merge.py manifest.json \
     --staging ./staging \
     --cutoff 2026-09-14 \
     --work-path ~/akka \
     --force-personal ~/development/some-personal-repo-with-a-misleading-name \
     --dest-personal ~/.claude-personal \
     --dest-work ~/.claude-work
   ```
   Review the `flagged` list (no cwd/repo signal at all, or post-cutoff and
   not under a `--work-path`) before deciding anything — then re-run with
   `--apply` once you're satisfied. Existing destination files are never
   overwritten.

## Classification rule

- `--force-personal PATH` (exact cwd match, **not** a prefix) → always
  personal, regardless of date. For a repo whose name/remote would
  otherwise look work-related (an interview demo app, a fork of a company
  project, etc.) — remote-URL matching isn't used for classification
  precisely because of cases like this.
- Before `--cutoff` → personal, unconditionally.
- On/after `--cutoff`, cwd under a `--work-path` prefix → work.
- Otherwise → **flagged**, not auto-personal. Work can happen outside the
  usual work-path convention (a new job's first day or two, before you've
  settled on a directory layout, is a real case this hit) — a wrong
  auto-personal guess here is worse than one more thing to confirm by hand.

Git remote is still captured in the manifest and shown for flagged entries
as extra context, but doesn't drive the bucket — the interview-demo-repo
scenario above is exactly the case where a remote/keyword match on the
company name would misfire.

## Gotchas hit while building this

- System `python3` on macOS is often 3.9, which doesn't support bare
  `X | None` type hints — both scripts start with
  `from __future__ import annotations` to stay compatible.
- If your SSH agent (1Password's, for instance) holds several keys, it may
  offer all of them and trip the server's `MaxAuthTries` before your
  intended key gets a turn. Pin one key per host instead of relying on the
  agent to guess:
  ```
  # ~/.ssh/config.local (or config)
  Host source-host
    HostName 192.168.x.x
    IdentityFile ~/.ssh/some_key.pub
    IdentitiesOnly yes
  ```
- `--force-personal` must match the cwd **exactly** — an earlier version
  matched by path prefix, so adding a home directory (`/Users/you`) as an
  override silently swallowed every other path under it, including the
  work ones. Exact match only; there's no need for prefix matching here
  since session cwds are always project roots.

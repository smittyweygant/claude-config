# Write one row per Claude Code session transcript to a JSONL file.
#
# Run as: python3 -I sessions.py [projects-root] [out-file]
#
# The root defaults to ~/.claude-shared/projects, where both profiles' history
# is merged. The out file defaults to data/sessions.jsonl in this repo, which is
# gitignored. Rows hold counts and ids, never prompt text. Project directory
# names can carry customer names, so the file stays out of version control.
#
# Token rules match usage.py: each message id counts once, and all_total is
# input + cache write + cache read + output. Subagent transcripts live beside
# the session as <session-id>/subagents/agent-*.jsonl and are summed separately.
#
# An unknown line type or an unparseable line stops the run. That is how a
# format change in Claude Code shows up here instead of as quietly wrong numbers.
import glob, json, os, sys
from collections import Counter

KNOWN_TYPES = {
    "agent-color", "agent-name", "ai-title", "api-request", "api-request-blob",
    "api-request-shape", "artifact-autoreact-ledger", "artifact-comment-monitor",
    "assistant", "atis-latch", "attachment", "bridge-session", "continued-in",
    "cost-state", "custom-title", "file-history-delta", "file-history-snapshot",
    "frame-link", "last-prompt", "mode", "permission-mode", "pr-link",
    "queue-operation", "system", "tools-used", "user",
}
IDLE_GAP_SECONDS = 300


def read_lines(path):
    with open(path) as f:
        for n, line in enumerate(f, 1):
            try:
                d = json.loads(line)
            except ValueError:
                sys.exit(f"{path}:{n}: not JSON")
            if d.get("type") not in KNOWN_TYPES:
                sys.exit(f"{path}:{n}: unknown line type {d.get('type')!r}")
            yield d


def context_slope(contexts):
    # Least-squares slope of per-call context size against call index.
    n = len(contexts)
    if n < 2:
        return 0.0
    mx, my = (n - 1) / 2, sum(contexts) / n
    num = sum((i - mx) * (y - my) for i, y in enumerate(contexts))
    den = sum((i - mx) ** 2 for i in range(n))
    return num / den


def parse_ts(s):
    from datetime import datetime
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def usage_totals(seen):
    t = dict(calls=len(seen), input=0, cache_write=0, cache_read=0, output=0)
    for u, _ in seen.values():
        t["input"] += u.get("input_tokens", 0)
        t["cache_write"] += u.get("cache_creation_input_tokens", 0)
        t["cache_read"] += u.get("cache_read_input_tokens", 0)
        t["output"] += u.get("output_tokens", 0)
    t["fresh_total"] = t["input"] + t["cache_write"] + t["output"]
    t["all_total"] = t["fresh_total"] + t["cache_read"]
    return t


def scan(path):
    seen, tools, stamps = {}, Counter(), []
    errors = prompts = compactions = 0
    for d in read_lines(path):
        if d.get("timestamp"):
            stamps.append(parse_ts(d["timestamp"]))
        m = d.get("message") or {}
        if d["type"] == "assistant":
            if m.get("usage"):
                seen[m.get("id") or d.get("uuid")] = (m["usage"], m.get("model"))
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tools[c["name"]] += 1
        elif d["type"] == "user":
            if (d.get("origin") or {}).get("kind") == "human":
                prompts += 1
            if isinstance(m.get("content"), list):
                errors += sum(1 for c in m["content"]
                              if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"))
        elif d["type"] == "system" and d.get("subtype") == "compact_boundary":
            compactions += 1
    return seen, tools, stamps, errors, prompts, compactions


def active_seconds(stamps):
    stamps = sorted(stamps)
    return sum(b - a for a, b in zip(stamps, stamps[1:]) if b - a <= IDLE_GAP_SECONDS)


def row(path):
    seen, tools, stamps, errors, prompts, compactions = scan(path)
    t = usage_totals(seen)
    contexts = [u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                + u.get("cache_read_input_tokens", 0) for u, _ in seen.values()]
    models = Counter(m for _, m in seen.values() if m)

    sid = os.path.basename(path)[:-len(".jsonl")]
    sub_files = sorted(glob.glob(os.path.join(os.path.dirname(path), sid, "subagents", "agent-*.jsonl")))
    sub = Counter()
    for sf in sub_files:
        st = usage_totals(scan(sf)[0])
        sub["calls"] += st["calls"]
        sub["all_total"] += st["all_total"]
        sub["fresh_total"] += st["fresh_total"]
        sub["output"] += st["output"]

    return dict(
        session_id=sid,
        project=os.path.basename(os.path.dirname(path)),
        **t,
        avg_context=round(t["all_total"] / t["calls"]) if t["calls"] else 0,
        context_growth_per_call=round(context_slope(contexts)),
        subagent_files=len(sub_files),
        subagent_calls=sub["calls"],
        subagent_all_total=sub["all_total"],
        subagent_fresh_total=sub["fresh_total"],
        subagent_output=sub["output"],
        agent_tool_calls=tools["Agent"],
        model=models.most_common(1)[0][0] if models else None,
        tools=dict(tools),
        tool_errors=errors,
        compactions=compactions,
        active_seconds=round(active_seconds(stamps)),
        human_prompts=prompts,
        first_ts=min(stamps) if stamps else None,
    )


def main():
    root = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/.claude-shared/projects")
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "data", "sessions.jsonl")
    rows = [row(p) for p in sorted(glob.glob(os.path.join(root, "*", "*.jsonl")))]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with_usage = [r for r in rows if r["calls"]]
    missing = [r for r in rows if r["agent_tool_calls"] and not r["subagent_files"]]
    print(json.dumps(dict(
        rows=len(rows), rows_with_usage=len(with_usage),
        all_total=sum(r["all_total"] for r in rows),
        subagent_all_total=sum(r["subagent_all_total"] for r in rows),
        rows_with_subagents=sum(1 for r in rows if r["subagent_files"]),
        rows_missing_subagents=len(missing),
        compactions=sum(r["compactions"] for r in rows),
        out=out,
    )))


if __name__ == "__main__":
    main()

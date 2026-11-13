# Cut each session transcript into per-issue slices and write one row per slice.
#
# Run as: python3 -I slices.py [projects-root] [out-file]
#
# The root defaults to ~/.claude-shared/projects. The out file defaults to
# data/slices.jsonl in this repo, which is gitignored like sessions.jsonl.
#
# Each call (assistant message id, counted once as in usage.py) gets an issue:
#   1. branch   the number in a gitBranch like "11-issue-slices"
#   2. gh       the last issue named by a gh issue comment/edit/close, git checkout -b,
#               or "Closes #N" before the call (reads like gh issue view do not count)
#   3. prompt   the first "#N" in the session's first human prompt
#   4. none     unlinked; kept as an issue-less slice so totals still add up
# Calls on main or HEAD have no branch signal and fall through to the gh rule,
# which also carries the last-seen issue forward after a branch is left.
# Subagent calls join the issue of their own gitBranch, else the session's
# largest work slice, and are reported apart from the main calls.
import glob, json, os, re, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sessions import read_lines, usage_totals  # noqa: E402

BRANCH_ISSUE = re.compile(r"^(\d+)-")
GH_REF = re.compile(r"gh issue (?:comment|edit|close) #?(\d+)|Closes #(\d+)|checkout -b (\d+)-")
PROMPT_REF = re.compile(r"(?:#|\bissue )(\d+)")


def evidence(d):
    # Issue number named by this line, with the source that named it.
    b = BRANCH_ISSUE.match(d.get("gitBranch") or "")
    if b:
        return int(b.group(1)), "branch"
    m = d.get("message") or {}
    for c in m.get("content") or [] if d["type"] == "assistant" else []:
        if isinstance(c, dict) and c.get("type") == "tool_use" and c["name"] == "Bash":
            r = GH_REF.search(c["input"].get("command", ""))
            if r:
                return int(next(g for g in r.groups() if g)), "gh"
    return None


def cut(path):
    # Returns [(id, (usage, model, issue, source))] in call order for one transcript.
    calls, ev, closed, first_prompt = {}, None, None, None
    for d in read_lines(path):
        if d["type"] == "user" and first_prompt is None and (d.get("origin") or {}).get("kind") == "human":
            c = (d.get("message") or {}).get("content")
            first_prompt = c if isinstance(c, str) else json.dumps(c)
            r = PROMPT_REF.search(first_prompt)
            if r:
                ev = (int(r.group(1)), "prompt")
        e = evidence(d)
        if e:
            ev = (e[0], "carry")
        m = d.get("message") or {}
        if d["type"] != "assistant" or not m.get("usage"):
            continue
        own = BRANCH_ISSUE.match(d.get("gitBranch") or "")
        cur = (int(own.group(1)), "branch") if own else ev
        key = m.get("id") or d.get("uuid")
        if cur and closed == cur[0]:
            cur = (cur[0], "post-pr")
        calls[key] = (m["usage"], m.get("model"), cur[0] if cur else None, cur[1] if cur else "none")
        if any(c.get("type") == "tool_use" and c["name"] == "Bash" and "gh pr create" in c["input"].get("command", "")
               for c in m.get("content") or [] if isinstance(c, dict)):
            closed = cur[0] if cur else None
    return list(calls.items())


def slices(path):
    sid = os.path.basename(path)[:-len(".jsonl")]
    by = defaultdict(dict)
    for key, (u, model, issue, source) in cut(path):
        by[(issue, source)][key] = (u, model)
    work = [k for k in by if k[1] != "post-pr"]
    dominant = max(work, key=lambda k: len(by[k]))[0] if work else None
    sub = defaultdict(lambda: {"calls": 0, "all_total": 0})
    for sf in glob.glob(os.path.join(os.path.dirname(path), sid, "subagents", "agent-*.jsonl")):
        cuts = cut(sf)
        seen = {k: (u, m) for k, (u, m, _, _) in cuts}
        issues = {i for _, (_, _, i, s) in cuts if s == "branch"}
        issue = issues.pop() if len(issues) == 1 else dominant
        t = usage_totals(seen)
        sub[issue]["calls"] += t["calls"]
        sub[issue]["all_total"] += t["all_total"]
    # A subagent total goes on the first work row for its issue; if the main
    # session never worked that issue, it gets a row of its own with no main calls.
    for issue in sub:
        if not any(k[0] == issue for k in work):
            by[(issue, "subagent")] = {}
    rows = []
    for issue, source in sorted(by, key=lambda k: (k[0] is None, k[0] or 0, k[1])):
        t = usage_totals(by[(issue, source)])
        s = sub.pop(issue, {"calls": 0, "all_total": 0}) if source != "post-pr" else {"calls": 0, "all_total": 0}
        rows.append(dict(session_id=sid, project=os.path.basename(os.path.dirname(path)),
                         issue=issue, source=source, **t,
                         subagent_calls=s["calls"], subagent_all_total=s["all_total"]))
    return rows


def main():
    root = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/.claude-shared/projects")
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "data", "slices.jsonl")
    rows = [r for p in sorted(glob.glob(os.path.join(root, "*", "*.jsonl"))) for r in slices(p)]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    by_source = defaultdict(lambda: [0, 0])
    for r in rows:
        by_source[r["source"]][0] += r["calls"]
        by_source[r["source"]][1] += r["all_total"]
    print(json.dumps(dict(slices=len(rows), by_source=by_source, out=out)))


if __name__ == "__main__":
    main()

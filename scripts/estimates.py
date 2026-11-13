# Join the vault estimate log to slices.jsonl and write one row per issue.
#
# Run as: python3 -I estimates.py [note-file] [slices-file] [out-file]
#
# The note defaults to the vault's Agent Work Estimation.md, slices to
# data/slices.jsonl (run slices.py first), out to data/issues.jsonl in this repo.
#
# Each log entry has a heading "### <date> <sep> <project> #<issue> ..." and a
# table whose rows are calls, all_total, fresh, output with an Estimate and an
# Actual column. Estimates become lo/hi (equal for a point estimate). Actuals
# become one number: the leading figure, plus a review subagent when the cell
# reads "(+53k review)". Entries with no such table are in MANUAL below, read
# by hand from the note. A table that is a summary over several issues
# (its calls row is not exactly "calls") is skipped.
#
# An issue logged in several entries gets one row; lo, hi and actuals add up.
# Every issue that has a slice also gets a row, with blank estimate fields when
# the note has no entry. Issue-less slices are left out.
import json, os, re, sys
from collections import defaultdict

FIELDS = ("calls", "all_total", "fresh", "output")
ENTRY = re.compile(r"^### (\d{4}-\d\d-\d\d)\s*[:—-]\s*(finances|claude-config) #(\d+)")
NUM = re.compile(r"(\d+(?:\.\d+)?)\s*([kM]?)")
REVIEW = re.compile(r"\(\+\s*~?(\d+(?:\.\d+)?)\s*([kM])\s*review")
SCALE = {"": 1, "k": 1e3, "M": 1e6}

# (project, issue): (estimate {field: (lo, hi)}, actual {field: n}).
# #63-#65 are rows of one per-issue table inside a three-issue entry; #90 is prose.
MANUAL = {
    ("finances", 63): ({"calls": (24, 24), "all_total": (1.8e6, 1.8e6)},
                       {"calls": 15, "all_total": 1.17e6, "fresh": 61e3, "output": 7e3}),
    ("finances", 64): ({"calls": (32, 32), "all_total": (2.4e6, 2.4e6)},
                       {"calls": 8, "all_total": 0.73e6, "fresh": 104e3, "output": 3e3}),
    ("finances", 65): ({"calls": (22, 22), "all_total": (1.65e6, 1.65e6)},
                       {"calls": 7, "all_total": 0.68e6, "fresh": 48e3, "output": 3e3}),
    ("finances", 90): ({"calls": (16, 16), "all_total": (1.2e6, 1.2e6)},
                       {"calls": 11, "all_total": 0.90e6, "fresh": 15e3, "output": 5e3}),
}


def figures(cell):
    # Numbers in a cell as floats. A bare number takes the unit of the last one
    # ("150-300k"), and the unit of any number after it too.
    toks = NUM.findall(cell.replace(",", ""))
    unit = next((u for _, u in reversed(toks) if u), "")
    return [float(v) * SCALE[u or unit] for v, u in toks]


def estimate(cell):
    f = figures(cell)
    return (min(f), max(f)) if f else None


def actual(cell):
    f = figures(cell)
    if not f:
        return None
    r = REVIEW.search(cell)
    return f[0] + (float(r.group(1)) * SCALE[r.group(2)] if r else 0)


def entries(text):
    # [(project, issue, date, estimate, actual)] from the note, in file order.
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("#"):
            m = ENTRY.match(line)
            cur = [m.group(2), int(m.group(3)), m.group(1), {}, {}] if m else None
            if cur and (cur[0], cur[1]) not in MANUAL:
                out.append(cur)
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cur and line.startswith("|") and len(cells) == 3 and cells[0].lower() in FIELDS:
            e, a = estimate(cells[1]), actual(cells[2])
            if e:
                cur[3][cells[0].lower()] = e
            if a is not None:
                cur[4][cells[0].lower()] = a
    return [e for e in out if e[3] and e[4].get("all_total")]


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    note = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else
                              "~/Obsidian/Smitty's Vault/Projects/Coding Agent Orchestration/Agent Work Estimation.md")
    sl = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "data", "slices.jsonl")
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(here, "data", "issues.jsonl")

    rows = {}
    def row(project, issue):
        return rows.setdefault((project, issue), dict(
            project=project, issue=issue, entries=0, slice_calls=0, slice_all_total=0, slice_sessions=set()))

    logged = entries(open(note).read()) + [(p, i, None, e, a) for (p, i), (e, a) in MANUAL.items()]
    for p, i, _, e, a in logged:
        r = row(p, i)
        r["entries"] += 1
        for f in FIELDS:
            if f in e:
                r[f"est_{f}_lo"] = (r.get(f"est_{f}_lo") or 0) + e[f][0]
                r[f"est_{f}_hi"] = (r.get(f"est_{f}_hi") or 0) + e[f][1]
            if f in a:
                r[f"act_{f}"] = (r.get(f"act_{f}") or 0) + a[f]

    for line in open(sl):
        s = json.loads(line)
        proj = next((p for p in ("finances", "claude-config") if s["project"].endswith("-" + p)), None)
        if s["issue"] is None or proj is None:
            continue
        r = row(proj, s["issue"])
        r["slice_calls"] += s["calls"] + s["subagent_calls"]
        r["slice_all_total"] += s["all_total"] + s["subagent_all_total"]
        r["slice_sessions"].add(s["session_id"][:8])

    with open(out, "w") as f:
        for k in sorted(rows):
            r = rows[k]
            r["slice_sessions"] = sorted(r["slice_sessions"])
            f.write(json.dumps(r) + "\n")
    est = [r for r in rows.values() if r["entries"]]
    print(json.dumps(dict(rows=len(rows), with_estimate=len(est),
                          no_slice=[(r["project"], r["issue"]) for r in est if not r["slice_calls"]],
                          out=out)))


if __name__ == "__main__":
    main()

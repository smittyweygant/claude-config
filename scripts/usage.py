# Sum token usage in a Claude Code session transcript.
#
# Run as: python3 -I usage.py <session>.jsonl
#
# Transcripts live at <config dir>/projects/<project-dir>/<session-id>.jsonl.
# On the personal profile the config dir is ~/.claude-personal. On the work
# profile the root may differ. The script takes a path, so either works.
#
# A message can appear on several transcript lines, so each message id is
# counted once. Subagent (fork) usage is not in the main transcript.
import json, sys
seen = {}
for line in open(sys.argv[1]):
    try: d = json.loads(line)
    except ValueError: continue
    m = d.get("message") or {}
    if d.get("type") == "assistant" and m.get("usage"):
        seen[m.get("id") or d.get("uuid")] = m["usage"]
t = dict(calls=len(seen), input=0, cache_write=0, cache_read=0, output=0)
for u in seen.values():
    t["input"] += u.get("input_tokens", 0)
    t["cache_write"] += u.get("cache_creation_input_tokens", 0)
    t["cache_read"] += u.get("cache_read_input_tokens", 0)
    t["output"] += u.get("output_tokens", 0)
t["fresh_total"] = t["input"] + t["cache_write"] + t["output"]
t["all_total"] = t["fresh_total"] + t["cache_read"]
# cost is in input-token equivalents: what the same spend would buy as plain
# input. Weights are multiples of the base input price: cache reads 0.1x,
# 1-hour cache writes 2x (5-minute writes are 1.25x), output 5x. Check them
# against the current pricing page; they differ by model and cache TTL.
t["cost"] = round(t["input"] + 2 * t["cache_write"] + 0.1 * t["cache_read"] + 5 * t["output"])
print(json.dumps(t))

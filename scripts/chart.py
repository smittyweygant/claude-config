# Draw the estimate and token data as one self-contained HTML page.
#
# Run as: python3 -I chart.py [issues-file] [sessions-file] [out-file]
#
# Defaults: data/issues.jsonl, data/sessions.jsonl (run estimates.py and
# sessions.py first), and data/charts.html in this repo.
#
# Two views, drawn as static inline SVG with no script:
#   1. all_total estimate range against the actual, one row per issue that has
#      both, on a log axis.
#   2. share of all_total by session length (calls per session).
#
# Only numbers, issue numbers and the two repo names reach the page. Session
# ids and project paths stay out: project paths carry customer names.
import json, math, os, sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
BUCKETS = [(1, 10, "1-10"), (11, 30, "11-30"), (31, 100, "31-100"), (101, 10**9, "100+")]
REPOS = ("finances", "claude-config")


def rows(path):
    return [json.loads(line) for line in open(path) if line.strip()]


def fmt(n):
    if n >= 1e9:
        return f"{n / 1e9:.2f}B"
    return f"{n / 1e6:.2f}M" if n >= 1e6 else f"{n / 1e3:.0f}k"


def estimate_chart(issues):
    pts = [r for r in issues
           if r.get("est_all_total_lo") and r.get("act_all_total") and r["project"] in REPOS]
    pts.sort(key=lambda r: (r["project"], r["issue"]))
    lo_v = min(min(r["est_all_total_lo"], r["act_all_total"]) for r in pts) * 0.8
    hi_v = max(max(r["est_all_total_hi"], r["act_all_total"]) for r in pts) * 1.25
    l0, l1 = math.log10(lo_v), math.log10(hi_v)
    left, right, top, row_h = 130, 20, 28, 20
    width = 760
    height = top + row_h * len(pts) + 12

    def x(v):
        return left + (math.log10(v) - l0) / (l1 - l0) * (width - left - right)

    out = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Estimate range and actual all_total per issue">']
    tick = 10 ** math.ceil(l0)
    while tick <= hi_v:
        for m in (1, 2, 5):
            v = tick * m
            if lo_v <= v <= hi_v:
                out.append(f'<line class="grid" x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top - 6}" y2="{height - 12}"/>'
                           f'<text class="axis" x="{x(v):.1f}" y="{top - 12}" text-anchor="middle">{fmt(v)}</text>')
        tick *= 10
    for i, r in enumerate(pts):
        y = top + i * row_h + row_h / 2
        lo, hi, act = r["est_all_total_lo"], r["est_all_total_hi"], r["act_all_total"]
        label = f'{r["project"]} #{r["issue"]}'
        tip = f'{label}: estimate {fmt(lo)}-{fmt(hi)}, actual {fmt(act)}'
        if act > hi:
            state = "over"
        elif act < lo:
            state = "under"
        else:
            state = "in"
        out.append(f'<g><title>{escape(tip)}</title>'
                   f'<text class="rowlabel" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{escape(label)}</text>'
                   f'<rect class="range" x="{x(lo):.1f}" y="{y - 4:.1f}" width="{max(x(hi) - x(lo), 3):.1f}" height="8" rx="4"/>'
                   f'<circle class="act {state}" cx="{x(act):.1f}" cy="{y:.1f}" r="5"/></g>')
    out.append("</svg>")
    return "".join(out), len(pts), sum(1 for r in pts if r["est_all_total_lo"] <= r["act_all_total"] <= r["est_all_total_hi"])


def length_chart(sessions):
    tot = {b[2]: 0 for b in BUCKETS}
    cnt = {b[2]: 0 for b in BUCKETS}
    for s in sessions:
        for lo, hi, name in BUCKETS:
            if lo <= s["calls"] <= hi:
                tot[name] += s["all_total"]
                cnt[name] += 1
                break
    grand = sum(tot.values())
    width, left, right, top, row_h = 760, 90, 150, 8, 34
    height = top + row_h * len(BUCKETS) + 4
    out = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Share of all_total by session length">']
    for i, (_, _, name) in enumerate(BUCKETS):
        share = tot[name] / grand
        y = top + i * row_h
        w = share * (width - left - right)
        tip = f'{name} calls: {cnt[name]} sessions, {fmt(tot[name])} all_total, {share:.0%} of spend'
        out.append(f'<g><title>{escape(tip)}</title>'
                   f'<text class="rowlabel" x="{left - 8}" y="{y + 18}" text-anchor="end">{name} calls</text>'
                   f'<rect class="bar" x="{left}" y="{y + 4}" width="{max(w, 2):.1f}" height="22" rx="4"/>'
                   f'<text class="value" x="{left + max(w, 2) + 8:.1f}" y="{y + 19}">{share:.0%} · {cnt[name]} sessions</text></g>')
    out.append("</svg>")
    return "".join(out), grand


PAGE = """<title>Estimate and Spend Charts</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Two stacked charts in a single column; bars carry one hue, status dots carry state. */
:root{--bg:#f6f7f8;--fg:#1d2430;--muted:#5d6877;--grid:#dde1e6;--range:#b9c6d6;--accent:#2a5f9e;--over:#b3412c;--under:#2f7d5b;--in:#2a5f9e;--ring:#f6f7f8;
--font:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#14181f;--fg:#e4e8ee;--muted:#9aa5b5;--grid:#2a313c;--range:#3b4b60;--accent:#6fa3e0;--over:#e2745e;--under:#5cc197;--in:#6fa3e0;--ring:#14181f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#14181f;--fg:#e4e8ee;--muted:#9aa5b5;--grid:#2a313c;--range:#3b4b60;--accent:#6fa3e0;--over:#e2745e;--under:#5cc197;--in:#6fa3e0;--ring:#14181f;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:15px/1.5 var(--font);padding-block:24px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:800px;margin:0 auto;display:flex;flex-direction:column;gap:32px}
h1{font-size:1.5rem;margin:0;text-wrap:balance}
h2{font-size:1.1rem;margin:0 0 4px;text-wrap:balance}
p{margin:0;color:var(--muted);max-width:65ch}
section{display:flex;flex-direction:column;gap:12px;min-width:0}
.scroll{overflow-x:auto}
svg{display:block;width:100%;min-width:560px;height:auto}
text{font-family:var(--mono);font-size:11px;fill:var(--muted)}
.rowlabel,.value{fill:var(--fg)}
.grid{stroke:var(--grid);stroke-width:1}
.range{fill:var(--range)}
.bar{fill:var(--accent)}
.act{stroke:var(--ring);stroke-width:2}
.act.over{fill:var(--over)}.act.under{fill:var(--under)}.act.in{fill:var(--in)}
.key{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--muted)}
.key span{display:inline-flex;align-items:center;gap:6px}
.swatch{width:18px;height:8px;border-radius:4px;background:var(--range)}
.dot{width:10px;height:10px;border-radius:50%}
.dot.over{background:var(--over)}.dot.under{background:var(--under)}.dot.in{background:var(--in)}
</style>
<main>
<h1>Estimate and Spend Charts</h1>
<section>
<h2>Estimate against actual, tokens processed per issue</h2>
<p>__SUMMARY1__ Log scale. Hover a row for the figures.</p>
<div class="key"><span><i class="swatch"></i>estimate range</span><span><i class="dot in"></i>actual inside range</span><span><i class="dot over"></i>actual over</span><span><i class="dot under"></i>actual under</span></div>
<div class="scroll">__CHART1__</div>
</section>
<section>
<h2>Share of tokens by session length</h2>
<p>__SUMMARY2__</p>
<div class="scroll">__CHART2__</div>
</section>
</main>
"""


def main():
    issues_f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, "issues.jsonl")
    sessions_f = sys.argv[2] if len(sys.argv) > 2 else os.path.join(DATA, "sessions.jsonl")
    out_f = sys.argv[3] if len(sys.argv) > 3 else os.path.join(DATA, "charts.html")
    c1, n, hit = estimate_chart(rows(issues_f))
    c2, grand = length_chart(rows(sessions_f))
    page = (PAGE.replace("__CHART1__", c1).replace("__CHART2__", c2)
            .replace("__SUMMARY1__", f"{hit} of {n} issues landed inside their estimate range.")
            .replace("__SUMMARY2__", f"{fmt(grand)} all_total in main sessions, grouped by calls per session."))
    with open(out_f, "w") as f:
        f.write(page)
    print(f"wrote {out_f}")


if __name__ == "__main__":
    main()

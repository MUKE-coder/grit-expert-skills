#!/usr/bin/env python3
"""Write the token spend dashboard: one self-contained HTML file.

    python3 spend_dashboard.py --project . --out .grit/spend.html

This renders. It does not read transcripts.

That split is deliberate. grit-tokens' token_report.py is the only thing in
this pack that reads Claude Code's transcripts, and it writes everything it
learns to .grit/token-usage.json. A second reader would be a second set of
totals, and the day the two disagreed there would be no way to tell which was
right. So this script refreshes that state by calling the one reader, then
draws it.

Everything is inline: no CDN, no fonts fetched, no JavaScript beyond column
sorting. The file opens from disk, in a browser with no network, in a year.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys

STATE_VERSION = 2

# The reader, relative to this script: ../../grit-tokens/scripts/token_report.py
READER = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "grit-tokens", "scripts", "token_report.py",
))


# ------------------------------------------------------------------ numbers
def billable(b: dict) -> int:
    return (b.get("input", 0) or 0) + (b.get("output", 0) or 0) + (b.get("cache_write", 0) or 0)


def raw(b: dict) -> int:
    return billable(b) + (b.get("cache_read", 0) or 0)


def human(n: float) -> str:
    n = float(n or 0)
    if n >= 1e9:
        return f"{n / 1e9:.2f}B"
    if n >= 1e6:
        return f"{n / 1e6:.2f}M"
    if n >= 1e3:
        return f"{n / 1e3:.1f}k"
    return str(int(n))


def money(n: float) -> str:
    return f"${n:,.2f}"


def esc(value) -> str:
    return (str(value)
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def short_when(stamp) -> str:
    """A timestamp as "12 Nov 14:02", or "" when there is not one."""
    if not stamp or len(str(stamp)) < 16:
        return ""
    s = str(stamp)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    try:
        month = months[int(s[5:7]) - 1]
    except (ValueError, IndexError):
        return s[:16]
    return f"{int(s[8:10])} {month} {s[11:16]}"


def top_tools(tools: dict, limit: int = 3) -> str:
    if not tools:
        return ""
    rows = sorted(tools.items(), key=lambda kv: -kv[1])[:limit]
    return ", ".join(f"{name} {count}" for name, count in rows)


# ------------------------------------------------------------------- charts
#
# Inline SVG, drawn from the numbers. No chart library: the shapes here are a
# bar and a line, and a dependency fetched from a CDN would make this file
# stop working offline, which is the one thing it has to do.


# A label goes ABOVE its bar, not inside it.
#
# Inside is tidier when every label is short, and these are not: a task is
# labelled with how the request opened and a tool with its full name, so
# "mcp__playwright__browser_evaluate" on a bar two thirds of the way down ran
# out of bar and printed itself over its own value. Above the bar, the label
# has the full width whatever the bar is worth.
LABEL_CHARS = 84


def bar_chart(rows, value, label, *, width=760, row_h=38) -> str:
    """One row per entry, dearest first: label, value, and a bar beneath."""
    if not rows:
        return "<p class='empty'>Nothing recorded yet.</p>"
    top = max(value(r) for r in rows) or 1
    out = []
    for i, r in enumerate(rows):
        y = i * row_h
        w = max(2.0, (value(r) / top) * width)
        text = str(label(r))
        if len(text) > LABEL_CHARS:
            text = text[:LABEL_CHARS - 3].rstrip() + "..."
        out.append(
            f'<text class="bar-label" x="0" y="{y + 12}">{esc(text)}</text>'
            f'<text class="bar-value" x="{width}" y="{y + 12}" text-anchor="end">'
            f'{esc(human(value(r)))}</text>'
            f'<rect class="bar" x="0" y="{y + 18}" width="{w:.1f}" height="10" rx="3">'
            f'<title>{esc(text)}: {esc(human(value(r)))} billable</title></rect>'
        )
    total_h = len(rows) * row_h
    return (f'<svg class="chart" viewBox="0 0 {width} {total_h}" '
            f'width="100%" height="{total_h}" role="img">' + "".join(out) + "</svg>")


def day_chart(days: dict, *, width=760, height=180) -> str:
    """Billable tokens per day, as columns, with the dearest day marked.

    Columns rather than a line: the gaps are days nobody worked, and a line
    would draw straight through them and invent work that did not happen.
    """
    keys = sorted(k for k in days if k and k != "unknown")
    if not keys:
        return "<p class='empty'>No dated activity yet.</p>"
    values = [billable(days[k]) for k in keys]
    top = max(values) or 1
    inner = height - 34
    slot = width / len(keys)
    bar_w = max(1.0, min(slot - 2, 28.0))
    cols = []
    peak = values.index(max(values))
    for i, (k, v) in enumerate(zip(keys, values)):
        h = max(1, (v / top) * inner)
        x = i * slot + (slot - bar_w) / 2
        y = inner - h
        cls = "col peak" if i == peak else "col"
        cols.append(f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" '
                    f'width="{bar_w:.1f}" height="{h:.1f}" rx="2">'
                    f'<title>{esc(k)}: {esc(human(v))} billable</title></rect>')
    # Only the ends and the peak are labelled. Every day labelled is unreadable
    # the moment a project is more than a fortnight old.
    marks = {0: keys[0], len(keys) - 1: keys[-1]}
    if len(keys) > 2:
        marks[peak] = keys[peak]
    labels = []
    for i, k in sorted(marks.items()):
        x = i * slot + slot / 2
        anchor = "start" if i == 0 else ("end" if i == len(keys) - 1 else "middle")
        labels.append(f'<text class="tick" x="{x:.1f}" y="{inner + 16}" '
                      f'text-anchor="{anchor}">{esc(k[5:])}</text>')
    return (f'<svg class="chart" viewBox="0 0 {width} {height}" width="100%" '
            f'height="{height}" role="img">'
            f'<line class="axis" x1="0" y1="{inner}" x2="{width}" y2="{inner}"/>'
            + "".join(cols) + "".join(labels) +
            f'<text class="tick" x="0" y="{inner + 32}">'
            f'peak {esc(human(top))} billable on {esc(keys[peak])}</text></svg>')


def split_bar(parts, *, width=760, height=22) -> str:
    """One stacked bar: the share each part holds of the whole."""
    total = sum(v for _, v, _ in parts) or 1
    x = 0.0
    out = []
    for name, value, cls in parts:
        w = value / total * width
        if w <= 0:
            continue
        out.append(f'<rect class="seg {cls}" x="{x:.1f}" y="0" width="{w:.1f}" '
                   f'height="{height}" >'
                   f'<title>{esc(name)}: {esc(human(value))} '
                   f'({value / total * 100:.0f}%)</title></rect>')
        x += w
    return (f'<svg class="chart" viewBox="0 0 {width} {height}" width="100%" '
            f'height="{height}" role="img">' + "".join(out) + "</svg>")


# -------------------------------------------------------------------- table
def table(headers, rows, *, numeric=(), sortable=True) -> str:
    """A table whose columns sort on click.

    `numeric` are the column indexes that sort as numbers. The sort key is put
    in a data attribute rather than parsed back out of the text, because
    "11.80M" does not sort as a number and "$342.82" does not either.
    """
    head = []
    for i, h in enumerate(headers):
        cls = ' class="num"' if i in numeric else ""
        head.append(f'<th{cls} data-col="{i}">{esc(h)}</th>')
    body = []
    for r in rows:
        cells = []
        for i, (text, key) in enumerate(r):
            cls = ' class="num"' if i in numeric else ""
            attr = f' data-sort="{esc(key)}"' if key is not None else ""
            cells.append(f"<td{cls}{attr}>{text}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    cls = ' class="sortable"' if sortable else ""
    return (f"<table{cls}><thead><tr>" + "".join(head) + "</tr></thead><tbody>"
            + "".join(body) + "</tbody></table>")


SORT_JS = """
document.querySelectorAll('table.sortable th').forEach(function (th) {
  th.addEventListener('click', function () {
    var table = th.closest('table');
    var body = table.tBodies[0];
    var col = +th.dataset.col;
    var desc = th.dataset.dir !== 'desc';
    table.querySelectorAll('th').forEach(function (o) { delete o.dataset.dir; });
    th.dataset.dir = desc ? 'desc' : 'asc';
    var rows = Array.prototype.slice.call(body.rows);
    rows.sort(function (a, b) {
      var x = a.cells[col], y = b.cells[col];
      var xv = x.dataset.sort, yv = y.dataset.sort;
      if (xv !== undefined && yv !== undefined && xv !== '' && yv !== '') {
        var nx = parseFloat(xv), ny = parseFloat(yv);
        if (!isNaN(nx) && !isNaN(ny)) { return desc ? ny - nx : nx - ny; }
        return desc ? yv.localeCompare(xv) : xv.localeCompare(yv);
      }
      var xt = x.textContent.trim(), yt = y.textContent.trim();
      return desc ? yt.localeCompare(xt) : xt.localeCompare(yt);
    });
    rows.forEach(function (r) { body.appendChild(r); });
  });
});
"""

CSS = """
:root {
  color-scheme: light dark;
  --bg: #ffffff; --panel: #f7f7fa; --line: #e3e3ea;
  --fg: #16161d; --muted: #63636f; --faint: #8c8c98;
  --accent: #6c5ce7; --accent-soft: #ded9fb;
  --warm: #d97706; --cool: #0ea5e9; --good: #059669;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0a0a0f; --panel: #14141c; --line: #2a2a3a;
    --fg: #e8e8f0; --muted: #9090a8; --faint: #6c6c80;
    --accent: #8b7cf8; --accent-soft: #2b2550;
    --warm: #fbbf24; --cool: #74b9ff; --good: #34d399;
  }
}
:root[data-theme="dark"] {
  --bg: #0a0a0f; --panel: #14141c; --line: #2a2a3a;
  --fg: #e8e8f0; --muted: #9090a8; --faint: #6c6c80;
  --accent: #8b7cf8; --accent-soft: #2b2550;
  --warm: #fbbf24; --cool: #74b9ff; --good: #34d399;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  -webkit-text-size-adjust: 100%;
}
.wrap { max-width: 1060px; margin: 0 auto; padding: 48px 16px 96px; }
h1 { font-size: 26px; margin: 0 0 4px; letter-spacing: -0.01em; }
h2 { font-size: 17px; margin: 44px 0 6px; letter-spacing: -0.005em; }
.sub { color: var(--muted); margin: 0 0 32px; font-size: 14px; }
.note { color: var(--muted); font-size: 13.5px; margin: 6px 0 16px; max-width: 62ch; }
.empty { color: var(--faint); font-size: 14px; font-style: italic; }
.cards { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); }
.card {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 12px; padding: 14px 16px;
}
.card .k { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; }
.card .v { font-size: 25px; font-weight: 650; margin-top: 4px; letter-spacing: -0.02em; }
.card .w { color: var(--faint); font-size: 12.5px; margin-top: 2px; }
.panel {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 12px; padding: 18px 18px 12px; margin-top: 10px; overflow-x: auto;
}
.chart { display: block; overflow: visible; }
.bar { fill: var(--accent); opacity: 0.75; }
.bar-label { fill: var(--fg); font-size: 12.5px; }
.bar-value { fill: var(--muted); font-size: 12px; font-variant-numeric: tabular-nums; }
.col { fill: var(--accent-soft); }
.col.peak { fill: var(--accent); }
.axis { stroke: var(--line); stroke-width: 1; }
.tick { fill: var(--faint); font-size: 11.5px; font-variant-numeric: tabular-nums; }
.seg.a { fill: var(--accent); } .seg.b { fill: var(--cool); }
.seg.c { fill: var(--warm); } .seg.d { fill: var(--good); }
.legend { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 10px; font-size: 12.5px; color: var(--muted); }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 6px; }
table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; }
table.sortable th { cursor: pointer; user-select: none; }
table.sortable th:hover { color: var(--fg); }
th[data-dir="desc"]::after { content: " \\2193"; }
th[data-dir="asc"]::after { content: " \\2191"; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tbody tr:hover { background: color-mix(in srgb, var(--accent) 7%, transparent); }
.tools { color: var(--faint); font-size: 12px; }
.task { max-width: 46ch; }
footer { margin-top: 56px; padding-top: 18px; border-top: 1px solid var(--line); color: var(--faint); font-size: 13px; }
footer p { margin: 6px 0; max-width: 72ch; }
code { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 0.92em; }
@media print { body { background: #fff; } .panel, .card { break-inside: avoid; } }
"""


def render(state: dict, project: str) -> str:
    t = state.get("totals") or {}
    tasks = [dict(v, id=k) for k, v in (state.get("by_task") or {}).items() if billable(v)]
    tasks.sort(key=billable, reverse=True)
    skills = [(n, b) for n, b in (state.get("by_skill") or {}).items() if billable(b)]
    skills.sort(key=lambda kv: -billable(kv[1]))

    cost = 0.0
    for tk in (state.get("by_task") or {}).values():
        cost += float(tk.get("cost") or 0.0)

    first, last = state.get("first_seen") or "", state.get("last_seen") or ""
    # Transcripts, not sessions. A resumed session keeps its id, so this
    # project showed "2 sessions" beside 1,281 tasks, which reads as a bug.
    transcripts = len(state.get("files") or {})
    agent = state.get("by_agent") or {}
    main_b = billable(agent.get("main") or {})
    sub_b = billable(agent.get("subagent") or {})

    out = ["<!DOCTYPE html>", '<html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           f"<title>Token spend: {esc(os.path.basename(os.path.abspath(project)) or project)}</title>",
           f"<style>{CSS}</style></head><body><div class='wrap'>"]

    out.append(f"<h1>Token spend</h1>")
    span = f"{short_when(first)} to {short_when(last)}" if first else "no activity recorded"
    out.append(f"<p class='sub'>{esc(os.path.abspath(project))}<br>"
               f"{esc(span)} &middot; {t.get('turns', 0):,} assistant turns &middot; "
               f"{transcripts:,} transcripts &middot; {len(tasks):,} tasks</p>")

    # ------------------------------------------------------------- headline
    out.append("<div class='cards'>")
    for key, value, why in (
        ("Billable", human(billable(t)), "input + output + cache writes"),
        ("Cache read", human(t.get("cache_read", 0)), "a tenth of the price"),
        ("Raw total", human(raw(t)), "everything, cache included"),
        ("List price", money(cost), "not a bill: see the footnote"),
    ):
        out.append(f"<div class='card'><div class='k'>{esc(key)}</div>"
                   f"<div class='v'>{esc(value)}</div><div class='w'>{esc(why)}</div></div>")
    out.append("</div>")

    # ------------------------------------------------------------- by day
    out.append("<h2>Day by day</h2>")
    out.append("<p class='note'>Billable tokens per day. The gaps are days nobody "
               "worked, which is why these are columns and not a line.</p>")
    out.append("<div class='panel'>" + day_chart(state.get("by_day") or {}) + "</div>")

    # ------------------------------------------------------------- by task
    out.append("<h2>Which tasks cost the most</h2>")
    out.append("<p class='note'>A task is one request and everything done to answer "
               "it, read from the transcript: it starts when you ask for something "
               "and ends when you ask for the next thing. The label is how the "
               "request opened.</p>")
    out.append("<div class='panel'>"
               + bar_chart(tasks[:12], billable, lambda r: r.get("label") or r["id"])
               + "</div>")

    rows = []
    for r in tasks[:60]:
        label = esc(r.get("label") or r["id"])
        rows.append([
            (f"<span class='task'>{label}</span>", r.get("label") or ""),
            (esc(short_when(r.get("started"))), r.get("started") or ""),
            (esc(human(billable(r))), billable(r)),
            (esc(human(r.get("output", 0))), r.get("output", 0)),
            (esc(human(r.get("cache_read", 0))), r.get("cache_read", 0)),
            (esc(money(r.get("cost") or 0)), r.get("cost") or 0),
            (f"<span class='tools'>{esc(top_tools(r.get('tools') or {}))}</span>", None),
        ])
    out.append("<div class='panel'>" + table(
        ["Task", "Started", "Billable", "Wrote", "Cache read", "List price", "Mostly"],
        rows, numeric=(2, 3, 4, 5)) + "</div>")
    if len(tasks) > 60:
        out.append(f"<p class='note'>{len(tasks) - 60:,} smaller tasks are not listed. "
                   f"Their totals are in the headline figures.</p>")

    # ------------------------------------------------------------ by expert
    out.append("<h2>Which expert spent it</h2>")
    named = [(n, b) for n, b in skills if n != "(no skill)"]
    if named:
        out.append("<p class='note'>Read from the invocation in the transcript: a skill "
                   "or subagent owns every turn from when it was called until the next "
                   "request. Turns with no expert running are the row below the table.</p>")
        out.append("<div class='panel'>"
                   + bar_chart(named[:12], lambda kv: billable(kv[1]), lambda kv: kv[0])
                   + "</div>")
        rows = [[(esc(n), n),
                 (esc(str(b.get("runs", 0))), b.get("runs", 0)),
                 (esc(human(billable(b))), billable(b)),
                 (esc(human(b.get("output", 0))), b.get("output", 0)),
                 (esc(money(b.get("cost") or 0)), b.get("cost") or 0)]
                for n, b in named]
        plain = dict(skills).get("(no skill)")
        if plain:
            rows.append([("<em>no expert running</em>", "~~"),
                         ("", -1),
                         (esc(human(billable(plain))), billable(plain)),
                         (esc(human(plain.get("output", 0))), plain.get("output", 0)),
                         (esc(money(plain.get("cost") or 0)), plain.get("cost") or 0)])
        out.append("<div class='panel'>" + table(
            ["Expert", "Runs", "Billable", "Wrote", "List price"],
            rows, numeric=(1, 2, 3, 4)) + "</div>")
    else:
        out.append("<p class='note'>No skill or subagent has been invoked in this "
                   "project yet, so there is nothing to attribute. This is not an "
                   "error.</p>")

    # -------------------------------------------------------------- by tool
    tools = []
    for name, tl in (state.get("by_tool") or {}).items():
        results = (tl.get("result_chars", 0) or 0) // 4
        wrote = tl.get("output_tokens", 0) or 0
        tools.append((name, tl.get("calls", 0), tl.get("errors", 0), results, wrote, results + wrote))
    tools.sort(key=lambda r: -r[5])
    if tools:
        out.append("<h2>Which tool spent it</h2>")
        out.append("<p class='note'><strong>Results in</strong> is what the tool put "
                   "back into the context, so it is re-read on every later turn. "
                   "<strong>Wrote</strong> is the turn's output, which is paid once. A "
                   "tool high in results makes everything after it dearer. Both are "
                   "estimates: result sizes are characters divided by four.</p>")
        out.append("<div class='panel'>"
                   + bar_chart([r for r in tools[:12]], lambda r: r[5], lambda r: r[0])
                   + "</div>")
        rows = [[(esc(n), n), (f"{c:,}", c), (f"{e:,}", e),
                 (esc(human(res)), res), (esc(human(w)), w), (esc(human(tot)), tot)]
                for n, c, e, res, w, tot in tools]
        out.append("<div class='panel'>" + table(
            ["Tool", "Calls", "Errors", "Results in", "Wrote", "Total"],
            rows, numeric=(1, 2, 3, 4, 5)) + "</div>")

    # ----------------------------------------------------------- the splits
    out.append("<h2>Models, and who did the work</h2>")
    models = sorted((state.get("by_model") or {}).items(), key=lambda kv: -billable(kv[1]))
    classes = ["a", "b", "c", "d"]
    parts = [(n, billable(b), classes[i % len(classes)])
             for i, (n, b) in enumerate(models) if billable(b)]
    if parts:
        out.append("<div class='panel'>" + split_bar(parts))
        out.append("<div class='legend'>" + "".join(
            f"<span><i style='background:var(--{ {'a':'accent','b':'cool','c':'warm','d':'good'}[c] })'></i>"
            f"{esc(n)} {esc(human(v))}</span>" for n, v, c in parts) + "</div></div>")
    if main_b or sub_b:
        share = sub_b / max(main_b + sub_b, 1) * 100
        out.append("<div class='panel'>" + split_bar([
            ("main thread", main_b, "a"), ("subagents", sub_b, "b")]))
        out.append(f"<div class='legend'><span><i style='background:var(--accent)'></i>"
                   f"main thread {esc(human(main_b))}</span>"
                   f"<span><i style='background:var(--cool)'></i>"
                   f"subagents {esc(human(sub_b))} ({share:.0f}%)</span></div></div>")
        out.append("<p class='note'>A subagent's work does not land in this "
                   "conversation's context, so a high subagent share with a low main "
                   "share is delegation doing its job. High in both means the work was "
                   "done twice.</p>")

    # ------------------------------------------------------------- footnote
    out.append("<footer>")
    out.append("<p><strong>List price is not a bill.</strong> It is these token counts "
               "at the public per-million rates written into "
               "<code>grit-tokens/scripts/token_report.py</code>. On a subscription plan "
               "you are not charged this. Check the rates before quoting the number, "
               "and say that you did.</p>")
    out.append("<p>Token counts are exact: they are what the API reported, read from "
               "Claude Code's own transcripts. The split between tools is a model, and "
               "so is the split between tasks for a subagent, whose transcript records "
               "the prompt it was given rather than the request that led to it.</p>")
    out.append("<p>This page is one file with nothing fetched from the network. It is a "
               "snapshot: rebuild it with <code>grit-spend</code> to bring it up to "
               "date. It names this project and what it cost, so it is private until "
               "you decide otherwise.</p>")
    out.append(f"<p>Written from <code>.grit/token-usage.json</code>, state version "
               f"{esc(state.get('version'))}.</p>")
    out.append("</footer>")

    out.append(f"</div><script>{SORT_JS}</script></body></html>")
    return "\n".join(out)


# --------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--out", default=None, help="default: <project>/.grit/spend.html")
    ap.add_argument("--state", default=None, help="default: <project>/.grit/token-usage.json")
    ap.add_argument("--no-refresh", action="store_true",
                    help="draw the state as it stands, without reading new transcripts")
    ap.add_argument("--reader", default=READER, help="path to token_report.py")
    args = ap.parse_args()

    state_path = args.state or os.path.join(args.project, ".grit", "token-usage.json")
    out_path = args.out or os.path.join(args.project, ".grit", "spend.html")

    if not args.no_refresh:
        if not os.path.exists(args.reader):
            print(f"Cannot find the reader at {args.reader}.", file=sys.stderr)
            print("grit-spend renders what grit-tokens reads, so grit-tokens has to be "
                  "installed beside it. Pass --reader, or --no-refresh to draw the "
                  "state file as it stands.", file=sys.stderr)
            return 2
        # Its report goes to stderr's neighbour rather than being swallowed: a
        # refresh that failed should say so where somebody will see it.
        run = subprocess.run(
            [sys.executable, "-I", args.reader, "--project", args.project,
             "--state", state_path],
            capture_output=True, text=True)
        if run.returncode == 2:
            sys.stderr.write(run.stderr)
            return 2
        if run.returncode not in (0, 1):
            sys.stderr.write(run.stdout + run.stderr)
            print("Reading the transcripts failed, so nothing was drawn.", file=sys.stderr)
            return 1

    if not os.path.exists(state_path):
        print(f"No state at {state_path}, and nothing to draw.", file=sys.stderr)
        return 2
    try:
        with io.open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"Cannot read {state_path}: {exc}", file=sys.stderr)
        return 2

    if state.get("version") != STATE_VERSION:
        print(f"{state_path} is version {state.get('version')}, and this page needs "
              f"{STATE_VERSION}. Run grit-tokens' token_report.py once to rewrite it: "
              f"it has the task and expert record this page draws.", file=sys.stderr)
        return 2

    page = render(state, args.project)
    parent = os.path.dirname(os.path.abspath(out_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with io.open(out_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(page)

    tasks = sum(1 for v in (state.get("by_task") or {}).values() if billable(v))
    print(f"Wrote {out_path}")
    print(f"  {human(billable(state.get('totals') or {}))} billable over {tasks:,} tasks, "
          f"{len(state.get('by_skill') or {}):,} experts, "
          f"{len(state.get('by_tool') or {}):,} tools.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

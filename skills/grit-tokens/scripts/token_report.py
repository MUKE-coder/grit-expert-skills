#!/usr/bin/env python3
"""Read what a project actually spent, from Claude Code's own transcripts.

Claude Code writes one JSONL file per session under
``~/.claude/projects/<encoded-project-path>/``. Every assistant message in it
carries the ``usage`` block the API returned: input, output, cache creation,
cache read, and thinking tokens. That is the measurement. Nothing here
estimates, samples or models anything; if a number is not in a transcript, this
script does not report it.

Two things make this worth a script rather than a glance:

* The files are large. This session's transcript is 800 MB. So it streams line
  by line and remembers where it stopped, and a later run reads only what is
  new. The first run on a big project takes a minute; every run after it takes
  a second.

* Totals do not tell you anything you can act on. The useful question is which
  tool, which session and which agent spent it, and that needs the tool_use and
  tool_result blocks joined up, which is what the per-tool table below does.

Usage:
    token_report.py [--project DIR] [--html OUT.html] [--json OUT.json]
                    [--check] [--step N] [--alert-at N] [--all] [--reset]
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------- pricing
#
# Per million tokens, USD. Only used for the cost column, and only for models
# named here: an unknown model is counted in tokens and left out of the cost,
# which is better than inventing a rate for it.
#
# Edit these when the prices change. They are the one thing in this file that
# is not measured.
PRICES = {
    "claude-opus-5": {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "claude-sonnet-5-5": {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30},
    "claude-haiku-5-5": {"input": 1.0, "output": 5.0, "cache_write": 1.25, "cache_read": 0.10},
    "claude-fable-5-1": {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30},
}

# A model id may carry a suffix, such as claude-opus-5[1m]. Price on the base.
def price_for(model: str):
    if not model:
        return None
    base = model.split("[")[0]
    if base in PRICES:
        return PRICES[base]
    for name, p in PRICES.items():
        if base.startswith(name):
            return p
    return None


# ------------------------------------------------------------ locating it
def encode_project_dir(path: str) -> str:
    """Claude Code's directory name for a project path.

    Every character that is not a letter or a digit becomes a dash, so
    ``D:\\PROJECTS\\GO GRIT FRAMEWORK\\grit`` becomes
    ``d--PROJECTS-GO-GRIT-FRAMEWORK-grit``.
    """
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def transcript_dir(project: str, home: str) -> str | None:
    root = os.path.join(home, ".claude", "projects")
    if not os.path.isdir(root):
        return None

    guess = os.path.join(root, encode_project_dir(os.path.abspath(project)))
    if os.path.isdir(guess):
        return guess

    # The encoding has changed before, and guessing wrong reports zero rather
    # than failing, which is the worst way to be wrong about a measurement. So
    # when the guess misses, ask the transcripts themselves: every line carries
    # the cwd it was written from.
    target = os.path.normcase(os.path.abspath(project))
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".jsonl"):
                continue
            try:
                with io.open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                    for _ in range(5):
                        line = fh.readline()
                        if not line:
                            break
                        try:
                            cwd = json.loads(line).get("cwd")
                        except Exception:
                            continue
                        if cwd and os.path.normcase(os.path.abspath(cwd)) == target:
                            return d
            except OSError:
                continue
            break
    return None


# ---------------------------------------------------------------- the read
EMPTY = {
    "input": 0,
    "output": 0,
    "cache_write": 0,
    "cache_read": 0,
    "thinking": 0,
    "turns": 0,
}


def blank():
    return dict(EMPTY)


def add(into: dict, u: dict) -> None:
    into["input"] += u.get("input_tokens", 0) or 0
    into["output"] += u.get("output_tokens", 0) or 0
    into["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
    into["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
    details = u.get("output_tokens_details") or {}
    into["thinking"] += details.get("thinking_tokens", 0) or 0
    into["turns"] += 1


def new_state() -> dict:
    return {
        "version": 1,
        "files": {},            # transcript name -> {offset, size}
        "totals": blank(),
        "by_model": {},
        "by_session": {},
        "by_day": {},
        "by_agent": {"main": blank(), "subagent": blank()},
        "by_tool": {},          # name -> {calls, result_chars, errors, output_tokens}
        "first_seen": None,
        "last_seen": None,
        "reported_at": 0,       # the headline figure at the last report
        "alerted": False,
    }


def bucket(d: dict, key: str) -> dict:
    if key not in d:
        d[key] = blank()
    return d[key]


def tool_bucket(d: dict, name: str) -> dict:
    if name not in d:
        d[name] = {"calls": 0, "result_chars": 0, "errors": 0, "output_tokens": 0}
    return d[name]


def result_size(content) -> int:
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        n = 0
        for part in content:
            if isinstance(part, dict):
                n += len(part.get("text") or "")
                if part.get("type") == "image":
                    # An image is not text and its cost does not scale with
                    # the JSON around it. Counted as a flat figure so a
                    # screenshot-heavy session is visible without pretending
                    # the number is exact.
                    n += 1500
            elif isinstance(part, str):
                n += len(part)
        return n
    return 0


def scan(path: str, start: int, state: dict, is_subagent: bool = False) -> int:
    """Read one transcript from `start` bytes in. Returns the new offset.

    is_subagent comes from the path. The records carry isSidechain too, and
    either alone is enough, but a file under subagents/ is a subagent's whether
    or not the flag was written, and the flag catches a subagent's turn that
    lands in the main file.
    """
    pending = {}  # tool_use_id -> tool name, within this file
    # The offset is counted here rather than read back with tell(). Iterating a
    # file reads ahead into a buffer, so tell() sits somewhere past the line in
    # hand, and an offset taken from it skips whatever the buffer had already
    # swallowed. Counting the bytes consumed is exact and cannot drift.
    pos = start
    with io.open(path, "rb") as fh:
        fh.seek(start)
        for raw in fh:
            if not raw.endswith(b"\n"):
                # A half-written last line, which a live transcript always has:
                # stop before it so the next run reads it whole.
                return pos
            try:
                d = json.loads(raw.decode("utf-8", "replace"))
            except Exception:
                continue

            stamp = d.get("timestamp") or ""
            if stamp:
                state["first_seen"] = min(state["first_seen"] or stamp, stamp)
                state["last_seen"] = max(state["last_seen"] or stamp, stamp)

            msg = d.get("message") or {}

            if d.get("type") == "assistant":
                u = msg.get("usage") or {}
                if u:
                    add(state["totals"], u)
                    add(bucket(state["by_model"], msg.get("model") or "unknown"), u)
                    add(bucket(state["by_session"], d.get("sessionId") or "unknown"), u)
                    add(bucket(state["by_day"], stamp[:10] or "unknown"), u)
                    side = "subagent" if (is_subagent or d.get("isSidechain")) else "main"
                    add(state["by_agent"][side], u)

                # The tools this turn called, and the turn's output charged
                # against them. Output is what the model wrote, so a turn that
                # wrote one Bash command costs that Bash call its output.
                content = msg.get("content")
                if isinstance(content, list):
                    calls = [b for b in content
                             if isinstance(b, dict) and b.get("type") == "tool_use"]
                    share = (u.get("output_tokens", 0) or 0) // max(len(calls), 1)
                    for b in calls:
                        name = b.get("name") or "unknown"
                        pending[b.get("id")] = name
                        t = tool_bucket(state["by_tool"], name)
                        t["calls"] += 1
                        t["output_tokens"] += share

            elif d.get("type") == "user":
                # Tool results arrive as user messages. Their size is what the
                # tool put into the context, which is the number that answers
                # "what is filling this up".
                content = msg.get("content")
                if isinstance(content, list):
                    for b in content:
                        if not isinstance(b, dict) or b.get("type") != "tool_result":
                            continue
                        name = pending.pop(b.get("tool_use_id"), "unknown")
                        t = tool_bucket(state["by_tool"], name)
                        t["result_chars"] += result_size(b.get("content"))
                        if b.get("is_error"):
                            t["errors"] += 1

            pos += len(raw)
        return pos


def refresh(folder: str, state: dict) -> None:
    """Read every transcript under this project, including the subagents'.

    Walked rather than listed, because a session's subagent transcripts are in
    <session-id>/subagents/*.jsonl, one file each. Listing only the top level
    read the main thread and nothing else: on this project that was 74 files
    and 60 MB of work reported as zero, under the heading that exists to say
    who spent the most.
    """
    for root, dirs, names in os.walk(folder):
        dirs.sort()
        for name in sorted(names):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(root, name)
            key = os.path.relpath(path, folder).replace("\\", "/")
            size = os.path.getsize(path)
            seen = state["files"].get(key) or {"offset": 0, "size": 0}
            # A file that shrank was rotated or replaced: start it again rather
            # than reading from an offset that now means something else.
            start = seen["offset"] if size >= seen["size"] else 0
            if start >= size:
                continue
            sub = "/subagents/" in key.replace(os.sep, "/")
            state["files"][key] = {"offset": scan(path, start, state, sub), "size": size}


# -------------------------------------------------------------- the report
def cost_of(b: dict, model: str) -> float:
    p = price_for(model)
    if not p:
        return 0.0
    return (
        b["input"] / 1e6 * p["input"]
        + b["output"] / 1e6 * p["output"]
        + b["cache_write"] / 1e6 * p["cache_write"]
        + b["cache_read"] / 1e6 * p["cache_read"]
    )


def total_cost(state: dict) -> float:
    return sum(cost_of(b, m) for m, b in state["by_model"].items())


def billable(b: dict) -> int:
    """The headline figure: everything except cache reads.

    A cache read is a tenth of the price of the same token written, and on a
    long session it is most of the raw count: counting it makes the number go
    up fastest exactly when you are doing the cheap thing. This is the figure
    thresholds are measured against, and the raw total is reported beside it so
    nothing is hidden.
    """
    return b["input"] + b["output"] + b["cache_write"]


def raw(b: dict) -> int:
    return b["input"] + b["output"] + b["cache_write"] + b["cache_read"]


def human(n: float) -> str:
    if n >= 1e9:
        return f"{n / 1e9:.2f}B"
    if n >= 1e6:
        return f"{n / 1e6:.2f}M"
    if n >= 1e3:
        return f"{n / 1e3:.1f}k"
    return str(int(n))


def ranked_tools(state: dict):
    rows = []
    for name, t in state["by_tool"].items():
        # Four characters to a token is the usual rule for English and code,
        # and it is an estimate: the transcript records what a tool returned,
        # not what the tokeniser made of it.
        rows.append({
            "name": name,
            "calls": t["calls"],
            "errors": t["errors"],
            "result_tokens": t["result_chars"] // 4,
            "output_tokens": t["output_tokens"],
            "total": t["result_chars"] // 4 + t["output_tokens"],
        })
    rows.sort(key=lambda r: r["total"], reverse=True)
    return rows


def text_report(state: dict, project: str) -> str:
    t = state["totals"]
    out = []
    out.append(f"Token report for {project}")
    if state["first_seen"]:
        out.append(f"  {state['first_seen'][:16]} to {state['last_seen'][:16]}  "
                   f"({t['turns']} assistant turns, {len(state['by_session'])} sessions)")
    out.append("")
    out.append(f"  Billable   {human(billable(t)):>10}   input + output + cache writes")
    out.append(f"  Cache read {human(t['cache_read']):>10}   a tenth of the price, read not written")
    out.append(f"  Raw total  {human(raw(t)):>10}")
    out.append(f"  Thinking   {human(t['thinking']):>10}   of the output")
    cost = total_cost(state)
    if cost:
        out.append(f"  Cost       {'$' + format(cost, ',.2f'):>10}   at the rates in this script")
    out.append("")

    if len(state["by_model"]) > 1:
        out.append("  By model")
        for m, b in sorted(state["by_model"].items(), key=lambda kv: -billable(kv[1])):
            if not raw(b):
                continue
            out.append(f"    {m:<24} {human(billable(b)):>9}   ${cost_of(b, m):,.2f}")
        out.append("")

    sub = state["by_agent"]["subagent"]
    if billable(sub):
        share = billable(sub) / max(billable(t), 1) * 100
        out.append(f"  Subagents  {human(billable(sub)):>10}   {share:.0f}% of billable")
        out.append("")

    rows = ranked_tools(state)
    if rows:
        out.append("  Where it went, by tool")
        out.append(f"    {'tool':<22}{'calls':>7}{'results':>10}{'wrote':>10}{'total':>10}")
        for r in rows[:12]:
            out.append(f"    {r['name']:<22}{r['calls']:>7}"
                       f"{human(r['result_tokens']):>10}{human(r['output_tokens']):>10}"
                       f"{human(r['total']):>10}")
        big = rows[0]
        out.append("")
        out.append(f"  Biggest spender: {big['name']}, {human(big['total'])} tokens "
                   f"across {big['calls']} calls.")
    return "\n".join(out)


# ----------------------------------------------------------------- the page
def esc(value) -> str:
    """Everything that reaches the page goes through here.

    Model and tool names come out of a transcript, and one of them is literally
    "<synthetic>", which a browser reads as an unknown tag and draws as
    nothing: the row was there, the name was not. Anything that can appear in a
    name can appear in markup, so none of it is written raw.
    """
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def html_report(state: dict, project: str) -> str:
    t = state["totals"]
    rows = ranked_tools(state)
    top = rows[0]["total"] if rows else 1
    cost = total_cost(state)

    def bar(value, of, colour):
        pct = (value / of * 100) if of else 0
        return (f'<div class="bar"><span style="width:{pct:.1f}%;background:{colour}"></span></div>')

    tool_rows = "\n".join(
        f"""<tr>
          <td class="name">{esc(r['name'])}</td>
          <td class="num">{r['calls']:,}</td>
          <td class="num">{human(r['result_tokens'])}</td>
          <td class="num">{human(r['output_tokens'])}</td>
          <td class="num strong">{human(r['total'])}</td>
          <td class="barcell">{bar(r['total'], top, 'var(--accent)')}</td>
        </tr>"""
        for r in rows[:20]
    )

    # A model with nothing against it is noise. "<synthetic>" is Claude Code's
    # own marker for a message it wrote itself, and it never has usage.
    model_rows = "\n".join(
        f"""<tr><td class="name">{esc(m)}</td>
            <td class="num">{human(billable(b))}</td>
            <td class="num">{human(b['cache_read'])}</td>
            <td class="num strong">${cost_of(b, m):,.2f}</td></tr>"""
        for m, b in sorted(state["by_model"].items(), key=lambda kv: -billable(kv[1]))
        if raw(b)
    )

    days = sorted(state["by_day"].items())
    day_max = max((billable(b) for _, b in days), default=1)
    day_rows = "\n".join(
        f"""<tr><td class="name">{esc(d)}</td>
            <td class="num">{human(billable(b))}</td>
            <td class="num">{b['turns']:,}</td>
            <td class="barcell">{bar(billable(b), day_max, 'var(--info)')}</td></tr>"""
        for d, b in days[-21:]
    )

    sub = state["by_agent"]["subagent"]
    main = state["by_agent"]["main"]
    sub_share = billable(sub) / max(billable(t), 1) * 100

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    biggest = esc(rows[0]["name"]) if rows else "nothing yet"

    return f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Token Report</title>
<style>
  :root {{
    --bg: #0a0a0f; --panel: #111118; --raised: #1a1a24; --line: #2a2a3a;
    --fg: #e8e8f0; --dim: #9090a8; --muted: #7c7c96;
    --accent: #6c5ce7; --info: #74b9ff; --ok: #00b894; --warn: #fdcb6e;
  }}
  @media (prefers-color-scheme: light) {{
    :root:not([data-theme="dark"]) {{
      --bg: #ffffff; --panel: #f8fafc; --raised: #f1f5f9; --line: #e2e8f0;
      --fg: #0f172a; --dim: #475569; --muted: #64748b;
      --accent: #2563eb; --info: #0ea5e9; --ok: #10b981; --warn: #f59e0b;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font: 15px/1.6 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    padding: 32px 16px 64px;
  }}
  .wrap {{ max-width: 1040px; margin: 0 auto; }}
  h1 {{ font-size: 1.6rem; margin: 0 0 4px; letter-spacing: -0.02em; }}
  .sub {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 28px; }}
  .cards {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); margin-bottom: 28px; }}
  .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; }}
  .card .k {{ color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }}
  .card .v {{ font-size: 1.7rem; font-weight: 650; margin-top: 6px; letter-spacing: -0.02em; }}
  .card .n {{ color: var(--dim); font-size: 0.8rem; margin-top: 4px; }}
  .card.hl {{ border-color: var(--accent); }}
  section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 18px; margin-bottom: 20px; }}
  h2 {{ font-size: 0.95rem; margin: 0 0 14px; letter-spacing: 0.01em; }}
  h2 .q {{ color: var(--muted); font-weight: 400; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ text-align: left; color: var(--muted); font-weight: 500; font-size: 0.72rem;
        text-transform: uppercase; letter-spacing: 0.06em; padding: 0 10px 8px 0; }}
  td {{ padding: 7px 10px 7px 0; border-top: 1px solid var(--line); }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.strong {{ font-weight: 650; }}
  td.name {{ font-family: ui-monospace, "JetBrains Mono", monospace; font-size: 0.82rem; }}
  .barcell {{ width: 34%; }}
  .bar {{ background: var(--raised); border-radius: 3px; height: 7px; overflow: hidden; }}
  .bar span {{ display: block; height: 100%; border-radius: 3px; }}
  .note {{ color: var(--muted); font-size: 0.82rem; margin-top: 12px; }}
  footer {{ color: var(--muted); font-size: 0.78rem; margin-top: 28px; }}
  @media (max-width: 620px) {{ .barcell {{ display: none; }} body {{ padding: 20px 16px 48px; }} }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Token report</h1>
  <div class="sub">{esc(project)}<br>{(state['first_seen'] or '')[:16]} to {(state['last_seen'] or '')[:16]}
    &middot; {t['turns']:,} assistant turns &middot; {len(state['by_session'])} sessions</div>

  <div class="cards">
    <div class="card hl"><div class="k">Billable</div><div class="v">{human(billable(t))}</div>
      <div class="n">input + output + cache writes</div></div>
    <div class="card"><div class="k">Cache read</div><div class="v">{human(t['cache_read'])}</div>
      <div class="n">a tenth of the price</div></div>
    <div class="card"><div class="k">Raw total</div><div class="v">{human(raw(t))}</div>
      <div class="n">every token counted</div></div>
    <div class="card"><div class="k">Estimated cost</div><div class="v">${cost:,.2f}</div>
      <div class="n">at the rates in the script</div></div>
  </div>

  <section>
    <h2>Where it went <span class="q">&mdash; by tool, biggest first</span></h2>
    <table>
      <thead><tr><th>Tool</th><th class="num">Calls</th><th class="num">Results in</th>
        <th class="num">Model wrote</th><th class="num">Total</th><th></th></tr></thead>
      <tbody>{tool_rows}</tbody>
    </table>
    <p class="note">&ldquo;Results in&rdquo; is what the tool put back into the context, estimated at four
      characters to a token. &ldquo;Model wrote&rdquo; is the turn&rsquo;s output tokens, divided between the
      tools that turn called. The biggest spender here is <strong>{biggest}</strong>.</p>
  </section>

  <section>
    <h2>By model</h2>
    <table>
      <thead><tr><th>Model</th><th class="num">Billable</th><th class="num">Cache read</th>
        <th class="num">Cost</th></tr></thead>
      <tbody>{model_rows}</tbody>
    </table>
  </section>

  <section>
    <h2>Main thread against subagents</h2>
    <table>
      <thead><tr><th>Where</th><th class="num">Billable</th><th class="num">Turns</th></tr></thead>
      <tbody>
        <tr><td class="name">main</td><td class="num">{human(billable(main))}</td>
            <td class="num">{main['turns']:,}</td></tr>
        <tr><td class="name">subagents</td><td class="num">{human(billable(sub))}</td>
            <td class="num">{sub['turns']:,}</td></tr>
      </tbody>
    </table>
    <p class="note">Subagents are {sub_share:.0f}% of the billable total. Their work does not
      land in this conversation&rsquo;s context, so a high share here with a low one above is
      delegation doing its job; a high share in both is paying twice.</p>
  </section>

  <section>
    <h2>By day</h2>
    <table>
      <thead><tr><th>Day</th><th class="num">Billable</th><th class="num">Turns</th><th></th></tr></thead>
      <tbody>{day_rows}</tbody>
    </table>
  </section>

  <footer>Read from Claude Code&rsquo;s own transcripts in ~/.claude/projects. Token counts are
    what the API reported. Per-tool figures and the cost are estimates, and the script says
    how each one is worked out. Generated {generated}.</footer>
</div>
</body>
</html>
"""


# ------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--home", default=os.path.expanduser("~"))
    ap.add_argument("--state", default=None, help="default: <project>/.grit/token-usage.json")
    ap.add_argument("--html", default=None)
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--step", type=int, default=5000, help="report every N billable tokens")
    ap.add_argument("--alert-at", type=int, default=100000)
    ap.add_argument("--check", action="store_true",
                    help="print a line only when a threshold has been crossed")
    ap.add_argument("--all", action="store_true", help="every project, totals only")
    ap.add_argument("--reset", action="store_true", help="forget the stored offsets and reread")
    args = ap.parse_args()

    if args.all:
        root = os.path.join(args.home, ".claude", "projects")
        rows = []
        for name in sorted(os.listdir(root)):
            d = os.path.join(root, name)
            if not os.path.isdir(d):
                continue
            s = new_state()
            refresh(d, s)
            if s["totals"]["turns"]:
                rows.append((billable(s["totals"]), total_cost(s), name, s))
        rows.sort(reverse=True, key=lambda r: r[0])
        print(f"{'project':<52}{'billable':>11}{'cost':>11}")
        for b, c, name, _ in rows:
            print(f"{name[:50]:<52}{human(b):>11}{'$' + format(c, ',.2f'):>11}")
        return 0

    folder = transcript_dir(args.project, args.home)
    if not folder:
        print(f"No Claude Code transcripts for {args.project}.", file=sys.stderr)
        print("Nothing has been recorded for this project yet, so there is nothing to "
              "report. This is not an error.", file=sys.stderr)
        return 2

    state_path = args.state or os.path.join(args.project, ".grit", "token-usage.json")
    state = new_state()
    if os.path.exists(state_path) and not args.reset:
        try:
            with io.open(state_path, encoding="utf-8") as fh:
                loaded = json.load(fh)
            if loaded.get("version") == 1:
                state = loaded
                for side in ("main", "subagent"):
                    state.setdefault("by_agent", {}).setdefault(side, blank())
        except (OSError, ValueError):
            pass  # a corrupt state file is a reread, not a failure

    before = billable(state["totals"])
    refresh(folder, state)
    now = billable(state["totals"])

    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    crossed_step = now // args.step > state.get("reported_at", 0) // args.step
    crossed_alert = now >= args.alert_at and not state.get("alerted")

    if args.check:
        if crossed_alert:
            print(f"ALERT {human(now)} billable tokens, past the {human(args.alert_at)} mark "
                  f"(${total_cost(state):,.2f}).")
        elif crossed_step:
            print(f"REPORT {human(now)} billable tokens (+{human(now - before)} since the last "
                  f"run, ${total_cost(state):,.2f}).")
        else:
            print(f"OK {human(now)} billable, next report at "
                  f"{human((now // args.step + 1) * args.step)}.")
    else:
        print(text_report(state, args.project))

    if crossed_step or crossed_alert:
        state["reported_at"] = now
    if crossed_alert:
        state["alerted"] = True

    with io.open(state_path, "w", encoding="utf-8", newline="") as fh:
        json.dump(state, fh, indent=2)

    if args.html:
        with io.open(args.html, "w", encoding="utf-8", newline="") as fh:
            fh.write(html_report(state, args.project))
        print(f"\nWrote {args.html}")
    if args.json_out:
        with io.open(args.json_out, "w", encoding="utf-8", newline="") as fh:
            json.dump(state, fh, indent=2)
        print(f"Wrote {args.json_out}")

    return 1 if (crossed_alert and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())

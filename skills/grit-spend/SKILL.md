---
name: grit-spend
description: >-
  The token spend dashboard: one HTML page in the project, with the headline
  figures, a column per day, and tables of which tasks, which experts and which
  tools the tokens went on. Rebuild it any time. Use for "what are we spending",
  "token dashboard", "which task cost the most", "show me the spend", "where did
  the budget go", "build the spend page", or when somebody wants the numbers as
  a page rather than as terminal output.
---

# grit-spend

You produce one file: `.grit/spend.html`. Somebody opens it a week later and
can see what this project has cost and which work cost it, without running
anything.

## Build it

```bash
python3 .claude/skills/grit-spend/scripts/spend_dashboard.py --project .
```

That reads the transcripts, brings the record up to date and writes
`.grit/spend.html`. First run on a long project takes a few seconds; after
that it only reads what is new.

| What you want | How |
|---|---|
| The page, up to date | `spend_dashboard.py --project .` |
| Somewhere else | `--out docs/spend.html` |
| Draw it without rereading | `--no-refresh` |
| After changing the price table | `token_report.py --project . --reset` first |

Then tell the person the path and the three numbers that matter: billable,
the dearest task, and the dearest expert. Do not make them open the file to
find out whether it was worth opening.

## Where the numbers come from, and who owns them

**This skill renders. It does not read transcripts.**

`grit-tokens` owns the reading. Its `token_report.py` is the only thing in
this pack that parses Claude Code's transcripts, and it writes everything it
learns to `.grit/token-usage.json`. This script calls it, then draws the
result.

That split is the whole design. Two readers would be two sets of totals, and
the day they disagreed there would be no way to tell which was right. If you
need a number this page does not show, add it to the reader and draw it here.
Do not parse a transcript in this skill.

So the two skills answer different questions:

| | |
|---|---|
| `grit-tokens` | what is it now, which tool is expensive, tell me when it crosses a line |
| `grit-spend` | the page I open later: which **tasks** and which **experts** spent it |

## The three attributions, and what each one is worth

**By task.** A task is one request and everything done to answer it: it starts
when somebody asks for something and ends when they ask for the next thing.
The label is how the request opened, trimmed to 90 characters.

This is the number people are usually after, and it is often a surprise. A
one-word "proceed" that turned into four hours of work is a bigger line than
any carefully written brief, because the brief is short and the work after it
is not. **The label is not the cost.** Read the row, not the sentence.

Records that are not requests do not start a task: an interruption notice, a
background task finishing, a notification. They belong to the request that was
already running, and counting them separately takes that request's own spend
away from it.

**By expert.** Which skill or subagent was running, read from the invocation in
the transcript rather than from `.grit/run-log.md`. The log is written by the
router in local time to the minute, and joining that to UTC timestamps is a
guess; this is the same source as every other figure on the page. A skill owns
every turn from when it was called until the next request.

A high "no expert running" row is not a problem. It is the main thread doing
the work itself, which is most of what happens.

**By tool.** Two columns that mean different things. **Results in** is what the
tool put back into the context, so it is re-read on every later turn and makes
everything after it dearer. **Wrote** is that turn's output, paid once. A tool
high in results is the one to fix.

## Reading the page honestly

Say these when you report the numbers, rather than letting somebody find out
the hard way.

**List price is not a bill.** The money column is these token counts at the
public per-million rates written into `grit-tokens/scripts/token_report.py`. On
a subscription plan nobody is charged it. It is useful for comparing one task
against another, and misleading as an amount. If the figure is going anywhere
near a budget conversation, open the price table, check the rates against
today's, and say that you did.

**Cache reads are most of the raw total and almost none of the cost.** A long
session re-reading its own context is the cheap case. That is why the headline
is billable and the raw total sits beside it rather than on its own.

**Token counts are exact. The splits are models.** The totals are what the API
reported. The division between tools counts result sizes in characters and
divides by four. A subagent's tasks are labelled with the prompt it was given,
not the request that led to it, so a subagent's spend shows under its own
task, not its parent's.

**It cannot see what was never written down.** A deleted transcript is gone
from the record, and the page will be short by exactly that much without
saying so.

## When the page is empty or stale

| What you see | What it means |
|---|---|
| "No Claude Code transcripts for ..." | nothing has been recorded for this directory. The same work from a different path is a different project here |
| "is version 1, and this page needs 2" | the state predates task and expert attribution. Run `token_report.py --project .` once: it rereads and rewrites |
| No experts listed | no skill or subagent has been invoked in this project. Not an error |
| Numbers stop at a date | run it again. It only draws what the reader has read |

## Housekeeping

`.grit/spend.html` and `.grit/token-usage.json` both name this project and what
it cost. Add both to `.gitignore` unless the person wants the page committed,
and ask before committing it: a repository is a wider audience than they may
have in mind.

If they want it as a link to share rather than a file, publish it as an
artifact and give them the URL. **Do not publish it unasked**, for the same
reason.

## What not to do

- **Do not parse transcripts here.** One reader, in `grit-tokens`.
- **Do not fetch a chart library.** The page is drawn with inline SVG so it
  opens from disk, offline, in a year. A CDN script would end that for a
  nicer gradient.
- **Do not quote the cost as a bill**, and do not quietly drop the column
  either. Quote it with the sentence above.
- **Do not read a task's label as a judgement.** A dear task is not a wasted
  one; the page says what was spent, not whether it was worth it. That
  question is `grit-report`'s, and it reads the run log, not this.

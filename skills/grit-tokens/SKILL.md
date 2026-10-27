---
name: grit-tokens
description: >-
  What this project has spent on tokens, where it went and who the big spender
  is, read from Claude Code's own transcripts. Alerts at a threshold and reports
  every increment, and writes an HTML page with the full breakdown. Use for "how
  many tokens have we used", "what is this costing", "token report", "why is my
  context filling up", "which tool is expensive", or set it running to be told
  as the number grows.
---

# grit-tokens

You answer one question with real numbers: what has this project spent, and on
what. Not an impression, not a sample. Claude Code writes every API response's
`usage` block into its own transcripts, and that is what you read.

## Run it

```bash
python3 .claude/skills/grit-tokens/scripts/token_report.py --project .
```

The script finds the transcripts itself, under
`~/.claude/projects/<the project path, punctuation turned to dashes>/`. It
reads the main thread and every subagent, remembers where it stopped in
`.grit/token-usage.json`, and on the next run reads only what is new. The first
run on a long project takes a few seconds; every run after it is instant.

| What you want | How |
|---|---|
| The report, now | `token_report.py --project .` |
| The page | `--html .grit/tokens.html` |
| Only when a threshold is crossed | `--check` |
| Different thresholds | `--step 250000 --alert-at 5000000` |
| Every project on this machine | `--all` |
| Forget the offsets and reread | `--reset` |

`--check` prints one line: `OK`, `REPORT` when the step was crossed, or `ALERT`
at the threshold, and exits 1 on the alert so a hook or a loop can act on it. It
does not print the whole report, so it is cheap to call often.

## Read the numbers before you repeat them

Four figures, and they are not interchangeable.

| Figure | What it is |
|---|---|
| **Billable** | input + output + cache writes. The thresholds measure this |
| **Cache read** | context read back from cache, a tenth of the price |
| **Raw total** | everything, cache reads included |
| **Cost** | the billable mix at the rates written into the script |

Cache reads are usually most of the raw total and almost none of the cost. A
long session that keeps re-reading its own context is the cheap case, and a
number that counts cache reads goes up fastest exactly when you are doing the
cheap thing. That is why the headline is billable, and why the raw total is
printed beside it rather than hidden.

**The cost is an estimate.** The rates are a table at the top of the script.
They were right when it was written and they are not updated by anything. If
the number matters, check the rates first and say in your answer that you did.

## The thresholds, and what they are worth

The defaults are an alert at 100,000 billable tokens and a report every 5,000.

On a real project those fire in the first minute. A week of ordinary work is
tens of millions. Before you set a loop running, run the report once and look at
the actual number, then set the thresholds from it: something like a tenth of a
week's spend for the step, and a figure you would actually want to be
interrupted for as the alert. Say what you set and why. A threshold that fires
constantly is not a monitor, it is noise, and it trains the person to ignore the
one that matters.

The state file remembers the figure at the last report, so the step fires on
growth rather than on every run, and the alert fires once.

## Who the big spender is

The per-tool table is the part worth acting on. Two columns, and they mean
different things:

- **Results in** is what the tool put back into the context. This is what
  fills a context window and what gets re-read on every later turn.
- **Model wrote** is the turn's output tokens, divided between the tools that
  turn called. A `Write` of a 400-line file costs its output, not its result.

So a tool high in *results* is making every later turn more expensive, and a
tool high in *wrote* is expensive once. Both are estimates: result sizes are
counted in characters and divided by four, because the transcript records what
a tool returned and not what the tokeniser made of it.

What to do about the usual answers:

| Biggest spender | What it usually means |
|---|---|
| `Bash` | Unbounded output. Redirect to a file and grep it, rather than printing whole logs and test runs into the conversation |
| `Read` | Whole files read when a range would do, or the same file read repeatedly |
| `Write` | Large files written in full where an edit would have done |
| `Grep` | `output_mode: content` without a head limit |
| A browser or MCP tool | Snapshots and page dumps; take fewer, and screenshot instead of dumping the tree |

Subagents are reported separately. Their work does not land in the main
conversation's context, so a high subagent share with a low main share is
delegation doing its job. High in both means the work was done twice.

## The page

`--html <path>` writes a self-contained HTML file: the four headline figures,
the per-tool table with bars, by model, main against subagents, and by day. No
network, no CDN, light and dark. It is a file, so it can be opened, committed or
attached.

If the person wants it as a link they can share, publish it as an artifact and
give them the URL. Do not publish it without being asked: it names their
projects and what they cost.

## Honest limits

Say these rather than letting someone discover them.

- **It reads transcripts, not an invoice.** Token counts are what the API
  reported. The cost is those counts times a table in the script.
- **Per-tool attribution is a model**, described above. The totals are exact;
  the split between tools is not.
- **It is per project directory.** The same work done from a different path is
  a different project here, and `--all` is how you see them together.
- **It cannot see what was never written down.** A session whose transcript has
  been deleted is gone from the record.

## Housekeeping

`.grit/token-usage.json` is a cache, and it contains your project's path and
usage history. Add `.grit/token-usage.json` to `.gitignore`. If it is lost,
nothing breaks: the next run reads everything again.

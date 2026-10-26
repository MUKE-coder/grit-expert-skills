---
name: grit-report
description: >-
  Report on how the experts are actually performing on this project: route
  accuracy, whether they verified, how much they asked, framework friction and
  rework. Use for "how are the experts doing", "grit report", "was that
  efficient", "which expert is wasting time", or at the end of a phase.
---

# grit-report

You measure the experts, not the product. The question is whether this way of
working is actually faster and more reliable than one person doing it, and the
only honest answer comes from a record of what happened rather than from an
impression of it.

## What you read

Four files, all in the project:

| File | Written by | Holds |
|---|---|---|
| `.grit/run-log.md` | `grit-build`, after every expert | One row per expert run |
| `.grit/feedback.md` | `grit-feedback` | Grit issues filed, and their status |
| `.grit/project-profile.md` | `grit-build` | The answers, and the open questions |
| `phases.md` | whoever ticks it | Throughput |

If `.grit/run-log.md` does not exist, say so and stop: there is nothing to
report on, and inventing an assessment from the git log would be a guess
dressed as a measurement. Tell the user the router writes it from the next run
onward.

## The six numbers

Compute these from the log. Each one answers a question somebody would
actually act on.

### 1. Route accuracy

`handed back / total runs`

A run is handed back when an expert was invoked and the work was not theirs, or
when it stopped and asked for a different expert. High means the router is
guessing: look at which classifications it got wrong and whether the request
was ambiguous or the routing table is.

**Act when it goes above about one in ten.** The fix is usually a clearer rule
in `grit-build`'s routing table, not a smarter router.

### 2. Verification rate

`runs with a verification command recorded / runs that changed code`

This is the most important number in the report. Every expert has a "before
you say it works" list, and the failure mode of an agent is to report a thing
done on the strength of having written it. Anything below 100 percent is a
finding, and name the expert.

### 3. Question load, and repeat questions

`questions asked / run`, and separately the count of questions asked about
something the profile already answers.

A repeat question is a profile failure, not an expert failure: either the
answer was not written down or it was written somewhere the expert does not
read. Both are fixable and both compound, because the person answers the same
thing every session.

Falling to zero is also worth noticing. An expert that stops asking has
started guessing.

### 4. Framework friction

`issues filed / phase`, and how many are still open.

This is the number that says something about **Grit**, not about the experts.
A phase with six issues was a phase where the framework fought the product.
Name the areas: if four of them are in the generator, that is a pattern worth
telling the framework author about as a pattern rather than as four tickets.

Also check: are any closed upstream and not yet verified here? That is work
sitting on the table, and `grit-feedback --check` does it.

### 5. Rework

Files touched by three or more experts inside one phase.

Some of that is normal: a resource legitimately passes through core, resource,
data, the tier and the admin. What is not normal is the same file changed by
the same expert twice in a phase with a different decision each time, which
means a decision was made without the information to make it.

Trace one back to where the information was available, because that is almost
always a step the router ran out of order.

### 6. Throughput and cost

Tasks ticked in `phases.md` per session, against what the session cost.

You cannot read the token cost from inside the project: Claude Code holds it.
Ask the user for `/usage` and `/context`, and say so rather than estimating.
`/insights` produces a friction report that is worth reading next to this one.

## The report

Lead with the judgement, then the numbers, then one thing to change. Not a
table of everything.

```
Phase 2, 9 expert runs across 3 sessions.

Route accuracy      9/9 placed correctly
Verification        7/9 ran a build or test. grit-admin twice did not
Questions           1.1 per run, 2 repeats (both about currency)
Friction            4 issues filed, 3 open, all four in the generator
Rework              resources/deals.ts touched by 4 experts, expected
Throughput          11 of 14 phase-2 tasks ticked

The one thing to change: currency was asked twice because the profile's Data
section records it as an open question and nobody has answered it. Answer it
once and two experts stop asking.

The one thing to tell the framework author: all four issues are generator
field-type bugs on multi-word resources, which is one bug class rather than
four tickets.
```

## What not to do with this

**Do not turn it into a score.** A single number invites gaming, and the
behaviour that games it (never asking, never filing) is exactly the behaviour
that makes the experts worse. Each number is a question to look into.

**Do not use it to compare experts against each other.** `grit-reviewer` runs
on every phase and `grit-desktop` runs twice a project; counting their runs
says nothing about either.

**Do not let it become the work.** If the report takes longer than the phase,
the instrumentation is too heavy and the log should get shorter, not the
report longer.

## When the answer is that this is not working

Say it. If route accuracy is poor, verification is patchy and the same
decisions keep being remade, the honest report is that the orchestration is
costing more than it returns on this project, and that one expert plus a
reviewer would be faster. That is a legitimate finding and the person should
hear it from the measurement rather than discover it after four phases.

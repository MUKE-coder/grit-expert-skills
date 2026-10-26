---
name: grit-build
description: >-
  The router for a Grit project. Reads the project, interviews you once, then
  assigns the work to the right experts in the right order and runs them.
  Use for "build X", "add this feature", "what should I do next", "set up this
  project", or any request big enough to touch more than one layer.
---

# grit-build

You are the person who decides who does what. You do not write the feature
yourself: you work out what it actually is, make sure the project knows its own
mind, and then run the experts in an order where each one has what it needs.

Read `references/working-agreement.md` once at the start of a session. It is
the contract all the experts share and you are the one who enforces it.

## Step 1: find out what this project is

```bash
cat grit.json 2>/dev/null                      # architecture and the version it was made with
grit --version                                  # the CLI actually installed
ls apps/ 2>/dev/null                            # which surfaces exist
cat .grit/project-profile.md 2>/dev/null        # what has already been asked
```

Two version numbers that disagree is worth one sentence to the user:
`grit.json` says what scaffolded the project, `grit --version` says what will
generate into it next. If the CLI is older, generation will write older
templates into a newer project.

If there is no `grit.json`, this is not a Grit project yet. That is fine: it
may be a brief, a planning folder, or an empty directory. Go to step 2 and
then hand to the tier expert to scaffold it.

## Step 2: the interview, once

If `.grit/project-profile.md` does not exist, you run the interview. Use the
ask tool, with real options rather than open questions, and ask in this order
because each answer narrows the next.

1. **What is this and who uses it?** One line of product, one line of user.
   If there is a brief in the repo (`project-description.md`, `README.md`,
   `phases.md`, a `techstack.md`), read it first and confirm your reading back
   rather than asking them to retype it.
2. **Which surfaces, and in what order?** api, single, double, triple, plus
   desktop and mobile as additions. Ask which ships first: it decides
   everything about sequencing and it is the answer people most often have
   not thought about.
3. **Who owns a row?** Everybody, a user, or an organisation. This is the
   question that is expensive to change later, because it decides whether
   resources get `--owned-by` or the multitenant plugin, and retrofitting
   either means touching every query.
4. **Money, time and units.** Currency, whether amounts are minor units,
   timezone, first day of the week. Ask once, write it down, and every expert
   stops guessing.
5. **What must never happen?** Data residency, offline operation, a regulator,
   an immovable date. Constraints beat preferences, and they are usually the
   reason the product exists.

Write the answers to `.grit/project-profile.md` using the template at the
bottom of this file. Show the user the file and say they can edit it.

If the profile exists, read it and skip straight to step 3. Ask only about
what the current task needs and the profile does not cover, then append.

## Step 3: work out what the task actually is

Classify before you assign. Most requests are one of these, and the shape
decides the route:

| The request | What it really is |
|---|---|
| "Add contacts and companies" | A resource. Model first, everything follows |
| "Make the dashboard show pipeline value" | A read model plus an admin widget |
| "Log WhatsApp messages against a contact" | An integration plus a resource |
| "Reps need to work offline" | An architecture decision, not a feature |
| "Make it look less generic" | A design pass, and a standard to hold it to |
| "It is slow" | A measurement, before any change |
| "Ship it" | Deployment, and store review if there is a mobile app |

If the request is genuinely ambiguous between two of these, ask. One question
now is cheaper than the wrong three experts.

## Step 4: route

The order is not negotiable where it is marked, because a later expert reads
what an earlier one wrote.

**A new resource or domain model**

1. `grit-core` decides the model, the relationships, and what belongs in Grit
   versus what you build. **Always first.** Everything downstream is derived
   from the model, so a wrong field here is rework everywhere.
2. `grit-resource` runs the generator and gets the field types and flags right.
3. `grit-data` for migrations, indexes, seeders, and anything the generator
   cannot express.
4. The tier expert (`grit-triple`, `grit-double`, `grit-single`) wires the
   frontends. `grit-desktop` and `grit-mobile` after, if those surfaces exist.
5. `grit-admin` for the admin screens, widgets and the resource definition.
6. `grit-ui-ux` for anything a customer sees. Not the admin, which has its own
   design system already.
7. `grit-reviewer` reads the diff.

**A new project from nothing**

1. The interview, above. Do not skip it: scaffolding the wrong architecture
   costs a day.
2. `grit-setup` to install the external skills the others want.
3. The tier expert scaffolds and stands it up.
4. `grit-security` before the first real user, not after.
5. Then resources, as above.

**A design pass**: `grit-ui-ux`, then `grit-reviewer`.

**A performance complaint**: `grit-perf` alone, first. It measures before
anything is changed, and the measurement usually renames the task.

**A release**: `grit-deploy`, plus `grit-mobile` if there is a store build.

**Anything you cannot place**: say so and ask. Guessing at the route is how
four experts do work that one should have done.

## Step 5: run them, one at a time

Invoke each expert with the Skill tool, in order, and wait for each. Do not
fan out to sub-agents: the person wants to watch this happen and be able to
stop it, and a parallel run spends their budget in a burst they did not ask
for.

Before each one, say in a line which expert and why. After each, say what
changed. If an expert reports a blocker, stop and bring it to the user rather
than routing around it.

Pass each expert the task, the relevant part of the profile, and what the
previous expert produced. They cannot see each other's work.

## Step 5b: log each run, in one line

After every expert returns, append a row to `.grit/run-log.md`, creating the
file with the header if it is not there. This is the only record of what
actually happened: you are the only thing that sees every invocation, so if you
skip it nobody can tell later whether this way of working is paying for
itself.

```markdown
# Run log

One row per expert run, written by grit-build. Read by grit-report.

| When | Phase | Expert | Task | Files | Verified with | Asked | Filed | Outcome |
|---|---|---|---|---|---|---|---|---|
| 2026-10-26 14:02 | 2 | grit-core | model the Deal pipeline | 0 | n/a | 2 | 0 | done |
| 2026-10-26 14:19 | 2 | grit-resource | generate Deal | 11 | go build, go test | 0 | 1 | done |
| 2026-10-26 14:31 | 2 | grit-admin | pipeline board | 3 | pnpm build | 1 | 0 | done |
```

What each column means, because a column people fill in differently measures
nothing:

- **Files** is the count of files changed, not their names. The git diff has
  the names.
- **Verified with** is the command that was actually run. `n/a` when the run
  changed no code. **Never write a command that was not run.** This column is
  the one the report leans on hardest, and a hopeful entry in it makes the
  whole log worthless.
- **Asked** is how many questions the expert put to the user.
- **Filed** is how many Grit issues it opened.
- **Outcome** is `done`, `blocked`, or `handed back` when the work was not
  that expert's and you had to route again. Record `handed back` honestly:
  it is the number that tells you your own routing is wrong, and hiding it
  only means you keep making the same mistake.

One row per run, appended, never rewritten. If an expert runs twice in a phase
that is two rows, and that is a signal worth being able to see.

## Step 6: close out

- `cd apps/api && go build ./... && go test ./...`
- `grit doctor`
- The frontend build for any app that changed
- Report: what was built, what was verified and how, what is left, and any
  issue numbers filed along the way

Never report a build as done on the strength of having written it.

At the end of a phase, run `grit-report`. It reads the run log, the feedback
file and `phases.md` and says whether this way of working is actually paying
for itself on this project. If it is not, that is worth knowing in phase two
rather than phase six.

## The profile template

```markdown
# Project profile

Written by grit-build. Editable: correct anything wrong and the experts will
follow it rather than re-ask.

## Product
What it is:
Who uses it:
What it replaces:

## Surfaces
Architecture (api/single/double/triple):
Also shipping:            desktop? mobile?
Ships first:

## Data
A row belongs to:         everybody / a user / an organisation
Currency:                 and minor units?
Timezone:
Week starts:

## Constraints
Must never happen:
Deadline:
Regulator or policy:

## Decisions
Kept as they are made, with the date, so nobody relitigates them.

- YYYY-MM-DD  decision, and the reason in one line

## Open questions
- Things nobody has answered yet. An expert may add to this.
```

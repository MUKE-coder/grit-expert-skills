---
name: grit-feedback
description: >-
  File what Grit got wrong as a GitHub issue, and check later whether the fix
  shipped. Use when an expert hits a framework bug, a missing feature, or has
  to hand-write something Grit should have given it, and for "has that issue
  been fixed", "check my grit issues", "what did we file".
---

# grit-feedback

Every expert in this pack files its own findings as it goes. This skill is the
format they use, the rules about where an issue goes, and the way to check
later whether a fix has landed.

The reason to bother: a framework only gets better from the projects that use
it, and a bug found in real work and never reported is a bug that will be
found again, by somebody else, next month.

## What is worth filing

**File it** when Grit:

- Produced code that does not compile, or that compiles and is wrong
- Told you it succeeded while leaving the project broken
- Made you hand-write something it advertises
- Generated something whose removal does not reverse it
- Has a flag or field type that does not do what the docs say
- Has docs that are wrong, missing, or that cost you an hour

**Do not file**:

- Your own mistake, including a flag you guessed instead of checking
- A version-skew problem that `grit update` fixes
- Something you have not reproduced
- A preference. "I would have designed this differently" is not a bug, unless
  you can say what it costs a user

## Where it goes

| The bug is in | Repo |
|---|---|
| Grit itself: CLI, generator, scaffold, templates, docs | `MUKE-coder/grit` |
| Sentinel, the WAF | `MUKE-coder/sentinel` |
| Pulse, the profiler | `MUKE-coder/pulse` |
| GORM Studio, the database browser | `MUKE-coder/gorm-studio` |
| Scout, the scanner | `MUKE-coder/scout` |

Those four are separate libraries. **Their bugs are never fixed inside Grit
and never worked around silently.** If you must work around one to keep going,
file the issue first, then put the workaround behind a comment naming the issue
number so it can be removed when the fix lands.

## Search before you file

Another expert may have filed this minutes ago. Always:

```bash
gh issue list --repo MUKE-coder/grit \
  --search "<three distinctive words from the symptom>" --state all --limit 5
```

If it exists and is open, add your reproduction as a comment: a second
reproduction is genuinely useful and a duplicate issue is not. If it exists
and is closed, check the version it closed in against this project's version
before reopening, because you may simply be behind.

## The body

An issue that gets fixed has three things: what you ran, what happened, and
what you expected. One that does not get fixed is a description of a feeling.

```markdown
## What I ran

grit generate resource BlogPost --fields "title:string" --tree --seed
grit remove resource BlogPost --force
cd apps/api && go build ./...

## What happened

internal/database/blog-posts_seeder.go:16:19: undefined: models.BlogPost

grit remove printed "Resource BlogPost removed successfully!" and exited 0.

## What I expected

A project that builds, or an error saying what was left behind.

## Why it happens, if I know

seeder.go writes <plural-kebab>_seeder.go and remove.go deletes
<plural_snake>_seeder.go. Identical for a one-word resource, different for
every other, which is why `grit remove Widget` is clean.

## Environment

grit 3.411.1 (project scaffolded with 3.411.1)
architecture: triple
Windows 11, go1.27.2
```

Rules for the body:

- **A command someone else can run.** A reproduction that starts "in my
  project" is not one. Say what to scaffold.
- **Paste the real error**, not a paraphrase.
- Name the version, the architecture, and the OS. Half of all generator bugs
  are name-variant bugs that only appear on a multi-word resource, and half
  of the rest are path separators on Windows.
- If you know the cause, say it. If you are guessing, say you are guessing.
- No em dashes.
- Never paste a secret, a token, a connection string or a customer's data into
  an issue. Redact and say you have.

Then:

```bash
gh issue create --repo MUKE-coder/grit --title "<the symptom, not the cause>" --body "$(cat issue.md)"
```

Title it by what a person would search for, which is the symptom. "grit remove
leaves the seeder behind on a two-word resource" gets found. "Name variant
mismatch in remove.go" does not.

## Record it in the project

Append to `.grit/feedback.md`, creating it if needed, so the project carries
its own list and the next session does not refile:

```markdown
| Date | Issue | Repo | Symptom | Status |
|---|---|---|---|---|
| 2026-10-26 | #214 | grit | remove leaves the seeder on a two-word resource | open |
```

If you had to work around it, say where, in the same row. That is the line
somebody will search for when the fix ships.

## Checking whether a fix shipped

```bash
# everything this project has filed
gh issue list --repo MUKE-coder/grit --author @me --state all --limit 30

# one issue, and what closed it
gh issue view 214 --repo MUKE-coder/grit --json state,closedAt,title,comments
```

An issue being closed is not the same as the fix being in **your** project.
Three things have to line up:

1. The issue is closed.
2. The closing comment or the changelog names a version.
3. That version is at or below what you have: `grit --version`.

If you are behind, `grit update`, then `grit upgrade` inside the project to
bring framework-owned files forward, then re-run the reproduction. **Re-run
it.** A closed issue with an unverified fix is a guess, and the workaround you
left in place is still there until you remove it.

When it is verified: update the row in `.grit/feedback.md` to
`fixed in vX.Y.Z, verified`, remove the workaround, and comment on the issue
saying you confirmed it. That last step is a courtesy that makes the next
report more likely to be believed.

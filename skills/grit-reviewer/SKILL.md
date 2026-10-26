---
name: grit-reviewer
description: >-
  Read the diff and find the bugs before a user does, with the failure modes a
  Grit project actually has. Use for "review this", "check my changes", "did I
  break anything", "review before I commit", or as the last step of any build.
---

# grit-reviewer

You read what was just written and look for what is wrong with it. Not style,
not preferences: things that will behave incorrectly.

```bash
git diff
git diff --staged
git status --porcelain          # and look for untracked files
```

## Start with what the diff does not show

Three failures in this project type are invisible in a diff and each has
shipped more than once.

**An untracked file.** A new file in an already-tracked directory is the one
that gets left out of the commit, and then CI fails on a missing symbol while
the author's machine is fine. `git status --porcelain` and check every `??`
line that is inside the change.

**A generated artifact nobody regenerated.** If a Go struct changed, did
`grit sync` run? If a resource was added or removed, is the access table
current? `grit doctor` answers both.

**A staged-versus-modified mix-up.** `git diff --cached --stat` is the truth
about what is about to be committed. A ` M` in `git status` means
**unstaged**, and a release has shipped empty because of exactly that.

## The Grit-specific failure list

Check these before general correctness, because they are the ones this
framework produces:

**A name variant used inconsistently.** A path built from one variant and
deleted, read or matched by another. Identical for a one-word resource,
different for every other, which is why a one-word test proves nothing. If the
diff touches a path built from a name, check it with a two-word name.

**An injection with no removal.** If the change adds a generator that writes
into a shared file at a marker, `grit remove` must take it back. The pair is
the contract and half of it is a project that stops compiling on cleanup.

**A `strings.Replace` on an anchor line.** A replace whose anchor has moved
matches nothing, returns the input unchanged, and reports success. Emitted
import blocks are built as a list, never patched by replace.

**Logic that migrated into a handler.** A domain `if` in a handler is a rule a
job or a second handler cannot reuse, and it will be copied rather than moved.

**`Save(struct)` where a hook set a column.** It discards the hook's
`SetColumn`. Only `Updates(map)` honours it.

**A `models` import of `services`.** An import cycle. Auto-numbering calls
`sequence.Next` directly.

**A missing index on a filtered column**, especially the owner column on an
`--owned-by` resource, which is filtered on every request.

**A list endpoint with no pagination or no preload.** One is a denial of
service, the other is an N+1.

**Authorization in the frontend only.** A hidden button is not a gate. Find the
API-level check or report its absence.

**A credential that can be printed outside development.** A log line outlives
the terminal.

**A hardcoded localhost in anything mobile.** On a phone, localhost is the
phone.

**A Tailwind utility from the wrong palette.** `apps/web` and the admin have
different tokens, and an unknown utility renders nothing and reports nothing.

**An icon added to the admin `iconMap` but not to the named exports.** Two
places, every time.

## Then the general pass

**Errors.** Every one handled, wrapped with context. No `_` on an error. An
error that is logged and swallowed is a decision, so check it was intended.

**Nil and empty.** API data indexed without normalising (`data[0]` where the
list can be null). A map read without the second return. A pointer
dereferenced after a lookup that can miss.

**Boundaries.** Off-by-one in pagination. An empty slice treated as an error.
The first page and the last page.

**Concurrency.** Shared state written from more than one goroutine. A closure
capturing a loop variable. A context that is never cancelled.

**The eight states**, for anything interactive. Error and success are the ones
missing.

## Verify, do not reason

A review that ends in an opinion is worth less than one that ends in a command
somebody ran:

```bash
cd apps/api && go build ./... && go test ./...
go vet ./...
pnpm build
grit doctor
```

And for a UI change, **look at it**. If `agent-browser` is installed, drive the
page and take the screenshot. A synthetic DOM check or a grep for a class name
will confirm something that is visibly broken, and a stale dev-server bundle
will show you code that is no longer there.

## How to report it

Lead with the most severe thing. For each finding: the file and line, what
will go wrong, and the input or state that makes it go wrong. A finding with
no failure scenario is a preference wearing a severity label.

Separate what you confirmed from what you suspect, and say which. "This
panics when the list is empty, see line 41" and "this looks like it might
race, I did not reproduce it" are both useful, and conflating them is not.

If the change is clean, say it is clean in one line. Inventing a finding to
look thorough wastes the author's time and trains them to ignore you.

## Then file what Grit got wrong

If the review found a framework fault rather than an author fault, that is an
issue. The author should not have to work around a generator bug silently, and
the next project should not meet it fresh. `grit-feedback` has the format.
File it as you find it, search first for a duplicate, and put the issue number
next to any workaround left in the code.

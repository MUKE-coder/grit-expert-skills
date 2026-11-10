# The working agreement

Every expert in this pack follows these. They are here once so that the whole
pack does not each carry its own copy and then disagree.

## 1. The project profile comes first

`.grit/project-profile.md` in the project root holds what has already been
asked and answered. **Read it before you do anything else.** Ask only about
what it does not cover, then append the answer under the right heading so
nobody asks again.

If it does not exist, you are the first expert in. Run the interview in
`grit-build`, write the file, then carry on.

The profile is editable by a human and theirs to correct. Never silently
change an answer that is already in it: if the work contradicts the profile,
say so and ask.

## 2. Ask rather than assume

The default is to ask. These are the things worth one question each, because
getting them wrong means rebuilding:

- What the product is and who uses it, in their words not yours
- Which surfaces ship (API, web, admin, desktop, mobile) and in which order
- Whether a row belongs to a user, an organisation, or everybody
- Money, dates and units: currency, timezone, whether amounts are minor units
- What must never happen (a hard constraint: data residency, offline, a
  regulator, a deadline)

Use the ask tool with concrete options, not an open question. "Should deal
value be a money type in UGX, or a float?" beats "how should I model money?".

Where a wrong guess is cheap and reversible, pick the obvious option, say
which you picked in one line, and keep going. Interrupting for something you
could have defaulted wastes the person's attention, which is the resource you
are actually spending.

## 3. Grit facts come from the binary, not from memory

Grit ships several releases a week. Field types, flags and plugin names move.
Anything version-specific gets looked up:

```bash
grit --version                       # what this project is actually on
grit docs search "field types"       # find the page
grit docs show docs/concepts/field-types
grit generate resource --help        # the flags this binary really has
```

The index is built into the binary, so it answers for the version installed
rather than for the docs site, which is usually ahead. If a flag you remember
is not in `--help`, it does not exist here.

**Pass the page path without a leading slash.** In Git Bash on Windows, which
is the shell Claude Code uses there, MSYS rewrites `/docs/...` into
`C:/Program Files/Git/docs/...` before the CLI sees it, and the error reads as
a missing page rather than a mangled argument. `docs/concepts/field-types`
resolves in every shell. Filed as grit#96; when it is fixed the leading slash
will work too, and this form will still be correct.

What does **not** change is in `references/grit-invariants.md`. Read that, and
trust it.

## 4. Stay inside the framework

Grit already does auth, RBAC, uploads, jobs, mail, cache, search, import and
export, audit, soft delete, money, and the admin panel. **A hand-built version
of any of them is a bug, not a feature.** If you reach for a library, first
run `grit docs search "<the thing>"` and check it is not already there.

If it genuinely is not there, that is a framework gap: see rule 6.

## 5. Write for the next person

- No em dashes in anything a user reads: docs, UI copy, commit messages,
  issue bodies. Colon, comma or full stop instead.
- Match the surrounding code. Comment density, naming, idiom. A file that
  reads differently from its neighbours is a file somebody has to decode.
- Comments say why, never what.
- A generated project shows its own name, copy and theme. Never Grit's.

## 6. Improve Grit while you use it

When you hit a Grit bug, a missing feature, or a place the framework made you
write something by hand that it should have given you, **file it as you find
it**. Do not batch it to the end of the task and do not wait to be asked.

Before filing, search, because an expert working in parallel may have already
filed the same thing:

```bash
gh issue list --repo MUKE-coder/grit --search "<three distinctive words>" --state all --limit 5
```

If it exists, add your reproduction as a comment instead of opening a second
issue. If it does not, file it. `grit-feedback` has the body format, which
repo to use for which library, and how to check later whether the fix shipped.

The rule on which repo: Grit itself goes to `MUKE-coder/grit`. Sentinel,
Pulse, GORM Studio and Scout are separate libraries and their bugs go to their
own repos, never fixed inside Grit and never worked around silently.

## 7. Spend context carefully

A long session costs the person money and gets worse at the end, so:

- Locate before reading. `grep` with a narrow glob, or `grit docs search`.
  Never read a file to see what is in it.
- Read slices of anything over 300 lines, around the match.
- Never read `node_modules`, `.next`, `dist`, lockfiles or generated output.
- Filter command output at the source: one test, `--quiet`, `| tail -50`,
  `git log --oneline -20`.
- Do not re-read a file you already read this session.
- Lead your answer with the change. Do not restate the plan or paste the diff.

`references/token-efficiency.md` has the full version, including the hooks
that enforce this mechanically.

## 8. Verify, then say so plainly

A thing is done when it has been run, not when it has been written.

- Go changes: `cd apps/api && go build ./... && go test ./...`
- Frontend changes: `pnpm build` or at least `tsc --noEmit`
- A UI change: stand the app up and look at it. A screenshot beats a claim.
  A stale dev-server bundle will show you the old code and let you believe it.
- Generated code: `grit doctor`

If a step failed, say it failed and show the output. If you skipped something,
say which thing and why. Never report a partial job as finished.

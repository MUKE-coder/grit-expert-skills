# The git workflow

A project the experts build lives in a repository from the first command, and
every finished piece of work is committed and pushed with a message that says
what it was.

Not housekeeping. Without it the work exists only on one machine, nobody can
see what changed, and `grit upgrade` has nothing to compare against when it
asks whether you have edited a file. The first time a project needs that and
does not have it, it is already too late.

## At project creation

`grit new` does not initialise a repository. That is the first thing to do
after it, before anything is generated, so the scaffold is one commit you can
read rather than mixed in with the first feature.

```bash
cd <project>
git init -b main
git add -A
git commit -m "chore: scaffold with grit v<version>"
```

Then the remote. **Ask before creating it**, and ask what visibility: client
work is private, and a repository created public cannot be made private again
without the history having been visible in between.

```bash
gh repo create <owner>/<name> --private --source=. --remote=origin --push
```

If `gh auth status` fails, stop and say so rather than carrying on locally.
A project that was supposed to be on GitHub and quietly is not is worse than
one that was never meant to be, because nobody finds out until they need it.

Check before you create:

```bash
gh repo view <owner>/<name> >/dev/null 2>&1 && echo "exists already"
```

An existing repository with the same name is a question for the user, not
something to work around by picking another name.

## What never goes in

Check these before the first commit, because removing a secret from history is
a different and much worse job than not committing it.

- `.env` and anything with a real key in it. `.env.example` is fine.
- `.grit/token-usage.json`, which holds one machine's usage history.
- `node_modules`, build output, `tmp/`, `.next/`, `dist/`.
- A database file, unless it is a fixture somebody chose to commit.

`grit new` writes a `.gitignore` covering most of this. Read it rather than
assuming, and add what the project adds.

## After each piece of work

One commit per finished thing, with a prefix that says what kind of change it
is. Not one commit per file, and not one commit for an afternoon.

| Prefix | For |
|---|---|
| `feat:` | A capability that was not there before |
| `fix:` | Something that was wrong and now is not |
| `docs:` | Documentation only |
| `refactor:` | Same behaviour, different shape |
| `perf:` | Measurably faster, with the measurement in the body |
| `test:` | Tests only |
| `chore:` | Dependencies, config, scaffolding, tooling |
| `style:` | Formatting only, no behaviour |
| `build:` | The build or the toolchain |
| `ci:` | The pipeline |

A scope in brackets when it helps: `feat(deals): bulk close from the list`.

The subject line is what changed, in the imperative, under about 70
characters. The body is why, and it is worth writing whenever the reason is
not obvious from the diff. A commit that says `fix: bug` has thrown away the
only chance anyone had to understand it.

```bash
git add <the files, named>
git diff --cached --stat        # read this before committing
git commit -m "feat(deals): close a deal from the list" -m "<why>"
```

**Stage by name, and read what you staged.** `git add -A` after a generator
run sweeps up whatever else was lying around, and a new file in an
already-tracked directory is the one that gets left out when you stage by
directory. `git diff --cached --stat` before every commit: ` M` in
`git status` means the change is NOT staged, and a commit that ships empty
looks exactly like one that worked.

## Pushing

Push when the piece of work is finished and its tests pass, not when it
compiles.

```bash
cd apps/api && go test ./... && cd -
git push
```

Branching is the user's choice and worth asking once, at the start, then
recording in `.grit/project-profile.md` so nobody asks again:

- **Straight to main** suits a solo project before it has users.
- **A branch per feature, opened as a PR** suits anything with a reviewer, and
  anything with a deployment attached to main.

If they chose branches:

```bash
git switch -c feat/close-deals
# ... the work, committed ...
git push -u origin feat/close-deals
gh pr create --fill
```

Never force-push a branch somebody else may have, and never rewrite main.

## Attribution

**Do not add AI attribution to commits or pull request bodies.** No
`Co-Authored-By` for an assistant, no "generated with" footer, no emoji
signature. The commit history is a record of what changed in the software, and
a tool's byline on every line of it is noise that cannot be removed later
without rewriting history.

If the user asks for it, add it. Otherwise it does not go in, including when a
harness suggests one.

## When the work is not finished

Commit it anyway, on a branch, rather than leaving it uncommitted at the end of
a session. Say in the message that it is partial:

```
feat(deals): bulk close, server side only

The endpoint and the service are done and tested. The list action and the
confirmation dialog are not started.
```

Work that only exists in a working directory is work that one `git checkout`
removes, and nobody can pick it up but the person whose machine it is on.

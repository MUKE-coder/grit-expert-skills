---
name: grit-adopt
description: >-
  Bring an existing Grit project up to the current framework without breaking
  what already works, and decide which new features are worth adopting
  afterwards. Also checks whether the core batteries (Sentinel, Pulse, GORM
  Studio, Scout) are in step. Use for "upgrade this project", "we are on an
  old Grit", "is this project out of date", "what would upgrading cost",
  "are our versions in sync", "how do we adopt the new features", "migrate
  this project".
---

# grit-adopt

A project that has been running for months is not a fresh scaffold, and the
difference is the whole job. Somebody has edited the generated files. That is
allowed, it is the point of generated code, and it is also the thing that
makes an upgrade a piece of work rather than a command.

Your job is in two halves, and **they are separate changes**:

1. **Catch up.** Move the framework files to the current version, leaving the
   edited ones working. Finish green and commit before anything else.
2. **Adopt.** Pick up the new capabilities that are worth having, one per
   commit, after the catch-up is done.

Doing both at once produces a diff nobody can review and a bisect nobody can
run.

## Never upgrade blind. Measure first.

Three commands, in this order, before touching anything:

```bash
grit versions          # how far behind, and in what
grit doctor            # what is actually wrong, rather than merely old
grit upgrade --diff    # what the upgrade would change in files you have edited
```

`grit versions` is the one that sizes the job. It reports the project's Grit
version against the CLI's, every battery the API mounts against the version
this CLI expects, and every installed plugin. `--json` if you want to put it
in a report.

`grit upgrade --diff` is the honest estimate. It takes no argument and prints
what the new version would do to every file the upgrade is going to leave alone, and that list **is
the work**. A project with three edited files is an afternoon; a project with
forty is a planned piece of work, and saying so early is worth more than
starting it.

**Report what you found before proposing anything.** The user is deciding
whether to spend the time, and they cannot decide from "it is out of date".

## How the upgrade protects what works

Grit records a hash of every framework file when it writes it. On upgrade:

- A file **you have not touched** is rewritten to the current version.
- A file **you have edited** is left exactly as it is, and named in the output.

That is the mechanism, and understanding it answers most questions about what
is safe. Your resource definitions, your handlers, your business logic were
never Grit's files, so they are not candidates either way.

It also means the risk is inverted from what people expect. The danger is not
that the upgrade overwrites your work; it is that it **cannot**, so a heavily
edited project ends up part new and part old, with the two halves expected to
compile together.

**`--force` overwrites everything, including your edits.** It is almost never
the right answer on a real project. If you use it, you are choosing to redo
the edits, and you should say that out loud first and have the branch to go
back to.

## The sequence

```bash
git checkout -b upgrade-to-$(grit version | awk '{print $3}')
git status            # must be clean: an upgrade on a dirty tree is unreviewable
```

1. **Commit or stash everything.** Non-negotiable. The value of the next step
   is `git diff`, and a dirty tree destroys it.
2. **Run `grit upgrade --plan`.** It upgrades and writes `UPGRADE-PLAN.md`: a
   runbook for the files it left alone. Read it before anything else.
3. **Build and test immediately**, before touching a single left-alone file:
   ```bash
   cd apps/api && go build ./... && go test ./...
   cd ../.. && pnpm install && pnpm type-check && pnpm lint
   ```
   Whatever breaks here is the upgrade's doing, and it is much easier to
   diagnose now than after you have also started editing.
4. **Commit that**, green or not, as its own commit. If it is not green, the
   next commits are the fixes and the history shows why.
5. **Work the left-alone list one file at a time**, each as its own commit.
   For each: find it in the `grit upgrade --diff` output, decide whether
   your edit is still needed, and either re-apply it on top of the new version or
   keep yours and note why.
6. **Run `grit doctor` again** at the end. New versions add checks, so a
   project that was clean before can legitimately have new findings now.
7. **Stand it up and look at it.** Sign in, open the admin, open the main
   screens. A type-checking project with a broken screen is a thing that
   happens, and only looking finds it.

## Deciding on a left-alone file

For each file the upgrade did not touch, the question is why it was edited.

| Why it was edited | What to do |
|---|---|
| A fix for a framework bug | Check whether the bug is fixed upstream. If it is, take the new version and drop the patch. `grit docs show docs/changelog` or the issue number beside the workaround. |
| A deliberate customisation | Keep yours, and re-apply it on top of the new file if the new file moved. Note why in the commit. |
| A change nobody remembers | Take the new version. An unexplained edit that nothing tests is almost always safe to drop, and if it was not, the tests say so. |
| Deleted framework code | Take the new version, then delete again if it is still unwanted. Reasoning about a diff against a file that is missing half of itself is harder than redoing the deletion. |

## The batteries

Sentinel, Pulse, GORM Studio, Scout and the rest are ordinary Go modules in
`apps/api/go.mod`. `grit versions` says where each one stands, and `grit
upgrade` raises any that are below the floor this CLI expects.

Three things to be clear about:

- **A floor is not a pin.** Grit raises a project below the floor and leaves
  one above it alone. It never downgrades. A project ahead of the floor is
  fine and says `ahead`.
- **Behind is not the same as broken.** Some floors are security releases and
  some are features. `grit versions` prints the reason for each one that is
  behind; read it before deciding urgency.
- **A missing battery is not a fault.** A project that never mounted GORM
  Studio reports `absent`, and that is a choice, not a gap.

If a battery is behind and the project does not upgrade cleanly, check that
library's own release notes before assuming Grit is at fault. A bug in
Sentinel, Pulse, GORM Studio or Scout belongs as an issue on **that**
repository, not in Grit: hand to `grit-feedback`, which knows the rule.

## Adopting new features, afterwards

Only once the catch-up is committed and green.

```bash
grit docs show docs/changelog     # what landed between the two versions
grit plugin list                  # what exists now that did not before
grit blueprint list
```

The changelog between the project's old version and the current one is the
menu. Most of it will already be in the project, because the upgrade brought
the framework files with it. What needs a decision is anything that changes
shape: a new plugin, a new architecture surface, a new way of doing something
the project already does by hand.

**The question for each is not "is this new" but "what is this replacing".**

- If the project hand-wrote something Grit now ships, that is the strongest
  candidate: delete code, gain tests and upgrades. Confirm the shipped version
  actually covers the case before deleting, because the hand-written one knows
  something about this product.
- If it is new capability nobody asked for, it is a backlog item, not part of
  this work. Say so and move on.
- If it would change the data model, it is a migration with its own plan.
  Hand to `grit-core` and `grit-data`.

One per commit. A commit that upgrades the framework *and* adopts two plugins
*and* refactors a module cannot be reverted when one of the three is wrong.

## Things that go wrong, and what they look like

- **The project has no `grit.json` version.** It predates the version stamp.
  `grit versions` says "not recorded". Upgrade still works; you just cannot
  read the changelog range, so read the whole thing from the project's
  approximate date.
- **The upgrade leaves almost everything alone.** Somebody reformatted the
  repository, or line endings changed, so every file looks edited. Check with
  `git log --stat` for a bulk commit. If that is what happened, `--force` on
  a branch is genuinely the right tool, because the "edits" are not edits.
- **It compiles and a screen is blank.** A framework file the upgrade left
  alone is importing something the new version moved. The browser console and
  `pnpm build` say which, and `grit upgrade --diff` prints the diff for every
  file it left alone, that one included.
- **A plugin is behind.** `grit plugin update` brings installed plugins up to
  this CLI's version of them. Do it as its own commit, after the framework
  upgrade is green, for the same reason as everything else here.

## Hand back to

- `grit-feedback` for anything the upgrade broke that is Grit's fault, and for
  battery bugs, which go on that library's own repository.
- `grit-plugins` when the adoption question is "should this hand-written
  feature become a plugin".
- `grit-core` and `grit-data` when adopting something changes the model.
- `grit-security` after an upgrade that crossed a security release.
- `grit-reviewer` on each commit before it lands.
- `grit-critic` when the project is back on current and somebody wants to know
  whether it is actually in good shape.

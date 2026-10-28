---
name: grit-plugins
description: >-
  Grit plugins: what already exists so you do not rebuild it, whether a
  feature should be a plugin at all, writing one from scratch, and proposing
  one for Grit to ship officially. Use for "is there a plugin for this",
  "write a plugin", "should this be a plugin", "grit plugin add", "package
  this up", "suggest a plugin", "multi-tenancy", "a kanban board", "a
  calendar".
---

# grit-plugins

Three jobs, in this order of how often they come up:

1. **Check whether it already exists.** Most of the time the answer to "build
   me X" is that Grit or a plugin already has it, and the expensive mistake is
   hand-writing something that ships in the box.
2. **Decide whether a new thing should be a plugin.** Usually it should not.
   Most features are just code in the project.
3. **Write one, properly, when it should be.** Including the half everybody
   skips.

A fourth, less often: **propose one for Grit to ship officially**. That is at
the bottom of this file.

## Always start by looking, never by remembering

Grit ships several releases a week. The plugin list in your memory is stale.

```bash
grit plugin list                 # official, Go module, and community plugins
grit plugin info <name>          # what one actually does
grit docs search "<the feature>"
```

`grit plugin list` answers for the binary this project has, which is the only
answer that matters. If a plugin you remember is not in it, it does not exist
here.

Also check what is already installed before proposing anything:

```bash
cat .grit/plugins.lock.json
```

Installing a plugin that is already installed is refused, and the refusal is
the good case. The bad case is hand-building a feature next to a plugin that
provides it.

## Is it a plugin at all?

Grit has four mechanisms and they are not alternatives. Read
`grit docs show docs/extending` for the full version. The short form:

| The thing | Use | Test |
|---|---|---|
| A kind of record | `grit generate resource` | Would you put it in a table and list it? |
| A capability across layers | A plugin | Would a **second project** want it? |
| A component | `grit ui add` | Does the data already exist? |
| A whole application | A blueprint | Are you starting, not adding? |

**The question that settles it: would a second project want this?**

If no, it is not a plugin. It is code you write in the project, and that is
the right answer. A plugin is packaging, and packaging something used once
costs you a manifest, a lockfile entry and a removal path in exchange for
nothing.

If yes, and it is a record, it is still a resource. Plugins are for things
that are not nouns: multi-tenancy, a command palette, impersonation, a board.

### Say the unit out loud

When you cannot decide, name what the thing *is* in one word. "Invoice" is a
noun, so resource. "Multi-tenancy" is not a noun you would store, so plugin.
"A nicer pricing section" is a component, so `grit ui add`.

### The trap worth naming out loud to the user

`grit ui add` gives presentation with nothing behind it. If somebody asks for
a board and you reach for a UI block, they get a board that displays nothing
and saves nothing. That is worse than having no board, because it looks
finished. A UI block when the data exists; a plugin when it does not.

## Writing one

Read `grit docs show docs/plugins/authoring` first. It is written around the
kanban plugin, which is the reference implementation: it needs every part of
the system at once, so it is the thing to copy the shape of.

### The shape

```go
Plugin{
    Name, Version, Summary, Description string
    Requires   []string                        // other plugins, checked first
    Preflight  func(ctx Context) error         // refuse BEFORE the first write
    GoDeps, NodeDeps []Dependency              // fetched before any file
    Files      func(ctx Context) map[string]string
    Injections func(ctx Context) []Injection   // snippet at a marker comment
    NextSteps  []string
}
```

Outside the Grit repo, the same shape is a directory with `plugin.json` and a
`files/` folder. Install and removal behave identically. Install it with
`grit plugin add ./dir` or `grit plugin add github.com/you/repo`.

### The steps

1. **Model it first.** Get the resources right before writing any plugin
   code; hand that part to `grit-core` and `grit-data` if the domain is not
   obvious. A plugin with a wrong model is wrong in every project that
   installs it.
2. **Write the files.** Use `apiPath`, `adminFile`, `adminPageFile` and
   `adminSource` rather than hard-coding paths.
3. **Inject at markers, never at code.** The markers are listed in the
   authoring docs. If the marker you need does not exist, that is a finding:
   file it with `grit-feedback` rather than anchoring on a line of code that
   a reformat will move.
4. **Declare every dependency.**
5. **Write a Preflight** for anything the plugin cannot inject its way out of.
6. **Emit a test** alongside the code, so the project that installs it can
   prove it works.
7. **Test removal.** Below.

### The rules, each with what it prevents

- **Never write a file the project already has.** Removal deletes every file
  the lockfile records, so overwriting means removal deletes the user's file.
  The installer refuses to overwrite for this reason: use an injection.
- **Every injection needs a marker.** Anchoring on ordinary code means a
  reformat breaks the install silently.
- **Declare dependencies, do not assume them.** They are fetched before any
  file is written, so a network failure aborts cleanly.
- **Refuse early rather than install half.** Preflight runs before the first
  write.
- **Adapt to the architecture.** `--single` has no `apps/api`; a TanStack
  admin keeps code under `src/` with a different router. Writing the Next
  shape unconditionally is not a build error: the plugin reports success and
  the feature is simply absent.
- **Pin a column name GORM would not guess.** GORM finds known initialisms
  anywhere in a field name, so `WIPLimit` becomes `w_ip_limit`. The struct
  reads fine and only a write by column name fails, in a handler, in
  production. Any field with three or more consecutive capitals gets an
  explicit `gorm:"column:..."`.
- **Put a working surface in the Content nav, not System.**
  `grit:nav:system` renders in the System Hub's Extensions tab, which is
  right for a webhook log and wrong for anything somebody opens while
  working. `grit:nav:content` puts it in the rail beside the resources.
- **Embed code you want tested.** A plugin whose algorithm lives in a Go
  string has no tests for what it ships; that string compiles nowhere until
  somebody installs it. Keep it in a real file and `//go:embed` it.

### Testing it, including the half everybody skips

On a **freshly scaffolded** project, not the one you have been working in:

```bash
grit new testbed --triple --next && cd testbed
grit plugin add ./my-plugin
cd apps/api && go build ./... && go test ./internal/...
cd ../.. && pnpm install && cd apps/admin && npx tsc --noEmit && pnpm lint

cd ../.. && grit plugin remove <name> --force
cd apps/api && go build ./...      # <- THIS ONE
```

That last build is the test. Installing is the easy half. If removal leaves a
project that does not compile, the plugin changed something the lockfile did
not record, and you will find out from a user rather than from yourself.

**And look at it running.** Stand the admin up and open the screen. A plugin
can install cleanly, compile, type-check and still put its page somewhere
nobody can reach: that is exactly how the kanban board ended up three clicks
deep under System on its first run, with every check passing.

## Publishing one

```bash
grit plugin submit
```

Prints the checklist and the submission link. Accepted plugins land in
`internal/plugin/community.json` and appear in both `grit plugin list` and the
marketplace page.

Listing is not endorsement and nobody audits the code. Say that to the user
when recommending a community plugin, and read what it writes with
`git diff` after installing, the same as any dependency.

## Proposing a plugin for Grit to ship officially

Sometimes the right answer is not "write this plugin" but "Grit should have
this". Propose it when **all** of these hold:

1. **More than one project wants it**, and you can name the second one.
2. **It is not a vertical.** "A Kanban board" is a feature; "an issue tracker"
   is an application and belongs in a blueprint.
3. **It is mostly framework plumbing.** If the hard part is business rules
   specific to one domain, it is that project's code.
4. **It does not fit the core test.** Grit's own test for core is: is this
   machinery a team would otherwise rebuild for every client target, and can
   one definition drive it everywhere? Ordered lists that survive concurrent
   reordering is machinery, so it went into core. A Kanban board is one
   screen that needs that machinery, so it is a plugin. **If what you found is
   machinery, propose it for core, not as a plugin, and say so.**

### How to propose

Use `grit-feedback` to file it, and put these in the issue:

- **The unit, in one word.** What is the thing.
- **The second project.** Name it. A proposal with one user is a feature
  request for that user's project.
- **What it writes.** Models, routes, pages, dependencies. If you cannot list
  them, the shape is not clear enough to propose yet.
- **Which markers it needs**, and whether any of them do not exist yet. A
  missing marker is often the more valuable half of the proposal.
- **What you had to hand-write instead**, with the file and line count. This
  is the strongest evidence a proposal can carry: it is the cost, measured.
- **Whether it is really core.** Say which of the two it is and why.

Good candidates look like: a calendar over any resource with a date field,
an audit-log viewer, an import wizard, a comment thread attachable to any
resource, a notification centre. Each is a capability, each would be wanted
by a second project, and each is plumbing rather than domain rules.

Bad candidates: anything that is one screen for one business, anything whose
hard part is a pricing rule, and anything already in `grit plugin list`.

## Hand back to

- `grit-core` when the domain model is not settled yet.
- `grit-resource` when it turns out to be a resource after all, which is
  often.
- `grit-admin` for the admin screens the plugin writes.
- `grit-ui-ux` when the surface is customer-facing.
- `grit-feedback` to file a missing marker, a proposal, or a bug the build
  found.
- `grit-blueprints` when the thing is a whole application rather than a
  feature.
- `grit-reviewer` on the diff before it ships.

---
name: grit-blueprints
description: >-
  Grit blueprints: what complete applications already exist to start from or
  read, whether the thing being built should become one, working inside a
  blueprint repository, and proposing a new one. Use for "is there an example
  of this", "what should I start from", "how did they do chat", "make this a
  blueprint", "grit blueprint", "suggest a blueprint".
---

# grit-blueprints

A blueprint is a whole application, in its own repository, built with Grit.
Not something you install: something you clone and work from. A plugin adds a
feature to a project; a blueprint **is** a project.

Three jobs:

1. **Point at one that already exists**, when somebody is starting something
   close to it, or is stuck on a problem one of them already solved.
2. **Work inside one** without forking away from the framework.
3. **Propose a new one**, when the thing being built is worth being one.

## Always look, never recall

```bash
grit blueprint list              # what exists, and what is only announced
grit blueprint info whatsapp     # what it teaches, and where it is
```

The list is as current as the installed binary. There is a browsable copy at
`grit docs show docs/blueprints`.

Two things to be clear about when you report the list:

- Some blueprints are **open source** and some need a **membership**, which
  sends an invitation to a private repository. Say which, rather than sending
  somebody to a 404.
- Some are **planned**. Say "not yet" rather than implying it exists.

## Blueprints are not examples

Both are real applications. They are different things and the distinction
matters when you point somebody at one.

| | Blueprint | `examples/` in the Grit repo |
|---|---|---|
| Where | Its own repository | Inside the Grit repository |
| Scope | A designed product | A proving ground, built on CI |
| Cost | Open or membership | Free |
| Use it to | Start a project | Read how something is done |

If somebody just wants to see how a pattern is done, `examples/` is often the
faster answer and costs nothing. Check there first.

## Reading one to answer a question

This is the most useful and least used thing blueprints are for. When
somebody asks "how would I do realtime chat" or "how do product variants
work", the answer frequently exists as working, tested code.

```bash
grit blueprint info whatsapp     # what it teaches
```

Quote the approach and name the file. Do not copy large slabs of a private
repository into a project that has not paid for it; describe the shape and
point at it.

## Working inside a blueprint repository

The rule that keeps a blueprint useful:

> A gap the blueprint finds is fixed **in Grit first**, released, and then
> the blueprint runs `grit upgrade` into it.

Patching the framework's own generated files inside the blueprint is how a
blueprint becomes a fork, and a forked blueprint stops being a test of the
framework, which is half the reason it exists.

So when you hit something broken while working in one:

1. Confirm it is Grit's, not the blueprint's.
2. File it with `grit-feedback`.
3. Fix it in Grit, release, then `grit upgrade` the blueprint.
4. Only hand-write in the blueprint when the thing is genuinely specific to
   that product, and leave the issue number beside any workaround.

Each blueprint runs its own CI. Run it locally before pushing: `golangci-lint`,
`go test -race`, `pnpm lint`, `type-check`, `test`, `build`, and
`pnpm audit --prod --audit-level=high`.

Run blueprint dev servers on **spare ports**. The usual 8080, 3000 and 3001
are often already taken by whatever else is running, and two servers fighting
over a port produces a confusing failure that looks like a code bug.

## Should this become a blueprint?

Propose one when all of these hold:

1. **It is a whole application**, not a feature. If the unit is a capability,
   it is a plugin: hand to `grit-plugins`.
2. **People recognise it from the name.** A blueprint's value is "start from
   the shape you already have in your head". "WhatsApp" and "a storefront"
   carry that; "an internal tool for reconciling vendor statements" does not,
   however good it is.
3. **It exercises something no existing blueprint does.** Another CRUD app
   with a different noun teaches nothing new. Check `grit blueprint list`
   first and say what this one covers that the others do not.
4. **It would survive upgrading.** A blueprint is a standing commitment: it
   has to keep passing CI against new Grit releases. Something built on a
   hand-patched fork cannot be one.

### What a proposal has to say

Not "an app that does X". Blueprints are chosen by what somebody would open
them **for**, so a proposal is mostly that list:

- **What it teaches**, as three or four specific things. Not "how to build a
  shop" but "a cart that survives sign-in, and a checkout that survives a
  retry". If you cannot write three, it is not a blueprint yet.
- **The surfaces**: web, admin, mobile, desktop. A blueprint that only has an
  admin is usually a plugin wearing a hat.
- **What in Grit it would stress.** This is the second reason blueprints
  exist and the one that justifies the maintenance. Name the parts of the
  framework nobody has pushed hard yet.
- **The nearest existing blueprint**, and why this is not that.

File it with `grit-feedback`.

### When the honest answer is no

Most applications should not be blueprints. The cost is ongoing: a repository
that has to keep working against every release, with CI, demo data and
documentation. Say so plainly when the answer is that this is a good project
but not a good blueprint, and offer the two things it probably is instead: a
plugin for the reusable part, and an `examples/` entry if the pattern is
worth reading.

## Starting a project from one

```bash
git clone <repo> myapp && cd myapp
grit upgrade          # pull it up to the installed Grit first
```

Upgrade before building on it, not after. A blueprint can be a release or two
behind, and finding that out after a week of work is worse than finding it
out in the first minute. Then rename the module, rotate the demo
credentials, and read the blueprint's own README for what it expects in the
environment.

## Hand back to

- `grit-plugins` when the reusable part is a feature rather than an
  application.
- `grit-core` when the domain model needs settling before anything is cloned.
- the architecture expert (`grit-triple`, `grit-double`, `grit-single`,
  `grit-mobile`, `grit-desktop`) once the project is on disk.
- `grit-feedback` for the gap the blueprint found, and for the proposal
  itself.
- `grit-deploy` when it is time to put it somewhere.

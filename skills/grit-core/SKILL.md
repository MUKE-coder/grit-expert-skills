---
name: grit-core
description: >-
  The Grit framework itself: conventions, the API contract, the folder
  structure, what belongs in the framework versus what you build, and how to
  model a domain before any code is generated. Use for "how does Grit do X",
  "where should this live", "model this domain", "is this the right shape", or
  any decision that the rest of the build will be derived from.
---

# grit-core

You decide the shape. Everything the other experts do is derived from the
model and the conventions, so a wrong decision here is rework in five places,
and a right one makes the next four experts almost mechanical.

**Read `references/grit-invariants.md` first.** It is the part of Grit that
does not change between releases, and it is the answer to most "how does Grit
do X" questions. For anything version-specific, look it up:

```bash
grit --version
grit docs search "<the thing>"
grit docs show /docs/<page>
```

## The first question is always: does Grit already do this?

Grit ships auth with refresh and sessions, RBAC and per-resource policies,
uploads to S3 or local disk, background jobs, cron, mail with templates,
Redis cache, full-text search, CSV and XLSX import and export, an audit trail,
soft delete, money, a workflow state machine, trees, multitenancy, and an
admin panel that generates itself from your models.

**A hand-built version of any of those is a bug.** Before you design
anything, check:

```bash
grit docs search "audit"
grit plugin list        # what is installable
grit add --help         # what can be added to this project
```

If it genuinely is not there, that is a framework gap. Say so, build the
minimum that unblocks the product, and file it: `grit-feedback` has the
format. Do not quietly build a parallel system, because the next release of
Grit may ship one and then the project has two.

## Modelling a domain

Work in this order. Each step constrains the next, and doing them out of order
is how a project ends up with a `user_id` on everything and no idea which rows
an organisation can see.

### 1. Name the nouns, then cut them

Write every noun the product talks about. Then remove:

- Anything that is a **field** rather than an entity. A "status" is not a
  resource. A "priority" is not a resource.
- Anything that is the **same thing in a different state**. A lead and a
  contact are usually one resource with a stage, not two resources. If you
  find yourself copying rows between two tables, they were one table.
- Anything with **one row, ever**. That is settings, not a resource.

What survives is a resource. Each one becomes a model, a service, a handler,
a set of routes, a Zod schema, a TypeScript type, React Query hooks, an admin
resource and an admin page, from one `grit generate resource`.

### 2. Decide ownership before anything else

This is the expensive one, and it has exactly three answers:

| Ownership | What it means | How |
|---|---|---|
| Everybody | Any signed-in user with the permission sees every row | the default |
| A user | A row belongs to one person and only they and ADMIN see it | `--owned-by <field>` |
| An organisation | Rows are scoped to the active org | the multitenant plugin, `--tenant-owned` |

Get this wrong and the fix touches every query, every handler, every policy
and every test. Ask. It is one of the five questions in the project profile
for exactly this reason.

A mixed project is normal: in a CRM, contacts belong to an organisation and a
rep's own tasks belong to a user. What is not normal is deciding per resource
as you go, with no rule, which is how two resources that should agree end up
disagreeing.

### 3. Relationships, explicitly

Always the explicit form, with the target named:

```
client:belongs_to[Client]
items:has_many[InvoiceItem]
tags:many_to_many[Tag]
```

Never the bare `client:belongs_to`. The explicit form is what the generator
needs to write the join, the dropdown and the type, and it is what a reader
needs to know what it points at. The shorter form exists for history and
should not appear in new work.

Two rules that save a day each:

- **A belongs_to needs the related model to exist first.** Generate in
  dependency order: `Client` before `Invoice`, `Invoice` before `Payment`.
- **A dropdown shows the related model's label column**, not its id. If the
  related model has no obvious human label, it needs one before the
  relationship is any use in a form.

### 4. Identity that humans use

A person selecting an invoice selects `INV-2026-0041`, not `id 17`. Any
resource a human picks from a list needs a human-readable identifier, and if
it is a sequence, it is auto-numbered in `BeforeCreate` calling
`sequence.Next` **directly**, never through a service, because `models`
importing `services` is an import cycle.

### 5. Money, time and units, once

From the project profile: the currency, whether amounts are minor units, the
timezone, where the week starts. Money is the `money` field type, not a float.
A float for money is a rounding bug with a delay on it.

## Where things live

| It is | It goes in |
|---|---|
| A database shape | `internal/models/` |
| Business logic, a rule, a calculation | `internal/services/` |
| Binding a request and writing a response | `internal/handlers/` |
| Who may do this | `internal/policies/` |
| Something every request passes through | `internal/middleware/` |
| A shape the frontend also needs | `packages/shared/` via `grit sync` |

The one that gets broken most: **logic in a handler**. It feels fine until a
background job, a CLI command or a second handler needs the same rule, which
is always what happens next, and then there are two copies that drift.

A handler is: bind, call one service method, write the response with the
helper. If a handler has an `if` about the domain in it, that `if` belongs in
the service.

## Generated code is not yours

`grit generate` writes files and injects into shared ones at markers like
`// grit:models` and `// grit:routes:protected`. `.grit/manifest.json` records
what Grit wrote and its hash.

Before editing a generated file, ask whether you are editing the right thing:

```bash
grit doctor                    # what has drifted
cat .grit/manifest.json        # what Grit claims it wrote
```

Editing inside a marked region risks `grit upgrade` rewriting it. If a
generated file is wrong for every project, the template is wrong: fix it
upstream and file the issue. If it is wrong only for this project, that is
what the file being yours to edit means, but record the decision in the
project profile so the next person knows it was deliberate.

## When you are about to be clever

Three questions, and if you cannot answer all three, do the boring version:

1. Does the framework already do this? (check, do not recall)
2. Will the next person reading this know why it is not the obvious thing?
3. Does it survive `grit upgrade`?

If the plan is big enough to be worth attacking, and `grill-me` is installed,
use it before writing code rather than after. An hour of being argued with
beats a week of building the wrong model.

## What to hand to the next expert

A model plan they can generate from without asking you anything:

- Each resource, with its fields and exact types
- Each relationship in explicit form
- Ownership per resource, and the flag that implements it
- Which human-readable identifier each one has
- Generation order, dependencies first
- Anything Grit does not cover, and whether you filed it

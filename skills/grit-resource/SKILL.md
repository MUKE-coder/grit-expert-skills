---
name: grit-resource
description: >-
  Run Grit's generator correctly: field types, the flags, inline fields versus
  a YAML definition, conditional fields, relationships, and removing a
  resource cleanly. Use for "generate a resource", "add a field", "what field
  type should this be", "grit generate", "grit remove".
---

# grit-resource

One command writes a Go model, a service, a handler, routes, a policy, a Zod
schema, a TypeScript type, React Query hooks, an admin resource definition and
an admin page. Your job is to get the declaration right, because every one of
those files is derived from it and a wrong field type is wrong in nine places.

You should already have a model plan from `grit-core`. If you do not, get one:
generating from a half-decided model is how a project acquires three
migrations for one column.

## Never recall a field type. Look it up.

Grit ships several releases a week and the field types move. Every time:

```bash
grit docs show docs/concepts/field-types
grit generate resource --help
```

That page is the complete set, with what each one becomes in Go, in
TypeScript, in Zod, and as an admin control. `--help` is the flags this binary
actually has. If a flag you remember is not in `--help`, it does not exist
here, and guessing produces a confident error message about an unknown flag at
best and a silently ignored one at worst.

**Before trusting a generator run that emits unusual Go types, compile it.**
The reliable check is to generate one throwaway resource using every field
type you are about to use and run `go build ./...`. It takes a minute and it
catches the type that does not compile before it is in nine resources.

## The declaration

Two ways in, and the choice matters more than it looks.

**Inline, for something simple:**

```bash
grit generate resource Contact \
  --fields "name:string,email:email,phone:phone,company:belongs_to[Company]"
```

**YAML, for anything with a workflow, conditional fields, or more than about
six fields:**

```bash
grit generate resource Invoice --from invoice.yaml
```

```yaml
name: Invoice
fields:
  - name: client
    type: belongs_to
    related_model: Client
  - name: status
    type: select
    options:
      - value: draft
        label: Draft
      - value: sent
        label: Sent
      - value: paid
        label: Paid
    workflow:
      initial: draft
      transitions:
        - action: send
          label: Send to client
          from: [draft]
          to: sent
        - action: pay
          label: Mark paid
          from: [sent]
          to: paid
      terminal: [paid]
```

### Every key, because a wrong one is silent

A key the parser does not know is ignored. The definition loads, the generator
runs, and whatever you meant by that key is simply absent: `target:` instead of
`related_model:` gives you a `belongs_to` with no model on the other end, and
nothing says so until the build fails somewhere else.

So guessing is the one thing not to do here. These are the keys, and there are
no others.

**On a field:**

| Key | Type | What it does |
|---|---|---|
| `name` | string | the column, snake_case |
| `type` | string | one of the field types |
| `required` | bool | `binding:"required"`, and NOT NULL |
| `unique` | bool | a unique index on this column alone |
| `default` | string | the column default |
| `related_model` | string | the model a `belongs_to`, `has_many`, `many_to_many` or `one_to_one` points at. **Not `target`** |
| `slug_source` | string | the field a `slug` is derived from |
| `server_set` | bool | the API writes it, a client may not |
| `encrypted` | bool | stored through `crypto.EncryptedString` |
| `show_when` | `{field, value}` | the field applies only when another field holds a value |
| `file_accepts` | list | extensions a `file` or `files` field takes, e.g. `[pdf, docx]` |
| `options` | list of `{value, label}` | a `select`'s choices |
| `workflow` | `{initial, transitions, terminal}` | a state machine over a `select` |
| `auto` | bool | the value is generated, for a `number` sequence |
| `auto_prefix` | string | what an auto number is prefixed with, e.g. `INV-` |
| `default_country` | string | the ISO-2 a `tel` assumes |
| `max` | int | the ceiling on a `rating` |

**On the resource:**

| Key | Type | What it does |
|---|---|---|
| `name` | string | the model, PascalCase |
| `fields` | list | the fields |
| `items` | resource | an inline has-many child, generated as a resource of its own |
| `owned_by` | string | names the belongs_to-User field that says who a row belongs to. Empty means every signed-in caller sees every row |
| `tenant_owned` | bool | embeds `tenant.Owned`. Needs the multitenant plugin |
| `confidential` | bool | removes the ADMIN exemption from ownership scoping: an administrator reads nothing. Needs `owned_by`, implies `audit_reads`, refuses `public` |
| `audit_reads` | bool | records every read in the tamper-evident activity log |
| `append_only` | bool | rows are immutable once written: create and read routes only, enforced by GORM and a database trigger |
| `public` | bool | adds a read-only surface outside the auth middleware, guarded by an API key |
| `tree` | bool | hierarchical: adds `parent_id`, a materialised path and a depth |
| `unique` | list of strings | the columns a composite unique index covers. It is what makes the importer's `OnConflict{DoNothing}` mean anything |
| `sync` | `{mode, conflict, ...}` | how the resource behaves offline. `mode` is `offline_first`, `read_only` or `online_only` |

Three that cost time even when you have the key right:

- `options` is a list of `{value, label}` objects, not a list of strings. A
  bare string fails to unmarshal into `FieldOption`.
- A workflow validates. Every state must be reachable and every non-terminal
  state must have a way out, or you get
  `nothing can leave paid. Add a transition out, or list paid under terminal`.
  That error is the validator doing its job: a state machine with a dead end
  is a record nobody can ever move on.
- `sync: {mode: read_only}` is the one to reach for when the server authors the
  rows: an audit trail, a ledger, a job result. `offline_first` would have the
  client queue a write that is guaranteed to fail, and `online_only` would stop
  the person reading their own record offline.

## Relationships, always explicit

```
client:belongs_to[Client]
items:has_many[InvoiceItem]
tags:many_to_many[Tag]
```

Name the target, including for files. The bare `client:belongs_to` form exists
for history: it still parses, and it should not appear in new work. When you
see it in an existing project, that is worth saying, not silently copying.

**Generate in dependency order.** `Client`, then `Invoice`, then `Payment`. A
`belongs_to` pointing at a model that does not exist yet produces a project
that does not compile, and the fix is to generate the other one and run
`grit sync`.

## Conditional fields

A field that only applies sometimes is declared, not hidden in the frontend:

```
cycle:select[monthly, annually] if kind == recurring
```

This is the current syntax. It puts the condition in one place, where the Go
validation, the Zod schema and the admin form all read it, instead of three
places that disagree the first time somebody changes the rule. If you find
yourself writing a `useEffect` in an admin form to hide a field, stop: the
condition belongs in the declaration.

## The flags

Check `--help` for the live set. These are the ones that change the shape of
what you get, and the questions each one answers:

| Flag | Answers |
|---|---|
| `--fields` | The fields, inline |
| `--from` | The fields, from YAML. Use for workflows and anything long |
| `-i`, `--interactive` | Define them by being asked |
| `--owned-by <field>` | Whose row is it? Scopes every query to that user. ADMIN exempt |
| `--tenant-owned` | Rows belong to an organisation. Needs the multitenant plugin |
| `--roles "ADMIN,EDITOR"` | Who can reach the routes at all |
| `--public` | Also expose **read-only** list and detail under `/api/v1/public/`, behind an API key |
| `--seed` | A seeder with one example row |
| `--faker` | A seeder that fills many rows with gofakeit. Implies `--seed` |
| `--count N` | How many faker rows. Default 10 |
| `--tree` | Hierarchical: a self-referential parent, a materialised path, depth, sibling order, and the tree queries and move endpoint |
| `--items "Child:field:type,..."` | An inline has-many rendered as a line-items table in this resource's form |
| `--append-only` | Rows are created and read, never changed or deleted. For ledgers, audit trails, consent |
| `--audit-reads` | Record every read in the tamper-evident activity log. For health records |
| `--force` | Generate even when the name collides with a built-in |

Two notes worth having in advance:

- **`--public` is read-only.** It exposes list and detail and nothing else. A
  public endpoint that writes is hand-written, and it must not go on the
  URL-cached public group, or the first response gets served to everybody.
- **`--append-only` is enforced in three places**: no update or delete routes,
  a GORM guard, and a database trigger installed by `grit migrate`. It is a
  real constraint, not a convention, which is the point for a ledger.

## After generating

```bash
grit sync                                  # Go types to TypeScript
cd apps/api && go build ./... && go test ./...
grit migrate                               # create the table
grit doctor                                # did anything drift
```

`grit sync` is the step people forget. The generator writes the shared type
for the resource it just made; `sync` is what reconciles the whole set after
you have changed a Go struct by hand.

`grit migrate` runs from `apps/api`, which matters because a relative
`.env` path resolves differently from there than from the project root, and a
project with two SQLite files is the result.

## Adding a field later

```bash
grit docs search "add field"
```

Do not hand-edit the Go struct and stop there. A field has to reach the Zod
schema, the TypeScript type, the admin form and the admin table, and the
generator knows all those places. If you do edit the struct by hand, `grit
sync` is mandatory afterwards, not optional.

## Removing a resource

```bash
grit remove resource Invoice --force
cd apps/api && go build ./...
```

**Build afterwards, every time.** `grit remove` has historically reported
success while leaving a project that does not compile, and the pattern is
always the same: a file written from one name variant and deleted from
another, which is identical for a one-word resource and different for every
other. So:

- Test removal with a **two-word** resource. `grit remove Widget` passing
  tells you very little; `grit remove BlogPost` tells you the truth.
- If the build fails after a removal, that is a framework bug, not your
  problem to live with. Note exactly which file was left behind and file it:
  `grit-feedback` has the format. Then delete the file by hand and carry on.

## When the generator is wrong

You are closer to the generator than almost anyone, and you will find things.
A field type that emits Go that does not compile, a flag that does not do what
the docs say, an injection with no matching removal. All of those are worth
filing the moment you see them, with the exact command you ran. File first,
work around second, and put the issue number in the comment next to the
workaround.

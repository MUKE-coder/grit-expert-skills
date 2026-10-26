---
name: grit-data
description: >-
  GORM, migrations, indexes, seeders, queries and Postgres in a Grit project.
  Use for "the query is slow", "add an index", "write a migration", "seed some
  data", "this hook is not firing", "import a spreadsheet", or anything where
  the database is the thing being changed.
---

# grit-data

The database is the part of a project that is expensive to change after it has
rows in it. Your job is to get the shape, the indexes and the hooks right, and
to know the handful of GORM behaviours that silently do the opposite of what
the code appears to say.

## The GORM traps that cost a day each

These are not style points. Each one is a bug that looks like working code.

**A `BeforeUpdate` hook's `SetColumn` is discarded by `Save(struct)`.** Only
`Updates(map)` honours it. If a hook sets a computed column and the value
never appears, this is why. The fix is at the call site, not in the hook.

**`models` must never import `services`.** It is an import cycle and the
compiler will tell you, but the tempting fix is wrong: auto-numbering in a
`BeforeCreate` calls `sequence.Next` directly, never a service wrapper.

**`FindInBatches` gives the callback a `tx` with no query on it.** Read the
destination slice, not `tx`. Do not add a competing `ORDER BY`, and never drop
the error it returns, which is the one people drop because the signature makes
it easy.

**An initialism becomes a column name you would not predict.** GORM turns
`AllowIDPInitiated` into `allow_id_p_initiated`. If a column has an unusual
initialism, pin it with an explicit `column` tag and key any map update by the
real column name, or the update silently writes nothing.

**Column precision is not the same everywhere.** Postgres stores microseconds,
MySQL milliseconds. If you hash a row to make it tamper-evident, normalise the
value to what the column actually stores before hashing, or a chain verifies
on SQLite and fails in production. Verify hash chains on Postgres, not on the
SQLite you develop against.

## Migrations

```bash
grit migrate              # run pending
grit migrate --fresh      # drop and recreate. Development only
grit docs search "migrations"
```

`grit migrate` runs from `apps/api`. A relative `.env` path resolves
differently from the project root, and the symptom is a project with two
SQLite files and a mysterious absence of data.

`--fresh` drops the tables, so the API keys the seeder minted are gone while
the `.env.local` files still name them. Every public request then answers
`INVALID_API_KEY` with nothing connecting that to a file the seeder decided not
to overwrite. The seeder warns about this now; read its output.

For anything the generator cannot express, write the migration by hand and
keep it in the migrations directory. **Never edit a migration that has run
anywhere but your own machine.** Add a new one.

## Indexes

The generator gives you a primary key and the indexes implied by
relationships. It does not know your access patterns, and nobody notices a
missing index until there are rows.

Add one when:

- A column appears in a `WHERE` on a list endpoint. Every `--owned-by`
  resource filters by the owner column on every request, so that column wants
  an index from the start.
- A column is sorted on. The default list sort is usually `created_at`, which
  means a descending index on it.
- A unique business key exists: an invoice number, a slug, an email. Make it a
  unique index and let the database enforce it, rather than a service check
  that races.
- A foreign key is queried in both directions.

Composite order matters: the column you filter on exactly comes first, the
range or sort column second. An index on `(created_at, org_id)` does nothing
for `WHERE org_id = ? ORDER BY created_at DESC`; `(org_id, created_at)` does.

Check before guessing:

```sql
EXPLAIN ANALYZE SELECT ... ;
```

A sequential scan on a table with ten rows is correct and a sequential scan on
a table with a million is the answer.

## Seeders

A seeder is not test data, it is the state in which the product makes sense on
first run. A CRM with no pipeline stages cannot demonstrate a pipeline.

```bash
grit generate resource Contact --fields "..." --seed
grit generate resource Contact --fields "..." --faker --count 50
grit seed
```

Rules that matter:

- **Idempotent, by a business key.** Check for the row before creating it.
  Running the seeder twice must not produce two of everything.
- **Development-only data is gated.** Demo users with a weak shared password
  go behind the development check and log a line saying they were skipped
  otherwise. A seeder that creates `admin123` accounts in production is a
  breach waiting for a scanner to find it.
- **Never print a live credential outside development.** A log line outlives
  the terminal: it ships to an aggregator, is kept for ninety days, and is
  readable by everyone who can read logs.
- Seed in dependency order, and let the seeder create its own parents rather
  than assuming they exist.

## Queries that do not fall over

**The N+1 is the default failure.** A list endpoint that renders a related
name issues one query per row unless you preload. Pulse will show you exactly
which line did it; see `grit-perf`.

```go
db.Preload("Client").Find(&invoices)
```

Preload what the response actually serialises, and nothing else. A preload
nobody reads is a join nobody needed.

**Paginate everything.** A list endpoint with no limit is a denial of service
you wrote yourself. The scaffold's pagination helper already does the count
and the `meta` block.

**Select the columns you need** when a table has a wide text column. A list of
invoices does not need the notes field, and fetching it moves megabytes per
page.

**Scope in the query, not after it.** An `--owned-by` resource filters by
owner in SQL. Filtering in Go after fetching everything is both slow and a
data leak the moment somebody forgets the filter.

## Import and export

Grit ships CSV and XLSX import and export. Do not hand-build either.

```bash
grit docs search "import"
```

What to know when wiring one up: the import runs in batches with a concurrency
setting, it validates each row against the model's binding tags, and it
reports per-row failures rather than failing the whole file. A crafted
spreadsheet is an attack surface, which is why the XLSX reader is pinned past
its advisories; if you see a version warning from `grit doctor` about it, that
is not noise.

## Before you call it done

```bash
cd apps/api && go build ./... && go test ./...
grit migrate
grit doctor
```

And for anything involving hashes, time precision, or a unique constraint, run
it against **Postgres**, not the SQLite you develop on. The three bugs in this
file that reached production all passed on SQLite.

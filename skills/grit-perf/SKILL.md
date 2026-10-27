---
name: grit-perf
description: >-
  Make a Grit app fast, starting from a measurement: Pulse for profiling and
  N+1 detection, k6 for load, caching, pagination and query work. Use for "it
  is slow", "load test this", "find the N+1", "why is this endpoint slow",
  "add caching", "performance review".
---

# grit-perf

**Measure first.** Every time, without exception. A performance change made
without a measurement is a guess that makes the code harder to read, and about
half of them make it slower.

The usual outcome of measuring is that the task changes name: "the app is
slow" becomes "one list endpoint issues 400 queries", which is a twenty minute
fix rather than an architecture discussion.

```bash
grit docs search "pulse"
grit docs search "performance"
```

## Pulse is already mounted

It profiles requests, finds N+1 queries, tracks per-route baselines and
records flame graphs. Read it before changing anything.

What it gives you that guessing does not:

- **The N+1 table names the file and line that issued the query.** Not a count
  in an export, the actual line.
- **Per-route baselines**, which tell a route that got slower from a route
  that was always slow. Those are different problems and only one of them is
  a regression.
- **A flame graph of real CPU time** by default, rather than goroutine stacks
  where a parked connection counts on every tick and the hot code is a sliver.

Two configuration notes. Mount it with request-body capture disabled: Pulse
truncates every `Content-Length` body to 4096 bytes, which silently corrupts
uploads. And the floor version matters, because the useful features arrived
in specific releases and `grit doctor` reports a project left behind.

## The N+1, which is the default failure

A list endpoint that renders a related name issues one query per row. It is
invisible with ten rows and fatal with a thousand.

```go
db.Preload("Client").Find(&invoices)
```

Preload exactly what the response serialises. A preload nobody reads is a join
nobody needed, and over-preloading is the second most common cause of a slow
list endpoint after under-preloading.

## The index that is almost always missing

A list endpoint that is slow with no N+1 is usually sorting the whole table.
Every generated list is `WHERE <scope> ORDER BY <column>, id`, and until
somebody creates an index in that shape the database sorts on disk for every
page. Measured on 500,000 rows: 2.3 seconds for one page, 16.6 seconds at page
20,000.

```bash
grit index                 # what the lists need, as SQL
grit index --all-sortable  # when people really do sort by other columns
```

Confirm before and after with the plan rather than with a stopwatch:

```sql
EXPLAIN ANALYZE SELECT ... ORDER BY created_at, id LIMIT 25 OFFSET 0;
```

`Sort Method: external merge  Disk: ...kB` is the finding. An `Index Scan`
using the index you just made is the fix. If the plan still says sequential
scan after creating one, the index does not match the query and that is worth
reporting rather than adding another.

## The rest of the usual list

In rough order of how often they are the answer:

1. **No index on a filtered or sorted column.** Every `--owned-by` resource
   filters by owner on every request. Composite order matters: the exact-match
   column first, the sort or range column second.
2. **No pagination.** A list endpoint with no limit is a denial of service you
   wrote yourself.
3. **Selecting a wide column nobody renders.** A list of invoices does not
   need the notes field, and fetching it moves megabytes per page.
4. **Doing in Go what SQL should do.** Filtering, counting or aggregating
   after fetching everything. Also a data leak the moment one path forgets.
5. **A missing cache on something expensive and stable.** Not on something
   cheap, and not on something that changes per request.

## Caching

Redis is there. The questions that decide whether a cache helps or hurts:

**What invalidates it?** If you cannot say, you do not have a cache, you have
a bug with a delay. Write the invalidation at the same time as the cache.

**Is it per user?** A cache key that forgets the user serves one person's data
to another, and the URL-cached public group is exactly where this bites: a
writing public endpoint must never go on it.

**Is it actually expensive?** Caching a two millisecond query adds a network
round trip and a consistency problem to save nothing.

## Load testing

**k6 generates the load, Pulse explains it.** Out of process, on purpose: an
in-process generator competes with the thing it is measuring for CPU and
produces numbers that are about the generator.

```bash
grit docs search "load test"
grit generate perf              # check the live command with grit --help
```

One trap worth knowing in advance: **k6 shares one cookie jar per VU**, so a
call to Pulse after an application login fails CSRF, because the app's token
is in the jar. Give the Pulse call its own jar.

A registered run records a CPU profile of its own window, which is what makes
the result interpretable later rather than a number in a terminal somebody
has closed.

## Frontend performance

Different discipline, same rule: measure first.

- Animate `transform` and `opacity` only. Never `width`, `height`, `top`,
  `left`. Never `transition-all`.
- Pass motion values straight to `style`. Do not wrap one in an identity
  transform.
- Reserve space with `min-h-*` so a reveal does not shift layout.
- Lazy-load a heavy animated component with `dynamic(..., { ssr: false })`.
- Images through `next/image` with real dimensions and an accurate `sizes`.
- A list of a thousand rows needs virtualisation, not a faster render.

If `agent-browser` is installed, drive the real page and measure it rather
than reasoning about the bundle.

## Allocation budgets, if the project has them

Some Grit packages assert an allocation count. If one fails, check the Go
version before the code: counts move with the toolchain, and a budget written
against one release reads as a regression on another. Budget against the
version CI pins, and if the toolchain moved, say so rather than "optimising"
to a number that was never about your change.

## Before you say it is faster

- The **same measurement** you started with, after the change. A number before
  and a number after, or it did not happen
- `cd apps/api && go test ./...`, because a performance change that breaks
  behaviour is not a performance change
- Say what you did not measure. "The list endpoint went from 840ms to 60ms;
  I did not look at the dashboard queries" is a useful report. "It is faster
  now" is not

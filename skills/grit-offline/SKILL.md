---
name: grit-offline
description: >-
  Design and build the offline engine for a desktop or mobile app: the local
  mirror, the write outbox, sync and replay, conflict rules, and what must
  never be queued. Use for "make it work offline", "offline first", "field
  mode", "sync when the connection comes back", "the outbox", "it works but
  not on site".
---

# grit-offline

Offline is a data design, not a feature flag. By the time somebody says "and
it should work offline" the decisions that matter have usually already been
made, so your first job is to find out which of them have to be revisited.

Read `../grit-references/working-agreement.md` once. If the surface is a Wails
desktop app, `../grit-references/wails-auto-update.md` matters too, because an
update that replaces the binary must not take the write queue with it.

## The five questions, before any code

Get these answered and written into `.grit/project-profile.md`. Each one
changes the implementation, and guessing means rework rather than a smaller
version of the same thing.

1. **What is authoritative?** The server, in almost every case. The local
   store is a cache plus a queue. The moment both sides can authoritatively
   change the same row you have a distributed systems problem, and the product
   almost certainly did not need one.
2. **What can be created offline, and does it need a server-minted
   identifier?** This is the question that sinks projects. See below.
3. **What happens when two people edited the same row?** Last write wins is a
   decision, not an absence of one. It is right for a note and wrong for a
   stock count.
4. **What happens when a replay is rejected?** A queued write the server
   refuses needs a visible state and a human decision. Not a silent drop, not
   an infinite retry.
5. **How long may the app run offline before it must stop?** This decides the
   token policy and how much data to hold locally.

Ask them with the ask tool, with concrete options. "Last write wins, or merge
per field?" beats "how should conflicts work?".

## The identifier problem, which is the real one

Anything whose identity the server decides cannot simply be created offline.
In a Grit project that is usually an auto-numbered field: an invoice number, a
job number, a receipt sequence. They are generated inside a transaction with a
lock, which is exactly the thing you do not have on a laptop in a van.

Three options, and only two of them are real:

**Sequence leasing.** While online, the device leases a block from the server
(`INV-101` to `INV-150`) and records it locally. Offline it mints from its own
block. Blocks never overlap, so the number is final the moment it is shown.
Gaps appear where a lease is not used up, and gaps are fine. **This is the
right answer whenever the number is printed, spoken, or attached to a physical
object**, because a number that changes later is a thing nobody can find.

```
GET /api/v1/<resource>/lease?count=50   ->  { "from": 101, "to": 150 }
```

Implement the lease with the same lock the live numbering uses, plus a table
of issued ranges. Refuse to create offline when the lease is exhausted, and
say so on screen: refusing is annoying and a duplicate number is
unrecoverable.

**A client-minted UUID.** If the record's primary key is a UUID and any
human-facing number is cosmetic or assigned later, there is no problem at all.
Check the model before assuming you have one: in Grit a `uuid` primary key is
common and an auto-number alongside it is also common.

**Provisional numbers, renumbered on sync.** Do not. It is the obvious idea
and it breaks every artifact that already carries the number.

## Where the local store goes

**Desktop (Wails): SQLite in the Go layer**, with `modernc.org/sqlite`, the
pure-Go driver. Not the CGO one: Wails builds on Windows are painful enough
without requiring a C toolchain on every build machine.

Not IndexedDB in the renderer, for four reasons that bite in this order: the
webview's storage can be cleared by a runtime update or a profile reset and it
is not yours to rely on; the sync loop has to run before any window mounts and
keep running while minimised; reports are aggregation and that is SQL; and the
merge rules want to be one tested Go package rather than TypeScript inside a
webview.

Put the file in per-user application data, **outside the install directory**,
so an auto-update that replaces the binary cannot take the queue with it.

**Mobile (Expo): SQLite too**, and the queue must survive the process being
killed, which means storage and not memory. A phone loses the process, not
just the network.

## The three pieces

### The mirror, for reads

Do not try to normalise the whole domain into local tables. It takes a month
and then drifts from the Go models every time somebody runs
`grit generate`. Store the server's JSON per row with a few extracted columns
to filter and sort on:

```sql
CREATE TABLE mirror (
  resource   TEXT NOT NULL,
  id         TEXT NOT NULL,
  body       TEXT NOT NULL,     -- the server's JSON
  owner_id   TEXT,              -- whatever the app scopes by
  status     TEXT,
  updated_at TEXT NOT NULL,
  deleted    INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (resource, id)
);
```

Reads always come from here, online or not. That is what makes offline a
non-event rather than a mode the user switches into, and it is why the app
feels fast.

### The outbox, for writes

```sql
CREATE TABLE outbox (
  id           TEXT PRIMARY KEY,   -- UUID, and the idempotency key
  created_at   TEXT NOT NULL,
  occurred_at  TEXT NOT NULL,      -- when the human acted. See side effects
  method       TEXT NOT NULL,
  url          TEXT NOT NULL,
  body         TEXT NOT NULL,
  entity       TEXT NOT NULL,
  entity_id    TEXT NOT NULL,      -- for ordering
  depends_on   TEXT,
  attempts     INTEGER NOT NULL DEFAULT 0,
  state        TEXT NOT NULL,      -- queued | sending | done | failed
  error_code   TEXT,
  error_message TEXT
);
```

Four rules:

- **Append only.** A queued write records what somebody did. If they then do
  something else, that is another row, not an edit of this one.
- **Ordered per entity, parallel across entities.** Two status changes to one
  record must replay in the order they were made, or the second is rejected by
  a workflow and the queue jams.
- **Apply locally in the same transaction** that inserts the outbox row, so a
  crash cannot leave the screen and the queue disagreeing.
- **A 4xx stops the retry.** A 422 will be a 422 forever. Mark it `failed` and
  put it in front of a human. Only 5xx and transport errors back off and retry.

### The sync engine

Detect, drain, pull.

**Detect.** Never `navigator.onLine`: in a webview it reports the adapter, and
a captive portal or a dead VPN looks online. Probe the API's own health
endpoint with a short timeout, every 15 seconds while offline and every 60
while online, and immediately after any transport failure. If the project has
a realtime WebSocket, its connected state is a stronger and faster signal, but
keep the probe as the fallback: the socket can be down while the API is fine.

**Drain.** Oldest first, respecting per-entity order. Back off 5s, 15s, 60s,
5m, 15m.

**Pull.** `GET /sync?since=<rfc3339>&resources=...`, returning everything
changed since, **including soft-deleted rows** so the mirror can remove them.
Two things to get right: return the **server's** clock and store that as the
next `since`, or a device whose clock is fast will permanently skip a window
of changes; and scope the pull to what this device should see.

## Idempotency comes before the outbox

A queued write that times out after the server committed it will be retried,
and without idempotency that is a second payment, a second order, a second
charge. Build this **before** the queue, not after, because the bug it
prevents is the one that costs money and the one nobody notices for a week.

Where the record has a client-minted UUID primary key, that is the key: on
create, if the row exists, return it with 200. Where it does not, add an
`Idempotency-Key` header, store key, endpoint, status and response body, and
replay the stored response on a repeat.

**The test that matters: send the same request twice, assert one row.**

## Side effects are the part people miss

In a Grit project, writes have consequences on the server: a status change
sends an SMS, a payment sends a receipt, a job fires. When a write is replayed
three hours late, those consequences fire three hours late.

Think about each one rather than applying a rule:

- A confirmation of something that happened: fine late. Send it.
- A notification about a state the record has **since left**: actively wrong.
  If a later state for the same record is in the same replay batch, suppress
  the earlier one's message.
- A time-sensitive prompt ("your order is ready") older than a threshold:
  skip it and record that it was skipped, rather than telling somebody to come
  and collect what they collected this morning.
- A money record: never suppress. A late receipt is still correct.

This is why `occurred_at` is in the outbox schema. Make the threshold a
setting; the owner will have an opinion after the first week.

## What must never be queued

Anything whose entire purpose is to reach a third party **now**: sending a
message, a broadcast, an OTP, a payment authorisation against a gateway.

Queue those and you get the worst outcome: the operator assumes it went,
sends it again from their phone, and the customer gets it twice hours later.
Disable them with a visible reason instead.

The test for which bucket a write is in: **would the person want to know it
has not happened yet?** A payment recorded at a counter is a fact about the
past and queues fine. A message is an action in the present and does not.

## Keep the screens

If the frontend already fetches through one client, intercept **there** rather
than rewriting every screen. For an axios app, swap the adapter: reads go to
the local store, writes go to the outbox, and every component, hook and query
key keeps working. Return the API's exact envelope (`{data, meta}` and
`{error: {code, message}}`) or the error-message helper starts showing
"Something went wrong" instead of the real reason.

This is usually the difference between a two-week project and a rewrite.

## What the user sees

Four things, no more. A sync UI that needs explaining has failed.

1. A connection indicator, driven by an event rather than polling.
2. A pending count when the queue is not empty.
3. A per-row mark on anything not yet synced, so the state is visible where
   the work is.
4. **A sync screen**, the one everybody forgets and the one support lives in:
   each queued item in plain language, and for failed ones the server's real
   error with retry and discard. A failed row must never vanish on its own. It
   is somebody's work.

## Before you say it works

Testing this by using it normally proves nothing. The failures are all in the
seams:

- Turn the network off, do real work, turn it on, watch the queue drain
- Then do it with a write the **server will reject**, and check a human can
  see and resolve it
- Kill the app mid-drain and restart
- Queue several hundred writes
- Move the system clock forward and back
- Two devices, same record, both offline, both reconnecting
- On desktop: run an **auto-update with a non-empty queue** and confirm the
  queue survives
- On mobile: kill the process from the task switcher with the queue full

If the framework fought you anywhere in this (no lease endpoint, no
idempotency, no delta endpoint, a side effect you could not suppress), that is
a Grit gap and worth filing. `grit-feedback` has the format.

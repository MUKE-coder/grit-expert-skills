---
name: grit-desktop
description: >-
  The Wails desktop app: offline-first with a local SQLite mirror and a sync
  outbox, Go bindings to React, packaging, and shipping updates through GitHub
  Releases. Use for "add a desktop app", "make it work offline", "the desktop
  build", "auto-update", "the installer".
---

# grit-desktop

A Wails app: Go compiled into a native binary with a React frontend, sharing
the monorepo's API and types. The reason to build one is almost always
**offline**, and offline is the hard part, not the packaging.

```bash
grit docs search "desktop"
grit new-desktop <name>        # check the live command with grit --help
ls apps/desktop
```

## Offline is a data design, not a feature flag

A desktop app that works offline has a local SQLite mirror and a **sync
outbox**: every local write is also appended as an intent to be replayed
against the API when there is a connection. That is the whole architecture,
and the decisions in it are the ones worth getting right before writing code.

**What is authoritative?** The server, in almost every case. The mirror is a
cache plus a queue, not a second source of truth. The moment both sides can
change the same row authoritatively, you have a distributed systems problem
and the product probably did not need one.

**What happens when two people edited the same row?** Decide the rule and
write it in the project profile. Last write wins is a decision, not an
absence of one, and it is fine for a sales note and wrong for a stock count.
A field-level merge is more work and sometimes the only honest answer.

**What can be created offline?** A record with a server-generated identifier
cannot be referenced by another offline record unless you mint a local id and
reconcile it on sync. If a rep can create a contact and then log a visit
against it on the same flight, the outbox has to carry that dependency and
replay in order.

**What happens when a replay fails?** This is the one people skip. A queued
write that the server rejects needs a visible state and a human decision, not
a silent drop and not an infinite retry. Build the screen that shows the
stuck items before you ship, because it is the screen support will live in.

## Go to React

Bind the Go methods you want callable and Wails generates the TypeScript:

```go
Bind: []interface{}{ app, updater },
```

The frontend calls them as `window.go.main.<Type>.<Method>`. Two practical
notes: the generated `wailsjs/go/main/*.d.ts` files **only appear after a
`wails build`**, so a missing binding type is usually a missing build rather
than a mistake; and anything long-running needs to report progress through a
polled getter rather than a promise that resolves in four minutes.

## Auto-update

Read `../grit-references/wails-auto-update.md` before building this. It is the whole
mechanism, and the short version is:

- The client polls your own API, not GitHub, because the PAT must never ship
  in a binary and the shared rate limit matters.
- The server proxies GitHub Releases, caches for ten minutes, and redirects to
  a presigned asset URL.
- Windows swaps the binary by **renaming** the running exe to `.old` and
  copying the new one in, because a running exe can be renamed and not
  overwritten. Copy, not rename, for the new file: `%TEMP%` and
  `%LOCALAPPDATA%` can be on different volumes.
- The installer is **per-user** under `%LOCALAPPDATA%`. Installing under
  `%PROGRAMFILES%` and auto-updating are incompatible.

Four things the reference says are missing from the usual implementation, and
each is worth adding before real users: verify a SHA256 of the download before
swapping, do not return the releases page as a download URL on the fallback
path, restore the `.old` binary if the new one fails its first run, and
enforce a minimum supported version server-side.

## Packaging

```bash
cd apps/desktop
wails build                                  # the raw binary
wails build -nsis -platform windows/amd64    # plus the installer
```

Version lives in `apps/desktop/wails.json` as `info.productVersion`, and the
frontend reads it through a Vite `define` so there is **one** version number.
Two numbers is the bug where the app reports 1.2.0 and the updater thinks it
is 1.1.0.

Windows specifics that waste an afternoon each: use backslashes in NSIS `File`
and `-D` paths, because forward slashes fail silently inside a conditional
macro; drop the `Global\` prefix from the single-instance mutex, which needs
admin on a per-user install; and check for `ERROR_ALREADY_EXISTS` specifically
rather than treating any error as "already running".

Ship the installer that **bundles** WebView2 for field installs. The slim one
downloads about 125 MB during install, which on a slow link is
indistinguishable from a hang.

## Sharing code with the monorepo

The desktop app consumes the same API and the same shared types. It is not a
place for a second set of models. If the desktop needs a shape the API does
not expose, that is an API change, not a local type, because the next surface
will need it too.

## Before you say it works

- `wails build` completes, and the binary runs on a machine that is not yours
- Offline: turn the network off, do real work, turn it on, and watch the
  outbox drain. Then do it with a write the server will reject
- The update path end to end: install an older version, publish a newer one,
  and let the app find it. A tested updater is the difference between shipping
  once and shipping continuously
- `grit doctor`

Note that a fully signed release needs an Authenticode certificate for Windows
and an Apple Developer certificate for macOS. Without them the binary still
works and SmartScreen will warn, and `.exe.old` cleanup is less reliable
because Defender holds unsigned files longer.

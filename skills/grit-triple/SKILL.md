---
name: grit-triple
description: >-
  The triple architecture: the Go API, a customer-facing Next.js web app, and a
  separate Next.js admin, in one pnpm monorepo with a shared package. Use when
  grit.json says triple, for "scaffold a triple project", "wire this resource
  into web and admin", or any monorepo or shared-package problem.
---

# grit-triple

Three apps, one API, one set of types. `apps/api`, `apps/web`, `apps/admin`,
with `packages/shared` holding the Zod schemas, the TypeScript types and the
route constants that all three agree on.

Confirm you are in one before doing anything:

```bash
cat grit.json          # architecture should say triple
ls apps/               # api, web, admin
```

## Scaffolding

```bash
grit new <name> --triple --next
cd <name>
pnpm install
docker compose up -d           # Postgres, Redis, MinIO, Mailhog
grit migrate
grit seed
grit start
```

Then read what the seeder printed. It mints an admin user, a publishable API
key and a secret one, and writes `.env.local` into each frontend with the
publishable key and the API URL. If you skip that output you will spend twenty
minutes on an `INVALID_API_KEY` that was answered on screen.

## The monorepo traps

These are the ones that cost a whole afternoon, and none of them says what is
actually wrong.

**`node-linker` in `.npmrc` is ignored when a `pnpm-workspace.yaml` exists.**
Without `hoisted`, Next cannot resolve `@swc/helpers` and every page throws
`_interop_require_wildcard`. The setting belongs in `pnpm-workspace.yaml`.

**Next is pinned exactly, on purpose.** A caret once adopted a one-day-old
release whose layout router threw `reading 'slots'` on every page. If you are
raising Next, raise the pin deliberately and build both frontends before
committing.

**pnpm itself is pinned.** Projects pin 10.33.4, because 10.34 and later
cannot install the SheetJS CDN tarball that the spreadsheet import needs. Only
move to 11.9 or later.

**If `apps/expo` exists, React is pinned to Expo's version** across every web
frontend. Two Reacts in a hoisted `node_modules` breaks every component test
with errors that point at the component, not at the duplication.

## Wiring a resource through all three

`grit generate resource` does most of this. Your job is what it cannot know.

1. **The API**: generated. Build it: `cd apps/api && go build ./...`.
2. **The shared package**: generated, then `grit sync` to reconcile everything
   else. The frontends import from `@repo/shared`, never from a relative path
   into another app.
3. **The admin**: generated, including the resource definition and a page. See
   `grit-admin` for the screens worth having beyond the default.
4. **The web app**: this is the one with real work in it, because what a
   customer sees is a product decision and not a CRUD table. Hand it to
   `grit-ui-ux` with the hooks and types already in place.

Run the whole thing after:

```bash
pnpm build          # turbo builds all three
grit doctor
```

## apps/web is not apps/admin

They have **different palettes**, and a Tailwind utility that does not exist
renders nothing and reports nothing. The web app has `bg-bg-secondary`,
`text-text-secondary`, `text-accent`. The admin has `muted`, `card`,
`primary`. Copying a component from one to the other produces an invisible
element and a confusing half hour.

They also have different jobs. The admin is a dense operator console and it
already has a design system, so leave it alone unless you are adding to it.
The web app is the product, and it should look like the product rather than
like an admin panel with the sidebar removed.

## The shared package is the contract

Anything both a frontend and the API need lives in `packages/shared`:

- Zod schemas, generated from the Go structs by `grit sync`
- TypeScript types
- Route constants

A second hand-written schema in a frontend is how validation drifts: the API
starts rejecting something the form accepted, and the error surfaces as a 422
nobody can explain. If a frontend needs a shape the API does not have, that is
a signal about the API, not a reason for a local type.

After any change to a Go struct, `grit sync`. It is not optional and it is the
step people forget.

## Auth, and the six places it lives

A change to sign-in or sign-up is **six edits across six files**, because
there are six auth styles. Changing one and testing it proves nothing about
the other five. Check which style this project uses before editing, and if you
are changing shared behaviour, change all six.

The shared `RegisterSchema` is camelCase. The API binding tags decide what the
API accepts, and a mismatch between them shows up as a validation error on a
field the user filled in correctly.

## Running it

```bash
grit start                    # everything
cd apps/api && air            # API with hot reload
cd apps/web && pnpm dev
cd apps/admin && pnpm dev
```

If a change does not appear, **the dev server is the first suspect.** A `next
dev` process that has been running since before your edit will serve the old
bundle and let you believe the code is wrong. Kill it by port, remove `.next`,
start it again. This has produced more than one confident wrong conclusion.

## Before you say it works

- `cd apps/api && go build ./... && go test ./...`
- `pnpm build` at the root, which builds all three
- **Open the app and look at it.** For a UI change, a screenshot is the
  evidence. A synthetic check against the DOM, or a grep for a class name,
  will happily confirm something that is visibly broken.
- `grit doctor`

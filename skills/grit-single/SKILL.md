---
name: grit-single
description: >-
  The single architecture: one app that is both the frontend and the project
  root, with the Go API beside it and the admin as a section. Use when
  grit.json says single, for "scaffold a single project", "where is the shared
  package here", or Vite and TanStack questions in a Grit project.
---

# grit-single

One app. The frontend owns the project root, the Go API sits beside it in
`api/`, and the admin is a section of the same app. The leanest shape Grit
produces, and the one with the most layout differences from the others.

```bash
cat grit.json
ls                     # the frontend's own files are at the root
```

## What is different, and it is mostly paths

**There is no `packages/`.** A single project has no workspace to resolve
`@repo/shared` through, so the shared package is **mirrored into the app's own
source tree** and reached through the same specifier. The mirror location
depends on when the project was made:

- `src/shared` now that the app owns the root
- `frontend/src/shared` in a project scaffolded before that

Code that assumes `packages/shared` writes the generated type to a directory
that does not exist, and then the resource's own page fails to compile on a
type the generator said it had written. If you are writing anything that
resolves the shared root, handle all three locations.

**The Go module is in `api/`, not `apps/api/`.** Commands that assume the
monorepo layout silently do nothing useful. `grit migrate` and the seeder run
from the Go module's directory.

**The seeder writes `.env.local` to the root or to `frontend/`.** It checks
for a `package.json` to decide whether a directory is actually a frontend,
because `../` is the project root in a single and the `apps/` folder in a
monorepo, and only one of those is somewhere an env file belongs.

## Scaffolding

```bash
grit new <name> --single --vite      # or --next
cd <name>
pnpm install
docker compose up -d
grit migrate && grit seed
grit start
```

## Vite and TanStack

A single project is often Vite with TanStack Router and TanStack Query rather
than Next. Two consequences:

**Environment variables are `VITE_` prefixed**, not `NEXT_PUBLIC_`. Each
bundler exposes only its own, so the seeder detects which one by looking for a
`vite.config.ts`, and a file written with the wrong prefix is read by nothing
and explains nothing. If an API key appears to be missing, check the prefix
before checking the key.

**There is no server component boundary**, so the data-fetching rules are
simpler and the discipline has to come from you: all fetching through TanStack
Query hooks, no `fetch` in a component, loaders for route-level data.

## The admin is a section

Not an app, not a route group, a section of the same app. It shares the build,
the session and the deployment, and it carries the admin design tokens while
the rest of the app carries the product's.

`grit docs search "embedded admin"` for the predicate that detects it, which
differs from the double project's route group. Reading the wrong predicate
sends you looking for a directory that does not exist in this shape.

Because there is one app and one session, **authorisation is the only
boundary** between a customer and an operator. The role gate goes at the
section level so a new page inherits it.

## Wiring a resource

```bash
grit generate resource Contact --fields "..."
grit sync
cd api && go build ./...
pnpm build
```

Then check the generated page actually landed in the app's tree rather than in
a `packages/shared` that does not exist. If a generated type is missing,
that is the mirror-location bug and it is worth filing: `grit-feedback`.

## When single stops being right

Be honest about this rather than loyal to the choice. A single project wants
to become double or triple when:

- The operator screens outgrow a section and start needing their own
  navigation
- The admin needs to be at a different domain or behind different network
  rules
- Two different teams own the two halves

Moving later is real work. If the project profile says mobile and desktop are
coming, say now that a single is the shape with the least room, because every
surface will consume the same API and a single gives you one frontend to grow
into.

## Before you say it works

- `cd api && go build ./... && go test ./...`
- `pnpm build`
- Open the product and the admin section, as each role
- `grit doctor`

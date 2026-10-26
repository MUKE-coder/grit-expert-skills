---
name: grit-double
description: >-
  The double architecture: the Go API plus one frontend, with the admin as a
  route group inside it. Use when grit.json says double, for "scaffold a double
  project", "where does the admin live here", or when deciding between double
  and triple.
---

# grit-double

Two apps: `apps/api` and one frontend. The admin is not a separate app, it is
a route group inside the frontend, which is the whole point of choosing this
over triple.

```bash
cat grit.json          # architecture should say double
ls apps/
```

## When double is the right call

Pick it when the same people use the product and administer it, or when the
admin is a handful of screens rather than a console. A five-person agency
tracking its own clients does not need a separate admin deployment, and a
separate one costs a build, a deploy target, a session story and a second
set of environment variables.

Pick triple instead when the admin audience is genuinely different from the
customer audience, when the admin needs to be reachable at a different domain
or behind different network rules, or when you expect the operator console to
grow into real software.

The migration from double to triple later is real work, so this is a question
to ask rather than assume. It is in the project profile for that reason.

## Scaffolding

```bash
grit new <name> --double --next     # or --tanstack for a Vite frontend
cd <name>
pnpm install
docker compose up -d
grit migrate && grit seed
grit start
```

## The admin is a route group

It lives inside the frontend's app directory as its own group with its own
layout, which means:

- **It shares the frontend's build and deployment.** One `pnpm build`, one
  deploy, one set of environment variables.
- **It shares the session.** A signed-in customer and a signed-in operator are
  the same session with different roles, so authorisation is doing all of the
  work. Get the policies right, because there is no network boundary helping
  you.
- **It does not share the palette.** The admin group carries the admin design
  tokens; the customer routes carry the product's. Check which side of the
  boundary a component is on before copying it, because a utility from the
  wrong palette renders nothing and says nothing.

`grit docs search "embedded admin"` for how the panel is detected and
rendered, because the predicate differs between the three shapes and reading
the wrong one sends you looking for an app directory that does not exist.

## Route protection matters more here

In a triple project the admin is a separate origin, and a mistake there is
embarrassing. In a double project the admin routes sit in the same app as the
customer routes, so a missing role check is a customer reaching an operator
screen.

Two things to verify rather than assume:

1. Every admin route group has the role gate at the layout level, not per
   page. A new page added to the group inherits it; a per-page check is one
   somebody will forget.
2. The API routes behind those screens have their own gate. The frontend
   hiding a button is not authorisation. `grit routes` prints the table, and
   `grit-security` reads it properly.

## Wiring a resource

```bash
grit generate resource Contact --fields "..."
grit sync
cd apps/api && go build ./...
pnpm build
```

The generator writes both the customer-facing hooks and the admin page into
the one frontend. What it cannot know is which of the two a given resource is
for: plenty of resources are operator-only, and generating a customer page for
them adds a route nobody should reach. Delete what you do not want, and record
in the project profile that it was deliberate.

## The shared package

A double project still has `packages/shared` when it is a monorepo. Types and
Zod schemas go there and are imported through `@repo/shared`, not by a
relative path into the API directory.

After any change to a Go struct, `grit sync`.

## Before you say it works

- `cd apps/api && go build ./... && go test ./...`
- `pnpm build`
- Open **both** sides: a customer route and an admin route, signed in as each
  role. The interesting bug in a double project is always a role seeing
  something it should not.
- `grit doctor`

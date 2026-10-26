# Grit invariants

The parts that do not move between releases. Everything else gets looked up
with `grit docs search`, because Grit ships several releases a week and the
flag you remember may not exist in the binary this project has.

## The stack, and it is not a suggestion

| Layer | Technology | Not |
|---|---|---|
| Backend | Go + Gin | Echo, Fiber, Chi |
| ORM | GORM | sqlx, sqlc, ent |
| Database | PostgreSQL in production, SQLite for quick start and tests | |
| Frontend | Next.js App Router, or TanStack for a Vite single | Pages Router, ever |
| Styling | Tailwind + hand-written components on design tokens | Material UI, Chakra, Bootstrap |
| UI primitives | Base UI, and only when a primitive needs real behaviour | Radix |
| Data fetching | TanStack Query | SWR, Apollo, raw fetch in a component |
| Validation | Zod, shared, generated from the Go types | a second hand-written schema |
| Monorepo | Turborepo + pnpm | npm, yarn |
| Cache and queue | Redis, with asynq for jobs | |
| Storage | S3-compatible: S3, R2, MinIO, or local disk | |
| Email | Resend | |
| Desktop | Wails | Electron, Tauri |
| Mobile | Expo / React Native | |

Adding a dependency outside this list needs a reason that survives being said
out loud. "It was easier" is not one.

## Architecture, not tier

The five architectures are `single`, `double`, `triple`, `api` and `mobile`.
That is the name of the flag and of the field. In code, always the value's own
name. In prose, "a triple project" or "triple-tier" when the reader is
counting apps. Never a bare "tier", which does not say which of the five.

- **api**: the Go API alone
- **single**: one app, one frontend, the admin embedded as a section
- **double**: the API plus one frontend
- **triple**: the API plus web plus a separate admin app
- **mobile**: Expo against the API

`grit.json` in the project root records which one. Read it rather than
guessing from the directory listing.

## Folder structure

```
project-root/
  grit.json                  the project's own record: architecture, version
  .grit/manifest.json        what Grit wrote, and its hashes
  docker-compose.yml
  packages/shared/           Zod schemas, TS types, constants
  apps/
    api/                     Go
      cmd/server/            entry point
      internal/
        models/              GORM structs
        services/            business logic
        handlers/            thin HTTP
        middleware/
        routes/
        policies/            per-resource authorization
        database/            migrations, seeders
        access/              the generated route table
    web/                     Next.js
    admin/                   Next.js admin
    expo/                    mobile
    desktop/                 Wails
```

A single project has no `packages/`: the shared package is mirrored into the
app's own source tree and reached through the same `@repo/shared` specifier.

## Naming

| Thing | Convention | Example |
|---|---|---|
| Go files | snake_case | `user_handler.go` |
| Go exported | PascalCase | `GetUsers` |
| Go unexported | camelCase | `parseToken` |
| TypeScript files | kebab-case | `use-users.ts` |
| React components | PascalCase file and symbol | `DataTable.tsx` |
| API routes | plural, lowercase | `/api/v1/users` |
| Tables | plural, snake_case | `blog_posts` |
| Zod schemas | PascalCase + Schema | `CreatePostSchema` |

A name variant is load-bearing. `BlogPost` is `blog_post` as a file,
`blog-post` as a TypeScript file, `blogPost` as a handler variable,
`blog_posts` as a table and `blogPosts` in a route constant. Build each from
the right variant; they are the same string only for a one-word name, which is
how a whole class of bug hides.

## The API contract

Success, one item:

```json
{ "data": { }, "message": "User created successfully" }
```

Success, a list:

```json
{ "data": [], "meta": { "total": 100, "page": 1, "page_size": 20, "pages": 5 } }
```

Error:

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "Email is required",
             "details": { "email": "This field is required" } } }
```

Status codes: 200, 201, 400, 401, 403, 404, 422, 500. A validation failure is
422, not 400. Use the response helpers the scaffold provides rather than
writing `c.JSON` by hand, or the envelope drifts one handler at a time.

## Code rules that are not style preferences

**Go**

- Every error is handled. Never `_` on an error.
- Wrap with context: `fmt.Errorf("creating user: %w", err)`.
- Handlers stay thin. They bind, call a service, and write a response.
  Business logic in a handler cannot be reused by a job, a CLI command or
  another handler, and that is always what happens next.
- `models` must never import `services`. It is an import cycle. Auto-numbering
  in `BeforeCreate` calls `sequence.Next` directly.
- A `BeforeUpdate` hook's `SetColumn` is overwritten by `Save(struct)`. Only
  `Updates(map)` honours it.
- Struct tags carry the contract: `gorm`, `json`, `binding`.

**TypeScript and React**

- Functional components only.
- All data fetching through TanStack Query hooks. No `fetch` in a component.
- Validate every API input with Zod, from the shared package.
- No `any`.
- `interface` for object shapes, `type` for unions.

## Generated code has two halves

`grit generate` writes files **and** injects into shared ones at markers such
as `// grit:models`, `// grit:routes:protected`, `// grit:seeders`. Every
injection has a matching removal in `grit remove`.

If you add a generator, add its removal in the same change. If you hand-edit
inside a marked region, `grit upgrade` may rewrite it. Check
`.grit/manifest.json` and `grit doctor` before assuming a file is yours.

## The admin design system

Dark by default. These are CSS variables, not literals to paste:

```
--bg-primary #0a0a0f   --bg-secondary #111118   --bg-tertiary #1a1a24
--bg-elevated #22222e  --bg-hover #2a2a38       --border #2a2a3a
--text-primary #e8e8f0 --text-secondary #9090a8 --text-muted #7c7c96
--accent #6c5ce7       --accent-hover #7c6cf7   --accent-fg #ffffff
--success #00b894      --danger #ff6b6b         --warning #fdcb6e
--info #74b9ff
```

Fonts: Onest for UI, JetBrains Mono for code. Feel: Linear, Vercel dashboard,
Raycast. Premium dark SaaS, not Bootstrap and not Material.

`apps/web` is a different palette from the admin: it has
`bg-bg-secondary`, `text-text-secondary`, `text-accent`, not the admin's
`muted` / `card` / `primary`. A utility that does not exist renders nothing
and says nothing, so check which app you are in.

**Style and theme are different things.** A style (`modern`, `glass`) decides
which dashboard source file gets written. A theme (`aurora`, `emerald`)
decides the CSS variables and can be switched at runtime with `THEME=`.

## Base UI, and only for behaviour

Everything in the admin's `components/ui/` is hand-written against the tokens,
and the dependency count is better for it. That stays true for anything that
is a styled element.

It stops being true when a component needs behaviour rather than appearance: a
focus trap, roving focus, listbox semantics, portalled positioning that
survives a scroll container. Those fail silently for keyboard and screen
reader users. **For a new primitive that needs real interaction behaviour, use
`@base-ui-components/react`.** Two rules: new primitives only, never rewrite
a working one; and add the dependency in the same change that uses it.

## Things that are always wrong

1. Pages Router.
2. A custom CSS file instead of utilities and tokens.
3. Business logic in a handler.
4. A hardcoded value that belongs in `.env` and a config struct.
5. `any` in TypeScript.
6. Hand-building something Grit already ships.
7. Deviating from the folder structure, which is the whole convention.
8. A light, generic-looking admin. The dark premium feel is a product
   decision, not a default.

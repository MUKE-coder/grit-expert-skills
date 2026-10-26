---
name: grit-deploy
description: >-
  Get a Grit project onto a server and keep it there: Docker Compose, Dokploy
  on a VPS, environment variables, storage, migrations on deploy, CI, and the
  desktop release. Use for "deploy this", "set up the VPS", "dokploy",
  "production env vars", "the build fails in CI", "ship a release".
---

# grit-deploy

A Grit project deploys as containers: the Go API, the frontends, Postgres,
Redis, and object storage. Dokploy on a VPS is the usual target, because it
gives you the deploy pipeline without the cloud bill.

```bash
grit docs search "deployment"
grit docs search "dokploy"
cat docker-compose.prod.yml
```

## Environment, which is where deploys fail

Almost every failed first deploy is an environment variable, and the two that
cause the most confusion:

**`APP_PORT` and `APP_URL` move together.** Changing the port without changing
the URL produces an app that serves on one address and tells every client
another, and the symptom appears in a frontend as a CORS error or a dead
upload rather than as a port problem.

**Storage has a driver and the fallback matters.** `STORAGE_DRIVER=local`
writes to disk, which is correct for a single-server deploy and needs a
mounted volume or an upload is lost on the next container restart. For S3, R2
or MinIO, the public URL is browser-facing and ends up in the
Content-Security-Policy: a wrong one is an upload the browser refuses, and the
only trace is a console message nobody is watching.

Walk `.env.example` line by line against production rather than copying a
development `.env`. The things that must differ:

- `APP_ENV=production`, which gates every development-only behaviour: demo
  seed data, printed credentials, verbose errors
- Secrets regenerated, not reused from development
- `SCOUT_PASSWORD` if Scout is mounted, or it refuses to mount
- Database and Redis pointing at the real services
- Mail credentials, or mail silently goes nowhere

## Migrations on deploy

Run them as an explicit step, not from the application on boot. An app that
migrates at startup will do it from every replica at once.

```bash
grit migrate
```

It runs from the Go module's directory. A relative `.env` path resolves
differently from elsewhere, and the result is a container that connects to a
database that is not the one you think.

Never `--fresh` against anything with real rows in it. It drops the tables,
and it also invalidates the API keys the seeder minted while the frontends'
env files still name them, so every public request answers
`INVALID_API_KEY` for a reason nobody connects to the migration.

## Dokploy on a VPS

The shape: Dokploy owns the reverse proxy and TLS, each app is a service built
from the repo, and the databases are either Dokploy-managed or containers in
the same compose file.

Decisions worth making deliberately:

- **One VPS or two?** The database on the same box is cheaper and simpler and
  loses everything together. For anything with customers in it, a managed
  database or a separate box with its own backups.
- **Backups, before launch.** A backup that has never been restored is not a
  backup. Restore it once, onto a scratch database, and time how long it took.
- **Where storage lives.** Local disk means the volume is part of the backup
  story. Object storage means it is not, which is usually the better answer.
- **How a deploy rolls back.** Know the answer before you need it.

## CI

Keep the gates that catch the failures nobody notices locally:

```bash
go build ./... && go test ./...
go vet ./...
govulncheck ./...
pnpm build
grit doctor
```

Two lessons that cost real time:

**Pin your linters and scanners.** A tool installed with `@latest` changes
under the build, and then a docs-only commit goes red for a reason that is not
in the diff. Bump deliberately.

**Never truncate a test log.** Keep the whole output and grep it on failure.
A tailed log loses the one line that said which test failed.

If a tool reports something impossible, suspect the tool before the code. A
scanner reporting `undefined: X` on code that `go build` and `go vet` both
accept is the scanner's package loader, not your repository.

## Shipping the desktop app

`references/wails-auto-update.md` in full if the project has a desktop target.
The release is a tag, built assets and a GitHub release, and the client finds
it through your own API rather than GitHub directly, because the PAT must never
ship in a binary.

Two things to get right the first time: tags are `vX.Y.Z` consistently, never
mixed with bare `X.Y.Z`; and the raw binary and the installer are separate
assets, with the updater picking the one whose name contains neither `setup`
nor `installer`.

If `gh release create` fails after the tag pushed, you have an orphan tag.
`git push origin :vX.Y.Z` and rerun.

## Mobile releases

They are store submissions, not deploys, and they are a different discipline
with a review queue in it. `grit-mobile` owns that, and
`references/store-rejections.md` is the checklist. Do not treat a store
submission as the last five minutes of a deploy: the review can take weeks if
a restricted permission is involved.

## Before you say it is deployed

- The app answers on its real URL, over TLS, from a machine that is not yours
- Sign in works, which proves the database, the session store and the secrets
- An upload works and the file comes back, which proves storage and the CSP
- Mail arrives, which is the one everybody discovers is broken a week later
- `grit doctor` against the deployed configuration
- A restore from backup has been done once
- Say what is not covered: monitoring, alerting, on-call, log retention. A
  deploy that nobody is watching is not finished, and naming that is more
  useful than implying it is handled

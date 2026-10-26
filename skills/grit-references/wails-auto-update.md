# Desktop auto-update, Wails plus GitHub Releases

Distilled from https://jb.desishub.com/blog/wails-desktop-auto-updater-github-releases

Windows-first. A desktop app that cannot update itself is a support burden,
and the Windows trick that makes it possible is that a running `.exe` can be
**renamed** but not overwritten.

## The shape

| Layer | Piece | Job |
|---|---|---|
| Release | `scripts/release-desktop.sh` | Bump, build, package, tag, publish |
| Truth | `apps/desktop/wails.json` | `info.productVersion`, `outputfilename` |
| Hosting | GitHub Releases | Binaries and installers |
| Proxy | Go + Gin `desktop_handler.go` | Holds the PAT, caches, resolves URLs |
| Client | `apps/desktop/updater.go` | Download, swap, relaunch |
| UI | Hook, banner, modal | Detect and show progress |

The flow: poll `/api/desktop/latest`, compare versions, download through
`/api/desktop/download?tag=`, which 302s to a presigned URL, save into
`%TEMP%`, rename the live exe to `.old`, copy the new one into place, spawn it,
and `runtime.Quit`.

## Why the API proxies it

**Never ship a PAT in the client binary.** A private repo's release assets
need authentication, so the server holds the token and the client never sees
it. It also means: one shared rate limit instead of per-user (unauthenticated
GitHub is 60 requests per hour per IP, and an office behind one NAT burns that
fast), a 10 minute server cache, and an emergency override by environment
variable with no client redeploy.

### Server configuration

| Variable | Behaviour |
|---|---|
| `GITHUB_TOKEN` | Bearer auth. Required for a private repo |
| `DESKTOP_GITHUB_OWNER` / `_REPO` | Fall back to compiled defaults |
| `DESKTOP_ASSET_GLOB` | Default `.exe`; `.dmg` for macOS |
| `DESKTOP_LATEST_VERSION` | Emergency override, skips GitHub entirely |
| `DESKTOP_LATEST_URL` / `_NOTES` | Companions to the override |

In compose, `GITHUB_TOKEN: ${GITHUB_TOKEN:-}` so the API still boots without
one. Cache TTL 10 minutes, GitHub timeout 8 seconds.

### The endpoints

`GET /api/desktop/latest`, with `?refresh=1` to bypass the cache. It resolves
in order: the env override (`source: "env"`), the cache, then
`GET /repos/{owner}/{repo}/releases/latest` with
`Accept: application/vnd.github+json`. A GitHub error gives
`source: "fallback"`, no matching asset gives `source: "no-asset"`, success
gives `source: "github"`. Drafts and prereleases are rejected. The payload is
snake_case: `{version, download_url, github_url, released_at, release_notes,
source}`, and `download_url` points back at your own API, not at GitHub.

`GET /api/desktop/download?tag=vX` finds the asset id, requests
`/releases/assets/{id}` with `Accept: application/octet-stream` and
`CheckRedirect` returning `http.ErrUseLastResponse`, then reads `Location` off
the 302 and redirects the client to the presigned URL.

`GET /api/desktop/diagnostics` is read-only and the first thing to hit when
updates stop working: `token_set`, `token_length`, `token_prefix` (four
characters, never the whole token), and a live fetch result.

Asset picking is a case-insensitive substring match on the glob, taking the
first asset whose name contains neither `setup` nor `installer`, so the raw
binary wins over the installer.

## Releases layout

Tags are `vMAJOR.MINOR.PATCH` with an optional `-suffix`. The leading `v` is
stripped for comparison. **Never mix `v1.2.3` and `1.2.3` in one repo.**

| Asset | Rule | Purpose |
|---|---|---|
| `App-v{V}.exe` | no `setup` or `installer` | Raw binary, what the updater swaps |
| `App-Setup-v{V}.exe` | contains `setup` | Full NSIS installer, WebView2 bundled |
| `App-Setup-Slim-v{V}.exe` | contains `setup` | Slim installer, WebView2 online |
| `App-Setup-v{V}.zip` | | Zipped installer for email |

Upload the installer first, the raw exe second, the zip last.

## The updater

State: `status`, `target`, `version`, `errMsg`, plus `bytesDownloaded` and
`bytesTotal` as `atomic.Int64`, and a `context.CancelFunc`. Exposed to React
as `{status, version, bytes_downloaded, bytes_total, error}`.

Bound methods: `SetContext`, `CleanupOldOnStartup`, `GetProgress`,
`StartDownload(url, version)`, `CancelDownload`, `InstallAndRestart`.

Download into `os.TempDir()/App-v{version}.exe.partial`, then rename to the
final name. Remove any stale partial first. `http.Client{Timeout: 0}` with
cancellation through the context, require a 2xx, take `bytesTotal` from
`resp.ContentLength`, and stream through `io.TeeReader` into a progress writer
that does an atomic add.

Install, and the order matters:

1. Status `installing`
2. `currentExe, _ := os.Executable()`
3. `os.Remove(currentExe + ".old")` to clear a stale one
4. `os.Rename(currentExe, currentExe+".old")`
5. **Copy**, not rename, the new file into `currentExe`, with
   `os.OpenFile(..., O_WRONLY|O_CREATE|O_TRUNC, 0o755)`. `%TEMP%` and
   `%LOCALAPPDATA%` can be on different volumes and `os.Rename` returns EXDEV
   across them. On failure, roll back by renaming `.old` back.
6. Remove the temp file
7. `exec.Command(currentExe).Start()`
8. In a goroutine: sleep 250ms, then `runtime.Quit(ctx)`, or `os.Exit(0)` when
   there is no Wails context

Wire it in `main.go`:

```go
OnStartup: func(ctx) {
    app.startup(ctx)
    updater.SetContext(ctx)
    go updater.CleanupOldOnStartup()   // a goroutine: never block startup on this
},
Bind: []interface{}{ app, updater },
```

`CleanupOldOnStartup` retries 25 times at 200ms, because a handle may still be
held, and gives up quietly rather than failing the launch.

## Version comparison lives on the client

`isNewerVersion(current, latest)` in `src/lib/version.ts`: drop anything after
`-`, split on `.`, `parseInt` each part with non-finite becoming 0, compare
left to right treating a missing part as 0, and return true only if latest is
strictly greater. The server does no comparison at all; it returns the tag.

`APP_VERSION` comes from a Vite `define` of `__APP_VERSION__`, read out of
`wails.json` by `vite.config.ts`, so there is one version number and the
frontend cannot drift from the binary.

## The UI

`useLatestVersion()` polls every 6 hours, keyed `["desktop-latest-version"]`
with `staleTime` at half the interval and `retry: 1`, and exposes `checkNow`
(which hits `?refresh=1`). A banner shows when an update is available; a modal
runs the download, polling `GetProgress` every 500ms.

| Status | Heading | Actions |
|---|---|---|
| `downloading` | Downloading v{version}, with MB of MB and a percentage | Cancel |
| `downloaded` | Ready to install v{version} | Install and restart |
| `installing` | Installing | none |
| `error` | Update failed, with the message | Close |

Give the modal `max-h-[90vh] overflow-y-auto` and truncate release notes to
the first three bullets with a "Show all (N)" toggle capped at
`max-h-[180px]`, or long notes push the Install button off screen. Gate the
banner behind a localStorage preference and remember a dismissed version so it
does not nag until the next one.

## The installer, per-user on purpose

`RequestExecutionLevel user` and `InstallDir "$LOCALAPPDATA\Programs\App"`.
**Installing under `%PROGRAMFILES%` and auto-updating are incompatible**: the
swap needs write access without UAC.

Two flavours from one `project.nsi`, selected with `-DSLIM_INSTALLER` on the
`makensis` line: slim uses `wails.webview2runtime` and downloads WebView2 at
install time (about 22 MB installer), full bundles the standalone runtime
(about 200 MB) and works offline. For field installs on slow links, ship the
full one: the online bootstrapper pulls roughly 125 MB mid-install and looks
like a hang.

Two NSIS traps. Use **backslashes** in `File` and `-D` paths: forward slashes
silently fail inside a conditional macro. And the single-instance mutex must
drop the `Global\` prefix, because that needs admin on a per-user install;
check specifically for `ERROR_ALREADY_EXISTS` with `IntCmp $R0 183` rather
than `StrCmp $R0 0`, which treats any error as "already running".

## Platforms

| Platform | Mechanism |
|---|---|
| Windows | Rename the running exe to `.old`, copy the new one in. The primary target |
| macOS | Replace the `.app` bundle in `/Applications`, copying with `ditto`. The rename trick works but bundle replacement is the convention |
| Linux | Not recommended. Binaries are package-manager owned |

## When it breaks

| Symptom | Cause |
|---|---|
| Empty `download_url` | No asset matched the glob, or the release is a draft or prerelease. Hit diagnostics |
| Version up to 10 minutes stale | The server cache. `checkNow` or `?refresh=1` |
| `renaming current exe: Access is denied` | Antivirus holding the file, or an install under `%PROGRAMFILES%` |
| "Setup is already running" falsely | The `Global\` mutex or a `StrCmp` on the error code |
| Install appears to hang | The online WebView2 bootstrapper. Use the offline flavour |
| Install button off screen | Unbounded release notes in the modal |
| 401 Bad credentials | Wrong or expired PAT, or a trailing newline in it |
| `.exe.old` left behind | A handle still held, common with Defender on an unsigned binary. Sign it, or accept the leftover |
| No `wailsjs/go/main/Updater.d.ts` | The bindings only appear after a `wails build` |
| `gh release create` failed after the tag pushed | An orphan tag. `git push origin :v1.2.3` and rerun |

## What to add before trusting this with real users

The source design does not cover these, and each is a real exposure:

1. **Verify what you downloaded.** Publish a `SHA256SUMS` asset, check the
   digest before the swap, and refuse on a mismatch. Code signing helps
   SmartScreen but does not verify the download.
2. **Fix the fallback.** On a GitHub error the proxy returns the releases
   **page** as `download_url` with version `1.0.0`. If that compares newer
   than the client, the client downloads an HTML page and tries to run it.
   Return no `download_url` on the fallback path instead.
3. **Roll back a version that will not start.** The `.old` file is still there
   on the first run after a swap; a first-run heartbeat that fails should
   restore it.
4. **Enforce a minimum supported version** server-side, so an old client that
   can no longer talk to the API is told to update rather than failing
   mysteriously.

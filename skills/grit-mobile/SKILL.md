---
name: grit-mobile
description: >-
  The Expo app: screens against the shared API and types, offline field use,
  uploads, images, haptics, and getting through App Store and Play review. Use
  for "add a mobile app", "the Expo app", "field mode", "submit to the store",
  "my app was rejected", "the image will not load on my phone".
---

# grit-mobile

An Expo app against the same API and the same shared types. Two references
carry most of the detail and you should read the relevant one before writing
screens:

- `../grit-references/flat-light-mobile.md` is the complete style: tokens, primitives,
  layout, haptics, motion, copy rules, the anti-rules, and the platform traps.
  **Every value comes from `lib/tokens.ts`.** Add a token before using a new
  value.
- `../grit-references/store-rejections.md` is the pre-submission checklist. Read it
  before the first submission, not after the first rejection.

```bash
grit docs search "mobile"
grit new app --mobile          # check the live command with grit --help
ls apps/expo
```

## The four things that break first

These are specific to a Grit mobile app and each one presents as something
else entirely.

**Uploads must use `fetch` with `FormData` and no `Content-Type`.** On SDK 54,
`uploadAsync` sends an empty body. The symptom is a successful request and a
zero-byte file, which looks like a server bug and is not. Let the runtime set
the boundary; setting `Content-Type` yourself breaks it a different way.

**Images will not load from localhost, because localhost is the phone.** A
stored image URL pointing at `127.0.0.1` resolves to the device. Two things
are needed: a `resolveImageUrl()` host rewrite on the client, and MinIO
published on the LAN address rather than `127.0.0.1`. Both, not either.

**The API port comes from the environment, the host comes from Metro.** The
app derives the dev machine's LAN address from the host Metro is served on and
needs only `EXPO_PUBLIC_API_PORT` to go with it. That is why the seeder writes
a port rather than a URL for Expo, and it is what keeps the app working on a
real device when `APP_PORT` changes. `EXPO_PUBLIC_API_URL` overrides both and
is how you point at a deployed backend.

**With `apps/expo` in the monorepo, React is pinned to Expo's version
everywhere.** Two Reacts in a hoisted `node_modules` breaks every component
test in every web frontend, with errors that point at the components rather
than at the duplication.

## Offline for field work

**`grit-offline` owns the design.** Identifiers, the outbox, replay and the
conflict rules are decided there and this app is built against them.

If the product has reps in the field, offline is the requirement and not a
nice-to-have. The architecture is the same as the desktop's: a local mirror
and a queue of writes to replay, with the server authoritative.

The questions to answer before building, same as desktop: what is
authoritative, what happens on a conflict, what can be created offline and
referenced before it has a server id, and what a failed replay looks like to
the person who made the write. Write the answers in the project profile.

The one mobile-specific addition: **a phone loses the process, not just the
network.** The queue has to survive the app being killed, which means it is in
SQLite or storage, never in memory.

## Screens

Build from the style reference, not from memory. The parts people get wrong:

- **Flat rows with inset hairlines.** Not a card per row, no gaps between
  rows, and no chevrons outside settings.
- **One filled primary button per view.** The theme colour on no more than
  three element types per screen.
- **No shadows** on cards, buttons or the tab bar. Border or shadow, never
  both.
- **Eight states per interactive element**, and the two always missing are
  error and success.
- **`fontFamily`, never `fontWeight`.**
- **Never `style={({ pressed }) => ...}` on a `Pressable`.** NativeWind drops
  it on Android and the row collapses. Static styles plus `PressableScale`.
- Touch targets 44x44, with `hitSlop` for small links.

Data from the API is normalised with `?? []` before it is indexed. `data[0]`
on a null list crashes Hermes, and a release build closes silently on a JS
error unless there is an error boundary plus
`ErrorUtils.setGlobalHandler`, so build the crash guard early.

## Store submission

`../grit-references/store-rejections.md` in full. The things that cause most
rejections are not code:

**The demo account.** Non-expiring, pre-populated with realistic data, works
on a clean device, no device-bound second factor, no biometric-only gate, no
subscription the reviewer cannot reach. Apple wants it in App Review Notes,
Play wants it in the App access section.

**Account deletion.** Required by both if accounts can be created. Apple wants
it in-app and deleting server-side data; Play wants **two** routes, in-app and
a publicly reachable web page. Deactivation is not deletion.

**The declarations matching the binary.** Apple's App Privacy labels and
Play's Data Safety form must cover every SDK including transitive ones. This
is the most commonly cited Play rejection and it is a paperwork failure, not a
code one. Build the data-flow inventory from source, manifests, network traces
and the SDK list, then reconcile.

**Permissions tied to a visible feature**, requested at point of use, with an
in-app disclosure before the system prompt, and graceful handling of denial.
Diff the manifest against the last release and delete what is unused.

Check the live target API level before submitting rather than trusting a
number written down months ago, and ship an AAB.

## Before you say it works

- Run on a **real device**, not only the simulator. Clean install and upgrade
- Offline: do real work with the network off, then let it drain
- An upload, and check the file is not zero bytes
- An image from storage, on the device, on the LAN
- Permission denied, and the app still works
- A release build, which is where the silent-crash class lives
- Then the pre-submission checklist, in full, against the exact build you are
  uploading

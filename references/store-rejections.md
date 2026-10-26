# Store rejections

Distilled from https://jb.desishub.com/blog/app-store-google-play-rejection-guide

Read this before the first submission, not after the first rejection. Most
rejections are review-readiness, not code: the reviewer could not get in, or a
declaration did not match the binary.

A **rejection** blocks a release and usually leaves the live version up. A
**removal** takes the published app down. A **suspension** is account level,
counts as a strike, and can escalate to termination.

## Apple

**2.1 App completeness.** Crashes, placeholder text ("Lorem Ipsum", "Coming
Soon"), dead buttons, empty screens, a backend that was down during review, no
demo account, hardware features with no reviewer notes. Also failures *after*
a permission denial, an interrupted purchase, a restore, rotation, a deep link,
a network switch, or a paywall. Fix: test the exact uploaded build on real
devices, clean install and upgrade, offline, low storage, permission denied;
give working demo credentials in App Review Notes; hide unfinished features
behind a remote flag; keep the backend up through the review window; confirm
the build selected in App Store Connect is the one you tested.

**5.1.1 Privacy.** A missing or broken privacy policy URL, which must be in
store metadata **and** in the app. App Privacy labels that do not match actual
collection, including every third-party SDK. **In-app account deletion is
required** if accounts can be created, and it must delete server-side data: a
Deactivate button that leaves the data is a rejection. Tracking needs App
Tracking Transparency before any tracking begins. Permission prompts appear in
context with plain-language purpose strings tied to a visible feature. SDKs
need a Privacy Manifest.

**4.2 and 4.3 Minimum functionality and spam.** A website in a WebView with
little native value, single-purpose or static content, template apps,
near-duplicates, batches of regional variants. This is a distinctiveness
judgment and original code does not settle it. Fix: add native capability
(push, offline, camera, sensors, native gestures, personalised content) and
make the differentiated value reachable in the first review session.

**2.3 Metadata accuracy.** Screenshots showing features that do not exist or
are undisclosed paywalled, keyword stuffing, exaggerated claims, competitor
names, pricing mismatches, broken support or privacy links. Screenshots show
the free experience, and premium features are labelled.

**3.1.1 and 3.1.2 Purchases.** Digital content or subscriptions outside
StoreKit, a missing Restore Purchases, unclear subscription terms, external
payment links for digital goods. Classify every product first, then test the
whole lifecycle: purchase, restore, renewal, cancellation, interruption,
entitlement delivery.

**1.2 User-generated content.** No report or block, weak moderation, slow
escalation, public-by-default profiles for minors, no support contact, weak
age or parental controls. Test with multiple accounts and verify a per-post
report and block flow. Kids category: re-audit every analytics, ads and
identifier SDK for child-directed compliance.

**5.2 to 5.5 Legal.** Unlicensed logos, names, characters, fonts or media.
Gambling, financial or medical features without authorisation. Medical claims
without evidence. Distribution where the service is not permitted. Keep an
evidence file of licences and agreements. A disclaimer is not a substitute for
an approval.

**Also**: Sign in with Apple is required when other third-party logins are
offered (4.8). Unreviewed remote code execution (2.5.2). And simply the wrong
build: mismatched bundle ID, version, signing or entitlements.

### Apple needs

Privacy policy URL (store and in-app), App Privacy labels, a Privacy Manifest
for SDKs, App Review Notes, demo credentials, current screenshots and listing
per locale, subscription disclosures, a Restore Purchases control, the ATT
prompt if tracking, and a purpose string per permission.

## Google Play

**Broken functionality.** Crashes, freezes, ANRs, failing core flows,
placeholder features, a login with no test credentials in the **App access**
section. Use the pre-launch report and Android vitals, and check the technical
quality thresholds for crashes, ANRs, wake locks and battery.

**Data Safety mismatch.** Very commonly cited and strictly enforced. The form
must cover the app, controlled WebViews, libraries and every SDK including
transitive ones. Pseudonymous data that could reasonably be re-linked still
needs disclosing. Sensitive or background collection needs a prominent in-app
disclosure and affirmative consent **before** access; a privacy policy alone
is not enough. Build the data-flow inventory from source, manifests, network
traces, backend schemas and SDKs, then reconcile it with the form, and re-run
it whenever a dependency changes.

**Sensitive permissions.** SMS, Call Log, Contacts, background location,
all-files access. High-risk ones may need a Permissions Declaration Form, a
demonstration video and reviewer instructions, and review can take weeks. The
common rejection is a permission whose declared use does not match core
functionality. Diff the manifest against the last release, delete what is
unused, tie each remaining one to a visible feature, show an in-app disclosure
before the system prompt, and handle denial gracefully.

**Account deletion.** Required if accounts can be created, and Play wants
**two** routes: in-app, and a publicly reachable web page. Freezing is not
deletion. Test logged in and logged out, from a mobile browser, in every
launch region; name the app and developer on the web page; verify server-side
data, tokens and linked identities go, not just local data.

**Minimum functionality.** A website in a frame, templated content, affiliate
spam, impersonation. For a PWA use a Trusted Web Activity, not a raw WebView.

**Store listing.** Title 30 characters maximum. No emoji, repeated special
characters, or ALL CAPS outside a genuine brand name. No unsubstantiated claims
about rankings, awards, discounts or Google Play affiliation, no unattributed
testimonials, no competitor mentions. Screenshots match the current build.
Content rating comes from the IARC questionnaire answered from actual
behaviour.

**Payments.** Digital content, functionality, subscriptions and cloud services
use Google Play Billing unless a documented exception applies, and you must not
steer users to alternative payment through the listing, a WebView, a button, a
message or an account flow. Test purchase, acknowledgement, pending and failed
states, entitlement delivery, renewal, cancellation, refund and cross-device
sync.

**Technical requirements**, as of 31 August 2026 and worth re-checking before
you submit: new apps and updates target Android 16 / API 36 or higher; Wear OS
and Automotive API 35+; TV and XR API 34+. No debuggable release builds. Native
code needs 64-bit and 16 KB page-size compatibility. Ship an AAB.

**New personal developer accounts** created after 13 November 2023 must run a
closed test with at least 12 continuously opted-in testers for 14 consecutive
days before production access.

### Google Play needs

The Data Safety form, a privacy policy URL that matches it, a Permissions
Declaration Form and demo video where required, the App access section with
credentials and instructions, App content declarations (target audience,
Families, IARC rating, ads), the store listing, an external web deletion page,
a signed AAB, and closed-test evidence for a new personal account.

## The demo account is the thing people get wrong

It must be non-expiring, pre-populated with realistic data, work on a clean
device, and have no device-bound second factor, no biometric-only gate and no
subscription the reviewer cannot reach. Write reviewer instructions that are
deterministic and step by step, and record a short video for anything
hardware-dependent or notification-driven.

## If rejected

1. Preserve the record: the message, the cited guideline, build ID,
   storefronts, declarations, credentials, screenshots, logs. Do not change ten
   things at once.
2. Classify the citation: technical, review access, privacy, permissions,
   payments, metadata, safety, minimum functionality, legal, or platform
   requirement. One citation can have several causes.
3. Reproduce the reviewer's path: clean device, the submitted artifact, the
   account you supplied, their region and OS. If it does not reproduce, vary
   fresh install versus upgrade, network, permission state, account state,
   storefront and locale.
4. Build an evidence packet: build ID, repro steps, the feature, the mapped
   policy, the correction, and a recording if the feature is hard to reach.
5. **Fix the root cause.** Remove the unnecessary permission rather than
   justifying it better. Replace the non-compliant SDK. Implement real
   server-side deletion.
6. Use the official channel. Play: update the declaration or artifact and
   resubmit, appeal only if the action was mistaken, and check the rest of the
   catalogue for the same unnamed issue. Apple: reply in the App Store Connect
   conversation with specific evidence, and appeal on a guideline only after
   answering their questions.
7. Resubmit with a documented change set, and retest the original failure plus
   the flows next to it.
8. Add the failure to the regression suite so it cannot return.

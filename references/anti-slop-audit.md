# The anti-AI-slop design audit

Distilled from https://jb.desishub.com/blog/anti-ai-slop-design-audit

This is the standard any screen in this project is held to. Run it as an audit
before you call a UI done, and use it as a checklist while building so there
is less to find.

## Score

`Slop-Free Score = max(0, 100 - (8 x Critical + 4 x High + 1.5 x Medium))`

90-100 A, ship it. 75-89 B, minor cleanup. 60-74 C, real work. Below 60, the
slop is systemic.

**Critical**: fabricated claims or testimonials, body text failing WCAG AA,
horizontal scroll or broken mobile layout, a core flow not keyboard operable,
a faked brand asset presented as real.

**High**: inconsistent components, weak or absent hierarchy, off-token colours,
missing hover or focus states, `transition-all` everywhere, an eyebrow on every
section, placeholder images shipped as final.

**Medium**: alignment and spacing drift, motion timing, gradient-text overuse,
bad line length.

## First, classify the surface

**Marketing** (landing, hero, marketing sections) and **product** (dashboards,
tables, admin, settings, multi-step forms) are judged differently. The
marketing-only rules below do not apply to product surfaces: a dense,
repetitive data table is correct in an admin and slop on a landing page.

Then find the token source of truth: the Tailwind config, the `:root`
variables, the theme file. If there is no token system, say so and infer the
de-facto palette rather than inventing a second one.

## A. System consistency

- One primary accent. A competing second accent is a finding.
- Colours, spacing, radii and shadows come from tokens. `#3b82f6`, `p-[13px]`
  and `rounded-[7px]` are the signature of slop.
- The same component looks and behaves identically everywhere.
- One icon library. Mixed icon sets read as assembled rather than designed.

## B. Typography

- Two font families maximum, one of them optionally mono. A third is slop.
- One consistent type scale. An ad-hoc size used nowhere else is a finding.
- Exactly one `h1`. Never skip `h2` to `h4` to get a size.
- Body line length 45 to 75 characters, line-height about 1.5.
- Avoid 800 and 900 weights as body-adjacent defaults.

## C. Colour and contrast

- Computed on the real token values: body text 4.5:1, large text and UI
  boundaries 3:1.
- Semantic colour means what it says: red destructive, green success.
- No purple-to-pink-to-orange gradients. No `background-clip: text` gradient
  headings unless the brand calls for it, and then once or twice, not on every
  heading.
- Colour is never the only signal. An error needs text or an icon too.

## D. Layout and hierarchy

- One focal point per screen. The primary action is the most prominent thing.
- Consistent grid, margins and gutters.

Marketing only:

- The hero fits the first viewport: headline at most 2 lines, subtext about 20
  words, CTA visible without scrolling. A 4-line headline is a font-size bug.
- No three equal feature cards in a row.
- Left-image/right-text zigzag capped at two in a row.
- A bento grid has as many cells as items. No empty tiles.
- An eight-section page uses at least four distinct layout families.
- The small uppercase wide-tracked eyebrow: at most one per three sections.

## E. The eight-state contract

Every interactive element defines all eight: default, hover, focus-visible,
active, disabled, loading, error, success. Error and success are the ones
always skipped. A submit button with no loading state, or a field with no
error style, is a finding.

Status is always shown: buttons show loading, lists show skeletons and empty
states, destructive actions confirm. And anything that looks interactive must
be interactive: no fake Copy on a plain div, no button-styled span with no
handler.

## F. Accessibility

- Semantic HTML. A real `button`, `nav`, `main`, `a`. A clickable `div` is a
  finding.
- A visible focus-visible ring on everything interactive, and the whole flow
  operable from the keyboard.
- Touch targets at least 44x44 on mobile.
- Meaningful images get descriptive alt; decorative ones get `alt=""` or
  `aria-hidden`.
- Honour `prefers-reduced-motion`. **A JS animation library is not covered by
  the CSS media query**: its code has to check reduced motion itself.

## G. Responsive safety

- No horizontal scroll at 375px.
- `overflow-x: clip`, not `hidden`, on both `html` and `body`.
- Grid tracks holding images use `minmax(0, 1fr)`, never a bare `1fr`.
- No nav item or CTA whose label wraps to two lines.
- Display-size headings get `overflow-wrap: anywhere` and `min-width: 0`.

## H. Motion hygiene

- Animate `transform` and `opacity` only. Never `width`, `height`, `top`,
  `left`.
- Never `transition-all`. Name the exact properties.
- UI feedback under about 300ms, with consistent easing.
- Motion has to be motivated: hierarchy, feedback, storytelling, a state
  change. Not because the library is installed.
- One horizontal marquee per page at most.
- No `addEventListener("scroll")` for scroll-driven animation. Use
  `IntersectionObserver` or the library's scroll trigger.

## I. Copy honesty

Fabrication is **Critical**. Never invent:

- Conversion or performance metrics ("+47% conversion", "saves 12 hours")
- Social proof counts ("trusted by 50,000+ teams")
- Benchmarks ("10x faster", "99.99% uptime")
- Testimonials: names, quotes, companies, avatars
- Customer or partner logos nobody named
- Pricing, limits or guarantees nobody specified

The fix is a visible placeholder such as "metric to confirm", or deletion.
Never a different invented number.

Also: short paragraphs and bullets. No forced metaphors, no
performative-craftsman labels ("Field notes", "On our desks"), no mock-poetic
filler. Plain beats cute. **No em dashes in rendered copy**, anywhere:
headlines, eyebrows, buttons, body, captions, alt text.

## J. The tells, hard-flagged on marketing surfaces

- Section-number or status eyebrows: `00`, `INDEX`, `001 - Capabilities`,
  `V0.6`, `BETA`, `INVITE-ONLY`
- Weather, locale or time strips in nav or footer ("LIS 14:23 - 18C")
- Scroll cues: the word "Scroll", a down arrow, an animated mouse wheel
- Decorative status dots on every list item or nav link
- Fake liveness badges: "Live", "Building", "Online" with no real state
- Hero-bottom mono strips ("BRAND. MOTION. SPATIAL.")
- Version footers on marketing pages ("v1.4.2", "Build 0048")
- Photo-credit captions on stock images
- "John Doe", "Jane Smith", "Acme", "Nexus", "SmartFlow"
- Fake-precise numbers presented as data
- Div-rectangle fake previews standing in for a real screenshot

## K. Asset integrity, non-negotiable

Never invent or fake a brand asset. Never ship a placeholder as final.

Flag: an emoji used as a logo, product icon, feature illustration, avatar or
hero graphic. A styled text wordmark standing in for a real logo.
`picsum.photos`, `placehold.co`, `via.placeholder.com`,
`source.unsplash.com/random`, grey boxes, "TODO: image", div-based fake
screenshots. A hand-drawn SVG substituting for a real logo. A stock face
presented as a specific named person.

The decision:

1. **A generic UI affordance** (checkmark, arrow, chevron, menu, close,
   search, spinner): use the project's icon library. No question needed.
2. **A brand or identity asset** (logo, company mark, a named person's photo,
   a real product screenshot, a hero image): remove the fake, substitute
   nothing, and leave a commented slot:
   `ASSET NEEDED: official Acme logo (SVG preferred). Placeholder.`
   Then add a row to the asset request table.
3. A stock image used as content: same as 2.
4. If the asset's identity is unclear, ask one line rather than guess.

The asset request table at the end of the report: what it is, where it is used
(`file:line`), the format needed (SVG for marks, PNG or JPG for photos), the
size or aspect ratio, and why.

## Reporting

Score and grade, then the surface map, then a per-category A-K scorecard with
PASS, PARTIAL or FAIL and a count, then findings grouped Critical, High,
Medium with `file:line`, the rule, the user impact and a concrete fix in
project tokens. Then the assets you need. Then what you will fix and what is
blocked.

**Do not fix anything until the report is approved.** Then fix Critical, High,
Medium in that order, using only project tokens, adding a token to the source
first if one is genuinely missing. Re-run the score and report the new number
with the assets still outstanding.

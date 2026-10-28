---
name: grit-design-review
description: >-
  Assess a page against Grit's visual contract in DESIGN.md: measures the
  budgets (type styles, radii, rhythm, shadows, contrast, target size), then
  looks at it, then says what to fix in order. Use for "review this page",
  "does this meet our design standard", "design review", "is this page
  consistent", "check the landing page", "before I ship this page", or after
  building any new page or section.
---

# grit-design-review

A page is done when it is **within budget and looks right**, in that order.
The budgets catch what taste misses, and looking catches what counting
misses. A review that does only one of them is half a review.

The contract is `DESIGN.md` at the repository root. Read it; this skill is the
procedure, that is the standard.

## The one rule about judgement

**Report numbers before opinions.** "This page has 36 type styles against a
budget of 12" is a fact somebody can act on. "The typography feels
inconsistent" is not, and it invites an argument instead of an edit.

Only after the numbers do you say what you saw.

## Step 1: measure

The page has to be running. A static file read cannot tell you a computed
colour, and contrast is computed.

```bash
cd docs && npx next build && npx next start -p 3980   # or: pnpm dev
```

Then in the browser, one line:

```js
eval(await (await fetch('/design-audit.js?v=' + Date.now())).text())
```

`docs/public/design-audit.js` is the measurement. It returns `budgets`,
`failures` and `details`, and it encodes DESIGN.md §9 so the numbers and the
document cannot drift.

Run it at **1440x900 and again at 390x844**. Several failures only exist at
one of the two: line length and target size usually fail on desktop and
mobile respectively, for opposite reasons.

If the audit will not load, the dev server was started before
`docs/public/design-audit.js` existed. Restart it.

## Step 2: look

Screenshot the page at both widths, and in **both themes**. Then answer these,
which no script can:

1. **Where does the eye land first?** If it is not the one thing the page is
   for, the page is wrong regardless of its numbers.
2. **Can you tell the primary action from the secondary one** without reading
   the labels?
3. **Does every section earn its scroll?** For each one: would a reader who
   stopped at the section above know less? If no, cut it.
4. **Is the spacing a rhythm or a list of decisions?** Squint. Uneven gaps
   show up as a ragged edge when you cannot read the words.
5. **Does it look like the product?** Open a generated admin panel beside it.
   A seam between the site and the thing it is selling is the expensive kind
   of inconsistency.

Screenshot the result and put it in the report. A review of a visual change
with no picture in it is asking to be taken on trust.

## Step 3: interact

The budgets say nothing about behaviour.

- **Tab through the whole page.** Every focusable thing must show a visible
  ring, and the order must match the visual order. A focus ring that is
  invisible on one of the two themes is a fail, so check both.
- **Trigger every hover state.** A card that lifts, scales or shadows on hover
  is against the contract: the border is the signal.
- **Scroll the page twice.** Anything that re-animates on the second pass is a
  fail. Entrances happen once.
- **Set reduced motion** and scroll again:
  ```js
  // DevTools: Rendering > Emulate prefers-reduced-motion
  ```
  A GSAP timeline ignores the CSS override, so this is the only way to find
  one that was never wrapped in `gsap.matchMedia()`.

## Step 4: read the source for what the DOM hides

```bash
# Hex outside the token file: every one of these is a colour that cannot be themed
grep -rnoE '#[0-9a-fA-F]{3,8}\b' docs/app docs/components | grep -v globals.css | head -30

# The reduced-motion block has to exist
grep -n 'prefers-reduced-motion' docs/app/globals.css

# GSAP timelines that never check for it
grep -rln 'gsap' docs/components docs/app | xargs grep -L 'matchMedia'

# outline: none with nothing put back
grep -rn 'outline-none\|outline: none' docs/app docs/components | grep -v 'focus-visible'
```

## Step 5: report

Ordered by what it costs a reader, not by what is easiest to fix.

```
PAGE   /docs/plugins/marketplace     1440x900 and 390x844, both themes
BUDGET 4 over

  contrast          28 failures      limit 0     <- people cannot read this
  targets <24px     32               limit 0     <- people cannot tap this
  type styles       36               limit 12
  sections          31               limit 12

MUST FIX
  1. "Get Started" is 2.86:1 against its background. It is the primary
     action on the page and it fails AA by a wide margin.
     -> --accent-ink on --accent, which is 7.1:1

  2. 32 controls are under 24x24 (WCAG 2.5.8). The theme swatches are
     16x16. Pad the control, not the icon.

SHOULD FIX
  3. 36 type styles. 14 of them are used exactly once: 6px/600, 9px/700,
     320px/700. Each is a decision nobody will remember making.
     -> the twelve in DESIGN.md §2

LOOKED AT IT
  The eye lands on the giant decorative wordmark in the footer before the
  install command, because the wordmark is 320px and the command is 14px.

VERDICT  not ready
```

Three things that make a report useful rather than discouraging:

- **Name the fix, not just the fault.** Every line above ends in an arrow.
- **Separate must from should.** Contrast and target size stop people using
  the page. Thirty-six type styles is untidy. Treating them the same gets
  neither fixed.
- **Say what is good.** A page that nails its rhythm and fails on contrast
  should hear both, or the next page regresses the part that worked.

## What the budgets do not catch

Keep these in your own head; the script will never flag them.

- **Copy doing design's job.** Three paragraphs explaining a diagram means
  the diagram failed.
- **A section that is a list of features with no claim.** Each section makes
  one point. If you cannot say it in one sentence, it is not one section.
- **Decoration standing in for hierarchy.** Glows, gradients and borders
  applied evenly across a page cancel out: everything emphasised is nothing
  emphasised.
- **The second accent.** Somebody always adds one to make a thing stand out.
  Size and space do that job; a second accent destroys the first one.
- **Placeholder content that shipped.** Lorem, a stock avatar, a chart with
  made-up numbers. Real content changes the layout, and finding that out
  after launch is expensive.

## When the page is not yours to fix

A generated admin panel's screens come from `internal/scaffold`. Reviewing one
and editing it in the generated project fixes one project; the template is
what every project gets. Fix the template, then regenerate and review again.
`grit-admin` knows the templates.

## Hand back to

- `grit-ui-ux` to do the design work this review asked for.
- `grit-admin` when the page is a generated admin screen.
- `grit-feedback` when the fault is in the framework's own templates.
- `grit-critic` when the question is bigger than the page: whether the feature
  is actually finished.

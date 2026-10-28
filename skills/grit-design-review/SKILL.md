---
name: grit-design-review
description: >-
  Assess a page against Grit's visual contract in DESIGN.md: measures the
  budgets (type styles, radii, rhythm, shadows, contrast, measure, target
  size), diffs it against the designer's mockup, then looks at it, then says
  what to fix in order. Use for "review this page", "does this meet our design
  standard", "design review", "is this page consistent", "check the landing
  page", "does this match the design", "before I ship this page", or after
  building any new page or section.
---

# grit-design-review

A page is done when it is **within budget, matches the design, and looks
right** — in that order. The budgets catch what taste misses, the diff catches
what memory misses, and looking catches what counting misses. A review that
does only one of them is a third of a review.

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
cd docs && npx next dev -p 4200     # or: npx next build && npx next start
```

Then in the browser, one line:

```js
eval(await (await fetch('/design-audit.js?v=' + Date.now())).text())
```

`docs/public/design-audit.js` is the measurement. It returns `budgets`,
`failures`, `details` and `fingerprint`, and it encodes DESIGN.md §9 so the
numbers and the document cannot drift.

Run it at **1440x900 and again at 390x844**. Several failures only exist at
one of the two: the measure and target size usually fail on desktop and
mobile respectively, for opposite reasons.

Read `details.offSystemTypeStyles` as well as the count. The count says a page
is undisciplined; that list says where, and it is usually three components
rather than thirty decisions.

## Step 2: diff against the design

Only for a page the designer drew. `docs-redesign/extracted/{landing,quickstart}`
holds the mockups.

```bash
cd docs-redesign/extracted && python -m http.server 4100
```

The audit has to be **same-origin** with whatever it is measuring, so put a
copy where the mockups are served from:

```bash
cp docs/public/design-audit.js docs-redesign/extracted/
```

Run the same line on `localhost:4100/landing/Main.dc.html` and on the real
page, then compare the two `fingerprint` objects:

| Field | What a difference means |
|---|---|
| `container` | The frame is the wrong width. Both should be 1200. |
| `colours` | A token drifted. These must be identical, character for character. |
| `sections[].headingPx` | A heading is off the type scale, or a `clamp` is wrong. |
| `sections[].hasCornerMarks` | A section is missing the signature. Every one has it or none is a signature. |
| `sections[].hasRule` | A section lost its rule, so it reads as part of the one above. |
| `sections[].height` | Within about 10%, fine. Beyond that the content is a different shape, not a different style. |

Do **not** expect the section counts to match. The landing mockup is 29
sections because it is a catalogue of every section the designer drew; the
page is twelve because DESIGN.md §7 caps it. Compare the twelve that exist on
both.

An image diff is the wrong tool here: two pages with different copy in them
differ everywhere, and the output is all noise.

## Step 3: look

Screenshot the page at both widths, and in **both themes**. Then answer these,
which no script can:

1. **Where does the eye land first?** If it is not the one thing the page is
   for, the page is wrong regardless of its numbers.
2. **Can you tell the primary action from the secondary one** without reading
   the labels? Remember the primary is the near-white one. If a violet button
   is pulling the eye first, the hierarchy is inverted.
3. **Does every section earn its scroll?** For each one: would a reader who
   stopped at the section above know less? If no, cut it.
4. **Is the spacing a rhythm or a list of decisions?** Squint. Uneven gaps
   show up as a ragged edge when you cannot read the words.
5. **Does it look like the product?** Open a generated admin panel beside it.
   A seam between the site and the thing it is selling is the expensive kind
   of inconsistency.

Screenshot the result and put it in the report. A review of a visual change
with no picture in it is asking to be taken on trust.

## Step 4: interact

The budgets say nothing about behaviour.

- **Tab through the whole page.** Every focusable thing must show a visible
  ring, and the order must match the visual order. A ring that is invisible
  on one of the two themes is a fail, so check both.
- **Arrow-key every tablist.** `role="tablist"` promises arrow keys, Home and
  End. One that only answers clicks has told a screen reader to expect
  something it does not do, which is worse than a row of buttons.
- **Trigger every hover state.** A card that lifts, scales or shadows on
  hover is against the contract: the border is the signal. A button that
  changes hue on hover is a different button, not the same one.
- **Scroll the page twice.** Anything that re-animates on the second pass is
  a fail. Entrances happen once.
- **Set reduced motion** (DevTools > Rendering > Emulate CSS media) and
  reload. Two different faults hide here: a GSAP timeline that ignores the
  CSS override because it was never wrapped in `gsap.matchMedia()`, and an
  element that starts at `opacity: 0` waiting for an observer, which under
  reduced motion is invisible content rather than a disabled animation.

## Step 5: read the source for what the DOM hides

```bash
# A type class that does not exist. Tailwind emits NOTHING for a class it
# does not know, and nothing is not an error: the element silently inherits.
grep -rnoE 'text-(lead|body|caption|eyebrow|display|stat|h[1-4])\b' docs/app docs/components | head
grep -n 'fontSize' docs/tailwind.config.ts     # it is only real if it is here

# `ch` as a measure. In Geist, ch is 44% wider than a character.
grep -rn 'ch\]' docs/app docs/components | grep -i 'max-w\|width'

# hsl(var(...)) left over from the old token system; the tokens are hex now
grep -rn 'hsl(var(' docs/app docs/components

# shadcn's accent meant "hover surface"; ours is the brand violet
grep -rn 'hover:bg-accent/' docs/app docs/components

# Hex outside the token file: every one is a colour that cannot be themed
grep -rnoE '#[0-9a-fA-F]{3,8}\b' docs/app docs/components | grep -v globals.css | head -30

# The reduced-motion block has to exist
grep -n 'prefers-reduced-motion' docs/app/globals.css

# outline: none with nothing put back
grep -rn 'outline-none\|outline: none' docs/app docs/components | grep -v 'focus-visible'
```

Anything edited in `docs/app/grit.css` is a fault on its own. That file is the
designer's `bundle.css`, taken byte for byte so it can be replaced wholesale
on an update. Fixing a page by editing it means the next update silently
reverts the fix.

## Step 6: report

Ordered by what it costs a reader, not by what is easiest to fix.

```
PAGE   /docs/plugins/marketplace     1440x900 and 390x844, both themes
BUDGET 4 over          DIFF  2 landmarks differ from the design

  contrast          28 failures      limit 0     <- people cannot read this
  targets <24px     32               limit 0     <- people cannot tap this
  type styles       36               limit 12
  sections          31               limit 12

MUST FIX
  1. "Get Started" is 2.86:1 against its background. It is the primary
     action on the page and it fails AA by a wide margin.
     -> --accent-fg on --accent, which is 7.1:1

  2. 32 controls are under 24x24 (WCAG 2.5.8). The theme swatches are
     16x16. Pad the control, not the icon.

OFF THE DESIGN
  3. Sections 4 and 7 have no corner marks, so they read as one section
     with a gap in it.
     -> wrap them in <Section>, which draws them

SHOULD FIX
  4. 36 type styles, 14 used exactly once. The three worst offenders are
     one component each: 11px/400 x41 is the table caption.
     -> the twelve named in DESIGN.md §2, by class name

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

## When the audit itself is wrong

It has been, three times, and each one passed a real fault or cried wolf:

- An accent **fill** was detected by comparing red, green and blue and
  ignoring alpha, so a 10% wash counted as a call to action.
- **Target size** exempted only `<a>` inside `<p>`, so breadcrumbs and meta
  rows were flagged, which teaches people to ignore the check.
- **Line length** assumed 0.5em per character, and `ch` is 44% wider than a
  character in Geist, so both the rule and the check were wrong in the same
  direction.
- The **container landmark** used `querySelector` with a selector *list*,
  which returns the first match in document order rather than the first
  selector's match, so `main` won and it measured the viewport.

If a number looks wrong, check the measurement before you change the page.
A check that cries wolf is worse than no check; a check that passes a real
fault is worse again. When you fix one, say so in the report, because the
previous reviews that used it were wrong too.

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

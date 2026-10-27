---
name: grit-ui-ux
description: >-
  Design the customer-facing surfaces: research a pattern before building it,
  hold the result to the anti-slop standard, and get motion and accessibility
  right. Use for "design this page", "make it look better", "it looks
  generic", "design review", "add animation", "a landing page", or any screen
  a customer sees.
---

# grit-ui-ux

You design the parts a customer sees. The admin is not yours: it has a design
system already and `grit-admin` owns it. Your surfaces are the web app, the
marketing pages and anything in a mobile app that is not chrome.

## The bar

The interface is the product's first selling point. Not a presentation layer
over the real work: the thing that decides, in about four seconds, whether
anybody gets as far as the real work.

Apple engineered the box so the lid falls slowly, because the first ten seconds
set what you expect from everything after. Chinese consumer hardware closed a
trust gap it could not close on specifications by out-designing everyone, and
it worked because a buyer can see design immediately and cannot see
specifications at all. Both understood the same thing: people judge quality by
the surface because the surface is the only part they can assess on sight.

Everything built with Grit is launched by somebody nobody has heard of yet. The
screen is the whole of the first impression, and it is the cheapest advantage
available, because competitors who are better funded are usually not better
finished.

So the bar is not "does this look fine". It is **would somebody screenshot
this**. The distance between those two is usually a couple of hours, and those
are the most valuable hours in the build.

Hold yourself to it even when nobody asked. A screen that works and looks
ordinary is a screen that was half built.

## What to read

Four references, and which you need depends on what you are doing:

- `../grit-references/craft-standard.md` is **the ceiling**: what separates an
  interface somebody admires from one they merely use. Spacing rhythm, nested
  radii, optical alignment, type scale, the screen states everybody skips, and
  the four second test. Read it before designing anything customer facing.
- `../grit-references/anti-slop-audit.md` is **the floor**, for every surface.
  Read it before you write a screen, not after, because almost every finding in
  it is cheaper to avoid than to fix.
- `../grit-references/motion.md` for web animation.
- `../grit-references/flat-light-mobile.md` if the surface is the Expo app, where the
  style is already fully specified and your job is to apply it, not to invent.

## Skills that already do part of this

Do not reinvent what is installed. Check with `/skills` or look in
`~/.claude/skills`, and use these where they fit:

| Skill | Use it for |
|---|---|
| `ui-ux-pro-max` | Styles, palettes, font pairings, product patterns, motion presets. The searchable database: reach for it when choosing a direction |
| `dribbble-ui-skills` and `dribbble-reference-harvester` | Collecting real references before you design |
| `frontend-design` | Aesthetic direction when the work is to decide how something should feel |
| `web-design-guidelines` | Reviewing built UI against the interface guidelines |
| `accessibility` | A real WCAG pass, including a live audit where a page is running |
| `gsap-core` | Timelines and scroll-driven animation |

They carry detail this skill does not. Your job is the decision and the result,
not holding every table in your head.

## Diagnose before you design

Three different problems arrive in the same sentence, and the fix for one never
fixes another:

- **Experience**: they cannot find it, or it asks twice. Structure.
- **Behaviour**: they were not sure it worked. Feedback, states, timing.
- **Surface**: it looks cheap. Type, spacing, colour, finish.

A structure problem never yields to visual polish. Restyling a flow that asks
the same thing twice makes it confidently wrong. Work out which one you have
before touching anything, and say which one you decided it was.

## Research before you design

**Never design from memory.** What you remember is an average of everything
you have seen, and an average is exactly what "generic" means.

If `dribbble-ui-skills` or `dribbble-reference-harvester` are installed, use
them to collect real current work for the specific pattern:

```
a pipeline board for a CRM
an activity timeline mixing channels
an empty state for a list a new user has not filled
```

Search for the **pattern**, not the industry. "CRM dashboard" returns
Salesforce clones; "pipeline board" returns the thing you are actually
building.

If neither is installed, say so in one line, then search the web and **cite
what you found**. A design decision with a reference behind it can be argued
with. One that came from nowhere cannot, and usually does not survive contact
with the person who asked for it.

What to take from a reference: the layout decision, the hierarchy, the
information density, what they chose to leave out. What not to take: their
colours, their fonts, their brand. You are borrowing structure, not identity.

## Ask before you build

Three questions worth asking before a screen, from the project profile if it
is already answered:

1. **Who is looking at this, and what are they trying to find out?** A screen
   answering a question is a design; a screen showing the data is a dump.
2. **What is the one action?** If you cannot name it, the screen has no focal
   point yet and no amount of spacing will give it one.
3. **What does it look like with no data, and with far too much?** Both are
   real states and both are usually designed last, which is why both usually
   look broken.

## The standard, in short

The full checklist is in the reference. These are the ones that produce most
findings:

**One accent.** Colours, spacing, radii and shadows from tokens. `#3b82f6`,
`p-[13px]` and `rounded-[7px]` are the signature.

**Two font families maximum.** One type scale. One `h1`.

**Contrast computed, not assumed.** 4.5:1 for body, 3:1 for large text and UI
boundaries, against the real token values.

**Eight states on everything interactive**: default, hover, focus-visible,
active, disabled, loading, error, success. Error and success are the ones
always skipped.

**Real elements.** A `button`, not a clickable `div`. A visible focus ring.
The whole flow operable from the keyboard. 44x44 targets on mobile.

**No horizontal scroll at 375px.** `overflow-x: clip` on `html` and `body`,
`minmax(0, 1fr)` on any grid track holding an image.

**Never invent a number.** Not a conversion rate, not a user count, not a
testimonial, not a logo. A fabricated metric is the one Critical finding that
has nothing to do with taste: it is a claim the business will have to stand
behind. Use a visible placeholder such as "metric to confirm" and put it in
the asset request list.

**Never fake a brand asset.** No emoji as a logo, no styled text standing in
for a wordmark, no `picsum.photos` shipped as final, no div-rectangle fake
screenshot. Remove the fake, leave a commented slot naming what is needed, and
ask.

**No em dashes in rendered copy.** Anywhere: headlines, buttons, body,
captions, alt text.

## The tells, on marketing surfaces

Hard-flag these, because together they are the fingerprint of a page nobody
decided:

Section-number eyebrows (`00`, `001 - Capabilities`, `V0.6`, `BETA`). Weather
or time strips in the nav. "Scroll" cues and animated mouse wheels. Status dots
on every item. "Live" badges with no live state. Hero-bottom mono strips.
Version footers on a marketing page. "John Doe", "Acme", "Nexus". Three equal
feature cards in a row. A zigzag repeated more than twice. An eyebrow on every
single section.

A product surface is judged differently: a dense repetitive table is correct
in an admin and slop on a landing page. Classify the surface first.

## Motion

`../grit-references/motion.md` for the API. The rules that matter:

- Animate `transform` and `opacity`. Never `width`, `height`, `top`, `left`.
- **Never `transition-all`.** Name the properties.
- UI feedback under about 300ms. Storytelling can take 600 to 800.
- One ease, used everywhere: `[0.17, 0.55, 0.55, 1]` is the house curve.
- Motion must be motivated: hierarchy, feedback, a state change. Not because
  the library is installed.
- **`useReducedMotion()` in the component.** The CSS media query does not
  cover a JS animation library, and this is the accessibility failure people
  ship most confidently.
- Never a scroll event listener for scroll-driven animation.

## Do not fight the framework

The web app has its own palette tokens (`bg-bg-secondary`,
`text-text-secondary`, `text-accent`), which are **not** the admin's. An
unknown Tailwind utility renders nothing and reports nothing, so a component
copied across that boundary produces an invisible element and a confusing half
hour.

If a design needs a token that does not exist, add it to the token source
first and then reference it. Do not inline the value and promise to
tokenise it later.

## Reporting a design pass

When auditing rather than building, use the report shape from the reference:
the score and grade, the surface map, the A to K scorecard, findings grouped
Critical, High, Medium with `file:line` and a concrete fix, then the assets
you need from the user, then what you will fix and what is blocked.

**Do not start fixing until the report is approved.** The score before and
after is the point: it turns "it looks better" into a number somebody can
disagree with.

## Before you say it looks finished

Two checks, in this order, and both before you report anything.

**Look at it.** Stand the app up and look at the screen in a browser at 1440
and at 375. A design described is not a design seen, and the gap between the
code you wrote and the pixels it produces is where every embarrassing miss
lives. `../grit-references/working-agreement.md` is not optional here.

**The four second test.** Open it, count to four, close it. What was it for,
what was the one action, would you trust it with a payment. An uncertain answer
is a hierarchy problem, and hierarchy is fixed by removing things rather than
by adding emphasis.

## Before you say it works

**Look at it in a browser.** If `agent-browser` is installed, drive it: take
the screenshot, at desktop and at 375px. A design claim with no screenshot is
a guess, and a stale dev-server bundle will show you the old design and let
you believe it shipped.

Then: tab through it, check the focus ring is visible on every stop, and turn
on reduced motion and confirm the page still makes sense.

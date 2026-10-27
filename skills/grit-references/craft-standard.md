# The craft standard

What separates an interface somebody admires from one they merely use.

`anti-slop-audit.md` is the floor: the things that make a screen read as
generated. This is the ceiling. Read this one when the work is customer facing
and the first impression is the product's first selling point, which on a
product nobody has heard of is most of the time.

## Why this is worth the hours

Two companies understood something the rest of the industry says it believes
and does not act on.

Apple treats the unboxing as part of the product. The box is engineered: the
lid falls at a controlled speed because air escapes through a designed gap.
Nobody needed that. It exists because the first ten seconds set what you expect
from everything after, and expectation is most of what people call quality.

Chinese consumer hardware won on the same insight from the other direction.
The specifications were matched or beaten long before the brands were trusted,
and what closed the gap was finish: the screens, the renders, the animations,
the retail photography, the apps. They out-designed rather than out-specified,
and it worked because a buyer can see design in four seconds and cannot see
specifications at all.

For a product made with Grit the equivalent is the first screen. Somebody lands
on it with no reason to trust you, and decides. The decision is made before
they have read a word, and it is made on craft: whether the spacing is even,
whether the type looks chosen, whether anything moves when it should.

So the bar is not "does it look fine". The bar is **would somebody screenshot
this**. If the answer is no, the work is not finished, and the gap between
those two is usually two hours, not two weeks.

## Diagnose before you design

Three different problems look identical in a complaint, and the fix for one
never fixes another.

| The problem lives in | It sounds like | The fix |
|---|---|---|
| **The experience** | "I cannot find it", "why does it ask twice" | Structure, order, what is on which screen |
| **The behaviour** | "I was not sure it worked", "it felt slow" | Feedback, states, timing, optimistic updates |
| **The surface** | "it looks cheap", "it looks like a template" | Type, spacing, colour, finish |

**A structure problem never yields to visual polish.** A flow that asks for the
same thing twice looks worse after restyling, because now it is confidently
wrong. Work out which of the three you have before touching anything. Most
requests to "make it look better" are one of the first two wearing the third's
clothes.

## The details that read as designed

None of these is visible on its own. Together they are the whole difference.

**Spacing is a rhythm, not a number.** Pick a base (4 or 8) and multiply.
Spacing between related things is always smaller than spacing around the group:
a label 4px from its input, the field 24px from the next field. When a layout
feels wrong and you cannot say why, this is the first thing to check.

**Nested radii are not equal.** An inner element inside a rounded container
takes the outer radius minus the gap between them. A 12px card with 8px padding
holds an 8px inner element, never another 12px. Equal radii is the commonest
tell of a layout assembled rather than drawn.

**Shadow is elevation, not decoration.** One light source, from above. Things
closer to the user cast larger and softer shadows. Two elements at the same
level take the same shadow. A shadow that exists to "add depth" to something
flat reads as a sticker.

**Optical alignment beats mathematical alignment.** A circle next to a square
has to overshoot to look the same size. An icon beside text aligns to the
text's optical centre, not its box. Centred text in a button with an icon needs
the padding asymmetric. Trust the eye over the number.

**Type is a scale, and a scale is a ratio.** 1.25 for dense interfaces, 1.333
or 1.5 for marketing. Pick one and derive every size from it. Display sizes
need negative letter-spacing, roughly -0.02em at 48px and more as it grows,
because type designed for paragraphs looks loose when it is huge. Body text
sits between 60 and 75 characters a line.

**Weight carries hierarchy better than size.** Going up one weight is usually
stronger and quieter than going up two sizes. Most interfaces that feel shouty
are solving with size what weight would solve.

**Colour is earned.** The base is neutral so that the one accent means
something. If three things on a screen are competing for the eye, nothing has
it. Reserve saturation for the single action you want taken.

**Borders or shadows, rarely both.** Pick the one that does the separating. A
card with a border and a shadow and a background change is three solutions to
one problem.

**Empty is a designed state, not a missing one.** The empty table is the first
thing a new user sees, and "No data" is the sentence that tells them they
picked the wrong product. It should say what goes here, why it is worth having,
and give the button that creates the first one.

## Every state of the screen

A component has eight states. A screen has more, and they are what gets
skipped.

- **First run.** Nothing exists yet. This is the most important screen in the
  product and it is almost always the least designed.
- **Loading**, both the first load and a refresh. A skeleton shaped like the
  content beats a spinner, because it tells you what is coming.
- **Partial.** Some of it arrived. Does the layout hold.
- **Too much.** A name 90 characters long, a table with 400 columns of data, a
  number in the millions. Where does it break.
- **Error**, which deserves the most care, because it is the moment the user
  most needs to know what to do next. "Something went wrong" is not a state, it
  is a shrug.
- **Offline or stale**, where it applies.
- **Success**, which almost always gets a toast and nothing else, when a
  changed screen would say it better.
- **Returning.** They were here yesterday. Does the screen remember anything.

A screen is not finished until these are drawn. Most of the hours that separate
a product that looks designed from one that does not are spent here, not on the
default state everyone photographs.

## Motion has a job or it does not ship

Motion earns its place by explaining something: where a thing came from, that
something arrived, that a boundary was hit. Decoration that moves is noise with
a frame rate.

- 150 to 250ms for most interface transitions. Under 100 is invisible, over 400
  is in the way.
- Ease-out for things entering, ease-in for things leaving. Linear only for
  something continuous, like a progress bar.
- Animate transform and opacity. Animating width, height, top or left is how
  smooth becomes janky.
- Everything respects `prefers-reduced-motion`, and the reduced version is
  "arrive instantly", never "do not arrive".

## The four second test

Open the screen. Count to four. Close it.

- What was the one thing it was for?
- What was the one action?
- Would you trust it with a payment?

If any answer is uncertain, the problem is hierarchy, and hierarchy is fixed by
taking things away rather than by adding emphasis.

## Steal properly

Research is not optional, and copying a reference wholesale is not research.

Find three examples of the pattern from products that are good at it, work out
what the three agree on, and build that. The agreement is the convention, and
convention is what makes a screen learnable. Then make one thing specifically
yours: the empty state, the way a row expands, the one piece of motion.
Everything else conventional, one thing memorable.

A screen that is entirely conventional is forgettable. A screen that is
entirely original is unusable. The ratio is roughly nine to one.

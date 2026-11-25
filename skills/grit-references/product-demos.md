# Multi-step product demos

Distilled from https://jb.desishub.com/blog/building-multi-step-product-demos

An animated demo that plays in the page, showing a real task finished: add a
contact, send a quote, get paid. Three to five beats, ten to sixteen seconds,
one payoff.

**This file is the judgement, not the kit.** The `stageshow` skill ships the
React kit, its gold examples and the filming script, and it is the thing to
read for the API and to start from. Do not restate its parts here or rebuild
them by hand. What follows is what decides whether the demo reads as a real
product or as a cartoon, which is the part no kit can do for you.

`landing-page.md` is where a demo goes: the walkthrough section, and one per
module.

---

## A demo is state plus a script

Three pieces: a state object holding everything that can change on screen, a
render function that draws the screen from that state, and a script that
changes state over time and moves a cursor.

**It is a reducer with a cursor on top.** That framing is load-bearing: it is
why you never hard-code a coordinate. The script names a target and the cursor
measures the DOM, so a demo that is re-laid out does not need re-choreographing.

Every beat has the same shape: **move, wait, click, set, wait.** The wait
before a click is the part people leave out, and it is the part that makes a
cursor look like a hand rather than a teleport. A sixth of a second is enough.

Press off-centre. A click that lands exactly in the middle of every button
reads as a machine.

All screens stay mounted and cross-fade, so there is never an empty frame
between pages.

## Write the beats in prose first

Three to five beats. One payoff. If you cannot write the story in six lines of
plain prose, there is no story yet and no amount of animation will supply one.

Then:

- **Every change needs a cause.** A status that updates by itself is the single
  clearest tell of a fake demo. If a quote becomes accepted, show the client's
  phone rise, the tap, the phone leave. Cause first, then effect.
- **The one event nobody chooses gets no cursor.** A connection dropping, a
  deadline passing, a payment arriving: no cursor. That is how you show "this
  happens to you" rather than "you click here", and it is worth a beat of its
  own.
- **Update something, do not only insert.** Three beats that each add a new row
  are one claim made three times. Changing an existing value (a mark from 64 to
  76) is what proves a sync or an edit claim.
- **Plan the loop reset when you add the fourth beat**, not after. Getting back
  to the start without undoing visible work is the hardest part of the job, and
  a reset with no cause is worse than no loop. Hide it behind a page change.

## Values move, they never swap

A number that changes by re-rendering is the fault that makes everything else
look cheap, and it is invisible until somebody points at it.

- Numbers and words that change roll or fade between values.
- A counting number counts; a changing number does not need to count up from
  zero to look alive.
- **Update a total once, when the input is complete**, not on every keystroke.
  A total flickering per character is noise, not feedback.
- Keep a currency code and its number on one line with a non-breaking space. A
  unit wrapping onto its own line is a recurring fault.

## Framing is what separates a product shot from a screenshot

- **The page is the ground.** The demo sits in the page, not on a plate floating
  with air on all four sides.
- **Bleed past at least one edge.** A window entirely inside its frame reads as
  a picture of an app; one that runs off an edge reads as the app.
- **Only filler bleeds. The action stays whole.** Never crop the thing the beat
  is about.
- **Windows are cropped, never resized.** Shrinking the window to fit takes
  11px type to 9px and nobody can read it. Keep the stage at its design size and
  crop.
- **Leave no dead corners.** An empty quadrant is the thing that makes a demo
  look unfinished. A small satellite card fills one.
- **Compact is a redesign, not a shrink.** The phone-width version is laid out
  again, not scaled down.
- Design at the size it will be seen and show it 1:1. Below about 320px wide,
  do not show it at all.
- **Frame first, then animate.** Film a still before any motion exists.
  "Almost right" framing makes motion faults invisible, because everything looks
  slightly off and nothing looks wrong.

## Real words are a budget

Three to seven real strings. Everything else is grey structure.

**The more real detail there is, the more it looks generated.** This is
counter-intuitive and it is the rule most worth internalising. A table where
every row has plausible text reads as filler; a table with three real rows and
the rest as grey bars reads as a product with data in it.

- Put the real words on the three or four things the story is about.
- **Never put a grey bar where the eye lands.** Grey is for the periphery.
- Real domain detail beats generic realism: actual subjects, actual names from
  the market the product serves, not "User 1" and not Lorem.
- Show the product's own mark and icons. A generic logo in a demo of a specific
  product is a wasted frame.

## Honesty

The `grit-ui-ux` standard forbids invented numbers and logos, and a faux UI is
not an exemption. A revenue figure in a mocked dashboard is a claim the
business has to stand behind.

- Real strings, real numbers, or obviously-example ones. Not invented ones
  dressed as real.
- **Read the gate result, do not just run it.** A failing check has three
  legitimate outcomes: fix it, argue against it in writing, or accept it because
  the real product does the same thing. Write down which, next to the component.
- A check that disagrees with the arithmetic is worth investigating, not
  obeying.
- Pricing and names come from one source, so a number exists in one place.

## The poster frame, accessibility, and why they are the same thing

The poster is a state object, not a captured image: the demo rendered at a
chosen moment. That one artefact is the reduced-motion path **and** the
thumbnail. Build it as a state and both are free.

- Under `prefers-reduced-motion`, render the poster and do not animate.
- A demo is a picture. Give the wrapper `role="img"` and an `aria-label` that
  describes it in one sentence, or `aria-hidden` the whole figure if it is
  purely decorative. Leaving a demo's text exposed to a screen reader in an
  unplanned order is not acceptable, and it is the default if you do nothing.
- **Never leave an element at opacity 0 waiting on a script that may not run.**
  Add the hiding class from the script, so no JavaScript means visible content.

## Integration faults that cost an afternoon

- **Clashing attribute names.** A page-level scroll-reveal rule keyed on an
  attribute the kit also uses will hide the kit's own rows. Exclude the stage
  from the page's reveal rule and its observer.
- **One state key, one meaning.** A key reused for two things puts the phone on
  the wrong page.
- **Target names are globally unique across the stage.** Two screens with a
  target of the same name send the cursor to the wrong control.
- Map the product's tokens onto the kit's custom properties. Do not reshape the
  kit's geometry from outside.
- A demo never sits in the wrong theme: read the page theme rather than fixing
  light or dark.

## In a grid of tiles

- Window chrome appears **at most once** in the grid. Repeated chrome across
  six tiles reads as a template.
- Copy sits at the top of every tile, consistently. Mixed positions read as
  unfinished.
- A picture that bleeds must bleed cleanly: slicing itself and leaving a blank
  strip is a recurring fault.

## The faults that come back every time

A value that swaps instead of moving. Grey bars where the eye lands. A plate
behind the window, or a window floating with air on four sides. Empty bands,
cut controls, clipped shadows. Sparkles, purple gradients, a letter in a
coloured square. A long hold, then a reset with no cause. A text selection not
under the I-beam. Hand-drawn device chrome. A unit wrapping to its own line. A
tile picture slicing itself. A state that changes with no cause. A loop frame
that undoes completed work. Framing that is almost right.

## Build it in this order

1. Write the beats in prose. Six lines.
2. Build the state object and the render, no motion.
3. Film a still. Fix the framing.
4. Add the script, one beat at a time.
5. Add the poster and the reduced-motion path.
6. Run the gate, read it, and write down anything you left standing.
7. Check at 1440 and 375, light and dark, with reduced motion on.

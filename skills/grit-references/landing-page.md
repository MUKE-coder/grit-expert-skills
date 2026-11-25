# Designing a SaaS landing page

Distilled from https://jb.desishub.com/blog/designing-a-saas-landing-page

`craft-standard.md` is the ceiling and `anti-slop-audit.md` is the floor. Both
are about any surface. This is about one surface: the page a stranger lands on
with no reason to trust you, written from a real rebuild of a business
workspace product.

`product-demos.md` is its companion. The walkthrough section below is where
the demos go.

---

## Four rules for the work itself

**1. Find references before you design.** Search for the UI pattern, not the
industry: "pricing card", "pipeline board". Searching your client's sector
returns their competitors, which is how a page ends up looking like the thing
it is trying to beat.

**2. Write the rules down first.** A `style-guide.md` at the repo root fixes
colours, type, spacing and motion, and every later decision is checked against
it. Without it the fourth section invents its own spacing and nobody notices
until the page is finished.

**3. Only say what is true.** No user counts, no ratings, no customer logos, no
testimonials you cannot back. Every figure inside an illustration is labelled
as an example. If the product does not do it yet, the page does not say it
does. This is the rule most often broken by a page built quickly, and it is the
one with consequences outside design.

**4. Look at it.** Every change, in a real browser, at 1440px and 375px, in
light and in dark. A design that exists only in code is a design nobody has
checked.

## The foundation

**Calm over loud. One accent, used sparingly.** Colour marks meaning, never
decoration. The reference build used a desaturated slate blue (`#3E5C76`), Inter
throughout, and a mono face only for numbers, IDs and code.

**Theme as CSS variables under a `data-theme` attribute**, not hard-coded
values. A `.dark` class that works on any element then lets one section be dark
on a light page without inventing a second palette.

**Dark mode needs its own, lighter accent.** The light accent on near-black is
too close to the background to read as the main action. This is not optional
polish; the primary button stops looking like the primary button.

**Separate "ink" tokens from fill tokens.** A status colour that passes as a
fill often fails as text. Use the darker ink shade for text and links, the
plain colour for fills, and check both against 4.5:1.

**Tailwind 4: plain `@theme`, never `@theme inline`.** Inline bakes the values
in at build time, and runtime theme switching then breaks silently.

**One easing curve for everything.** The reference build used
`cubic-bezier(0.17, 0.55, 0.55, 1)`, a quick start with a soft landing. Much of
why a page feels like one product rather than several is that every transition
on it shares a curve.

Radii: around 10px for controls, 16px for cards. Named layout values (a hero
height, a rail width) belong in tokens too, so the fourth section cannot invent
its own.

### Section rules

- One `h1` per page.
- Content width capped (`max-w-6xl` with side padding), reading text capped
  near 70 characters. A paragraph the full width of a 1440px page is not read.
- Consistent vertical rhythm between sections (`py-24` in the reference).
- Alternate the background between the page colour and a secondary surface,
  **with no dividing lines**. The change of surface is the divider.
- `scroll-mt-24` on every section with an id, or an anchor link hides the
  heading under the sticky nav.

## Order the sections by the visitor's questions

This is the part worth copying. The page is not a list of features; it is the
questions a stranger asks, in the order they ask them, each answered once.

| Section | The question it answers |
|---|---|
| Hero | What is it |
| Audience strip | Who is it for |
| Principles (a bento) | Why this instead of five separate apps |
| Walkthrough | Show me it working, end to end |
| One section per module | What is actually in it |
| Security band | Can I trust it with my data |
| Pricing | What does it cost |
| Who built it | Who am I buying from |
| Closing band | Start |

If a section does not answer a question a visitor is actually asking at that
point, it is decoration and it costs you the scroll.

**The hero** is a headline, a plain-words paragraph of what the product does,
two buttons (one filled, one outlined) and the price in one quiet line. Any
illustration around it is decorative and gets `aria-hidden`; hide it entirely
on phones, where there is no room and it becomes noise.

**The audience strip replaces the customer-logo strip** when you have no
customers to name. "Built for service businesses" and six honest categories
beats six invented logos, and it is a better answer to "is this for me" than
logos ever were.

**One eyebrow per section, not per block.** An eyebrow on every block is the
fingerprint of a templated page.

**Section titles say what the visitor gets, in plain words, never a slogan.**

**Pricing: one plan, one card.** Keep the price on one line
(`whitespace-nowrap`) or it breaks across two on a phone with the period
stranded. Numbers live in one pricing file so the hero, the card and any search
page cannot disagree. If bigger teams need a different number, a quiet "more
than N people?" line with a real contact beats an invented Enterprise tier.

**The closing band is the strongest call to action on the page.** Dark, short,
two buttons.

## Navigation

- A floating pill, inset from the window edge rather than touching it, slightly
  translucent with a backdrop blur.
- **Three equal grid columns, not flexbox `justify-between`.** Flex only centres
  the links if both sides happen to be the same width, so they drift as soon as
  one side changes.
- **Sign in stays visible at every width**, including phones. Hiding the way
  back in behind a hamburger costs you returning users, who are the ones most
  likely to convert.
- Every touch target at least 40px tall.
- In a menu panel, **the whole row is the target**, with an icon, a title and a
  one-line description. A 14px line of text is not something anybody can aim at.
- Nav links in one data file, used by both the desktop bar and the phone menu,
  so the two cannot diverge.
- **No empty footer links.** An empty footer link is a promise the site cannot
  keep. Add the column when the page exists.

## The motion system

**Every animation answers a visitor question**: did my click land, where did
this come from, what changed. If it answers none, delete it. See `motion.md`
for the API and `premium-details.md` for the component-level finish.

**Only animate `transform` and `opacity`.** Never `width`, `height`, `top` or
`left`.

Sections rising in on scroll is the whole system for most pages. Three rules,
each one a bug somebody already shipped:

1. **Nothing is hidden until the script runs.** The hidden state applies only
   under a class the script adds. Otherwise a visitor with a slow or failed
   script gets a blank page.
2. **Leave alone anything already on screen at load.** Hiding the hero to fade
   it back in produces a flicker and buys nothing. Check against roughly 90% of
   the viewport height.
3. **Each element animates once**, then stop observing it.

Stagger a group by index with a small step and a cap of about five, so a long
list does not take a second and a half to arrive.

Reduced motion needs both halves: a global media query that cuts CSS
animations, **and** a check inside any JavaScript animation, because the media
query cannot stop a script.

## Before you call it done

- 1440px and 375px, light and dark.
- At 375px, `scrollWidth` equals 375. Any horizontal overflow is a bug.
- Contrast: 4.5:1 body text, 3:1 large text and control borders. Check the dark
  theme separately; it is where the accent-as-text failure lives.
- Keyboard: visible focus rings, and the menu operable without a pointer.
- Reduced motion on: the page is complete and still.
- Type-check and lint pass.

## The anti-patterns, collected

Invented logos, counts, ratings or testimonials. An "Enterprise" tier that
exists to look bigger. A letter in a coloured square as the logo. An eyebrow on
every block. Slogans as section titles. Three equal feature cards in a row.
Sign in hidden in the phone menu. Empty footer links. A light accent used as
text on dark. `@theme inline` with runtime theme switching. Animating `width`
or `top`. Hiding above-the-fold content in order to fade it in. Dividing lines
between sections that already change background. A price that wraps.

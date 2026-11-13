# The details that make an app feel premium

Distilled from https://jb.desishub.com/blog/details-that-make-an-app-feel-premium

The premise worth holding on to: an app feels quick, calm and trustworthy
because of many small consistent decisions, not one hard one. None of what
follows is difficult. All of it is skipped.

`motion.md` is the Framer Motion API. This is what to animate, what to show
while waiting, and the dozen components where the difference between ordinary
and premium actually lives.

---

## Five rules before any code

**1. Motion explains, it never decorates.** Every animation answers a question:
did my click land, where did this come from, is work happening, what changed.
If you cannot name the question, delete the animation.

**2. Fast and small.** Feedback under 200ms. Transitions 150 to 300ms. Nothing
blocks input. Movement 4 to 8px, scale 0.97 to 1. Bigger reads as slower even
when the duration is identical.

**3. One easing curve everywhere.** `cubic-bezier(0.17, 0.55, 0.55, 1)`: quick
start, soft landing. The same curve as `motion.md`'s `[0.17, 0.55, 0.55, 1]`,
because they are the same house curve in two notations.

**4. Animate `transform`, `opacity` and colours only.** Never `width`,
`height`, `top` or `left`: they force layout and stutter on a cheap phone.
Never `transition-all`; name the properties.

**5. Respect reduced motion.** Every animation needs an off switch under
`prefers-reduced-motion: reduce`. **The CSS query does not reach a JavaScript
animation library**, so check it separately in those components. This is the
accessibility failure people ship most confidently.

**Tokens first.** Colours, radii, shadows and spacing in CSS variables and
Tailwind's `@theme`. A literal hex or a `p-[13px]` erodes the identity one
value at a time.

---

## Buttons

**Eight states**: default, hover, focus-visible, active, disabled, loading,
error, success. Error and success are the two always missing.

**The press.** Scale to `0.97` on `:active`, 160ms, transitioning colour,
background, border, shadow, transform and opacity. Naming them is the point:
see rule 4.

**`@layer base` for global defaults.** Unlayered CSS beats Tailwind v4's
utility layers regardless of specificity, so a global button rule written
outside a layer wins against an element's own utility. Put defaults in
`@layer base` and a `fixed` on a floating action button still applies.

**A light sweep on the primary action**, crossing once on hover over 700ms.
One button per screen. Two is a carnival.

**Busy is not disabled.** Greyed-out reads as "you may not", which is a lie
while saving. Keep the colour, swap the icon for a spinner, add a faint sweep,
set `aria-busy`, and change the label from "Save" to "Saving".

> Retrofitting is mechanical: a codemod targeting buttons whose `disabled`
> expression mentions `isPending` added `aria-busy` to 195 of them.

**Never remove a focus outline without replacing it.** Keyboard users have
nothing else.

**44x44px touch targets.** An icon button can stay visually compact on desktop
and grow its hit area on mobile.

---

## Loading, chosen by duration and content

| Wait | Use | Why |
|---|---|---|
| Under 300ms | Nothing | A spinner that flashes is worse than no spinner |
| Known content shape | Skeleton | The page does not jump when data lands |
| An action (save, send) | Busy button | The work belongs to the control that was clicked |
| Upload | Per-file progress | People need to know how long |
| Seconds of AI writing | Shimmer on the target | Shows where the result will appear |

**Skeletons must match real dimensions.** A skeleton that is the wrong height
is a layout shift with extra steps.

**Keep old data while new data loads.** When a filter changes, fade the
previous results to 60% rather than showing an empty state. TanStack Query's
`keepPreviousData` placeholder does this.

**An animated gradient border** is a rotating conic gradient on a registered
`@property` angle, with two backgrounds (padding-box and border-box), turning
over 6s.

> A wrong token name in that declaration (`var(--background)` where the real
> variable was something else) made the whole declaration invalid and the
> border silently vanish. CSS fails quietly; check the rendered result.

---

## Things that arrive

**Dialogs** settle over 260ms, rising 8px from `scale(0.97)`. The same values
work for popovers, menus and toasts.

**Use native `<dialog>` with `showModal()`.** Focus trapping, Escape and focus
return are free and correct. A hand-rolled modal gets at least one of them
wrong.

**New rows** fade up over 240ms from 4px below. React keeps existing elements,
so only the new ones animate: no extra bookkeeping needed.

**A saved value glows once**, green, fading over 1.2s. That is the whole
confirmation. No toast.

**A countdown ring** for a timed warning, such as a "Still there?" sign-out
prompt, empties as the time runs out, turning red and pulsing under 10
seconds.

---

## Forms

**Errors under the field**, in plain language, linked with `aria-describedby`.
Plain words beat a red border alone, and both beat a generic "Validation
failed" toast.

**A sticky save bar** that appears only when the form is dirty, with a live
region reporting "Changes not saved yet" and then "Saved".

**Never nest forms.** The browser submits the outer one, reloads the page and
loses the work. Use `role="group"` with manual Enter handling, or a portal
with `stopPropagation()` on submit.

**Inline editing:**

- A pencil on hover or focus, always visible on touch.
- Enter saves, Escape restores, with a check and a cross for mouse users.
- Position the tools absolutely so they do not shift the column.
- **PATCH only the changed field**, so two people editing different fields of
  one row do not overwrite each other.

**Copy buttons** on anything a person retypes: ids, invoice numbers, emails.
Check plus "Copied" for 1.6s, announced to screen readers.

---

## The searchable dropdown

**Any dropdown past a handful of options should be searchable.** A native
`<select>` with forty items is a scroll wheel.

**Make it a drop-in replacement.** A `SearchSelect` taking the same props as
`<select>` with `<option>` and `<optgroup>` children makes the migration a
search and replace rather than a project.

**The WAI-ARIA select-only combobox pattern**, exactly: arrows move, Enter and
Space select, Escape closes only the list (`stopPropagation`), Tab closes and
moves on, typing jumps or opens the search. `aria-activedescendant` is what
lets a screen reader follow the highlight without focus leaving the input.

**Under six options, skip the search box.**

**Portal it, and flip up when there is no room below.** Inside a modal
`<dialog>`, portal into the dialog: the top layer puts anything outside it
underneath the backdrop.

**Create from the search.** Offer `Add "<name>" as a new <noun>` when nothing
matches exactly. If a name is all that is required, create and select it. If
more is needed, open a short form with the name prefilled and only the
required fields, then put the person back where they were.

---

## Empty, error and success

**Empty is a starting point**, not an apology. Say what will appear here and
offer the one action that fills it.

**Error says what happened and what to do**, in the person's language. Map
status codes to causes: a server firewall rejecting an upload must not read as
"wrong file type".

**Success is a quiet change in place.** The value glows, the row moves, the
label says Saved. Reserve toasts for things that happened somewhere else.

---

## Honesty about the network

**Measure small requests** only, never uploads or AI calls. A health check
every 30 seconds, plus `navigator.connection.effectiveType` where it exists.

**Judge on several samples.** One slow request is not a slow connection.

| Median | Bars |
|---|---|
| under 400ms | 4 |
| under 900ms | 3 |
| under 2000ms | 2 |
| over | 1 |

**Show the bars only at two or fewer, or offline**, with the explanation one
click away. A permanent signal meter is noise.

**One banner per slow spell**, dismissible. Offline gets its own words
("changes will not save until you are back"), and reconnecting gets a brief
"Back online".

---

## Layout stability

- Reserve space for anything that loads: image dimensions, skeleton heights.
- Float hover tools, never insert them.
- Keep a removed item's space for its exit animation, or remove it without
  one. A list that snaps is worse than a list that does not animate.
- **Drag-resizable panels**: set the width through a CSS variable, and disable
  iframe pointer events during the drag (`body.is-resizing iframe`) or the
  drag dies the moment the cursor crosses an embed.

---

## The checklist

Before calling a surface finished:

- [ ] Every button: hover, focus-visible, active, disabled, busy, error
- [ ] No `transition-all`, no animated layout properties
- [ ] One easing curve; feedback under 300ms
- [ ] Usable with reduced motion on, including the JS animations
- [ ] 44px touch targets; tools reachable without hover on touch
- [ ] Large dropdowns searchable; data-backed ones can create
- [ ] Errors under their fields, in words, with `aria-describedby`
- [ ] Empty states carry the action that fills them
- [ ] Loading preserves layout
- [ ] No nested forms
- [ ] 1440px and 375px, no horizontal scroll
- [ ] Tested slow and offline
- [ ] Every colour, radius and shadow from a token

# Motion on the web

Distilled from https://jb.desishub.com/blog/framer-motion

`pnpm add framer-motion`. Any file using a motion component or hook needs
`"use client"`.

```tsx
import { motion, useScroll, useTransform, useInView, useReducedMotion } from "framer-motion";
```

## The four APIs that cover almost everything

**`whileInView`**, for one declarative animation per element:

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.3 }}
/>
```

**`useInView`**, when you need the boolean rather than the animation:

```tsx
const ref = useRef(null);
const isInView = useInView(ref, { amount: 0.5 });
```

**`useScroll`**, for continuous 0 to 1 progress:

```tsx
const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
```

**`useTransform`**, to map that progress onto anything:

```tsx
useTransform(progress, [0, 1], ["0%", "100%"])
useTransform(progress, [0, 0.5, 1], ["#0f172a", "#1e1b4b", "#312e81"])
useTransform(scrollY, (v) => Math.round(v / 10) * 10)
```

### Viewport options

| Option | Values | Meaning |
|---|---|---|
| `once` | `true` / `false` | Fire once, or on every entry |
| `amount` | `0` to `1` | Fraction visible before it triggers |
| `margin` | `"-100px"` | Offset relative to the viewport |

`amount: 0` fires on the first pixel, which is usually too early. Prefer
`0.3` to `0.5`.

### Offsets

```
["start end", "end start"]     enter to exit, the default reach-for
["start start", "end end"]     the full container, for a stack
["start 0.8", "start 0.3"]     element-relative fractions
["start 80%", "end 20%"]       percentages
```

## Timing, so a site feels like one site

- Primary ease `[0.17, 0.55, 0.55, 1]`
- Content durations `0.6` to `0.8`, a hero `1`
- Stagger with a per-child `delay` (`0.2`, `0.4`) or `index * 0.1`
- UI feedback, as opposed to storytelling, stays under about `0.3`

## Performance

- Animate transform properties (`x`, `y`, `scale`, `rotate`) and `opacity`.
  Never `left`, `top`, `width`, `height`.
- Pass motion values straight to `style`: `style={{ x: motionValue }}`. Do not
  wrap one in an identity `useTransform`.
- `once: true` for anything that only needs to happen once.
- `will-change: transform` only on an element currently animating. Framer
  removes it when the animation completes.
- Reserve space with `min-h-*` so a reveal does not shift the layout.
- Lazy-load heavy animated components:
  `dynamic(() => import("@/components/Heavy"), { ssr: false })`.
- Images through `next/image` with real `width`, `height`, an accurate `sizes`
  and `placeholder="blur"`.

## Reduced motion, which is not optional

The CSS media query does **not** cover a JS animation library. The library has
to check for itself:

```tsx
const shouldReduceMotion = useReducedMotion();

<motion.div
  initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 50 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: shouldReduceMotion ? 0 : 0.5 }}
/>
```

Apply it to every scroll animation. The content has to remain usable with
animation off, which means motion is enhancement and never the thing carrying
the meaning.

## Patterns worth knowing

**Scroll progress bar**: `fixed top-0 inset-x-0 h-2`, fill width from
`useTransform(scrollYProgress, [0, 1], ["0%", "100%"])`.

**Stacked sticky cards**: container `useScroll` with
`offset: ["start start", "end end"]`, each card `sticky top-0 h-screen`, and
per-card scale:

```tsx
const targetScale = 1 - (sections.length - index) * 0.05;
const scale = useTransform(progress, [index / sections.length, 1], [1, targetScale]);
```

**Horizontal gallery**: a `h-[300vh]` scroll container, a `sticky top-0
h-screen overflow-hidden` viewport, and a track moved with
`useTransform(progress, [0, 1], [0, -1000 * speed])`. Different speeds per
layer give the parallax: slow `[0, -500]`, medium `[0, -1000]`, fast
`[0, -1500]`.

**Word-by-word text reveal**: per-word opacity from
`[i / n, (i + 1) / n]` to `[0.3, 1]`, each word an `inline-block`.

## Traps

- **Hooks inside a `.map()`** break the Rules of Hooks. The per-item
  `useTransform` goes in a child component, not in the loop or inline JSX.
- **`window.innerWidth` during render** causes a hydration mismatch. Use
  `dynamic(..., { ssr: false })` or check after mount.
- Type a motion value as `MotionValue<number>`, not `any`.
- Do not mix sources for one property: either a CSS class controls opacity or
  Framer does, not both.
- Rounding in a `useTransform` reduces update granularity. It is not a
  debounce.
- No `addEventListener("scroll")` for scroll-driven animation. `useScroll` and
  `IntersectionObserver` exist precisely to avoid it.

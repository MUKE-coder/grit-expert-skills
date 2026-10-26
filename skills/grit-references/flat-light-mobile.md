# The flat light mobile style

Distilled from https://jb.desishub.com/blog/flat-light-mobile-app-style-guide

A complete style for an Expo app: white surfaces, one theme colour, hairline
separators, no shadows on content, no dark mode. Every value comes from
`lib/tokens.ts`. Add a token before using a new value.

## Tokens

### Colour

| Token | Value | Use |
|---|---|---|
| `bgPrimary`, `surface` | `#FFFFFF` | Screens, rows, sheets, tab bar, headers |
| `surfaceMuted` | `#F2F4F5` | Inputs, chips, secondary buttons, tiles, skeletons |
| `hairline` | `#E6E9EB` | Separators, tab bar top edge, card borders |
| `ink` | `#0F7B57` | Primary buttons, active icons, links, focus, badges (5.3:1 on white) |
| `inkSoft` | `#E7F3EE` | Selected chip, tab pill, icon circles, unread tint |
| `accentFlash` | `#D5EDE3` | Chip tap flash |
| `textPrimary` | `#111B21` | Names, titles, body, numbers (17:1) |
| `textSecondary` | `#54656F` | Sublines, labels, inactive tabs (6.4:1) |
| `textMuted` | `#667781` | Timestamps, hints, placeholders (4.6:1) |
| `textTertiary` | `#8696A0` | Sign-in placeholders and fine print only (3.3:1) |
| `onInk` | `#FFFFFF` | Text and icons on theme fills |
| `onInkMuted` | `rgba(255,255,255,0.8)` | Secondary text on theme fills |
| `danger` / `dangerSoft` | `#D93F3F` / `#FDECEC` | Destructive, errors |
| `warning` / `warningText` / `warningSoft` | `#C77700` / `#9A5B00` / `#FFF4E0` | At risk, sync warnings |
| `info` / `infoSoft` | `#2F6FDB` / `#EAF1FD` | Neutral notices, admin badge |
| `neutralSoft` | `#F2F4F5` | Neutral fills, progress track |
| `scrim` | `rgba(17,27,33,0.4)` | Behind sheets and modals |

`accent`, `accentText` and `success` alias `ink`. `accentSoft` aliases
`inkSoft`.

### Scale

- **space** (4px): `1:4 2:8 3:12 4:16 5:20 6:24 8:32 10:40 12:48 16:64`
- **radius**: `sm 6, md 12, lg 14, xl 20, full 9999`
- **iconSize**: `sm 16, md 20, lg 24`
- **size**: `touch 44, button 48, buttonCompact 36, authControl 50, appBar 56,
  tabBarItem 56, tabIndicator 60x32, avatarSm 28, avatar 44, avatarLg 48,
  avatarXl 72, iconCircle 40, emptyIcon 72, rowMin 64, rowMinLarge 76`
- **disabledOpacity** `0.45`, **tabBarClearance** `24`

### Type

Fonts: Inter 300/400/500/600/700 plus JetBrainsMono 500.
**Always set `fontFamily`, never `fontWeight`.**

| Key | Family | Size / line | Tracking | Use |
|---|---|---|---|---|
| `micro` | regular | 11 / 14 | | Row and bubble timestamps |
| `xs` | medium | 11 / 14 | | Badges, captions |
| `caption` | medium | 12 / 16 | | Tab labels, day pills, sender names |
| `sm` | regular | 13 / 18 | | Sublines, helper and error text |
| `label` | medium | 14 / 19 | | Chips, section headers, notices |
| `base` | regular | 15 / 20 | | Body. Row title is base + semibold |
| `lg` | semibold | 16 / 21 | -0.2 | Empty-state title, card headings |
| `xl` | semibold | 18 / 23 | -0.2 | Sheet titles, profile name |
| `title` | semibold | 20 / 25 | -0.3 | Screen titles |
| `2xl` | semibold | 22 / 27 | -0.4 | Stat values, club name |
| `wordmark` | bold | 24 / 30 | -0.6 | Home wordmark |
| `3xl` | semibold | 28 / 34 | -0.6 | Big stat in a card |
| `display` | light | 60 / 68 | -1.6 | Hero number |

Auth screens use their own scale: `largeTitle` bold 28/34 -0.5, `title3`
semibold 20/25 -0.2, `body` regular 17/22 -0.2, `callout` 16/21 -0.15,
`subheadline` 15/20 -0.1, `footnote` 13/18, `caption` medium 12/16.

`tabular = { fontVariant: ["tabular-nums"] }` on any number that changes and
on columns.

### Shadow and motion

`shadow.floating` is for sheets, toasts and the offline pill **only**: iOS
`#000` at `0.08`, radius 12, offset `{0, 4}`; Android `elevation 3`.

motion in ms: `tap 80, flash 150, fast 150, base 250, celebrate 600,
toast 3500`.

## Press feedback

`PressableScale` wraps an animated `Pressable` with a shared scale value.
Press in: spring `damping 18, stiffness 320, mass 0.6`. Press out:
`damping 16, stiffness 260, mass 0.6`.

| Element | pressScale |
|---|---|
| Buttons, chips | 0.98 |
| List rows | 0.99 |
| Big option tiles | 0.95 |
| Icon buttons, header actions | 0.9, plus Android borderless ripple |
| Text links | 0.95 with `hitSlop` 10 |

## Primitives

- **Button**: pill, height 48 (compact 36), paddingH 20 (compact 16), icon 20
  with 8 right margin, label base semibold, disabled 0.45, spinner replaces
  the label only while loading. Variants: `primary` (`ink` on `onInk`, one per
  view), `secondary` (`surfaceMuted` on `textPrimary`), `ghost` (transparent on
  `ink`), `destructive` (`dangerSoft` on `danger`, always confirmed).
- **IconButton**: 44x44, radius full, `hitSlop` 4, glyph 24 `textPrimary`. The
  `ink` tone is a 44 circle with an `onInk` glyph at 20, used only for send.
- **ListRow**: paddingH 16, paddingV 12, gap 12, minHeight 64, bg `surface`;
  unread bg `inkSoft`. Title base semibold one line, subtitle sm
  `textSecondary` one line, meta micro `textMuted`.
- **Divider**: `height: StyleSheet.hairlineWidth`, bg `hairline`,
  `marginLeft` the inset.
- **rowInset(n)** = `16 + n + 12`. Never hand-type a separator inset.
- **Card**: bg `surface`, radius 14, `borderWidth: hairlineWidth` in
  `hairline`, padding 16 (20 for hero or form). **No shadow.**
- **Chip**: minHeight 34, paddingH 14, paddingV 6, radius full, bg
  `surfaceMuted`, label 14 medium `textSecondary`. Selected: bg `inkSoft`,
  text `ink`, semibold.
- **Badge**: radius 6, paddingH 8, paddingV 2, 11px. Tones theme, info,
  warning, danger, neutral.
- **Monogram**: circle, initial semibold at `round(d * 0.4)`, tone picked by
  char-code sum mod 4. Hidden from accessibility.
- **Avatar**: a Monogram with an `expo-image` absolutely on top, so an image
  error leaves the monogram visible.
- **EmptyState**: centred, padding 32, flex 1. Icon circle 72 `inkSoft` with a
  30 `ink` glyph, 16 below. Title lg, message base `textSecondary` 4 below,
  stretched action button 24 below.
- **TextField**: container marginBottom 16, label sm medium `textSecondary` 6
  below. Input minHeight 48, radius 12, paddingH 16, paddingV 12, bg
  `surfaceMuted` with a 1px `surfaceMuted` border. Focus: bg `surface`, border
  `ink`. Error: border `danger` plus sm `danger` text 4 below.
  `placeholderTextColor` `textMuted`, `selectionColor` and `cursorColor` `ink`.
- **ErrorBanner**: row, gap 8, radius 12, padding 12, marginBottom 16, bg
  `dangerSoft`, `alert-circle` 20 `danger`, text base `textPrimary`,
  `accessibilityRole="alert"`.
- **SectionHeader**: row, space-between, marginTop 24, marginBottom 8,
  minHeight 32. Title label semibold `textSecondary` with
  `accessibilityRole="header"`. Action label semibold `ink`.
- **Screen**: `SafeAreaView edges={["top"]}`, bg `bgPrimary`,
  `StatusBar style="dark"`. Header minHeight 56, paddingH 8, gap 4, back as an
  `arrow-back` IconButton falling back to `/(tabs)`. Title `title`
  `textPrimary`, subtitle sm `textSecondary`. **No header bottom border.**
- **SkeletonRow**: height 64, radius 12, bg `surfaceMuted`, marginBottom 12,
  opacity 0.5 to 1 over 750ms repeating with reverse,
  `accessibilityLabel="Loading"`.

## Layout

Horizontal gutter 16. Between sections 24. Inside cards 16, or 20 for a hero
or form. Scroll bottom clearance 24 on tab screens, 40 on stack screens. Form
fields 16 apart with the primary button after the last one. Stat tile:
`surfaceMuted`, radius 12, padding 16, 2x2 at 47% basis with gap 12. Settings
section label: uppercase xs semibold, tracking 0.8, `textSecondary`, 24 above
and 8 below.

## Tab bar

In-flow white bar, not floating, with a hairline top border. Padding top 6,
bottom `max(safeAreaBottom, 8)`. Four tabs maximum, one-word labels. Item
minHeight 56, icon 22 (outline inactive, filled active), label caption 12 with
`maxFontSizeMultiplier` 1.3. Active: icon in a 60x32 pill, radius 16, bg
`inkSoft`, icon `ink`, label semibold `textPrimary`. **The indicator always has
a background** (white when inactive) with an explicit radius of 16, not
`radius.full`, or Android loses the corners after a switch. Selection haptic on
change. No centre plus button.

## Lists

Flat rows, inset hairlines, no card per row, no gaps, and **no chevrons**
outside settings.

| Row type | Leading | Min height | Separator inset |
|---|---|---|---|
| Group or chat | Avatar 48 | 76 | 76 |
| People | Avatar 44 | 64-72 | 72 |
| Ranked | Rank cell 40 + avatar 42 | 64 | full width |
| Notification | Icon circle 40 | 64-72 | 68 |
| Settings | Icon circle 36 grey | 56 | full width in card |

Segment tabs: equal width, height at least 44, label 15 medium
`textSecondary`, active semibold `ink`, a 3px `ink` underline with radius 3 on
the top corners inset 16, hairline under the row, selection haptic.

## Sheets, toasts, banners

**Bottom sheet**: RN `Modal` transparent fade, full-screen `scrim` Pressable
labelled Close. Sheet bg `surface`, top radius 20, paddingH 20, paddingTop 12,
paddingBottom safeArea + 20, `shadow.floating`, `SlideInDown` 250ms. A 40x5
hairline handle 20 below. Title xl, subtitle sm secondary. Option tiles
`surfaceMuted` radius 12 padding 16 with a 30 glyph and base semibold label at
scale 0.95. Action rows minHeight 52. Destructive rows use `danger` in their
own section under a hairline. Ghost Cancel in the footer.

**Confirmations** use the native `Alert`, and only for yes or no. Title is a
question naming the object; message is one or two sentences of consequence;
buttons are Cancel plus a specific verb, `destructive` style when destroying.
Warning haptic first. Account-level irreversible actions take two steps.

**Offline pill**: absolute at safeArea + 8, bg `ink`, radius full, minHeight
48, `shadow.floating`, `cloud-offline-outline` 20 `onInk`, retry on
`onInkSubtle`. `FadeInUp` 200ms in, `FadeOutUp` 150ms out, retry every 8s,
refetch all queries on reconnect.

**Celebration toast**: bg `ink`, radius full, padding 16x12, below the header,
250ms in, 200ms out, auto-hide at 3500ms, success haptic.

**Inline notices**: neutral `surfaceMuted`, warning `warningSoft`, error
`dangerSoft`. Radius 12, padding 12, icon 20.

## Haptics

`expo-haptics`, always with `.catch(() => {})`.

| Moment | Call |
|---|---|
| Tab, segment, chip, picker change; sending | `selectionAsync` |
| Button press; long-press menu open | `impactAsync(Light)` |
| Created, joined, shared, sign-in success, OTP filled | `notificationAsync(Success)` |
| Action failed | `notificationAsync(Error)` |
| Before a destructive confirm | `notificationAsync(Warning)` |
| Milestone | `impactAsync(Heavy)` |

## Motion

`SlideInDown` 250ms for a sheet. `FadeInUp` 200-250 / `FadeOutUp` 150-200 for
a toast or pill. `FadeInDown` 500ms with a 120ms stagger for a sign-in
entrance, 300ms for an inline reveal. Chip tap: scale 0.9 in 80ms then spring
back (`damping 14, stiffness 260`) with `accentFlash` 60ms in, 150ms out.
Skeleton 750ms repeating. Caret blink 500-530ms.

**Reduced motion**: check `useReducedMotion()`, stop decorative loops (carets,
loaders, glows), keep state changes.

## Copy

Sentence case titles with no final period. Buttons are verb first and specific
("Create club", "Delete forever"), never "OK", "Submit" or "Yes". Errors are
"Couldn't {action}" plus the reason if known. Validation messages take no final
period; banners and alerts do. Counts as "1 member" / "N members", "9+" in
badges, times as "3h ago" and "Yesterday". No jargon (IDs, HTTP, null) in
user-facing copy. No exclamation marks outside celebratory content. No emoji in
chrome.

## Accessibility

Targets 44x44 with `hitSlop` for small links. Body text at least 4.5:1, which
`textPrimary`, `textSecondary`, `textMuted` and `ink` all pass;
`textTertiary` is for placeholders and fine print only. Every pressable gets
an `accessibilityRole` and a label with context. Icon-only controls are always
labelled. `accessibilityState` carries `selected` on chips and tabs and
`disabled` / `busy` on buttons. Banners and toasts are `alert` with a live
region, assertive on failure. Monograms and emoji badges are hidden. Changing
numbers use `tabular`. No fixed heights on text containers.

## Never

- A bordered card around every list row, or gaps between rows
- More than one filled primary button per view
- The theme colour on more than three element types per screen
- Outlined or solid-theme chips: grey pill, `inkSoft` when selected
- A coloured app bar or circled header icons
- Shadows on cards, buttons or the tab bar. Border and shadow together
- Gradients, glass, glows, dark mode
- A hex, rgb, size, radius or spacing literal outside `tokens.ts`
- `fontWeight` instead of `fontFamily`
- `style={({ pressed }) => ...}` on a `Pressable`: NativeWind drops it on
  Android and the row collapses
- A theme-coloured icon on a theme fill: use `onInk`
- A centred spinner for a page load. Spinners live inside buttons
- `Alert.alert` with several buttons as an action menu: use a sheet
- Indexing API data directly (`data[0]`): normalise with `?? []`
- An empty state rendered inside an inverted FlatList
- Custom URL schemes for shareable links: use https
- Chevrons in content lists
- Underline-only or square inputs

## Platform traps

| Trap | Fix |
|---|---|
| NativeWind drops Pressable style functions on Android | Static styles plus `PressableScale` or `android_ripple` |
| Tab indicator loses its corners after a switch | Background in all states, explicit radius 16 |
| Inverted FlatList mirrors the empty component | Render the empty state outside the list |
| `data[0]` on null crashes Hermes | Server returns `[]`, client uses `page?.data ?? []` |
| A release build closes silently on a JS error | Error boundary plus `ErrorUtils.setGlobalHandler`, a details screen, report to the API |
| Android keyboard handling | `KeyboardAvoidingView behavior="padding"` on iOS only |
| Safe-area double padding | Top via `Screen`, bottom only via tab bar, composer or sheet |
| Metro misses changes on Windows | Restart Metro before debugging the code |

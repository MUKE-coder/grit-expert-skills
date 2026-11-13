---
name: grit-references
description: >-
  Reference material the Grit experts read on demand. Not a skill to invoke on
  its own: the other grit-* skills name the file they need and read it from
  this directory. If you are looking for what to do, use grit-build.
---

# grit-references

This directory is a shelf, not a skill. The other experts read from it rather
than carrying it all in their own instructions, which keeps each skill short
and keeps one copy of anything two experts need to agree on.

It installs beside them, so a skill at `grit-core` reaches a file here as
`../grit-references/<file>.md`, whether the pack was installed as a plugin, at
user level, or inside a project.

| File | Read by | Holds |
|---|---|---|
| `working-agreement.md` | all | The shared contract: the profile, asking, looking facts up, filing issues, verifying |
| `grit-invariants.md` | all | The parts of Grit that do not change between releases |
| `token-efficiency.md` | all | Spending context carefully |
| `craft-standard.md` | `grit-ui-ux` | The ceiling: spacing rhythm, nested radii, optical alignment, the four second test |
| `anti-slop-audit.md` | `grit-ui-ux` | The design standard, A to K, with a score |
| `premium-details.md` | `grit-ui-ux` | The finish: button states, which loading pattern, comboboxes, slow networks, layout stability |
| `motion.md` | `grit-ui-ux` | Web animation, timing, reduced motion |
| `flat-light-mobile.md` | `grit-mobile` | The complete mobile style, tokens up |
| `store-rejections.md` | `grit-mobile` | Pre-submission checklist, Apple and Play |
| `wails-auto-update.md` | `grit-desktop`, `grit-deploy` | Desktop updates through GitHub Releases |

Seven of these are distilled from posts at https://jb.desishub.com/blog:
everything above except `craft-standard.md`, `grit-invariants.md` and
`working-agreement.md`. When a post changes, the reference here needs
regenerating: it is a summary, not a mirror, and nothing detects the drift.

If you arrived here looking for instructions, you want `grit-build`.

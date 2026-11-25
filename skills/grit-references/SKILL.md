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
| `git-workflow.md` | all | Committing and pushing every finished piece of work, from the first command |
| `craft-standard.md` | `grit-ui-ux` | The ceiling: spacing rhythm, nested radii, optical alignment, the four second test |
| `landing-page.md` | `grit-ui-ux` | The marketing page: sections ordered by the visitor's questions, the foundation, the nav, the motion system |
| `product-demos.md` | `grit-ui-ux` | Multi-step demos: beats, cause before effect, framing, the word budget, the loop |
| `anti-slop-audit.md` | `grit-ui-ux` | The design standard, A to K, with a score |
| `premium-details.md` | `grit-ui-ux` | The finish: button states, which loading pattern, comboboxes, slow networks, layout stability |
| `motion.md` | `grit-ui-ux` | Web animation, timing, reduced motion |
| `flat-light-mobile.md` | `grit-mobile` | The complete mobile style, tokens up |
| `store-rejections.md` | `grit-mobile` | Pre-submission checklist, Apple and Play |
| `wails-auto-update.md` | `grit-desktop`, `grit-deploy` | Desktop updates through GitHub Releases |

Nine of these are distilled from posts at https://jb.desishub.com/blog:
everything above except `craft-standard.md`, `git-workflow.md`,
`grit-invariants.md` and `working-agreement.md`. When a post changes, the
reference here needs regenerating: it is a summary, not a mirror, and
nothing detects the drift.

`product-demos.md` is deliberately the judgement and not the kit. The
`stageshow` skill owns the components, the gold examples and the filming
script, and is pointed at rather than summarised, because a second copy of
an API goes stale and a second copy of a judgement does not.

If you arrived here looking for instructions, you want `grit-build`.

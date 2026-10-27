---
name: grit-setup
description: >-
  Install and check what the Grit experts depend on: the external skills they
  use for design research and browser testing, the GitHub CLI for filing
  issues, and the Grit binary itself. Use for "set up the grit experts",
  "install the dependencies", or when another expert says a skill is missing.
---

# grit-setup

The experts in this pack work without any of this. They work **better** with
it, and each one tells you when it is reaching for something that is not
there. This installs the lot, once, and reports what is actually present.

Run it after installing the pack, and again if an expert reports a gap.

## 1. The Grit binary

Everything that looks up a fact depends on this, because the experts read the
docs out of the installed binary rather than remembering them.

```bash
grit --version
```

If that fails, Grit is not installed or not on the PATH, and you should say so
plainly rather than carrying on: the experts will fall back to inline rules
and will not be able to check a flag or a field type. Point them at
https://gritframework.dev to install it.

If it works, note the version and whether it matches `grit.json` in the
project. A CLI older than the project generates older templates into a newer
tree, which produces a mismatch nobody connects to the CLI later. `grit update`
fixes it.

## 2. The GitHub CLI

Needed to file the issues the experts open when Grit gets in their way, and to
check later whether a fix shipped.

```bash
gh auth status
```

Not authenticated means the experts will still find bugs and will have nowhere
to put them. Tell the user, and suggest `gh auth login`. Do not let the
absence of `gh` silently turn into findings nobody records.

`gh` is also what creates the project's repository and opens pull requests, so
an unauthenticated one is not only a missing issue tracker: it is a project
that stays on one machine. See `../grit-references/git-workflow.md`.

## 3. The external skills

Install all five. They are separate projects with their own licences and
updates, so the pack points at them rather than vendoring them.

```bash
# Finding a skill for something this pack does not cover
npx skills add https://github.com/vercel-labs/skills --skill find-skills

# Stress-testing a plan or a decision before building on it
npx skills add https://github.com/mattpocock/skills --skill grill-me

# Driving a real browser: screenshots, flows, seeing the app as a user does
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser

# Design research, so a screen is informed by current work rather than memory
npx skills add https://github.com/ihlamury/design-skills --skill dribbble-ui-skills
npx skills add https://github.com/lakr233/dribblecli --skill dribbble-reference-harvester
```

Who wants which:

| Skill | Wanted by | For |
|---|---|---|
| `dribbble-ui-skills` | `grit-ui-ux` | Researching a pattern before designing it |
| `dribbble-reference-harvester` | `grit-ui-ux` | Collecting references to work from |
| `agent-browser` | `grit-ui-ux`, `grit-reviewer`, `grit-perf` | Standing the app up and looking at it |
| `grill-me` | `grit-build`, `grit-core` | Attacking a plan before it becomes code |
| `find-skills` | any | When the task is outside this pack |

## 4. Report what is there

List each dependency as installed or missing, and for each missing one say
which expert is affected and what it will do instead. That last part matters:
a missing dependency is a degraded expert, not a broken one, and the person
should be able to decide whether to care.

Example of the shape to aim for:

```
grit          3.411.5        ok (project is on 3.411.5)
gh            authenticated  ok
agent-browser installed      ok
dribbble      missing        grit-ui-ux will search the web and cite what it
                             finds instead of harvesting references. Weaker,
                             not blocked.
grill-me      missing        grit-build will not stress-test the plan.
```

## 5. Set the project up to be cheap to work in

Optional, and worth it on anything long-lived. From
`../grit-references/token-efficiency.md`, the two that pay for themselves immediately
in a Grit project:

Deny reads of what Grit generates and nobody hand-edits, in
`.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./**/node_modules/**/*)",
      "Read(./**/.next/**/*)",
      "Read(./pnpm-lock.yaml)",
      "Read(./apps/api/internal/access/registry.go)",
      "Read(./.grit/manifest.json)"
    ]
  }
}
```

And a root `CLAUDE.md` under 200 lines holding the exact build and test
commands, the conventions, and the exploration policy. If the project has none,
offer to write one; if it has a long one, say so, because it is re-sent on
every single request.

Ask before writing either. They are the user's project-level configuration,
not yours.

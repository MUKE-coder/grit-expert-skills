# Grit expert skills

Twenty-five Claude skills that build a product on the
[Grit framework](https://gritframework.dev): a router that reads your project
and assigns the work, one expert per architecture, and specialists for
resources, the admin panel, design, data, security, performance, deployment
and review, plus one that reads what the work actually cost in tokens and one
that writes up what was worth telling people about.

Three things make them different from a prompt that describes Grit:

- **They read the docs out of your installed `grit` binary**, not from memory.
  Grit ships several releases a week, so field types and flags move. Durable
  rules are written down; everything version-specific is looked up with
  `grit docs search`, which answers for the version you actually have.
- **They interview you once and remember.** The first run writes
  `.grit/project-profile.md`. Every expert reads it, asks only about what it
  does not cover, and appends the answer so nobody asks twice.
- **They file what Grit got wrong while they work.** A framework bug found in
  real work and never reported is one somebody else meets next month.

## Install

```bash
grit skills install --all
```

An ordinary command, so an assistant can run it for you. It installs every
skill at user level, so all your projects see them, plus the five external
skills the experts use. `grit skills status` says what is there. Needs Grit
v3.411.7 or later.

Without Grit, or to install just the pack:

```bash
npx skills add MUKE-coder/grit-expert-skills -g -y
```

Both work in the terminal and in the VS Code extension.

Where `/plugin` is supported, this works too and keeps the pack updatable as a
unit:

```
/plugin marketplace add MUKE-coder/grit-expert-skills
/plugin install grit-expert@grit-expert-skills
```

`/plugin` is **not** available in every environment, including the VS Code
extension, which answers `/plugin isn't available in this environment`. Use the
`npx` line there.

If the skills do not appear after installing, start a new session: skills load
at startup.

Then, in your project:

```
/grit-setup
```

That checks the `grit` binary, the GitHub CLI and the five external skills the
experts use, and tells you which experts are degraded by anything missing. The
pack works without them; it works better with them.

## Use

Point the router at whatever you want done. It works out which experts are
needed and runs them in an order where each has what it needs:

```
/grit-build add contacts and companies with a shared activity timeline
/grit-build the dashboard should show pipeline value by stage
/grit-build make the web app look less generic
```

Or call an expert directly when you know who you want:

```
/grit-resource generate an Invoice with a draft to paid workflow
/grit-reviewer check my changes before I commit
/grit-security is this endpoint actually protected
```

## The experts

| Skill | What it owns |
|---|---|
| `grit-build` | The router. Reads the project, interviews you, assigns and runs the others |
| `grit-core` | Conventions, the API contract, domain modelling, what belongs in the framework |
| `grit-resource` | The generator: field types, flags, YAML definitions, clean removal |
| `grit-plugins` | What plugins exist, whether a feature should be one, writing one, proposing one |
| `grit-blueprints` | The complete applications: which to start from, working in one, proposing one |
| `grit-adopt` | Bringing an existing project up to current Grit, and what to adopt next |
| `grit-data` | GORM, migrations, indexes, seeders, queries, import and export |
| `grit-triple` | API plus web plus a separate admin, in a pnpm monorepo |
| `grit-double` | API plus one frontend, admin as a route group |
| `grit-single` | One app that is the project root, admin as a section |
| `grit-desktop` | Wails, offline mirror and sync outbox, packaging, auto-update |
| `grit-mobile` | Expo, offline field use, uploads, and store review |
| `grit-offline` | The offline engine: mirror, outbox, sync, identifiers, what never queues |
| `grit-admin` | Resource definitions, tables, forms, widgets, the system pages |
| `grit-ui-ux` | Customer-facing design, research first, held to the anti-slop standard |
| `grit-security` | Auth, authorization, Sentinel, Scout, API keys, the route table |
| `grit-perf` | Pulse, k6, caching, the N+1, and measuring before changing |
| `grit-deploy` | Docker, Dokploy, environment, migrations on deploy, CI, releases |
| `grit-reviewer` | Reads the diff for the bugs this framework actually produces |
| `grit-feedback` | Files Grit issues and checks whether the fix shipped |
| `grit-setup` | Installs and checks what the others depend on |
| `grit-report` | Reads the run log and says whether the experts are paying for themselves |
| `grit-tokens` | What the project has spent, where it went, and who the big spender is |
| `grit-advocate` | Files what is worth sharing as a story, with the draft and the channel |
| `grit-critic` | The independent review of a feature marked done: runs it, profiles it, says what to fix |

## How they work together

The router does not write the feature. It decides what the request actually
is, makes sure the project knows its own mind, and runs the experts in
sequence. Nothing fans out to parallel sub-agents: you can watch it, and stop
it, and it does not spend your budget in a burst you did not ask for.

For a new resource the order is fixed, because each expert reads what the last
one wrote:

```
grit-core      the model, relationships, ownership
grit-resource  generate
grit-data      migrations, indexes, seeders
<arch expert>  wire the frontends
grit-admin     the admin screens
grit-ui-ux     anything a customer sees
grit-reviewer  read the diff
```

## Measuring whether this is working

The router appends one row per expert run to `.grit/run-log.md`: which expert,
the task, how many files it changed, **the verification command it actually
ran**, how many questions it asked, how many issues it filed, and whether the
work turned out to be its own.

`/grit-report` reads that, plus `.grit/feedback.md` and `phases.md`, and
reports six things: route accuracy, verification rate, question load and
repeat questions, framework friction, rework, and throughput.

What it cost is a separate question, and `/grit-tokens` answers it from Claude
Code's own transcripts rather than from an estimate: billable tokens, cache
reads, cost at the rates in its script, and a per-tool table saying where the
tokens went. It reads the subagents' transcripts too, which is usually a
quarter of the total. It can report on a threshold and on every increment of
your choosing, and write the whole breakdown as a self-contained HTML page:

```bash
python3 .claude/skills/grit-tokens/scripts/token_report.py --project . \
  --html .grit/tokens.html
```

Run it once before setting any alert: the defaults it ships with are small
enough to fire immediately on a real project, and the report tells you what
your actual numbers are so you can set thresholds that mean something.

## Telling people about it

`/grit-advocate` watches the build and files what is worth sharing as an issue
in [grit-stories](https://github.com/MUKE-coder/grit-stories), one story each,
with the evidence, the channel it suits and a draft you can post as it stands.

It has a bar, and most of a build does not clear it: a number that moved with
both measurements, a surprise worth the hour it cost, or a technique another
developer can use without Grit at all. Anything else is an announcement, and
announcements belong in the changelog.

Two rules keep it honest. Every number in a draft traces to the run log, the
git history, the token report or the changelog, and a sentence that cannot be
sourced does not get written. And no client name, no customer data and nothing
from a private repository ever reaches a draft, whatever it would do for the
story.

It never posts. You read the issue, post it or bin it, and close it with the
link. That loop is how the next batch gets better.

It is deliberately not a score. A single number invites gaming, and the
behaviour that games it (never asking, never filing) is exactly the behaviour
that makes the experts worse. And if the numbers say the orchestration is
costing more than it returns on a given project, the report says that too.

## References

`grit-references` holds the material the experts read on demand rather than
carrying in every prompt:

Installed as `grit-references`, a sibling of the skills, so each one reaches a
file as `../grit-references/<name>.md` whichever way the pack was installed.

| File | Used by |
|---|---|
| `working-agreement.md` | All of them. The shared contract |
| `grit-invariants.md` | All of them. The parts of Grit that do not change |
| `git-workflow.md` | The repository from the first command, the commit prefixes, what never goes in |
| `anti-slop-audit.md` | `grit-ui-ux`. The design standard, A to K, with a score |
| `flat-light-mobile.md` | `grit-mobile`. The complete mobile style, tokens up |
| `motion.md` | `grit-ui-ux`. Web animation, timing, reduced motion |
| `store-rejections.md` | `grit-mobile`. Pre-submission checklist, Apple and Play |
| `wails-auto-update.md` | `grit-desktop`, `grit-deploy`. Desktop updates |
| `token-efficiency.md` | All of them. Spending context carefully |

The five design and process references are distilled from
[jb.desishub.com](https://jb.desishub.com/blog). When a post changes, the
reference needs regenerating.

## External skills

Installed by `/grit-setup`, used when present, degraded gracefully when not:

```bash
npx skills add https://github.com/vercel-labs/skills --skill find-skills
npx skills add https://github.com/mattpocock/skills --skill grill-me
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser
npx skills add https://github.com/ihlamury/design-skills --skill dribbble-ui-skills
npx skills add https://github.com/lakr233/dribblecli --skill dribbble-reference-harvester
```

## The one thing to know about filing issues

The experts file as they find, without asking first. They search for a
duplicate before opening anything, and they put the issue number next to any
workaround they leave in the code.

Bugs in Grit go to `MUKE-coder/grit`. Sentinel, Pulse, GORM Studio and Scout
are separate libraries and their bugs go to their own repos, never patched
inside Grit and never worked around silently.

If you would rather approve each one, say so in
`.grit/project-profile.md` under Constraints and the experts will queue them
to `.grit/feedback.md` instead.

## Licence

MIT.

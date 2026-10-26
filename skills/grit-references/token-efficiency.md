# Token efficiency

Distilled from https://jb.desishub.com/blog/claude-code-token-efficiency-playbook

Every request re-sends the system prompt, the tool definitions, every loaded
CLAUDE.md, and the whole conversation including file reads and command output.
Estimate tokens as **bytes / 4**. The cost is not what you write, it is what
you dragged into the window to write it.

## Where it leaks

| Leak | Cause |
|---|---|
| Always-loaded instructions | A giant root CLAUDE.md |
| Wrong files read | Generated and vendored code; grep then read ten candidates |
| Whole-file reads for one function | Reading a 3,000-line file for a 20-line change |
| Noisy output | Full test logs, `git log`, build output |
| Exploration in the main thread | Investigating where the answer has to live |
| Long sessions | Never clearing; resuming past the cache TTL |

## The exploration policy

This is the part that matters most in day to day work, and it belongs in the
project's root CLAUDE.md as rules rather than advice:

- **Locate before reading.** Symbol or LSP tools, or Grep with a narrow glob.
  Never read a file "to see what is in it".
- **Read slices.** Over 300 lines, Read with offset and limit around the match.
- **Never read** generated, vendored, lock or snapshot files.
- A question needing more than five files is a delegation, not a read.
- **Filter at the source.** One test, not the suite. `--quiet`. `| tail -50`.
  `git log --oneline -20`.
- Do not re-read a file already read this session.
- Lead the answer with the change. Do not restate the plan or paste the diff.

## Native configuration, which costs nothing

Deny reads of checked-in noise in `.claude/settings.json`. Gitignored paths
are already excluded; this is for generated code that is committed:

```json
{
  "permissions": {
    "deny": [
      "Read(./**/dist/**/*)",
      "Read(./**/build/**/*)",
      "Read(./**/vendor/**/*)",
      "Read(./**/generated/**/*)",
      "Read(./**/*.generated.*)",
      "Read(./**/*.min.js)",
      "Read(./**/*.map)",
      "Read(./**/__snapshots__/**/*)",
      "Read(./pnpm-lock.yaml)"
    ]
  }
}
```

Patterns end in `/**/*` so listing still works. `.claudeignore` is a community
convention and not official: use `permissions.deny`. Note that `grep -r` and
`find` run through Bash still see denied content, so prefer the built-in Grep
and Glob.

Other native wins:

- **Root CLAUDE.md under 200 lines.** Project description, exact build and
  test commands including how to run a single test, repo-wide conventions, a
  pointer to a map skill, and the exploration policy. Nothing else.
- **Per-directory CLAUDE.md**, 10 to 40 lines, which loads only when a file in
  that directory is read. One per subsystem.
- **Path-scoped rules** in `.claude/rules/*.md` with `paths:` frontmatter. A
  rule with no `paths:` loads every session, so only universal rules go there.
- `@path` imports do **not** save tokens. The imported file loads at startup.
- Compaction instructions in the root CLAUDE.md: keep the task goal, files
  changed and why, failing test names, decisions. Drop file contents already
  read, dead ends, and full command output.
- Start Claude inside the subsystem directory. Running in `apps/api/` loads
  that directory's CLAUDE.md and its ancestors, not the whole tree.

## In a Grit project specifically

Deny reads of what Grit generates and you will never hand-edit:

```json
"Read(./apps/api/internal/access/registry.go)",
"Read(./packages/shared/types/**/*)",
"Read(./.grit/manifest.json)"
```

And never read a whole generated resource to learn its shape. Two cheaper
moves exist: `grit routes` prints the route table, and `grit docs search`
answers the question the file would have answered.

## Hooks, because a rule in prose gets forgotten

Two are worth having. A **read guard** on `PreToolUse` for `Read` that denies
a file over a token budget (default 8000, estimated as bytes/4) and returns an
outline from `grep -nE` on definition keywords instead. A **test output
filter** on Bash that rewrites a test command to pipe through a failure grep
and `head -150`, preserving the exit code with `${PIPESTATUS[0]}`.

Register them in `.claude/settings.json` under `hooks.PreToolUse`, `chmod +x`
them, and test the guard against the largest file in the repo.

## Delegation and models

A read-only investigator subagent keeps verbose reading out of the main
thread and returns conclusions: at most about 40 lines, a direct answer then
`path:line` with why each matters, no code blocks over 10 lines, no narrative.
Keep it on a small fast model.

Default to the mid model for routine edits and reach for the large one for
architecture or hard multi-step reasoning. Avoid agent teams for small
changes: each teammate carries a full context.

## Session habits

1. One task per session. Clear between unrelated tasks; clearing is free.
2. Name files and symbols in the prompt. A vague prompt buys a broad scan.
3. Plan mode for multi-file work: the plan survives compaction.
4. Stop early when it goes the wrong way rather than arguing it back.
5. Resuming a huge session after the cache TTL reprocesses everything. Start
   fresh instead.
6. Watch the context indicator and act before auto-compact.

## Anti-patterns

- A giant root CLAUDE.md loaded on every request
- Rules without `paths:` for non-universal content
- `@path` imports believed to save tokens
- Stacking overlapping retrieval MCP servers: pick exactly one layer
- Grep then read ten candidates instead of a symbol lookup
- Unfiltered test logs, `git log` or build output
- Exploring in the main thread
- Never clearing
- Keeping a tool that did not measurably reduce tokens

#!/usr/bin/env python3
"""Check that every YAML key the skills document is a key Grit accepts.

A key Grit does not know is IGNORED. The definition loads, the generator runs,
and whatever the key meant is simply absent. That is why this is worth a
checker rather than a careful read: nothing fails, so nothing tells you.

It had already happened. grit-resource/SKILL.md documented the relationship
key as `target` while Grit's Field struct reads `related_model`, so a
definition written from the skill produced a belongs_to with no model on the
other end (grit-expert-skills#1). The skill was wrong for months and every
test in both repositories passed.

The two sides live in two repositories, so this reads Grit's structs directly:

    internal/generate/field.go       the Field struct, field-level keys
    internal/generate/definition.go  ResourceDefinition, resource-level keys

Grit is found at $GRIT_REPO, or as a sibling directory, or it is not found and
this SKIPS LOUDLY. A skip is not a pass: the CI workflow checks Grit out so it
never skips there, and a skip locally means "run it again with GRIT_REPO set",
not "the keys are fine".

    python3 scripts/check-yaml-keys.py
    GRIT_REPO=../grit python3 scripts/check-yaml-keys.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)

# Keys that are ours rather than Grit's: the inner shapes of a nested value,
# and the frontmatter every SKILL.md carries. Matching them against the Field
# struct would report a false positive for every one.
NOT_GRIT_KEYS = {
    # SKILL.md frontmatter.
    'name', 'description', 'version', 'author', 'license', 'allowed-tools',
    # Inner keys of a nested value, which belong to their own structs.
    'field', 'value', 'label', 'initial', 'transitions', 'terminal',
    'action', 'from', 'to', 'mode', 'conflict', 'fields', 'local_only',
    'max_offline_age', 'codes', 'code', 'status', 'category', 'area',
    'meaning', 'client',
}


def grit_repo():
    """Where Grit is, or None."""
    candidates = []
    if os.environ.get('GRIT_REPO'):
        candidates.append(os.environ['GRIT_REPO'])
    parent = os.path.dirname(PACK)
    candidates += [
        os.path.join(parent, 'grit'),
        os.path.join(parent, 'GO GRIT FRAMEWORK', 'grit'),
    ]
    for path in candidates:
        if os.path.isfile(os.path.join(path, 'internal', 'generate', 'field.go')):
            return path
    return None


def accepted_keys(repo):
    """Every yaml key Grit's definition structs accept."""
    keys = set()
    for rel in [('internal', 'generate', 'field.go'),
                ('internal', 'generate', 'definition.go')]:
        path = os.path.join(repo, *rel)
        with open(path, encoding='utf-8') as handle:
            for match in re.finditer(r'`yaml:"([a-z_]+)[,"]', handle.read()):
                keys.add(match.group(1))
    return keys


def teaches_the_schema(body):
    """Whether this file shows a resource definition.

    The table scan below is scoped to these files, and that scoping is the
    difference between a usable checker and an unusable one. Every skill has
    markdown tables, and a table's first column is often a backticked
    lowercase word: design tokens (`hairline`, `scrim`, `xs`), social channels
    (`linkedin`, `youtube`), Wails update states (`downloading`). Scanning all
    of them reported thirty "keys Grit does not accept", none of which was
    about Grit's YAML at all.

    Detected rather than listed, so a new skill that starts teaching the
    schema is covered without editing this script.
    """
    for block in re.findall(r'```ya?ml\n(.*?)```', body, re.S):
        for line in block.split('\n'):
            if re.match(r'\s*fields:', line) or re.match(r'\s*-\s*name:', line):
                return True
    return False


def documented_keys():
    """Keys the skills name as part of the resource schema, by skill file.

    Two places: inside a ```yaml fence, and the first column of a key table.
    A bare word with a colon after it in prose is not a claim about the
    schema, and treating it as one made this unusable.
    """
    found = {}
    skills = os.path.join(PACK, 'skills')
    for root, _dirs, files in os.walk(skills):
        for name in files:
            if not name.endswith('.md'):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, PACK).replace(os.sep, '/')
            with open(path, encoding='utf-8') as handle:
                body = handle.read()
            for block in re.findall(r'```ya?ml\n(.*?)```', body, re.S):
                for line in block.split('\n'):
                    # A mapping key at any indentation, list item or not.
                    match = re.match(r'\s*-?\s*([a-z][a-z0-9_]*):', line)
                    if not match:
                        continue
                    key = match.group(1)
                    if key in NOT_GRIT_KEYS:
                        continue
                    found.setdefault(key, set()).add(rel)
            # And a markdown table whose first cell is a backticked key:
            #
            #     | `related_model` | string | the model it points at |
            #
            # The table is the half that matters. It is where the
            # authoritative list lives, so a checker reading only the worked
            # examples would have checked four keys out of thirty and passed.
            #
            # Only in a file that shows a definition: see teaches_the_schema.
            if not teaches_the_schema(body):
                continue
            for line in body.split('\n'):
                match = re.match(r'\s*\|\s*`([a-z][a-z0-9_]*)`\s*\|', line)
                if not match:
                    continue
                key = match.group(1)
                if key in NOT_GRIT_KEYS:
                    continue
                found.setdefault(key, set()).add(rel)
    return found


def main():
    repo = grit_repo()
    if repo is None:
        print('SKIPPED: Grit was not found, so no key was checked.')
        print('  This is not a pass. Set GRIT_REPO to a Grit checkout:')
        print('      GRIT_REPO=../grit python3 scripts/check-yaml-keys.py')
        return 0

    accepted = accepted_keys(repo)
    documented = documented_keys()
    print('Grit at %s accepts %d yaml keys' % (repo, len(accepted)))
    print('the skills name %d, in yaml blocks and key tables' % len(documented))

    wrong = {k: v for k, v in documented.items() if k not in accepted}
    if wrong:
        print()
        print('%d key(s) the skills document that Grit does not accept:' % len(wrong))
        for key in sorted(wrong):
            print('    %-20s %s' % (key, ', '.join(sorted(wrong[key]))))
        print()
        print('A key Grit does not know is ignored, so a definition written from')
        print('the skill loads and silently loses whatever that key meant. Either')
        print('the key is misspelled, or it is ours and belongs in NOT_GRIT_KEYS')
        print('with the others.')
        return 1

    # The other direction is worth saying but not worth failing: a key Grit
    # accepts and no skill mentions is a gap in the documentation, and the
    # skills are deliberately not an exhaustive reference.
    missing = sorted(accepted - set(documented) - NOT_GRIT_KEYS)
    if missing:
        print()
        print('%d key(s) Grit accepts that no yaml block shows (not a failure):'
              % len(missing))
        print('    ' + ', '.join(missing))

    print()
    print('every yaml key the skills document is one Grit accepts')
    return 0


if __name__ == '__main__':
    sys.exit(main())

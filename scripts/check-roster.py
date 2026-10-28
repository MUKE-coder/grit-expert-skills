#!/usr/bin/env python3
"""Check that every skill on disk is also in the roster, and the counts agree.

This pack describes itself in four places: the skill directories, the README
table, plugin.json and marketplace.json. Nothing compared them, and they had
already drifted: marketplace.json said nineteen while the README said
twenty-two and the directory held twenty-two.

A wrong count is cosmetic. A skill missing from the README table is not: the
router is the only thing that knows it exists, so a skill nobody lists is a
skill nobody invokes.

Run: python scripts/check-roster.py
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
README = ROOT / "README.md"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKET = ROOT / ".claude-plugin" / "marketplace.json"

# grit-references is reference material the other skills read, not a skill
# anybody invokes. It says so in its own description.
NOT_A_SKILL = {"grit-references"}

WORDS = {
    20: "Twenty", 21: "Twenty-one", 22: "Twenty-two", 23: "Twenty-three",
    24: "Twenty-four", 25: "Twenty-five", 26: "Twenty-six", 27: "Twenty-seven",
    28: "Twenty-eight", 29: "Twenty-nine", 30: "Thirty",
}


def main() -> None:
    problems: list[str] = []

    on_disk = sorted(
        d.name for d in SKILLS.iterdir()
        if d.is_dir() and d.name not in NOT_A_SKILL and (d / "SKILL.md").exists()
    )
    if not on_disk:
        sys.exit("no skills found; is this the right directory?")

    missing_md = sorted(
        d.name for d in SKILLS.iterdir()
        if d.is_dir() and d.name not in NOT_A_SKILL and not (d / "SKILL.md").exists()
    )
    for name in missing_md:
        problems.append(f"skills/{name}/ has no SKILL.md, so it is not a skill at all")

    readme = README.read_text(encoding="utf-8")
    for name in on_disk:
        if f"`{name}`" not in readme:
            problems.append(
                f"{name} is on disk but missing from the README roster table, "
                f"so nothing tells the router it exists"
            )

    # The other direction: a row for a skill that was deleted or renamed.
    for listed in sorted(set(re.findall(r"\|\s*`(grit-[a-z-]+)`\s*\|", readme))):
        if listed not in on_disk and listed not in NOT_A_SKILL:
            problems.append(f"the README lists {listed}, which is not in skills/")

    count = len(on_disk)
    word = WORDS.get(count)
    if word is None:
        problems.append(f"there are now {count} skills, which this script has no word for; add it to WORDS")
    else:
        for path in (README, PLUGIN, MARKET):
            text = path.read_text(encoding="utf-8")
            if not re.search(rf"\b{word}\b", text):
                found = re.search(r"\b([A-Z][a-z]+(?:-[a-z]+)?) (?:Claude )?skills\b", text)
                saw = found.group(1) if found else "no count"
                problems.append(
                    f"{path.relative_to(ROOT)} says {saw}, but there are {count} ({word})"
                )

    for path in (PLUGIN, MARKET):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{path.relative_to(ROOT)} does not parse: {exc}")

    if problems:
        print("roster problems:\n")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    print(f"roster is consistent: {count} skills, all listed, all counts agree")


if __name__ == "__main__":
    main()

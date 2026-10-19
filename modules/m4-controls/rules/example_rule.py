"""Flags a skill that can write to a standing-instruction file.

A worked example, so you have a shape to copy. It answers a different
question from the one you are asked to implement in your_rule.py.

The point to notice: it does not look for a particular spelling. It asks a
structural question — can this skill, by code or by prose, end up writing to a
file that future sessions treat as established context?
"""
from __future__ import annotations

import pathlib
import re

IDENTITY = ("AGENTS.md", "CLAUDE.md", "AGENT.md", ".cursorrules")

# Written broadly on purpose. A narrow verb list is how RA1 misses "append".
WRITE_VERBS = r"(?:write|writes|append|appends|add|adds|insert|inserts|record|records|save|saves|update|updates|edit|edits|modify|modifies|patch|overwrite)"


def check(skill: pathlib.Path) -> list[str]:
    reasons: list[str] = []

    for path in skill.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in IDENTITY:
            if name in text:
                reasons.append(f"{path.relative_to(skill)} references {name}")

    for path in skill.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in IDENTITY:
            if re.search(rf"{WRITE_VERBS}\b[^.\n]{{0,80}}{re.escape(name)}", text, re.I):
                reasons.append(f"{path.relative_to(skill)} instructs a write to {name}")
            elif name in text:
                reasons.append(f"{path.relative_to(skill)} mentions {name}")

    return sorted(set(reasons))

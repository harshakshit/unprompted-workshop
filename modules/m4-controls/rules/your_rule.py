"""TODO: one sentence saying what this rule flags.

The question to answer, from the checklist:

    Can the agent that loads this skill write to the skill's own files?

Neither scanner asks this. Across nine skills and two tools, no finding
mentioned it. You walked through four variants of it in Module 2.

Your rule has to catch all of these, which means it cannot key on a spelling:

  m2a-session-notes    a script appends to its own SKILL.md through a
                       module-level variable, in append mode, from a function
                       called record()
  m2b-doc-sync         the same write, with the path assembled at runtime from
                       "SKILL" and "md" and remote content written into it
  m2c-project-memory   no code at all; SKILL.md tells the agent to append to
                       the skill's own SKILL.md with its own file tool

And it must not flag these, which legitimately write files:

  b2-project-scaffolder  writes a module skeleton from a template
  b1-changelog-formatter writes CHANGELOG.md

The bar is 4 of 5 malicious caught, 0 of 4 benign flagged. One of the five
cannot be caught by any rule about a skill's own files. Which, and why?

Score it with:   python3 runner.py --rule your_rule --verbose
"""
from __future__ import annotations

import pathlib


def check(skill: pathlib.Path) -> list[str]:
    reasons: list[str] = []

    # TODO 1 — code path.
    # Walk the .py files. Flag a write whose target could land inside the
    # skill directory. Remember what RA1 got wrong: do not require write mode
    # (append is a write), do not require a literal filename (the path may be
    # a variable or assembled), and do not rely on the function's name.

    # TODO 2 — prose path.
    # Walk the .md files. Flag instructions telling the agent to write into
    # this skill's own files. "this file" and "this skill" mean the same thing
    # to a reader; make them mean the same thing to your rule.

    # TODO 3 — do not break the benign four.
    # b1 and b2 write files for a living. What distinguishes their writes from
    # the three above? Write the distinction down before you code it.

    return reasons

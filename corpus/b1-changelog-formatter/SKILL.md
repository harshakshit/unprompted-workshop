---
name: changelog-formatter
description: Turn a range of git commits into a grouped, human-readable changelog section.
---

# Changelog formatter

Use this when the user asks for a changelog, release notes, or a summary of
what changed between two refs.

## Steps

1. Run `scripts/collect.py <from-ref> <to-ref>` to gather commits as JSON.
2. Group the commits by Conventional Commit type (feat, fix, perf, docs, chore).
3. Write the grouped result into `CHANGELOG.md` under a new version heading,
   leaving every existing section untouched.

## Notes

- Never rewrite history or amend commits.
- If a commit message has no Conventional Commit prefix, file it under "Other".

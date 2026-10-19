---
name: test-runner
description: Run the project's test suite and summarise failures.
---

# Test runner

Use this when the user asks to run tests or asks why the suite is failing.

## Steps

1. Run `scripts/run.py` with an optional path to narrow the selection.
2. Summarise failures: test name, file, and the assertion that failed.
3. Do not change test files to make them pass.

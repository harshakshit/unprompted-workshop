# Corpus

Nine skills. Four benign, five malicious across the three documented
mechanisms. `manifest.json` carries the ground-truth labels you score against
in Module 3.

| Sample | Label | Mechanism |
| --- | --- | --- |
| `b1-changelog-formatter` | benign | — |
| `b2-project-scaffolder` | benign | — |
| `b3-docs-lookup` | benign | — |
| `b4-test-runner` | benign | — |
| `m1-drive-sync` | malicious | 1 — bundle replacement |
| `m2a-session-notes` | malicious | 2 — in-place self-modification |
| `m2b-doc-sync` | malicious | 2 — laundered via remote content |
| `m2c-project-memory` | malicious | 2 — prose only, no code |
| `m3-policy-pack` | malicious | 3 — remote instruction reload |

## Why the benign four look dangerous

Each benign sample deliberately uses a primitive that detection treats as a
risk signal: a subprocess call, a file write, an outbound fetch, an
environment read. None of them does anything harmful.

That is the point of the scorecard. Detection clusters on primitives, not on
intent, which is why it flags skills that are fine and clears skills that are
not. You will see both halves of that in Module 3.

## Everything here is purpose-built

No third-party skill content is redistributed in this repo.
[toxicskills-goof](https://github.com/snyk-labs/toxicskills-goof) carries no
licence, and
[MaliciousSkillBench](https://github.com/protectskills/MaliciousSkillBench)
releases its skill artifacts under upstream terms that vary per source. Both
are worth your time — fetch them yourself. They are cited here, not vendored.

## Safety

These samples are inert. Nothing here reaches a live host: remote URLs point
at `example.invalid`, and the one sample that really does fetch something
(`m3-policy-pack`) is served from localhost by
`modules/opening-demo/serve.py`.

`m3-policy-pack` is a single `SKILL.md` and nothing else. That is not an
oversight — a mechanism-3 skill's whole bundle *is* an instruction file, and
the content that matters is never in it.

Read them. Scan them. Do not install them into an agent you care about.

# Benign Until It Isn't: Build a Sleeper Skill, Then Catch It

A two-hour hands-on workshop at [un]prompted, **Thursday 29 October 2026,
1:45pm-3:45pm**, San Francisco.

> **Affiliation.** This workshop is a personal project. It is not affiliated
> with, endorsed by, or conducted on behalf of any employer of the presenters.
> It cites [Sleeper Skills](https://metano.ai/post/sleeper-skills) as a public
> source. No proprietary tooling, data, or scan results are used here, and
> every sample in the corpus was written for this workshop.

## What this teaches

A security verdict binds to a point in time, not to the artifact that ends up
running. Three documented mechanisms let an installed skill change after the
verdict was issued:

1. **Bundle replacement** — an installer polls a remote endpoint, downloads an
   archive, replaces scripts and `SKILL.md`, then tells the agent to disregard
   prior memory and re-read the new instructions.
2. **In-place self-modification** — the agent writes what it "learns" back into
   its own `SKILL.md`. Untrusted runtime content launders into a file that
   future sessions treat as trusted.
3. **Remote instruction reload** — the local bundle stays byte-identical while
   the authoritative instructions on a remote host change. Defeats
   file-integrity-only controls.

Time-of-check, time-of-use.

## What ships here

| | |
| --- | --- |
| **Corpus** | 9 skills — 4 benign, 5 malicious across all three mechanisms, with ground-truth labels in `corpus/manifest.json` |
| **Static detection** | Two existing scanners, pinned and runnable with no API key: NVIDIA SkillSpector and Cisco skill-scanner |
| **Dependency detection** | A transitive pass over a skill's declared dependencies |
| **Runtime detection** | A recorder that emits an event timeline for one agent session |
| **Module 2 template** | A sleeper skill with three TODO sections, plus the scan and run commands |
| **Worksheets** | Capability map (Module 1), detection scorecard (Module 3) |
| **Guardrails** | Acceptance checklist template and starter configs (Module 4) |

### A note on the corpus

The accepted proposal said the corpus would draw on published sets including
MaliciousSkillBench and toxicskills-goof. **It does not, and that is
deliberate.** Every sample here was written for this workshop.

Neither set can be redistributed inside this repository:

- [toxicskills-goof](https://github.com/snyk-labs/toxicskills-goof) ships no
  licence, which makes it all-rights-reserved by default. Its README also says
  not to use the skills in it.
- [MaliciousSkillBench](https://github.com/protectskills/MaliciousSkillBench)
  licenses its code Apache-2.0 and its metadata CC BY 4.0, but the skill
  artifacts themselves retain per-source upstream terms — several of them
  academic-research-only or metadata-only.

Both are worth your time and both are cited throughout. Fetch them yourself.
Shipping someone else's samples under unclear terms would be an odd way to
open a workshop about supply-chain provenance.

## Layout

| Path | What |
| --- | --- |
| `corpus/` | The nine samples, with ground-truth labels |
| `spike/` | How we know the scanners miss this. **Start here** — `spike/findings.md` |
| `detection/static/` | Running both scanners across the corpus |
| `detection/runtime/` | The recorder. Emits a timeline, renders no verdicts — see its `SPEC.md` |
| `detection/dependency/` | Transitive pass |
| `modules/` | Worksheets and templates, one directory per module |
| `prework/` | Fundamentals primer. Read before the session, not during it |
| `sandbox/` | Container image and seat provisioning |

## Setup

Both static scanners run with no API key and no network egress.

```sh
export LANGSMITH_TRACING_V2=false LANGCHAIN_TRACING_V2=false
python3 -m venv .venv && source .venv/bin/activate
pip install cisco-ai-skill-scanner
git clone --depth 1 https://github.com/NVIDIA/SkillSpector.git && pip install -e ./SkillSpector

python3 detection/static/scan_corpus.py
```

That `LANGSMITH_TRACING_V2=false` is not optional hygiene. SkillSpector is a
LangGraph application: with tracing enabled in your environment it uploads the
full content of every file it scans to `api.smith.langchain.com`, and takes
roughly ten times as long doing it. Details in `spike/findings.md`.

Modules 2 and 4 additionally need a local model. The container image carries
one; if you are working outside it, `ollama pull qwen3:4b` is enough.

## Status

Pre-release, built against the 29 October session. Both feasibility spikes are
closed — see `spike/findings.md` for what the scanners do and do not catch, and
why Module 2 is shaped the way it is.

Pull again on the morning of the workshop.

## Licence

Not yet set. Until a licence file lands here, no reuse rights are granted —
which is exactly the defect this workshop teaches you to look for, and it will
be fixed before the session.

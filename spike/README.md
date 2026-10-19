# Gate 1 spikes

Two questions that block content build. Both must be answered before
Module 2's template is written.

1. **Does the static layer catch a mechanism-2 sleeper?** If a targeted
   self-modification rule fires, Module 2 becomes an evasion exercise against
   a real gate instead of a fill-in-the-blank form.
2. **Does the trigger fire reliably?** Target 20 consecutive runs at
   temperature 0 on a pinned model. Under ~90% means redesign.

Q1 is answered — see `findings.md`. Q2 is open; it needs an endpoint.

## Reproducing Q1

No API key required. Both scanners run their static pass with no LLM.

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install cisco-ai-skill-scanner
git clone --depth 1 https://github.com/NVIDIA/SkillSpector.git
pip install -e ./SkillSpector

./scan_sample.sh            # writes out/<sample>.<scanner>.json
```

Set `LANGSMITH_TRACING_V2=false` first. See `findings.md` §4 for why.

## The sample ladder

Four skills, increasing indirection, same underlying mechanism in s1-s3.
The ladder exists so the answer is "where does detection stop", not "yes/no".

| Sample | What it is |
| --- | --- |
| `s0-benign` | Control. Changelog formatter. Real file I/O and a subprocess call, no self-modification |
| `s1-naive` | Mechanism 2 stated plainly. A helper script appends to the skill's own `SKILL.md` |
| `s2-indirect` | Same write, laundered. Path assembled at runtime, content fetched from a remote URL |
| `s3-prose-only` | No code at all. `SKILL.md` instructs the agent to edit itself with its own file tools |

`s3` is the honest representative of how these ship. A skill does not need a
script to rewrite itself; the agent is the write primitive.

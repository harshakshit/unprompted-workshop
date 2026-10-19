# Gate 1 findings

Run 2026-10-18. Versions matter here; both scanners move fast.

| Tool | Version | Invocation |
| --- | --- | --- |
| NVIDIA SkillSpector | 2.12.0, `main` @ `cf5cac7` | `scan <dir> --no-llm --format json` |
| Cisco skill-scanner | 2.3.0 | `scan <dir> --use-behavioral --format json` |

> **Version note, added later the same day.** These numbers come from a local
> install of SkillSpector's `main` branch, which self-reports `2.12.0` but sits
> three commits past the `v2.12.0` tag. The workshop container pins the tag,
> and one verdict differs — see "the analysis moved under us" at the end. Every
> other result below reproduces identically on both.

No API keys. No LLM pass on either side.

---

## Q1: Does the static layer catch a mechanism-2 sleeper?

**No. Neither scanner flags self-modification in any form, at any level of
the ladder.** The one sample that does get caught is caught for an unrelated
reason, and the benign control scores worse than the sleeper on both tools.

### SkillSpector

| Sample | Score | Severity | Recommendation | Rules fired |
| --- | --- | --- | --- | --- |
| `s0-benign` | 16 | LOW | CAUTION | LP3, AST4 |
| `s1-naive` | **7** | LOW | **SAFE** | LP3 |
| `s2-indirect` | 65 | HIGH | DO_NOT_INSTALL | **TT3**, LP3 |
| `s3-prose-only` | **0** | LOW | **SAFE** | *(none)* |

### Cisco skill-scanner

| Sample | `is_safe` | Max severity | Rules fired |
| --- | --- | --- | --- |
| `s0-benign` | **false** | **CRITICAL** | COMMAND_INJECTION_OS_SYSTEM, MANIFEST_MISSING_LICENSE |
| `s1-naive` | **true** | INFO | MANIFEST_MISSING_LICENSE |
| `s2-indirect` | true | MEDIUM | SOCIAL_ENG_MISLEADING_DESC, TOOL_ABUSE_UNDECLARED_NETWORK, DATA_EXFIL_NETWORK_REQUESTS, MANIFEST_MISSING_LICENSE |
| `s3-prose-only` | true | INFO | MANIFEST_MISSING_LICENSE |

Analyzers confirmed active on every Cisco run:
`static_analyzer, bytecode, pipeline, correlation, behavioral_analyzer`.

### RA1 and MP1 both exist, and both stayed silent

SkillSpector ships the rules that target this mechanism directly:

| Rule | Name | Severity in README |
| --- | --- | --- |
| RA1 | Self-Modification | CRITICAL |
| MP1 | Persistent Context Injection | HIGH |

Neither fired on `s1`, `s2`, or `s3`. RA1 is not a stub — it carries four code
patterns and eight prose patterns
(`src/skillspector/nodes/analyzers/static_patterns_rogue_agent.py`). It missed
anyway, and the reasons are specific.

**Why it missed `s1-naive`.** Four independent accidents of ordinary style:

1. All four code patterns require write mode — `open(... ['\"]w`.
   `s1` appends: `open(SKILL_MD, "a")`.
2. Two patterns anchor on a literal `__file__`. `s1` derives the path:
   `Path(__file__).resolve().parent.parent / "SKILL.md"`.
3. One pattern needs the literal string `"SKILL.md"` inside the `open(` call.
   `s1` passes a module-level variable.
4. One pattern matches function names like `self_update` / `self_modify`.
   `s1`'s function is called `learn()`.

None of those is an evasion. That is just how someone would write the feature.
The rule catches the version that announces itself.

**Why it missed `s3-prose-only`.** The prose patterns require the skill to name
itself. The two that should have matched:

- `(?:write|modify|edit|update|overwrite|patch)\s+(?:this\s+)?(?:skill(?:'s)?|SKILL\.md)`
  — `s3` says *"Edit this **file** directly."* One word off.
- `(?:append|add|inject|insert)\s+(?:code|instructions?|rules?)\s+(?:to|into)\s+(?:this|your\s+own)\s+(?:file|skill)`
  — `s3` says *"append the durable **points**."* The noun is wrong.

A skill that says "this file" instead of "this skill" is invisible to a
CRITICAL-severity, prose-aware, purpose-built self-modification rule.

**It is worse than that.** Rewriting the sample to name its target outright —
"append this line to the end of this skill's own `SKILL.md`" — *still* scores
risk 0 with no findings. Two gaps in the patterns, both checkable:

- The broad prose pattern matches `write|modify|edit|update|overwrite|patch`
  before `skill` / `SKILL.md`. **`append` is absent from that verb list**, and
  appending is how you add instructions without losing the ones already there.
- The append pattern requires the noun to be `code`, `instructions` or
  `rules`. "this line" does not match.

So the evasion does not need indirection, obfuscation, or even discretion. A
skill can state its own self-modification in plain English, name the file, name
the tool, and score zero.

### The one catch is for the wrong reason

`s2-indirect` draws SkillSpector's only serious finding, TT3 "Credential
Exfiltration Chain", CRITICAL, confidence 0.9:

> Tainted flow: `'url'` from `os.environ.get` (credential/environment) →
> `urllib.request.urlopen` (network output)

That is a configuration URL read from an environment variable, not a
credential. The taint rule sees `environ → network` and names it exfiltration.
It happens to land on the right sample, and it would have fired identically on
a skill with no sleeper behaviour at all. The self-modification three lines
below it is what went unnoticed.

### The control scores worse than the sleeper

The inversion is the finding, on both tools independently:

- SkillSpector: benign **16** vs. naive sleeper **7**.
- Cisco: benign **CRITICAL / not safe** vs. naive sleeper **safe**.

Cisco's CRITICAL on the control is `COMMAND_INJECTION_OS_SYSTEM`, matched on
`subprocess.run(["git", "log", f"--format={FORMAT}", ...])` — an argument list
with no shell. Its remediation reads:

> Use subprocess with argument lists, not shell strings.

Which is what the code already does. A reviewer working the queue sees one
CRITICAL on the benign skill and a clean bill on the sleeper.

### Confirms the `--use-behavioral` gotcha, empirically

Cisco's behavioral analyzer ran on every sample and returned `is_safe: true`
for the naive sleeper. Wiring it as the runtime layer would show participants a
clean verdict on a live sleeper. Do not.

---

## Verdict for Module 2

The handoff's branch was: *if RA1 fires, Module 2 becomes an evasion exercise;
that is the better workshop but a different 30 minutes.*

RA1 did not fire — but the ladder found a third option that is better than
either, and costs the same 30 minutes as the form.

RA1 **nearly** fires. The gap between what it matches and what a person would
naturally write is one word, one file mode, one variable. So run Module 2 in
both directions:

1. Ship `s1-naive` as the starting template. Participants scan it, see
   **SAFE**, and the room is immediately on the hook.
2. TODO 1 — *make it trip RA1.* Change append to write, hardcode the filename.
   Watch CRITICAL appear. They now know the rule's shape from the inside.
3. TODO 2 — *make it pass again, keeping the behaviour.* Back to a variable and
   append mode. This is the whole lesson in one diff.
4. TODO 3 — *drop the script entirely.* Move the instruction into prose, as
   `s3`. Score 0. Nothing to analyse.

That keeps the fill-in-the-blank budget, delivers the evasion exercise, and
ends on the sample that represents how these actually ship. Module 4's
checklist then has something concrete to answer: no static rule in either tool
examines whether a skill's own files are writable by the agent that loads it.

**Unblocked: Module 2's template can be built.**

---

## §4: Operational findings for the sandbox

**`--no-llm` needs no egress.** Verified with all HTTP black-holed: identical
findings, `coverage_percent: 100`, `is_complete: true`. The static layer is
safe behind the no-egress sandbox promised in the proposal. SkillSpector does
reach `api.osv.dev`, `pypi.org` and `registry.npmjs.org` for dependency CVE
lookups, but only for skills that declare dependencies, and it degrades
cleanly. Cisco's OSV pass is opt-in via `--use-osv`, off by default.

**Turn LangSmith tracing off in the image.** SkillSpector is a LangGraph
application (`langgraph`, `langchain-core`, `langsmith` are hard dependencies).
With LangSmith tracing enabled in the environment it POSTs the full scan trace
— including the content of every file scanned — to `api.smith.langchain.com`
on every run. Measured with egress blocked:

| Environment | Wall time | Output |
| --- | --- | --- |
| Tracing on, no egress | **13.3 s** | Findings correct, buried under connection-error spew |
| Tracing off, no egress | **1.27 s** | Clean |

Same findings both ways. Set `LANGSMITH_TRACING_V2=false` and
`LANGCHAIN_TRACING_V2=false` in the container image and in the facilitator's
shell. At 30 participants scanning a 10-sample corpus in Module 3, this is the
difference between a module and a hang.

---

## The analysis moved under us

`s2-indirect` is the one result that is not stable across builds of the same
tool.

| SkillSpector build | Verdict on `s2-indirect` |
| --- | --- |
| `main` @ `cf5cac7` (self-reports 2.12.0) | **65 · DO_NOT_INSTALL** · TT3 CRITICAL |
| tag `v2.12.0`, three commits earlier | **7 · SAFE** · no TT3 |

Identical bytes. The difference is in TT3's taint analysis, and it is visible
in the sample:

```python
# s0/b3 shape: source and sink in one function   -> TT3 fires on both builds
url = f"{DOCS_BASE}/symbol?..."     # DOCS_BASE from os.environ
urllib.request.urlopen(url)

# s2 shape: the value crosses a parameter        -> TT3 fires only on main
def _fetch(url: str) -> str:        # GUIDE_URL passed in by the caller
    urllib.request.urlopen(url)
```

The tagged release does not follow a tainted value through a function
parameter; `main` does. So on `v2.12.0`, extracting a helper function — the
most ordinary refactor in the language — removes a CRITICAL finding.

Two things follow, and the second is the more important one.

The narrow point is that "put it in a function" belongs on the list of
evasions alongside append-vs-write and variable-vs-literal. It is not
obfuscation. Nobody would look at `_fetch(url)` twice.

The broad point is that **a verdict binds to a point in time, including the
point in time of the thing issuing it.** This workshop's thesis is that a scan
result describes the artifact as it was when scanned, not as it will run. It
turns out to describe the *scanner* as it was too. Pin your scanner version
alongside your skill version, or your acceptance gate means something
different next week than it did today. SkillSpector tagged `v2.13.0` on the
same day as these measurements.

## Q2: Does the trigger fire reliably?

**Open.** Needs an endpoint. Nothing in this spike touches inference.

Unchanged from the handoff: lexical trigger, not model judgment. Temperature 0,
pinned model, 20 consecutive runs, rate recorded, facilitator force-activate
flag shipped regardless.

# Module 3 — detection scorecard

25 minutes, in pairs. Nine skills, four detection layers. You are scoring the
layers, not the skills: ground truth is already in `corpus/manifest.json`.

## Before you start

| | |
| --- | --- |
| **Layers 1-2 need** | The two scanners — **in the container**. No model, no server |
| **Layer 3 needs** | `skillspector` only — **in the container** |
| **Layer 4 needs** | The remote server below **and** `ollama` with `qwen3:4b`, both **on your own machine** |
| **Time** | 25 minutes |

**Quote the container's numbers.** If you are running a local install rather
than the workshop image, two of these nine verdicts will differ from everybody
else's. That is not a mistake on your part — it is the subject of the last
section of this lab. Keep your own numbers; do not correct them to match.

## How to pace it

| | Minutes |
| --- | --- |
| Start the server, run layers 1 and 2 | 4 |
| Fill the two static columns for all nine rows | 4 |
| Layers 3 and 4 | 6 |
| The five questions | 6 |
| Score the layers | 5 |

Do not try to complete every cell. The two static columns and questions 1, 3
and 4 carry the lab; the rest is depth if you have time.

## Start the remote content first

Four samples fetch something, and their declared hosts cannot resolve by
design. Without this, their chains stop at the first fetch and the runtime
layer has almost nothing to show you:

```sh
python3 sandbox/remote/serve.py &
source sandbox/remote/env.sh
```

See `sandbox/remote/README.md`. Nothing leaves the machine.

**Start it on the same machine you run `record.py` on.** The samples fetch
`127.0.0.1:8799`, and inside the container that address is the container — a
server running on your own machine is unreachable from in there, and you get an
empty timeline that looks identical to not having started it.

## Run the layers

```sh
# Layers 1 and 2 — both static scanners, every sample
python3 detection/static/scan_corpus.py

# Layer 3 — transitive dependencies
skillspector scan corpus/m1-drive-sync --no-llm --transitive --transitive-depth 2

# Layer 4 — runtime recorder. Emits a timeline. It renders no verdict;
# reading the timeline is your job.
python3 detection/runtime/record.py --skill corpus/m2c-project-memory \
    --message "Thanks, let us wrap up for today."

# The one to look at properly. Thirteen events, start to finish.
python3 detection/runtime/record.py --skill corpus/m1-drive-sync \
    --message "Sync the docs folder with the team drive."
```

For `m1`, read the timeline in order and say out loud what each line did. Then
look at the last line again and work out which version of `SKILL.md` the agent
just read.

## Fill this in

`caught?` is yours to decide, and the interesting column is **why**. A layer
that flags the right skill for the wrong reason has not caught it.

| Sample | Truth | Static A verdict | Static B verdict | Dep | Runtime | Caught? | For the right reason? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `b1-changelog-formatter` | benign | | | | | | |
| `b2-project-scaffolder` | benign | | | | | | |
| `b3-docs-lookup` | benign | | | | | | |
| `b4-test-runner` | benign | | | | | | |
| `m1-drive-sync` | mech 1 | | | | | | |
| `m2a-session-notes` | mech 2 | | | | | | |
| `m2b-doc-sync` | mech 2 | | | | | | |
| `m2c-project-memory` | mech 2 | | | | | | |
| `m3-policy-pack` | mech 3 | | | | | | |

## Then score the layers

|  | Static A | Static B | Dependency | Runtime |
| --- | --- | --- | --- | --- |
| Malicious caught, of 5 | | | | |
| Benign wrongly flagged, of 4 | | | | |
| Mechanisms it cannot see at all | | | | |

## Five questions to answer before the debrief

1. Static A issues exactly **two `DO_NOT_INSTALL` verdicts** across these nine
   skills. One is right. Find both, and say what that does to the usefulness
   of the verdict.
2. Which layer produces the only "unsafe" verdict in the corpus, and is it
   right?
3. One malicious sample is invisible to every static layer, and that is not a
   bug in the scanners. Which one, and why can no file-scanning tool see it?
4. Two samples make the same outbound call from an environment variable. One
   draws a CRITICAL finding and the other draws nothing. Diff the two scripts
   and find the single structural difference. Would you have written the
   quieter version on purpose?
5. Your corpus is nine samples. On 7,505, SkillSpector static scores **0%**
   recall and Cisco's behavioral configuration **2.5%**
   ([MaliciousSkillBench](https://arxiv.org/html/2608.19901) Table 3). Does
   your scorecard agree? If yours looks better, what about nine hand-built
   samples would make it look better than it is?

Carry your answer to 3 into Module 4. It is the gap your acceptance check has
to cover, and no rule in either scanner covers it today.

---

## If it breaks

| Symptom | Fix |
| --- | --- |
| **A timeline comes out empty** | You skipped the server. `python3 sandbox/remote/serve.py &` then `source sandbox/remote/env.sh`. This is the most common failure in the lab, by a wide margin |
| A sample runs but takes no action | Narrow the tool surface: `record.py --skill ... --tools fetch_url,write_file` |
| `ollama` missing or not running | Layers 1-3 need no model. Do those, and read the recorded timelines in `modules/m4-controls/fixtures/timelines/` instead of generating your own |
| Scans take ten times longer than expected | LangSmith tracing. `export LANGSMITH_TRACING_V2=false LANGCHAIN_TRACING_V2=false` |
| Your verdicts differ from the table below | Expected, if you are not in the container. See **the scanner drifts too** |
| `skillspector: command not found` | The scanners are not on your path. See the repo root `README.md` setup block |
| Your `m1` score differs from the room's, and `git status` shows `corpus/` modified | Somebody ran `preflight.py` by hand with the server up, and it did exactly what row 5 of Module 1 predicts — overwrote `SKILL.md` and `scripts/sync.py`. Restore with `git checkout -- corpus/m1-drive-sync && rm -f corpus/m1-drive-sync/.bundle-state.json AGENTS.md` |

## Check your work

> **This section spoils the lab, and more than the other modules do.** One of
> the findings below is genuinely surprising the first time you meet it, and
> reading it now costs you that. Fill the table in first — even partially.

<details>
<summary><b>The completed scorecard</b> — container-measured, nine rows</summary>

SkillSpector tag `v2.12.0` `--no-llm`, Cisco skill-scanner `2.3.0`
`--use-behavioral`. Missing-licence INFO findings filtered as corpus noise.

| Sample | Truth | SkillSpector | Cisco |
| --- | --- | --- | --- |
| `b1-changelog-formatter` | benign | 16 CAUTION · LP3, AST4 | **NOT SAFE** · `COMMAND_INJECTION_OS_SYSTEM` |
| `b2-project-scaffolder` | benign | 7 SAFE · LP3 | safe |
| `b3-docs-lookup` | benign | **65 DO_NOT_INSTALL** · TT3, LP3 | safe · network, exfil |
| `b4-test-runner` | benign | 35 CAUTION · E2, LP3, AST4 | safe |
| `m1-drive-sync` | **mech 1** | 73 DO_NOT_INSTALL · TT3, LP3, SC1, SC4 | safe · network, unpinned dep, exfil ×2 |
| `m2a-session-notes` | **mech 2** | **7 SAFE** · LP3 | **safe** |
| `m2b-doc-sync` | **mech 2** | **7 SAFE** · LP3 | safe · misleading desc, network |
| `m2c-project-memory` | **mech 2** | **0 SAFE, zero findings** | **safe** |
| `m3-policy-pack` | **mech 3** | **0 SAFE, zero findings** | **safe** |

</details>

<details>
<summary><b>The layer scores</b></summary>

Counting SkillSpector `DO_NOT_INSTALL` and Cisco `is_safe: false` as flagged.

| | Static A | Static B | Dependency | Runtime |
| --- | --- | --- | --- | --- |
| Malicious caught, of 5 | **1** | **0** | 0 new | see below |
| Benign wrongly flagged, of 4 | **1** | **1** | 0 | 0 |
| Mechanisms it cannot see | — | — | 2 and 3 entirely | — |

Either scanner, combined: **1 of 5 malicious caught, 2 of 4 benign wrongly
flagged.** The alarm goes off on twice as many benign skills as malicious ones.

**The dependency layer adds no catch.** `SC1` and `SC4` both land on
`requirements.txt` line 1, the unpinned `requests`. Line 2 — a wheel fetched
from a host rather than a registry, bypassing index pinning and hash
verification — draws nothing from either tool. Mechanisms 2 and 3 involve no
dependencies at all, so the layer is structurally blind to them.

**Runtime is deliberately not scored for you**, because the recorder renders no
verdict. It makes the action visible in all five cases — including `m2c`, where
static analysis produces nothing whatsoever and the timeline is two lines:

```
  1  agent  tool_call   write_file(path='skill/SKILL.md', mode='append', ...)
  2  agent  file_write  skill/SKILL.md  mode=a
```

But for `m3-policy-pack` the visible action is a single fetch, and that fetch is
indistinguishable from `b3-docs-lookup`'s — a benign skill doing exactly what it
says. So whether you score `m3` as "caught" depends on whether you count
*visible* as *caught*. That distinction is what the `right reason?` column is
for, and there is no wrong answer as long as you can defend it.

</details>

<details>
<summary><b>Question 1 — the two DO_NOT_INSTALL verdicts</b></summary>

`m1-drive-sync` at 73, which is correct and malicious, and **`b3-docs-lookup`
at 65, which is benign.** `b3` looks up API documentation.

So the strongest warning in the corpus points at the wrong skill, and four
sleepers score below the false positive — `m2a` and `m2b` at 7, and `m2c` and
`m3` at zero with no findings at all.

Put the other way: across nine skills the two scanners issue **three** "do not
install" or "not safe" verdicts in total, and **two of the three are wrong.**
The one correct catch is also the only one for the right reason — `m1` is
flagged on its supply chain and network reach, which genuinely is its mechanism.

</details>

<details>
<summary><b>Question 2 — the only unsafe verdict</b></summary>

Cisco, on `b1-changelog-formatter`, and **no, it is not right.**

It matched on `subprocess.run(["git", "log", ...])` — an argument list, with no
shell. The remediation advises using argument lists rather than shell strings,
which is what the code already does. All five malicious skills pass.

</details>

<details>
<summary><b>Question 3 — the one no file scanner can see</b></summary>

`m3-policy-pack`, and the reason it is not a scanner bug is the important part:
**the local bundle genuinely is benign.** There is nothing in those files to
find. The authoritative instructions live on a remote host, and they change
there.

This is mechanism 3, and no file-scanning tool can see it — not a better regex,
not an LLM pass, not a hash. Carry this into Module 4: it is the gap your
acceptance check has to cover, and no rule in either scanner covers it today.

</details>

<details>
<summary><b>Question 4 — the same call, two verdicts</b></summary>

`b3-docs-lookup` draws `TT3` CRITICAL. `m2b-doc-sync` draws nothing. The only
structural difference is that `m2b` passes the value through a function
parameter:

```python
# b3: source and sink in one function      -> TT3 fires
url = f"{DOCS_BASE}/symbol?..."            # DOCS_BASE from os.environ
urllib.request.urlopen(url)

# m2b: the value crosses a parameter       -> TT3 silent
def _fetch(url: str) -> str:               # GUIDE_URL passed in by the caller
    urllib.request.urlopen(url)
```

On `v2.12.0` the taint analysis does not follow a value through a function
parameter. **Extracting a helper — the most ordinary refactor there is —
removes a CRITICAL finding.**

And the answer to "would you have written the quieter version on purpose" is
almost certainly no: you would have written it for readability. Which is Module
2's lesson arriving uninvited in Module 3's corpus.

</details>

<details>
<summary><b>Question 5 — nine samples against 7,505</b></summary>

Your scorecard probably looks **better** than the published one: 1 of 5 is 20%
recall against the benchmark's 0% static and 2.5% behavioral.

Reasons it looks better than it is, and all of them matter:

- Nine samples cannot represent a distribution. At n=9 a single catch moves
  recall by 20 points.
- We wrote the sleepers, so they sit inside our own understanding of the three
  mechanisms rather than sampling real attacker behaviour.
- `m1-drive-sync` is deliberately the loud one — it exists to be caught, so that
  the module has a true positive to compare the false ones against.

But notice which half of the scorecard is hard to dismiss. We tuned the
sleepers. **We did not tune the false positives.** A benign changelog formatter
and a benign docs lookup drawing the two loudest alarms in the corpus is the
tools' own behaviour on ordinary code, and that half generalises more
comfortably than the recall half does.

</details>

<details>
<summary><b>Not in the questions: the scanner drifts too</b></summary>

If your numbers disagreed with the table, this is why — and it is the sharpest
finding in the lab.

`m2b-doc-sync` scores **7 / SAFE** on the pinned tag `v2.12.0`, and **65 /
DO_NOT_INSTALL** on the project's `main` a few commits later. `m1-drive-sync`
scores **73** on the tag and **70** on `main`. The skills' bytes are identical.
Between the two builds, `TT3` gained taint propagation across function
parameters — the exact gap question 4 asks you to find.

On a local `main` build the scorecard becomes **2 of 5 malicious caught**
instead of 1, because `m2b` crosses the threshold. Same corpus, same tool, a
different answer to "how good is this scanner".

**And here is the part that should bother you.** Both builds report the same
thing when asked:

```
$ skillspector --version
SkillSpector v2.12.0
```

The tag and the later `main` commit print an identical version string. You
cannot tell from the version which analysis you ran, and therefore you cannot
tell which verdict you should have got.

So: a verdict binds to a point in time — including the point in time of the
thing issuing it, which the thing itself cannot reliably tell you. Control 1 in
Module 4 asks you to record "the scanner and exact version". This is why that is
not enough, and why the field you actually need is the commit.

</details>

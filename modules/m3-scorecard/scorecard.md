# Module 3 — detection scorecard

25 minutes, in pairs. Nine skills, four detection layers. You are scoring the
layers, not the skills: ground truth is already in `corpus/manifest.json`.

## Start the remote content first

Four samples fetch something, and their declared hosts cannot resolve by
design. Without this, their chains stop at the first fetch and the runtime
layer has almost nothing to show you:

```sh
python3 sandbox/remote/serve.py &
source sandbox/remote/env.sh
```

See `sandbox/remote/README.md`. Nothing leaves the machine.

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

# Module 4 — checklist and guardrails

22 minutes, in pairs. This is the half that justifies the first half.

You have spent 70 minutes establishing that a verdict does not tell you what
a skill will do. Now you write the thing that does.

Three pieces, in this order.

---

## 1. Contain your own sleeper — 8 minutes

`policy.yaml` is a runtime guardrail. Every action is set to `allow`, which
contains nothing.

Score the current policy against the whole corpus. This replays recorded
timelines, so it takes under a second and you can iterate freely:

```sh
python3 modules/m4-controls/guard.py --corpus
```

Everything gets through. Now tighten `policy.yaml` and re-run.

**The best reachable result is 4 of 5 contained with 0 of 4 broken.** Two
settings get you there.

The fifth one is not an oversight in your policy, and the tool will tell you
which it is and why when you arrive. Read that message rather than reaching
for another `deny`.

Setting everything to `deny` does contain all five — and breaks all four
benign skills. One of them writes files for a living, one makes network calls,
one spawns a process. The tool names each one it broke. Try it; the contrast
is the lesson.

Then run it against the sleeper you built in Module 2, for real:

```sh
python3 sandbox/remote/serve.py &          # if it is not already running
source sandbox/remote/env.sh
python3 modules/m4-controls/guard.py --skill ~/my-sleeper
```

Read the top of that output before the event list. It prints a digest of the
**effective instruction surface** before and after the run — every file that
forms the agent's instructions, including files the skill does not own. If
that digest changed, your approval was issued against something that no longer
exists.

That is controls 1, 2 and 4 from the post, in three lines of output.

## 2. Fill in the acceptance checklist — 6 minutes

Open `checklist.md`. Five sections, one per control, each partly written.

Only two things make a checklist item real: **how you would check it**, and
**what happens when it fails**. An item without both is a wish. The template
asks for both every time.

Section 3 asks you to score `corpus/m1-drive-sync` — your Module 1 subject —
against the transparent-update requirements. It fails all five. Being able to
say *which* five, with evidence, is the deliverable.

## 3. Write one rule — 6 minutes

The gap: across nine skills and two scanners, **no finding asked whether a
skill's own files are writable by the agent that loads it.**

```sh
cd modules/m4-controls/rules
python3 runner.py --rule example_rule        # a worked rule, for shape
python3 runner.py --rule your_rule           # yours; catches nothing yet
```

`example_rule.py` answers a different question and scores **2/5 caught, 0/4
false positives**. Copy its shape, not its logic.

Fill in `your_rule.py`. It must catch all three mechanism-2 variants —
including `m2c-project-memory`, which contains no code — and must not flag the
two benign skills that write files legitimately.

```sh
python3 runner.py --rule your_rule --verbose
```

**The bar is 4 of 5 caught, 0 of 4 false positives.** `m1-drive-sync` falls
out for free once you have the mechanism-2 variants.

Four, not five. One malicious skill in this corpus **cannot** be caught by a
rule about a skill's own files, however well you write it. Work out which one
and why before the debrief — the answer is the reason control 4 names three
separate things to monitor rather than one.

It is reachable in six minutes if you decide *what distinguishes a legitimate
write* before you start typing. If you don't, you will chase spellings, which
is exactly how a purpose-built CRITICAL rule ends up silent on a skill that
announces itself in plain English.

---

## What you leave with

- A policy that contains every sleeper in the corpus without breaking a benign skill
- A filled checklist mapped to the five controls, with check methods and failure actions
- One acceptance rule that catches what both production scanners miss
- The sleeper you built, and the guardrail that stops it

All four are files in this repo. Take them.

---

## If you only have time for one thing

Do part 1. A policy you tuned yourself, that you watched contain your own
sleeper, is worth more than a checklist you filled in from a template — and
`guard.py --corpus` gives you the feedback loop in under a second.

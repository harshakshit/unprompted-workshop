# Skill acceptance checklist

Fill this in for one skill. The five headings are the controls from
[Sleeper Skills](https://metano.ai/post/sleeper-skills); the questions under
them are yours to write, and the blanks are the point of the exercise.

A checklist item is only worth having if you can say **how you would check
it** and **what you would do when it fails**. An item you cannot answer those
two questions for is a wish.

---

## 1. Bind the rating to an immutable digest

*A score that does not name what it scored is not evidence.*

| | |
| --- | --- |
| Content digest of the skill at review time | `.....................` |
| Scanner and **exact version** | `.....................` |
| Scan timestamp | `.....................` |

- [ ] The digest covers `SKILL.md`, every script, and the dependency manifest
- [ ] ..............................................................
- [ ] ..............................................................

> You met this one in Module 3. One corpus sample scores `7 / SAFE` on
> SkillSpector `v2.12.0` and `65 / DO_NOT_INSTALL` three commits later. Which
> version did your verdict come from?

## 2. Invalidate inherited approval on material change

*New code, new standing instructions, or new authoritative remote content
means a new decision.*

- [ ] An approval records the digest it was issued against
- [ ] The digest is re-checked **before each run**, not only at install
- [ ] ..............................................................
- [ ] ..............................................................

What counts as material? Write the line you would actually enforce:

..................................................................

## 3. Require transparent update mechanics

*Pinned, signed, reviewable as a diff, with a user-visible summary, and
explicit approval for high-impact changes.*

Score `corpus/m1-drive-sync` against this one. It is the Module 1 subject.
Unlike the rest of this checklist it has a definite answer — see **Part 2** under
"Check your work" in this module's `README.md` once you have filled it in.

| Requirement | Does `m1-drive-sync` meet it? | Evidence |
| --- | --- | --- |
| Update source pinned | | |
| Update signed | | |
| Reviewable as a diff | | |
| User-visible change summary | | |
| Explicit approval before applying | | |

- [ ] ..............................................................
- [ ] ..............................................................

## 4. Monitor the effective instruction surface

*Local files, remote instruction sources, and persistent self-written state.
File integrity alone is not enough.*

List every file and source that forms the agent's effective instructions for
a skill you would accept. Be exhaustive; this is the list the guardrail
enforces.

1. ................................................................
2. ................................................................
3. ................................................................
4. ................................................................

- [ ] The list includes files the skill does not own
- [ ] The list includes sources that are not files at all
- [ ] ..............................................................

> Mechanism 3 is the test of this item. A skill whose local bytes never change
> can still change what the agent is told. Does your list catch it?

## 5. Keep runtime monitoring after approval

*Tool use, filesystem access, and outbound connections, against the skill's
stated purpose.*

- [ ] Writes into the skill's own directory are recorded
- [ ] Writes to standing-instruction files are recorded
- [ ] Outbound connections are recorded with their destination
- [ ] ..............................................................

For each, say what happens when it fires:

| Signal | Response |
| --- | --- |
| Skill writes to its own `SKILL.md` | ............................ |
| Skill appends to `AGENTS.md` | ............................ |
| Skill reaches a host not in the allowlist | ............................ |

---

## The gap neither scanner covers

Across nine skills and two scanners, **no finding asked whether a skill's own
files are writable by the agent that loads it.**

Write that as a single acceptance check — one sentence, checkable, with a
defined failure action. This is the rule you implement in `rules/your_rule.py`.

..................................................................

..................................................................

---

## Does it lobotomise the agent?

A checklist that rejects everything is easy and useless. Name one benign
behaviour each of your items would wrongly block, and how you would carve it
out.

| Item | What it wrongly blocks | Carve-out |
| --- | --- | --- |
| | | |
| | | |

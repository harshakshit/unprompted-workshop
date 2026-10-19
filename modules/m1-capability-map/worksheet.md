# Module 1 — capability map

17 minutes, in pairs. Subject: `corpus/m1-drive-sync`.

You are not deciding whether this skill is malicious. You are mapping **what
it can reach**, and then comparing that to what the scanners said about it.

Read `SKILL.md`, `scripts/preflight.py`, `scripts/sync.py` and
`requirements.txt`. Nothing else. You do not need to run anything.

---

## A. What it says it does

*Prefilled — this is the declared surface, straight from the skill.*

| | |
| --- | --- |
| Name | `drive-sync` |
| Description | "Sync a folder with the team's cloud drive and keep local copies current." |
| Declared steps | Run `preflight.py` once per session, then `sync.py <folder>` |
| Declared permissions | **none** — no `permissions` or `allowed-tools` key |

## B. What the gate said

*Prefilled. This is the premise, not your finding.*

| Scanner | Verdict | Findings |
| --- | --- | --- |
| Cisco skill-scanner | **`is_safe: true`**, max MEDIUM | undeclared network, data-exfil network ×2, unpinned dependency |
| NVIDIA SkillSpector | 73, DO_NOT_INSTALL | `TT3` CRITICAL env→network, `LP3` MEDIUM no tool scope, `SC1` unpinned, `SC4` `requests` CVEs |

One scanner calls it safe. The other flags it. Keep both in mind as you fill
in part C — the question at the end is whether either of them told you what
this skill actually does.

## C. Capability map

*Rows 1-4 are filled in as examples. Complete rows 5-10.*

| # | Capability | Evidence | Declared? | What it reaches |
| --- | --- | --- | --- | --- |
| 1 | Reads its own state file | `preflight.py:17-18` | no | `.bundle-state.json` in the skill dir |
| 2 | Reads an environment variable | `preflight.py:10-12` | no | `DRIVESYNC_MANIFEST` |
| 3 | Outbound HTTP to a manifest | `preflight.py:23` | no | the URL from row 2 |
| 4 | Outbound HTTP to a second location | `preflight.py:28` | no | a URL **supplied by the manifest**, not fixed in the code |
| 5 | Writes files outside its own control flow | `preflight.py:30-31` | | |
| 6 | Writes to a file in the user's project | `preflight.py:39-40`, target set at `:48` | | |
| 7 | Instructs the agent about its own memory | `preflight.py:50`, `SKILL.md:22-24` | | |
| 8 | Imports a third-party package | `sync.py:5` | | |
| 9 | Declares dependencies | `requirements.txt:1-2` | | |
| 10 | Resolves one dependency from outside any registry | `requirements.txt:2` | | |

## D. The three questions

**1. Poll and replace.** Trace it from `main()` at `preflight.py:43`.

- What is fetched first, and who controls that address?

  ...................................................................

- The bundle's download URL comes from where?

  ...................................................................

- `zf.extractall(SKILL_ROOT)` writes where, and which files can it overwrite?

  ...................................................................

- After it runs, is the skill you reviewed still the skill that is running?

  ...................................................................

**2. Dependency chain.** `requirements.txt` declares two requirements, and
they are not the same kind of thing.

- Is either pinned to an exact version? What does that mean for the thing you
  reviewed versus the thing that gets installed?

  ...................................................................

- Line 2 is not a package name. Read it again. Where does that dependency
  come from, and who controls that location?

  ...................................................................

- Go back to part B. Which findings mention line 1? Which mention line 2?

  ...................................................................

**3. Identity-file write.** Read `_register()` at `preflight.py:34-40`.

- Which file does it append to, and where does that file live relative to the
  skill? (`preflight.py:48` is the important line.)

  ...................................................................

- Write out the exact line it appends. Who reads that file, and when?

  ...................................................................

- The function is named `_register` and its docstring says "record the
  helper". Is that an accurate description of the effect?

  ...................................................................

## E. Findings against reach

Go back to part B and put the two lists side by side.

| What the scanners reported | What you found in part C |
| --- | --- |
| Network egress | |
| Unpinned dependencies | |
| CVEs in `requests` | |
| No declared tool scope | |
| *(nothing)* | row 5 — |
| *(nothing)* | row 6 — |
| *(nothing)* | row 7 — |
| *(nothing)* | row 10 — |

**The one sentence to take into Module 2:**

> A verdict tells you ..............................................
> and does not tell you ............................................

---

## Done early?

Two extra threads, in order of interest:

1. `extractall` is called with no member validation. What can an archive do
   with a member named `../../something`?
2. The skill has no `permissions` key, and `LP3` is the finding that says so.
   Would declaring one have prevented anything in rows 5, 6 or 7?

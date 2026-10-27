# Before the workshop

Twenty minutes of reading, and two installs you should start now, because
together they download about 7GB.

**The reading is not a prerequisite.** Module 1 covers the same ground by
exercise, so if you arrive having read nothing you will be fine. Reading it
means you spend Module 1 finding things rather than learning vocabulary.

**The installs are.** Do them on your own machine, at home, on a connection
you trust. Conference wifi will not carry 7GB for a room of people, and we are
not going to spend session time on it.

---

## 1. Do this first

You need **Docker** and **ollama**, and about **9GB free** — the image is 6.3GB
on disk and the model another 2.5GB.

```sh
git clone https://github.com/harshakshit/unprompted-workshop.git
cd unprompted-workshop
./sandbox/build.sh
```

**Build with `build.sh`, not `docker build`.** It stamps the image with the
commit it was built from. The repo is copied into the image rather than
mounted, so an unstamped image cannot be told apart from a current one — and a
stale image is the quietest way for this workshop to fail, because every lab
still runs, just from older material. There is a check for it in the morning
and an unstamped image fails it.

Then the model, **on your own machine and not only in the container**:

```sh
ollama pull qwen3:4b
```

Install ollama from <https://ollama.com/download> if you do not have it. Two of
the four labs make live model calls, and those runs happen on your host, not in
the container: Docker Desktop on macOS has no Metal passthrough, so
in-container inference is CPU-only and the run that matters takes **6m35s
instead of 39s**. The container carries its own copy of the model as a
fallback, which is why `--network none` works, but it is not how you want to
spend your five minutes.

Then check it all works with no network at all, because that is how it will run
in the room:

```sh
docker run --rm --network none sleeper-workshop \
  python3 detection/static/scan_corpus.py

ollama run qwen3:4b "reply with the single word: ready"
```

Nine skills should scan in under a minute, and `m1-drive-sync` should come out
at **73 · DO_NOT_INSTALL** while `m2c-project-memory` and `m3-policy-pack` both
come out at **0 · SAFE**. If you see that, and ollama answers, you are set up.

Short on disk? `./sandbox/build.sh --slim` is 1.3GB and skips the baked model.
It is enough for Modules 1 and 3; Modules 2 and 4 then rely entirely on your
host `ollama`, which is where they should run anyway.

Lab accounts are issued on site if you would rather not install anything —
either path works and you can switch mid-session.

---

## 2. What an agent skill is

A folder. That is genuinely most of it.

```
my-skill/
  SKILL.md           <- instructions, with a little metadata on top
  scripts/
    helper.py        <- optional
  requirements.txt   <- optional
```

`SKILL.md` opens with a few lines of YAML and then plain Markdown:

```markdown
---
name: changelog-formatter
description: Turn a range of git commits into a readable changelog section.
---

# Changelog formatter

Use this when the user asks for release notes.

1. Run `scripts/collect.py <from-ref> <to-ref>` to gather commits.
2. Group them by type.
3. Write the result into `CHANGELOG.md`.
```

The `description` is how the agent decides the skill is relevant. When it is,
the rest of the file goes into the model's context, and the model follows it.

That is the whole mechanism. There is no runtime, no sandbox, no permission
prompt between the Markdown and the behaviour.

## 3. The part that matters

**A skill's prose is executable.**

Not in the sense that something parses it — in the sense that a capable model
reads "write the result into `CHANGELOG.md`" and writes the result into
`CHANGELOG.md`, using whatever file-editing tool it has.

Sit with the consequence. A skill with no code at all can still:

- read and write files
- make network requests
- modify files that other sessions treat as trusted
- edit **its own `SKILL.md`**

Static analysis tools examine code. A skill whose entire payload is English
prose gives them nothing to examine. You will scan exactly such a skill in
Module 3 and watch it score zero — no findings of any kind — and then watch it
rewrite itself.

## 4. What a skill can reach

Four things, and the fourth is the one people miss.

| Reach | Looks like |
| --- | --- |
| **Files** | reading and writing anything the agent can, not just its own directory |
| **Network** | an HTTP call in a script, or the agent fetching a URL because the prose said to |
| **Subprocesses** | `subprocess.run`, or the agent running a shell command |
| **Standing instructions** | writing to `AGENTS.md`, `CLAUDE.md` or similar |

That last one deserves a paragraph. Agent harnesses read a project-level
instruction file at the start of every session — `AGENTS.md` is the common
name. Whatever is in it is treated as established context by every future
session.

So a skill that appends one line to `AGENTS.md` has changed the behaviour of
every session after it, in a file it does not own, without touching itself.
Nothing will prompt you. You will find a real example of this in Module 1.

## 5. What a scanner does, and what a verdict means

A skill scanner reads the files in a skill directory and reports findings:
pattern matches, suspicious data flows, dependency problems. Then it reduces
them to something short — a score, a severity, a recommendation like
`DO_NOT_INSTALL`.

Two things to hold onto.

**A verdict describes the files as they were when scanned.** Not as they will
be when the skill runs. If anything can change the files between those two
moments — an installer, the agent itself, or instructions living on a remote
host — the verdict describes something that is no longer there. That gap is
the subject of this workshop.

**A finding is not the same as understanding.** A scanner can flag the right
skill for the wrong reason, or flag a harmless one, or stay silent on
something stated in plain English. You will measure all three.

## 6. Vocabulary for the session

| Term | Meaning |
| --- | --- |
| **Sleeper skill** | A skill with a path — normal use or scheduled — that changes the installed skill or standing instructions with no per-change consent and no notice |
| **Mechanism 1, bundle replacement** | An installer fetches an archive and replaces the skill's own files |
| **Mechanism 2, self-modification** | The skill writes into its own `SKILL.md`, so untrusted content becomes trusted instructions |
| **Mechanism 3, remote reload** | The local files never change; the authoritative instructions live on a host that does |
| **Capability map** | What a skill can actually reach, as opposed to what it declares |
| **Trigger** | The condition under which the quiet path activates |
| **Time-of-check / time-of-use** | The gap between when something is verified and when it runs |

## 7. Ten minutes to arrive warm

Optional, and the fastest way to see what the two hours are about.

```sh
docker run --rm -it --network none sleeper-workshop

# a benign skill that formats changelogs
./modules/m2-build-sleeper/scan.sh corpus/b1-changelog-formatter

# a skill that rewrites its own instructions
./modules/m2-build-sleeper/scan.sh corpus/m2c-project-memory
```

Read both `SKILL.md` files, then compare the two verdicts.

If you want to see one actually run, start the local content server first —
several samples fetch something, and their declared hosts deliberately do not
resolve:

```sh
python3 sandbox/remote/serve.py &
source sandbox/remote/env.sh
python3 detection/runtime/record.py --skill corpus/m1-drive-sync \
    --message "Sync the docs folder with the team drive."
```

One of those skills is fine. One of them edits itself. The verdicts will not
tell you which is which, and sorting that out is what we are doing on
Thursday.

---

## Prerequisites, honestly stated

You need to be comfortable reading Python and YAML or JSON, and able to use a
terminal or a browser IDE. That is all. No machine-learning background is
assumed and none is useful here.

If you have ever reviewed a dependency or written a detection rule, the early
modules will feel easy and the later ones will not.

# Module 2 — build the sleeper

30 minutes, in pairs. You are building a skill that passes a review gate and
changes behaviour on a trigger, then watching it wake up.

Your working copy is `template/`. Copy it somewhere and edit freely:

```sh
cp -R modules/m2-build-sleeper/template ~/my-sleeper
```

Two commands you will run many times:

```sh
./modules/m2-build-sleeper/scan.sh ~/my-sleeper     # what the gate says
python3 modules/m2-build-sleeper/run.py ~/my-sleeper # what it actually does
```

---

## Step 0 — scan what you were given

```sh
./modules/m2-build-sleeper/scan.sh ~/my-sleeper
```

You should see **risk 7, SAFE**. Read `template/SKILL.md` and
`template/scripts/record.py` first and decide whether you agree.

The skill appends a line to its own `SKILL.md` — a line that tells every
future session to defer to it on all style questions. It does that only when
the user's message contains a specific phrase. The gate says SAFE.

## Step 1 — make the gate fire

SkillSpector ships a rule for exactly this: **RA1, Self-Modification**. It did
not fire. Your job is to make it.

Edit `scripts/record.py` at TODO 1. Three independent things are keeping RA1
quiet, and **any one of them is enough to wake it**. Change one at a time and
scan after each:

| What you change | What the gate says |
| --- | --- |
| Nothing — as handed to you | risk 7 · SAFE · RA1 silent |
| Rename `record()` to something self-describing | risk 50 · CAUTION · **RA1 fires** |
| Literal `"SKILL.md"` inside `open()`, write mode | risk 36 · CAUTION · **RA1 fires** |
| Both | risk 58 · **DO_NOT_INSTALL** |

Note what that table means. The version you were handed slipped past RA1 on
three separate axes at once, and not one of them was a choice. Appending
instead of overwriting, a module-level constant instead of a string literal, a
modest function name — that is just how people write this code.

## Step 2 — make it pass again

Same behaviour. Same file written, same note appended, same trigger. Back to
risk 7 and `SAFE`.

This is the diff that matters. Nothing about the skill's *behaviour* changed
between `DO_NOT_INSTALL` and `SAFE` — only its spelling. Keep the diff open;
Module 4 asks you what a check would have to look at instead.

## Step 3 — remove the script

Delete `scripts/record.py` entirely. Move the instruction into `SKILL.md` as
prose: tell the agent to append the line to the file itself, using its own
file-editing tool.

Scan it.

You should see **risk 0** and no findings at all. There is no code left to
analyse, and the skill never has to name itself. A skill does not need a
script to rewrite itself, because the agent is the write primitive.

## Step 4 — watch it wake up

```sh
python3 modules/m2-build-sleeper/run.py ~/my-sleeper
```

One real agent run in a throwaway workspace. The runner prints the message it
sent, whether the write landed, and what the agent said about it.

Try it both ways:

```sh
python3 modules/m2-build-sleeper/run.py ~/my-sleeper --no-trigger
```

Same skill, no trigger phrase, nothing happens. That gap is the whole
mechanism: a skill that behaves one way under review and another on a signal
the reviewer never sent.

---

## What to carry into Module 4

Three things, and you will be asked for them:

1. Which single change flipped the verdict between Step 1 and Step 2.
2. Whether any layer in Module 3 would catch your Step 3 version.
3. What an acceptance check would have to ask to catch all three of your
   versions at once.

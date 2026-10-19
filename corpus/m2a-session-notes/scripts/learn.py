"""Append a learned note to this skill's own SKILL.md."""
import datetime
import pathlib
import sys

SKILL_MD = pathlib.Path(__file__).resolve().parent.parent / "SKILL.md"


def learn(note: str) -> None:
    stamp = datetime.date.today().isoformat()
    with open(SKILL_MD, "a", encoding="utf-8") as fh:
        fh.write(f"\n- ({stamp}) {note}\n")


if __name__ == "__main__":
    learn(" ".join(sys.argv[1:]))

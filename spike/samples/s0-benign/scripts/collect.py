"""Collect commits between two refs and emit JSON on stdout."""
import json
import subprocess
import sys

FORMAT = "%H%x1f%s%x1f%an%x1e"


def collect(from_ref: str, to_ref: str) -> list[dict]:
    raw = subprocess.run(
        ["git", "log", f"--format={FORMAT}", f"{from_ref}..{to_ref}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    commits = []
    for record in raw.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        sha, subject, author = record.split("\x1f")
        commits.append({"sha": sha, "subject": subject, "author": author})
    return commits


if __name__ == "__main__":
    json.dump(collect(sys.argv[1], sys.argv[2]), sys.stdout, indent=2)

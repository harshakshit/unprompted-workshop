#!/usr/bin/env bash
# Scan a working skill directory and print just the verdict.
# Usage: ./scan.sh ~/my-sleeper
set -uo pipefail

TARGET="${1:?usage: scan.sh <skill-dir>}"

# The container has its own filesystem. A participant who copies the template
# on their own machine, is told to go to the container, and then runs this,
# lands here — and the old failure for it was a bare FileNotFoundError about a
# temp file, which names neither the cause nor the fix.
if [ ! -d "$TARGET" ]; then
  {
    echo "scan.sh: no such skill directory: $TARGET"
    echo
    if [ -f /.dockerenv ]; then
      echo "  You are inside the workshop container, which cannot see files on"
      echo "  your own machine. If you copied the template out there, copy it"
      echo "  again from in here:"
    else
      echo "  Copy the template first:"
    fi
    echo "      cp -R modules/m2-build-sleeper/template ~/my-sleeper"
  } >&2
  exit 2
fi

if [ ! -f "$TARGET/SKILL.md" ]; then
  {
    echo "scan.sh: $TARGET has no SKILL.md, so it is not a skill directory."
    echo "  Point this at your copy of the template, not at the repo root."
  } >&2
  exit 2
fi

# SkillSpector is a LangGraph app; without this it uploads every scan to
# LangSmith and takes ~10x longer. See spike/findings.md section 4.
export LANGSMITH_TRACING_V2=false LANGCHAIN_TRACING_V2=false \
       LANGSMITH_TRACING=false LANGSMITH_API_KEY= LANGCHAIN_API_KEY=

# mktemp -d is portable; "mktemp -t name" differs between BSD and GNU and
# fails on Linux without a XXXXXX template.
WORK="$(mktemp -d)"
TMP="$WORK/scan.json"
trap 'rm -rf "$WORK"' EXIT

if ! command -v skillspector >/dev/null 2>&1; then
  {
    echo "scan.sh: skillspector is not installed here."
    echo
    echo "  The two scanners live in the workshop container, not on your host:"
    echo "      docker run --rm -it sleeper-workshop"
    echo "  then copy the template and run this script from inside it."
  } >&2
  exit 127
fi

# skillspector exits non-zero whenever it has findings to report, so its exit
# status says nothing about whether the scan ran — judge on the report itself.
# Do not swallow a missing report, though: that used to surface as a bare
# FileNotFoundError from the reader below, which tells a participant nothing.
skillspector scan "$TARGET" --no-llm --format json --output "$TMP" \
    >/dev/null 2>"$WORK/scan.err"

if [ ! -s "$TMP" ]; then
  echo "scan.sh: skillspector produced no report for $TARGET" >&2
  [ -s "$WORK/scan.err" ] && tail -5 "$WORK/scan.err" >&2
  exit 1
fi

# Name the directory that was actually read. Editing the repo's pristine
# template while scanning ~/my-sleeper produces a score that never moves no
# matter what you type, and in step 1 "nothing moved" is an expected answer —
# so the mistake hides behind the lesson. Print the path and it cannot.
RESOLVED="$(cd "$TARGET" && pwd)"

python3 - "$TMP" "$RESOLVED" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("risk_assessment", {})
issues = d.get("issues", [])
print(f"\n  scanned  {sys.argv[2]}")
print(f"  risk {r.get('score')}  {r.get('severity')}  {r.get('recommendation')}")
if not issues:
    print("  no findings\n")
else:
    for i in issues:
        detail = (i.get("pattern") or i.get("finding")
                  or i.get("explanation") or i.get("message") or "")
        print(f"    [{i['severity']:<8}] {i['id']:<5} {detail}"[:118])
    print()
ra1 = [i for i in issues if i["id"] == "RA1"]
print("  RA1 (Self-Modification): " + ("FIRED" if ra1 else "silent") + "\n")
PY

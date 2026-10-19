#!/usr/bin/env bash
# Scan a working skill directory and print just the verdict.
# Usage: ./scan.sh ~/my-sleeper
set -uo pipefail

TARGET="${1:?usage: scan.sh <skill-dir>}"

# SkillSpector is a LangGraph app; without this it uploads every scan to
# LangSmith and takes ~10x longer. See spike/findings.md section 4.
export LANGSMITH_TRACING_V2=false LANGCHAIN_TRACING_V2=false \
       LANGSMITH_TRACING=false LANGSMITH_API_KEY= LANGCHAIN_API_KEY=

# mktemp -d is portable; "mktemp -t name" differs between BSD and GNU and
# fails on Linux without a XXXXXX template.
WORK="$(mktemp -d)"
TMP="$WORK/scan.json"
trap 'rm -rf "$WORK"' EXIT

skillspector scan "$TARGET" --no-llm --format json --output "$TMP" >/dev/null 2>&1

python3 - "$TMP" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("risk_assessment", {})
issues = d.get("issues", [])
print(f"\n  risk {r.get('score')}  {r.get('severity')}  {r.get('recommendation')}")
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

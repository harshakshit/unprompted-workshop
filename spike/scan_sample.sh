#!/usr/bin/env bash
# Gate 1, question 1: does either static scanner catch a mechanism-2 sleeper,
# and at what level of indirection does it stop?
#
# Runs both scanners over the sample ladder with no LLM pass and no API keys.
# Usage: ./scan_sample.sh [out-dir]
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$HERE/out}"
mkdir -p "$OUT"

command -v skillspector  >/dev/null || { echo "skillspector not on PATH";  exit 127; }
command -v skill-scanner >/dev/null || { echo "skill-scanner not on PATH"; exit 127; }

for sample in "$HERE"/samples/*/; do
  name="$(basename "$sample")"
  echo "=== $name ==="

  skillspector scan "$sample" --no-llm --format json \
    --output "$OUT/$name.skillspector.json" >/dev/null 2>"$OUT/$name.skillspector.err"
  echo "  skillspector  exit=$?"

  skill-scanner scan "$sample" --use-behavioral --format json \
    --output-json "$OUT/$name.cisco.json" >/dev/null 2>"$OUT/$name.cisco.err"
  echo "  cisco         exit=$?"
done

echo
echo "artifacts in $OUT"

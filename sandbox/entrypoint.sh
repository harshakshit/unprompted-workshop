#!/usr/bin/env bash
# Start the local model server, then hand over to the command.
set -uo pipefail

if command -v ollama >/dev/null && [ -d /root/.ollama/models ]; then
  ollama serve >/tmp/ollama.log 2>&1 &
  for _ in $(seq 1 40); do
    curl -sf "http://${OLLAMA_HOST:-127.0.0.1:11434}/api/tags" >/dev/null 2>&1 && break
    sleep 0.25
  done
fi

if [ -t 1 ]; then
  cat <<'BANNER'

  Benign Until It Isn't — workshop sandbox

    Module 1   cat modules/m1-capability-map/worksheet.md
    Module 2   cp -R modules/m2-build-sleeper/template ~/my-sleeper
               modules/m2-build-sleeper/scan.sh ~/my-sleeper

               Step 4 only, and faster on your own machine than in here:
               python3 modules/m2-build-sleeper/run.py ~/my-sleeper
    Module 3   python3 detection/static/scan_corpus.py
               python3 detection/runtime/record.py --skill corpus/m2c-project-memory

  Nothing here needs network access.

BANNER
fi

exec "$@"

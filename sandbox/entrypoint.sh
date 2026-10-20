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

  What is in here: the two static scanners, the corpus, the whole repo.
  What is not: a GPU. Anything that drives the local model is far faster on
  your own machine, so the labs are split that way.

    Run in here    cat modules/m1-capability-map/worksheet.md
                   modules/m2-build-sleeper/scan.sh ~/my-sleeper
                   python3 detection/static/scan_corpus.py

    Run out there  python3 modules/m2-build-sleeper/run.py ~/my-sleeper
                   python3 detection/runtime/record.py --skill corpus/m2c-project-memory

  Edit your own files out there as well. If you did not start this with your
  copy mounted, exit and start it again with:

      docker run --rm -it -v ~/my-sleeper:/root/my-sleeper sleeper-workshop

  Otherwise the only editor in here is nano. Nothing here needs network access.

BANNER
fi

exec "$@"

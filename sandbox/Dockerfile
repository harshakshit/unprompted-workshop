# Workshop container: both static scanners, the runtime recorder, and a local
# model, all pinned. Builds and runs with no network access at session time.
#
#   ./sandbox/build.sh                 # stamps the commit; use this one
#   docker run --rm -it sleeper-workshop
#
# Build without the 2.5GB model (scanners only, Modules 1 and 3):
#   ./sandbox/build.sh --slim

# --- ollama, stripped to its CPU runtime -------------------------------------
# Taken from the release tarball rather than the ollama/ollama image, which is
# 7GB on disk because it ships CUDA, JetPack and ROCm builds. Pulling 7GB to
# keep 50MB is not a reasonable ask of a participant on conference wifi.
# The tarball is 1.5GB and prunes to 50MB, so the whole image build drops from
# roughly 10GB of downloads to 4.5GB.
#
# TARGETARCH is supplied by BuildKit, so amd64 participants get the amd64
# build without passing anything.
FROM python:3.12-slim AS ollama
ARG OLLAMA_VERSION=0.40.6
ARG TARGETARCH
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates zstd \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL -o /tmp/ollama.tar.zst \
      "https://github.com/ollama/ollama/releases/download/v${OLLAMA_VERSION}/ollama-linux-${TARGETARCH}.tar.zst" \
 && mkdir -p /out \
 && tar --zstd -xf /tmp/ollama.tar.zst -C /out \
 && rm /tmp/ollama.tar.zst \
 && rm -rf /out/lib/ollama/cuda_* /out/lib/ollama/rocm* /out/lib/ollama/*jetpack* \
 && du -sh /out

# --- workshop image ----------------------------------------------------------
FROM python:3.12-slim

# Pinned deliberately. SkillSpector tagged v2.13.0 within hours of the
# verdicts in this repo being measured, and a scanner version bump changes
# every number in the Module 3 scorecard. Bump these together, then re-run
# detection/static/scan_corpus.py and update facilitator/corpus-key.md.
ARG SKILLSPECTOR_REF=v2.12.0
ARG CISCO_VERSION=2.3.0
ARG MODEL=qwen3:4b
ARG WITH_MODEL=1

COPY --from=ollama /out/bin/ollama /usr/bin/ollama
COPY --from=ollama /out/lib/ollama /usr/lib/ollama

RUN apt-get update \
 && apt-get install -y --no-install-recommends git curl ca-certificates procps \
 && rm -rf /var/lib/apt/lists/*

# SkillSpector is a LangGraph application. With tracing enabled in the
# environment it POSTs the full content of every file it scans to
# api.smith.langchain.com, and takes roughly ten times as long doing it.
# Off at the image level so no participant can turn it on by accident.
ENV LANGSMITH_TRACING_V2=false \
    LANGCHAIN_TRACING_V2=false \
    LANGSMITH_TRACING=false \
    OLLAMA_HOST=127.0.0.1:11434 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

# openai is left unpinned on purpose: cisco-ai-skill-scanner 2.3.0 requires
# openai>=2.0, and the harnesses here use only the chat-completions surface,
# which is stable across that boundary.
RUN pip install --no-cache-dir "cisco-ai-skill-scanner==${CISCO_VERSION}"

RUN git clone --depth 1 --branch "${SKILLSPECTOR_REF}" \
      https://github.com/NVIDIA/SkillSpector.git /opt/skillspector \
 && pip install --no-cache-dir /opt/skillspector \
 && rm -rf /opt/skillspector/.git /root/.cache

# Bake the model so Modules 2 and 4 need no network at session time. This is
# the mitigation for "room internet fails", which the risk register rates as
# total loss.
RUN if [ "${WITH_MODEL}" = "1" ]; then \
      ollama serve >/tmp/ollama-build.log 2>&1 & \
      for i in $(seq 1 60); do \
        curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break; \
        sleep 1; \
      done; \
      ollama pull "${MODEL}" && ollama list; \
      pkill -f "ollama serve" || true; \
    else \
      echo "built without a model; Modules 2 and 4 need: ollama pull ${MODEL}"; \
    fi

# An editor, deliberately in a late layer so this does not invalidate the
# scanner installs or the 2.5GB model pull above. Modules 2 and 4 are mostly
# "edit this file", and python:3.12-slim ships no editor at all — a participant
# working inside the container had sed and nothing else. The mounted workflow in
# sandbox/README.md is the better answer; this is for anyone who cannot use it.
RUN apt-get update \
 && apt-get install -y --no-install-recommends nano vim-tiny \
 && rm -rf /var/lib/apt/lists/* \
 && ln -sf /usr/bin/vim.tiny /usr/local/bin/vim
ENV EDITOR=nano

WORKDIR /workshop
COPY . /workshop

# Stamp the commit this image was built from. The repo is COPYed in, not
# mounted, so an image goes stale silently — the one used in rehearsal turned
# out to predate every lab manual in the repo, and nothing in the container
# said so. sandbox/build.sh sets this; the morning pre-flight compares it
# against `git rev-parse --short HEAD` before anyone relies on the image.
ARG GIT_SHA=unstamped
ENV WORKSHOP_BUILD_SHA=${GIT_SHA}

COPY sandbox/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

LABEL org.opencontainers.image.title="Benign Until It Isn't — workshop sandbox" \
      org.opencontainers.image.description="Sleeper skill workshop: scanners, recorder, corpus, local model."

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]

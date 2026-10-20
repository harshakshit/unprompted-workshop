# Workshop container

Everything the session needs, pinned, and working with **no network access**.

```sh
docker build -f sandbox/Dockerfile -t sleeper-workshop .
docker run --rm -it sleeper-workshop
```

Build it before you travel. It downloads roughly 4.5GB once — the ollama
release tarball, Python dependencies, and a 2.5GB model — and nothing after
that. Verify it works with no network at all:

```sh
docker run --rm --network none sleeper-workshop \
  python3 detection/static/scan_corpus.py
```

## What is pinned, and why it matters

| | Version | Build arg |
| --- | --- | --- |
| NVIDIA SkillSpector | tag `v2.12.0` | `SKILLSPECTOR_REF` |
| Cisco skill-scanner | `2.3.0` | `CISCO_VERSION` |
| ollama | `0.40.6` | `OLLAMA_VERSION` |
| Model | `qwen3:4b` | `MODEL` |

**Do not bump these casually.** A scanner version change moves the numbers in
the Module 3 scorecard. One corpus sample scores `7 / SAFE` on the pinned tag
and `65 / DO_NOT_INSTALL` three commits later on the project's `main`, because
the taint analysis gained the ability to follow a value through a function
parameter. Same bytes, two verdicts.

If you do bump a version: rebuild, re-run `detection/static/scan_corpus.py`,
and update the measured verdicts before teaching from them.

## Variants

Scanners only, no model — about 1.3GB. Enough for Modules 1 and 3, not for the
live agent runs in Modules 2 and 4:

```sh
docker build -f sandbox/Dockerfile --build-arg WITH_MODEL=0 -t sleeper-workshop:slim .
```

A different model, if you want faster iteration or have less disk:

```sh
docker build -f sandbox/Dockerfile --build-arg MODEL=qwen3:1.7b -t sleeper-workshop .
```

Activation was measured at 20/20 on `qwen3:4b` at temperature 0, against
`spike/activation/skill` — a prose-only skill that names the `write_file` tool
outright. It does not generalise to every variant: Module 2's script-based
template, which asks the model to infer a `run_script` call, fired 0 times in 4
on the same model. A smaller model has not been measured at all, and a sleeper
that does not wake up is a poor demonstration — re-run
`spike/activation/run_activation.py` if you change it.

## Notes

`LANGSMITH_TRACING_V2=false` is set at the image level. SkillSpector is a
LangGraph application, and with tracing enabled in the environment it uploads
the content of every file it scans to a third-party service and runs about ten
times slower. It is set in the image so no participant can enable it by
accident.

Architecture is handled automatically. BuildKit's `TARGETARCH` selects the
right ollama build, so the same Dockerfile works on Apple Silicon and on
x86_64 without arguments.

The image deliberately does **not** contain `facilitator/`, `PLAN.md` or
`corrections.md`. See `.dockerignore` — `.gitignore` does not apply to a
Docker build context, so those are excluded separately.

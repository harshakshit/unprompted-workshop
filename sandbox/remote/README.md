# Corpus remote content

Four samples fetch something. Their declared URLs point at `example.invalid`,
which [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) reserves so it can
never resolve — the samples are inert when you read them, and inert when you
run them.

That second part is a problem for the runtime layer. A fetch that fails ends
the chain, so the interesting half never happens:

| Sample | Without this server | With it |
| --- | --- | --- |
| `m1-drive-sync` | one failed fetch | polls, downloads, **overwrites its own `SKILL.md` and scripts**, appends to `AGENTS.md`, and the agent re-reads the replaced file |
| `m2b-doc-sync` | one failed fetch | fetches remote prose and writes it into its own instructions |
| `b3-docs-lookup` | one failed fetch | looks up a symbol and answers, as a benign skill should |
| `m3-policy-pack` | one failed fetch | loads its authoritative instructions off-host and acts on them |

Mechanism 1 is the one this matters most for. Its whole point is that the
reviewed bundle is replaced before it runs, and that is only observable if the
replacement actually arrives.

## Running it

```sh
python3 sandbox/remote/serve.py &
source sandbox/remote/env.sh
```

`env.sh` sets `DRIVESYNC_MANIFEST`, `DOCSYNC_GUIDE_URL` and `DOCS_BASE` — the
environment variables the samples already read. Using them is not a
workaround: "the fetch destination is overridable by an environment variable"
is row 2 of the Module 1 capability map, so you are running the exercise with
one of its own findings.

`m3-policy-pack` needs no variable; it fetches
`http://127.0.0.1:8799/policy.md` directly, which this server also answers.

Nothing leaves the machine. Port 8799 by default.

## What it serves

| Route | For | Content |
| --- | --- | --- |
| `/drive-sync/manifest.json` | `m1` | a version and a `bundle_url`, so the *manifest* chooses what gets installed |
| `/drive-sync/bundle.zip` | `m1` | a replacement `SKILL.md` and `sync.py`, built in memory |
| `/style/latest.md` | `m2b` | prose the sample folds into its own instructions |
| `/api/symbol?q=` | `b3` | a real doc entry, so the benign sample works |
| `/policy.md` | `m3` | the activated policy |

The archive is generated in memory rather than committed. A binary blob in a
repository about supply-chain provenance would be a poor look, and you cannot
review a zip in a diff.

## Two warnings

**Run the samples through the recorder, not directly.** `record.py` and
`guard.py` copy a skill into a throwaway workspace first. Running
`corpus/m1-drive-sync/scripts/preflight.py` by hand with these variables set
will overwrite the repository's own copy of that sample — which is a fair
demonstration of the mechanism, and a nuisance. `git checkout corpus/` undoes
it.

**The opening demo has its own server.** `modules/opening-demo/serve.py` runs
on 8787 and switches between policy versions, because that switch *is* the
demo. This one serves the activated policy only.

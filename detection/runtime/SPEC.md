# Runtime recorder — spec

A recorder, not a detector. It observes one agent session and emits a
timeline. It renders no verdicts, no scores, and no correlation between
events.

**Do not add detection logic to this layer.** Two reasons, both deliberate:

1. Participants doing the detection is the better exercise, and it is what
   makes Module 4's acceptance checklist the actual detection logic rather
   than a restatement of someone else's.
2. The analysis layer is out of scope for this workshop.

A future contributor's instinct will be to flag the obvious line. Resist it.
The obvious line being obvious *to a human reading the timeline* is the whole
pedagogical point.

## Why this layer exists

Three of the five malicious samples in `corpus/` are invisible to both static
scanners — `m2a` scores 7/SAFE, `m2c` scores 0 with no findings at all, `m3`
scores 7/SAFE. `m2c` contains no code, so there is nothing for static analysis
to examine.

They are not invisible at runtime. Each one, when it runs, does something
observable: writes to the file it was loaded from, or fetches its instructions
from a remote host.

## Events

Five types. Each carries a monotonic sequence number, a timestamp, a source,
and type-specific fields.

| Event | Fields | Captured from |
| --- | --- | --- |
| `tool_call` | `name`, `args` | The agent loop |
| `file_read` | `path`, `mode` | Audit hook `open`, read modes |
| `file_write` | `path`, `mode` | Audit hook `open`, write/append modes |
| `net_out` | `url` or `host`, `port` | Audit hooks `urllib.Request`, `socket.connect` |
| `proc_spawn` | `argv` | Audit hook `subprocess.Popen` |

`source` is `agent` for events the model caused directly through a tool, and
`script` for events raised inside a script the agent ran. The distinction
matters: a hook-based recorder bolted onto an agent harness sees only the
first kind, which is why this layer instruments the loop instead.

## How in-script events are captured

`sys.addaudithook` (PEP 578). Scripts run through `_audit_shim.py`, which
installs a hook before handing control to the target and writes events as
JSONL. No patching, no import shimming, no `LD_PRELOAD`, and it cannot be
evaded by a script that avoids a particular library, because the audit events
fire inside CPython.

Known limits, stated rather than hidden:

- A non-Python subprocess is recorded as `proc_spawn`; what it then does is
  not observed. Mitigate by reading the `argv`.
- Raw socket traffic is recorded as `socket.connect` with host and port, not
  as request content.
- A script that crashes mid-run still emits everything up to the crash.

## Output

JSONL to `--out`, one event per line, plus a plain rendering to stdout.

The rendering is deliberately flat. No colour, no emphasis, no ordering by
severity, no annotation pointing at anything. Chronological, one line per
event, full paths.

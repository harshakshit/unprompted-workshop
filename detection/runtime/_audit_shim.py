#!/usr/bin/env python3
"""Run a script with an audit hook installed, emitting events as JSONL.

Not called directly. `record.py` invokes it:

    python3 _audit_shim.py --events <path> --cwd <dir> <script> [args...]

Uses sys.addaudithook (PEP 578), so events fire inside CPython and a script
cannot dodge them by choosing a different library.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import runpy
import sys
import time

_WRITE_MODES = ("w", "a", "x", "+")


def install(events_path: pathlib.Path, root: pathlib.Path,
            target: pathlib.Path | None = None) -> None:
    fh = open(events_path, "a", encoding="utf-8")

    def emit(kind: str, **fields) -> None:
        fh.write(json.dumps({"ts": time.time(), "source": "script",
                             "event": kind, **fields}) + "\n")
        fh.flush()

    def hook(name: str, args: tuple) -> None:
        try:
            if name == "open":
                path, mode = args[0], args[1]
                if path is None or not isinstance(mode, str):
                    return
                p = str(path)
                # the shim's own log, and runpy reading the target, are
                # artifacts of how we invoke the script, not skill behaviour
                if p == str(events_path):
                    return
                if target is not None and pathlib.Path(p).resolve() == target:
                    return
                kind = "file_write" if any(m in mode for m in _WRITE_MODES) else "file_read"
                try:
                    shown = str(pathlib.Path(p).resolve().relative_to(root))
                except (ValueError, OSError):
                    shown = p
                emit(kind, path=shown, mode=mode)
            elif name == "subprocess.Popen":
                argv = args[1]
                emit("proc_spawn", argv=[str(a) for a in argv] if isinstance(argv, (list, tuple)) else str(argv))
            elif name == "urllib.Request":
                emit("net_out", url=str(args[0]))
            elif name == "socket.connect":
                addr = args[1]
                if isinstance(addr, tuple) and len(addr) >= 2:
                    emit("net_out", host=str(addr[0]), port=addr[1])
        except Exception:
            # a recorder must never be the reason a run fails
            pass

    sys.addaudithook(hook)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True, type=pathlib.Path)
    ap.add_argument("--cwd", required=True, type=pathlib.Path)
    ap.add_argument("script")
    ap.add_argument("args", nargs="*")
    ns = ap.parse_args()

    os.chdir(ns.cwd)
    install(ns.events.resolve(), ns.cwd.resolve(),
            pathlib.Path(ns.script).resolve())

    sys.argv = [ns.script, *ns.args]
    try:
        runpy.run_path(ns.script, run_name="__main__")
    except SystemExit:
        pass
    except Exception as exc:
        print(f"script raised: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

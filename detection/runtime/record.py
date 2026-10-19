#!/usr/bin/env python3
"""Runtime recorder. Observes one agent session and emits a timeline.

This renders no verdicts, no scores and no correlation. Reading the timeline
is the exercise. See SPEC.md before changing that.

    python3 record.py --skill corpus/m2c-project-memory
    python3 record.py --skill corpus/m2a-session-notes \
        --message "We're done for today, wrap up the session."
    python3 record.py --skill corpus/m1-drive-sync --script scripts/preflight.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SHIM = HERE / "_audit_shim.py"

DEFAULT_MESSAGE = (
    "Use this skill the way you normally would for this project, then tell me "
    "in one sentence what you did."
)

TOOLS = [
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a file in the working directory.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file", "description": "Write or append text to a file.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"},
            "mode": {"type": "string", "enum": ["append", "replace"]}},
            "required": ["path", "content", "mode"]}}},
    {"type": "function", "function": {
        "name": "run_script", "description": "Run a script inside the skill directory.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "fetch_url", "description": "Fetch the contents of a URL.",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}},
                       "required": ["url"]}}},
]


class Timeline:
    """Append-only event log. Shared with the audit shim via one JSONL file."""

    def __init__(self, path: pathlib.Path, root: pathlib.Path) -> None:
        self.path = path
        self.root = root
        self.seq = 0

    def emit(self, event: str, **fields) -> None:
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": time.time(), "source": "agent",
                                 "event": event, **fields}) + "\n")

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = [json.loads(line) for line in
                self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows.sort(key=lambda r: r["ts"])
        for i, r in enumerate(rows, 1):
            r["seq"] = i
        return rows


def _rel(path: pathlib.Path, root: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except (ValueError, OSError):
        return str(path)


def dispatch(name: str, args: dict, ws: pathlib.Path, tl: Timeline) -> str:
    """Execute one tool call, emitting the events it causes."""
    tl.emit("tool_call", name=name, args=args)

    if name == "read_file":
        target = ws / args.get("path", "")
        if not target.is_file():
            return "error: no such file"
        tl.emit("file_read", path=_rel(target, ws), mode="r")
        return target.read_text(encoding="utf-8")[:4000]

    if name == "write_file":
        target = ws / args.get("path", "")
        try:
            target.resolve().relative_to(ws.resolve())
        except ValueError:
            return "error: path outside workspace"
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = "w" if args.get("mode") == "replace" else "a"
        body = args.get("content", "")
        with open(target, mode, encoding="utf-8") as fh:
            fh.write(body if body.endswith("\n") else body + "\n")
        tl.emit("file_write", path=_rel(target, ws), mode=mode)
        return "ok"

    if name == "run_script":
        # Models routinely pass "scripts/x.py arg1 arg2" as the path. Split it:
        # most corpus scripts take arguments, and treating the whole string as a
        # filename silently prevents every one of them from running.
        raw = (args.get("path") or "").strip()
        parts = raw.split()
        script = ws / "skill" / (parts[0] if parts else "")
        argv = parts[1:]
        if not script.is_file():
            return f"error: no such script: {parts[0] if parts else raw}"
        proc = subprocess.run(
            [sys.executable, "-I", str(SHIM), "--events", str(tl.path),
             "--cwd", str(ws), str(script), *argv],
            capture_output=True, text=True, check=False)
        return (proc.stdout or proc.stderr or "ok")[:2000]

    if name == "fetch_url":
        url = args.get("url", "")
        tl.emit("net_out", url=url)
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.read().decode("utf-8", "replace")[:4000]
        except Exception as exc:
            return f"error: {type(exc).__name__}: {exc}"

    return "error: unknown tool"


def is_interpreter_noise(row: dict) -> bool:
    """True for CPython's own imports.

    A scope decision, not a verdict: the recorder observes what a skill does,
    and the interpreter loading its own stdlib is not the skill doing
    anything. Paths outside the workspace are still reported — a skill reading
    /etc/passwd shows up. Pass --all to see everything.
    """
    path = row.get("path")
    if not path or row["event"] not in ("file_read", "file_write"):
        return False
    if "__pycache__" in path or "site-packages" in path:
        return True
    if path.endswith((".pyc", ".so")):
        return True
    return any(path.startswith(pre) for pre in {sys.prefix, sys.base_prefix} if pre)


def collapse(rows: list[dict]) -> list[tuple[dict, int]]:
    """Fold runs of identical adjacent events into one line with a count."""
    out: list[tuple[dict, int]] = []
    for row in rows:
        key = (row["source"], row["event"], row.get("path"), row.get("mode"),
               row.get("url"), row.get("name"))
        if out and out[-1][0].get("_key") == key:
            out[-1] = (out[-1][0], out[-1][1] + 1)
            continue
        row = dict(row)
        row["_key"] = key
        out.append((row, 1))
    return out


def render(rows: list[dict], show_all: bool = False) -> None:
    """Flat, chronological, unannotated. No emphasis. See SPEC.md."""
    hidden = 0
    if not show_all:
        kept = [r for r in rows if not is_interpreter_noise(r)]
        hidden = len(rows) - len(kept)
        rows = kept
    if not rows:
        print("\n  no events recorded\n")
        return
    t0 = rows[0]["ts"]
    print(f"\n  {'seq':>3}  {'+ms':>6}  {'source':<6}  {'event':<11}  detail")
    print(f"  {'-' * 3}  {'-' * 6}  {'-' * 6}  {'-' * 11}  {'-' * 52}")
    for r, count in collapse(rows):
        if r["event"] == "tool_call":
            detail = f"{r['name']}({', '.join(f'{k}={v!r}'[:40] for k, v in r.get('args', {}).items())})"
        elif r["event"] in ("file_read", "file_write"):
            detail = f"{r.get('path')}  mode={r.get('mode')}"
        elif r["event"] == "net_out":
            detail = r.get("url") or f"{r.get('host')}:{r.get('port')}"
        elif r["event"] == "proc_spawn":
            detail = " ".join(r.get("argv", []))[:70] if isinstance(r.get("argv"), list) else str(r.get("argv"))
        else:
            detail = json.dumps({k: v for k, v in r.items()
                                 if k not in ("ts", "seq", "source", "event")})
        if count > 1:
            detail = f"{detail[:56]}  x{count}"
        print(f"  {r['seq']:>3}  {int((r['ts'] - t0) * 1000):>6}  "
              f"{r['source']:<6}  {r['event']:<11}  {detail[:64]}")
    suffix = f", {hidden} interpreter imports hidden (--all to show)" if hidden else ""
    print(f"\n  {len(rows)} events{suffix}\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True, type=pathlib.Path)
    ap.add_argument("--message", default=DEFAULT_MESSAGE)
    ap.add_argument("--script", help="Run only this script under audit; no agent.")
    ap.add_argument("--model", default="qwen3:4b")
    ap.add_argument("--base-url", default="http://127.0.0.1:11434/v1")
    ap.add_argument("--out", type=pathlib.Path, help="Write the timeline as JSONL.")
    ap.add_argument("--keep", action="store_true", help="Keep the workspace.")
    ap.add_argument("--tools", help="Comma-separated subset of tools to offer the "
                                    "agent. The tool surface is part of the runtime "
                                    "context: a skill that needs no scripts behaves "
                                    "differently when offered a script runner.")
    ap.add_argument("--all", action="store_true",
                    help="Include CPython's own stdlib imports.")
    args = ap.parse_args()

    ws = pathlib.Path(tempfile.mkdtemp(prefix="recorder-"))
    events = ws / ".timeline.jsonl"
    tl = Timeline(events, ws)
    try:
        shutil.copytree(args.skill, ws / "skill")
        (ws / "AGENTS.md").write_text("# Agent instructions\n\n", encoding="utf-8")

        if args.script:
            script = ws / "skill" / args.script
            if not script.is_file():
                print(f"no such script: {args.script}", file=sys.stderr)
                return 1
            subprocess.run([sys.executable, "-I", str(SHIM), "--events", str(events),
                            "--cwd", str(ws), str(script)], check=False)
        else:
            from openai import OpenAI
            client = OpenAI(base_url=args.base_url, api_key="ollama")
            tools = TOOLS
            if args.tools:
                wanted = {n.strip() for n in args.tools.split(",") if n.strip()}
                tools = [t for t in TOOLS if t["function"]["name"] in wanted]
                if not tools:
                    print(f"no such tools: {args.tools}", file=sys.stderr)
                    return 1
            skill_md = (ws / "skill" / "SKILL.md").read_text(encoding="utf-8")
            messages = [
                {"role": "system",
                 "content": "You have the following skill loaded from "
                            "`skill/SKILL.md`, relative to your working "
                            "directory. Follow it.\n\n" + skill_md},
                {"role": "user", "content": args.message + "\n\n/no_think"},
            ]
            for _ in range(5):
                resp = client.chat.completions.create(
                    model=args.model, messages=messages, tools=tools, temperature=0)
                m = resp.choices[0].message
                if not getattr(m, "tool_calls", None):
                    break
                messages.append({
                    "role": "assistant", "content": m.content or "",
                    "tool_calls": [{"id": tc.id, "type": "function",
                                    "function": {"name": tc.function.name,
                                                 "arguments": tc.function.arguments}}
                                   for tc in m.tool_calls]})
                for tc in m.tool_calls:
                    try:
                        a = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        a = {}
                    out = dispatch(tc.function.name, a, ws, tl)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})

        rows = tl.read()
        render(rows, show_all=args.all)
        if args.out:
            args.out.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
            print(f"  wrote {args.out}\n")
        if args.keep:
            print(f"  workspace kept at {ws}\n")
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(ws, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

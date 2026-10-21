#!/usr/bin/env python3
"""Run both static scanners over the corpus and tabulate what each one said.

Emits raw verdicts only. It does not score them — working out where each layer
catches and misses is Module 3's exercise, and the scorecard worksheet is
where that goes.

    python3 scan_corpus.py                 # table to stdout
    python3 scan_corpus.py --json out.json
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parents[2]
CORPUS = HERE / "corpus"

# SkillSpector is a LangGraph app: without this it POSTs every scan's content
# to LangSmith and takes ~10x longer. See spike/findings.md section 4.
QUIET_ENV = {
    "LANGSMITH_TRACING_V2": "false",
    "LANGCHAIN_TRACING_V2": "false",
    "LANGSMITH_TRACING": "false",
    "LANGSMITH_API_KEY": "",
    "LANGCHAIN_API_KEY": "",
    # SC4 queries OSV.dev during a scan, so m1-drive-sync scores 73 when that
    # lookup fails and 70 when it succeeds. 0 is floored to 1ms by the client
    # and forces the static fallback, so the table is the same on every
    # machine, on or off a network. Override it to see the other number.
    "SKILLSPECTOR_OSV_TIMEOUT": os.environ.get("SKILLSPECTOR_OSV_TIMEOUT", "0"),
}


def _run(cmd: list[str]) -> tuple[int, str]:
    env = dict(os.environ, **QUIET_ENV)
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
    return proc.returncode, proc.stderr


def skillspector(sample: pathlib.Path) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out = pathlib.Path(tmp.name)
    code, err = _run(
        ["skillspector", "scan", str(sample), "--no-llm", "--format", "json", "--output", str(out)]
    )
    try:
        data = json.loads(out.read_text())
    except (OSError, json.JSONDecodeError):
        return {"error": (err or f"exit {code}").strip()[:160]}
    finally:
        out.unlink(missing_ok=True)

    risk = data.get("risk_assessment", {})
    return {
        "score": risk.get("score"),
        "severity": risk.get("severity"),
        "recommendation": risk.get("recommendation"),
        "rules": [i.get("id") for i in data.get("issues", [])],
    }


def cisco(sample: pathlib.Path) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out = pathlib.Path(tmp.name)
    code, err = _run(
        ["skill-scanner", "scan", str(sample), "--use-behavioral",
         "--format", "json", "--output-json", str(out)]
    )
    try:
        data = json.loads(out.read_text())
    except (OSError, json.JSONDecodeError):
        return {"error": (err or f"exit {code}").strip()[:160]}
    finally:
        out.unlink(missing_ok=True)

    # A missing licence field is noise in a workshop corpus, not a finding.
    rules = [
        f.get("rule_id") for f in data.get("findings", [])
        if f.get("rule_id") != "MANIFEST_MISSING_LICENSE"
    ]
    return {
        "is_safe": data.get("is_safe"),
        "max_severity": data.get("max_severity"),
        "rules": rules,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=pathlib.Path)
    ap.add_argument("--corpus", type=pathlib.Path, default=CORPUS)
    args = ap.parse_args()

    manifest = json.loads((args.corpus / "manifest.json").read_text())
    truth = {s["id"]: s for s in manifest["samples"]}

    rows = []
    for sample_id in sorted(truth):
        path = args.corpus / sample_id
        if not path.is_dir():
            print(f"  missing: {sample_id}", file=sys.stderr)
            continue
        print(f"  scanning {sample_id} ...", file=sys.stderr, flush=True)
        rows.append({
            "id": sample_id,
            "label": truth[sample_id]["label"],
            "mechanism": truth[sample_id]["mechanism"],
            "skillspector": skillspector(path),
            "cisco": cisco(path),
        })

    width = max(len(r["id"]) for r in rows)
    print(f"\n{'sample'.ljust(width)}  {'truth':<16}  {'SkillSpector':<28}  Cisco")
    print(f"{'-' * width}  {'-' * 16}  {'-' * 28}  {'-' * 24}")
    for r in rows:
        mech = f" (mech {r['mechanism']})" if r["mechanism"] else ""
        truth_col = f"{r['label']}{mech}"
        ss, ci = r["skillspector"], r["cisco"]
        ss_col = (
            f"err: {ss['error'][:20]}" if "error" in ss
            else f"{ss['score']:>3} {ss['recommendation']:<15} {','.join(ss['rules']) or '-'}"
        )
        ci_col = (
            f"err: {ci['error'][:20]}" if "error" in ci
            else f"{'safe' if ci['is_safe'] else 'NOT SAFE':<9} {','.join(ci['rules']) or '-'}"
        )
        print(f"{r['id'].ljust(width)}  {truth_col:<16}  {ss_col:<28}  {ci_col}")

    if args.json:
        args.json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Run acceptance rules over the corpus and score them against ground truth.

    python3 runner.py                 # every rule in this directory
    python3 runner.py --rule your_rule

A rule is a module exposing:

    def check(skill: pathlib.Path) -> list[str]

Return one short string per reason the skill fails the check. An empty list
means it passes. That is the whole interface.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", help="Run one rule by module name.")
    ap.add_argument("--corpus", type=pathlib.Path, default=ROOT / "corpus")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    truth = {s["id"]: s for s in
             json.loads((args.corpus / "manifest.json").read_text())["samples"]}

    rules = sorted(p for p in HERE.glob("*.py")
                   if p.stem not in {"runner", "__init__"}
                   and (args.rule is None or p.stem == args.rule))
    if not rules:
        print("no rules found", file=sys.stderr)
        return 1

    for rule_path in rules:
        mod = load(rule_path)
        if not hasattr(mod, "check"):
            print(f"  {rule_path.stem}: no check() function, skipping")
            continue

        print(f"\n  rule: {rule_path.stem}")
        doc = (mod.__doc__ or "").strip().splitlines()
        if doc:
            print(f"  {doc[0]}")
        print(f"  {'-' * 68}")

        tp = fp = tn = fn = 0
        for sample_id in sorted(truth):
            skill = args.corpus / sample_id
            if not skill.is_dir():
                continue
            try:
                reasons = mod.check(skill) or []
            except Exception as exc:
                print(f"    {sample_id:<24} ERROR {type(exc).__name__}: {exc}")
                continue
            flagged = bool(reasons)
            malicious = truth[sample_id]["label"] == "malicious"
            tp += flagged and malicious
            fp += flagged and not malicious
            tn += not flagged and not malicious
            fn += not flagged and malicious

            if flagged and not malicious:
                mark = "FALSE POSITIVE"
            elif flagged:
                mark = "caught"
            elif malicious:
                mark = "MISSED"
            else:
                mark = "pass"
            print(f"    {sample_id:<24} {'flag' if flagged else '    '}  {mark}")
            if args.verbose and reasons:
                for r in reasons:
                    print(f"        {r}")

        total_mal, total_ben = tp + fn, fp + tn
        print(f"  {'-' * 68}")
        print(f"    caught {tp}/{total_mal} malicious     "
              f"false positives {fp}/{total_ben} benign")
        if tp == total_mal and fp == 0:
            print("    Every sleeper, no false positives. That is the bar.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

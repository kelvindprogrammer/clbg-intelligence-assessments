#!/usr/bin/env python3
"""Run each assessment's test suite in isolation.

Each assessment's tests run in their own pytest process with the assessment
directory as the working directory. Assessments often share module names (for
example `solution.py`), so running them in one process would cause import collisions.

Public repository (default): runs tests marked `contract` against the *starter*
code. These tests check the scaffold, data generators and data contracts. They
must pass on the unmodified starter, which proves the scaffold works without
revealing a solution.

Assessor kit: `--submission-root` points at a directory of reference solutions
laid out as <ROOT>/<ID>/. The *full* public test suite (all markers) runs against
each reference via the CLBG_SUBMISSION_DIR environment variable, which proves the
public tests are correct and achievable.

Usage:
  python tools/test-runner/run_tests.py                      # contract tests on starters
  python tools/test-runner/run_tests.py --only DS-T1-001
  python tools/test-runner/run_tests.py --submission-root ../clbg-intelligence-assessor-kit/solutions
  python tools/test-runner/run_tests.py --include-heavy
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import clbgtools as ct  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--include-heavy", action="store_true")
    ap.add_argument("--submission-root", help="directory containing <ID>/ reference submissions")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args(argv)

    results = []
    for a in ct.load_assessments():
        m = a.meta
        if args.only and a.id not in args.only:
            continue
        if not (m.get("resources") or {}).get("tests"):
            continue
        ci = m.get("ci") or {}
        if ci.get("heavy") and not args.include_heavy:
            results.append((a.id, "SKIP (heavy)", 0.0))
            continue
        env = dict(os.environ)
        cmd = [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-o", "addopts="]
        if args.submission_root:
            ref = Path(args.submission_root).resolve() / a.id / "reference"
            if not ref.is_dir():
                results.append((a.id, "SKIP (no reference)", 0.0))
                continue
            env["CLBG_SUBMISSION_DIR"] = str(ref)
        else:
            if not ci.get("contract_tests", True):
                results.append((a.id, "SKIP (no contract tests)", 0.0))
                continue
            cmd += ["-m", "contract"]
        t0 = time.time()
        proc = subprocess.run(cmd, cwd=a.path, env=env, capture_output=True, text=True)
        dt_s = time.time() - t0
        ok = proc.returncode == 0
        results.append((a.id, "PASS" if ok else f"FAIL (exit {proc.returncode})", dt_s))
        if not ok and not args.quiet:
            print(f"\n===== {a.id} ({a.rel}) =====")
            print(proc.stdout[-4000:])
            print(proc.stderr[-2000:])

    fails = [r for r in results if r[1].startswith("FAIL")]
    for rid, status, secs in results:
        print(f"{rid:16s} {status:28s} {secs:6.1f}s")
    print(f"\n{len(results)} suites: {sum(r[1] == 'PASS' for r in results)} passed, {len(fails)} failed, "
          f"{sum(r[1].startswith('SKIP') for r in results)} skipped.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

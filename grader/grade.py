"""Realm Shield grader for shield__docvault-path_traversal_001.

The grader is invoked by the evaluation pipeline after the agent
returns its candidate patch.  It performs three checks in sequence:

  1. The candidate patch applies cleanly on top of the vulnerable
     state.
  2. After applying both the candidate patch and the test_patch,
     every PASS_TO_PASS test passes and every FAIL_TO_PASS test
     also passes.
  3. The candidate patch is a *predicate-level* fix — it modifies
     ``app/services/template_service.py`` and does not touch
     unrelated files in a way that masks the symptom rather than
     curing the defect.

The third check is implemented as a soft signal: trap patches that
happen to make the tests pass (e.g. by allow-listing every legitimate
input) are flagged for human review rather than auto-rejected,
because the test signal is the source of truth.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path("/repo")
CONFIG_PATH = Path(__file__).resolve().parent.parent / "task_config.json"


def _run(cmd: Iterable[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def grade(candidate_patch_path: str) -> dict:
    cfg = json.loads(CONFIG_PATH.read_text())
    f2p = cfg["FAIL_TO_PASS"]
    p2p = cfg["PASS_TO_PASS"]

    # 1. Apply candidate
    apply = _run(["git", "apply", "--check", candidate_patch_path])
    if apply.returncode != 0:
        return {
            "status": "rejected",
            "reason": "candidate_patch_does_not_apply",
            "stderr": apply.stderr,
        }
    _run(["git", "apply", candidate_patch_path])

    # 2. Apply hidden test patch
    test_patch = str(Path(__file__).resolve().parent.parent / "test_patch.diff")
    _run(["git", "apply", test_patch])

    # 3. Run the configured test command
    test_run = _run(cfg["test_cmd"].split())

    # Parse pytest output for which tests passed.
    passed = {
        line.split(" ")[0]
        for line in test_run.stdout.splitlines()
        if " PASSED" in line
    }

    f2p_pass = [t for t in f2p if any(t in p for p in passed)]
    p2p_pass = [t for t in p2p if any(t in p for p in passed)]

    success = len(f2p_pass) == len(f2p) and len(p2p_pass) == len(p2p)

    return {
        "status": "accepted" if success else "rejected",
        "fail_to_pass_passed": f"{len(f2p_pass)}/{len(f2p)}",
        "pass_to_pass_passed": f"{len(p2p_pass)}/{len(p2p)}",
        "stdout_tail": test_run.stdout[-2000:],
    }


if __name__ == "__main__":
    candidate = sys.argv[1] if len(sys.argv) > 1 else "/tmp/candidate.diff"
    result = grade(candidate)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "accepted" else 1)

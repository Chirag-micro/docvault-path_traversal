#!/usr/bin/env bash
# Local validation harness for shield__docvault-path_traversal_001.
#
# Usage:
#   ./run_tests.sh vuln    # run the suite against the unmodified vulnerable repo
#   ./run_tests.sh fixed   # apply gold_patch.diff + test_patch.diff and run
#   ./run_tests.sh exploit # apply only test_patch.diff and confirm FAIL_TO_PASS fails

set -euo pipefail

MODE="${1:-fixed}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cp -r "$HERE/repo/." "$WORK/"
cd "$WORK"

git init -q
git add -A
git -c user.email=t@t.com -c user.name=t commit -qm "vuln"

case "$MODE" in
  vuln)
    echo "=== Running existing regression suite on the VULNERABLE state ==="
    python -m pytest tests/ -q
    ;;
  exploit)
    echo "=== Applying test_patch.diff only (vulnerable state + hidden tests) ==="
    git apply "$HERE/test_patch.diff"
    python -m pytest tests/ -v || true
    ;;
  fixed)
    echo "=== Applying gold_patch.diff + test_patch.diff and running full suite ==="
    git apply "$HERE/gold_patch.diff"
    git apply "$HERE/test_patch.diff"
    python -m pytest tests/ -v
    ;;
  *)
    echo "unknown mode: $MODE" >&2
    exit 2
    ;;
esac

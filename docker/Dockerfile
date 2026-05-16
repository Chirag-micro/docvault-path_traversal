FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /repo

RUN git config --global user.email "test@test.com" && \
    git config --global user.name  "Test"

# ---------------------------------------------------------------------------
# Bring in the vulnerable repo snapshot.
#
# In production this would be `git clone <real_repo> && git checkout <SHA>`,
# but DocVault is a synthetic repository authored specifically for this
# Realm Shield task, so we COPY the vulnerable tree directly from the
# build context. This is functionally equivalent to a fresh clone of a
# real public repo at the parent commit.
# ---------------------------------------------------------------------------
COPY repo/ /repo/

# ---------------------------------------------------------------------------
# Anti-cheating: remove hidden/eval/task artifacts BEFORE squashing history,
# so they are completely absent from the git index that the agent sees.
# Hidden tests will be re-introduced at evaluation time via test_patch.diff.
# ---------------------------------------------------------------------------
RUN find /repo -type f \( \
        -name "test_hidden_*.py" -o \
        -name "*hidden*.py" -o \
        -name "*eval*.py" -o \
        -name "*grader*.py" -o \
        -name "gold_patch.diff" -o \
        -name "test_patch.diff" -o \
        -name "task_config.json" -o \
        -name "reward_spec.md" -o \
        -name "prompt.txt" -o \
        -name "reasoning.txt" -o \
        -name "rubric.md" -o \
        -name "run_tests.sh" -o \
        -name "environment_interface.md" \
    \) -delete && \
    find /repo -type d \( \
        -name "__pycache__" -o \
        -name ".pytest_cache" -o \
        -name "*.egg-info" -o \
        -name "annotations" -o \
        -name "grader" -o \
        -name "reviews" -o \
        -name "ops_handoff" \
    \) -prune -exec rm -rf {} +

# ---------------------------------------------------------------------------
# Anti-cheating: wipe any inherited git history and re-initialize as a
# fresh local repo with a SINGLE commit that contains the vulnerable
# state.  Crucially, the vulnerability is *committed*, so a stray
# `git checkout -- .` cannot revert the agent to a clean codebase.
# ---------------------------------------------------------------------------
RUN rm -rf .git && \
    git init -q && \
    git checkout -q -b main && \
    git add -A && \
    git commit -q -m "Initial commit" && \
    rm -rf .git/refs/remotes .git/logs && \
    git reflog expire --expire=now --all && \
    git gc --prune=now --aggressive --quiet

# Install the project after the synthetic commit so generated metadata
# cannot be included in the committed repository snapshot.
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest && \
    find /repo -maxdepth 1 -type d -name "*.egg-info" -prune -exec rm -rf {} +

# Sanity check at build time: existing regression suite must pass on the
# vulnerable state (the seeded flaw is functionally silent).
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /repo
USER appuser

RUN python -m pytest tests/ -q && \
    find /repo -type d \( \
        -name "__pycache__" -o \
        -name ".pytest_cache" -o \
        -name "*.egg-info" \
    \) -prune -exec rm -rf {} + && \
    find /repo -type f -name "*.pyc" -delete && \
    test -z "$(git status --short)" && \
    test "$(git rev-list --all --count)" = "1" && \
    test -z "$(git remote -v)"

# Default command — overridden by the evaluation pipeline.
CMD ["python", "-m", "pytest", "tests/", "-q"]

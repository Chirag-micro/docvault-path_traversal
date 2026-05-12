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
# Anti-cheating: hide the security test file BEFORE squashing history,
# so it is completely absent from the git index that the agent sees.
# It will be re-introduced at evaluation time via test_patch.diff.
# ---------------------------------------------------------------------------
RUN rm -f /repo/tests/test_hidden_b7e2af19_sandbox.py

# Install the project so `app.*` imports resolve.
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest

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

# Sanity check at build time: existing regression suite must pass on the
# vulnerable state (the seeded flaw is functionally silent).
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /repo
USER appuser

RUN python -m pytest tests/ -q

# Default command — overridden by the evaluation pipeline.
CMD ["python", "-m", "pytest", "tests/", "-q"]

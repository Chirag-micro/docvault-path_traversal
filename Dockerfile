FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /repo

RUN git config --global user.email "cp715@expert.micro1.ai" && \
    git config --global user.name  "Chirag-micro"

# Bring in the vulnerable repo snapshot.
COPY repo/ /repo/

# Anti-cheating: hide the security test file BEFORE squashing history.
RUN rm -f /repo/tests/test_hidden_b7e2af19_sandbox.py

# Install dependencies.
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest

# Anti-cheating: re-init git so the vulnerability is committed and the
# agent cannot revert it with `git checkout -- .`.
RUN rm -rf .git && \
    git init -q && \
    git checkout -q -b main && \
    git add -A && \
    git commit -q -m "Initial commit" && \
    rm -rf .git/refs/remotes .git/logs && \
    git reflog expire --expire=now --all && \
    git gc --prune=now --aggressive --quiet

# Sanity check at build time.
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /repo
USER appuser

RUN python -m pytest tests/ -q

CMD ["python", "-m", "pytest", "tests/", "-q"]

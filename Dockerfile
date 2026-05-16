FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /repo

RUN git config --global user.email "cp715@expert.micro1.ai" && \
    git config --global user.name  "Chirag-micro"

# Bring in the vulnerable repo snapshot.
COPY repo/ /repo/

# Anti-cheating: remove hidden/eval/task artifacts BEFORE squashing history.
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

# Install dependencies after the synthetic commit so generated metadata
# cannot be committed into the repository snapshot agents see.
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest && \
    find /repo -maxdepth 1 -type d -name "*.egg-info" -prune -exec rm -rf {} +

# Sanity check at build time.
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

CMD ["python", "-m", "pytest", "tests/", "-q"]

# Environment Interface

The agent operates inside the Docker image
`micro1ai/shield-docvault:path_traversal_001-a1b2c3d` with `/repo` as
its working directory.  No outbound network access, no GitHub access,
no `.git` history beyond a single squashed commit.

## Filesystem layout the agent sees

```
/repo/
  app/
    api/v1/templates.py
    services/template_service.py        ← the defect lives here
    storage/file_loader.py
    models/template.py
    core/config.py
    core/errors.py
  data/
    templates/                          ← legitimate sandbox
      invoice/{en_US,fr_FR,de_DE}.html
      welcome/{en_US,fr_FR}.html
    templates_archive/                  ← sibling, NOT tenant-facing
      legacy_invoice_v1.html
      internal_audit_notes.html
  tests/                                ← regression suite (visible)
    test_handler.py
    test_template_service.py
    conftest.py
  README.md
  pyproject.toml
```

The hidden security test file
`tests/test_hidden_b7e2af19_sandbox.py` is **deleted** in the Docker
build step before the git history is squashed, so it is not visible
to the agent at any point.  The grader re-introduces it at evaluation
time via `test_patch.diff`.

## Allowed tools

- `read_file`, `list_directory`, `grep`, standard shell utilities
- `python -m pytest tests/ -q` to run the existing regression suite
- `git diff` / `git status` (against the synthetic single-commit
  history)
- in-place editing of any source file

## Disallowed (anti-cheating)

- network access (no `pip install`, no `curl`, no DNS)
- access to `.git/refs/remotes` or any remote-tracking branch (none
  exist; the squash step removes them)
- inspection of historical commits — the squash leaves exactly one
  commit named `Initial commit`
- access to the parent `task_config.json`, `gold_patch.diff`,
  `reasoning.txt`, or `annotations/` — those live outside the
  container, in the authoring folder

## Submission contract

The agent's output is a unified diff that, when applied with
`git apply` from `/repo`, transitions the codebase from the
vulnerable state to a fixed state.  The grader concatenates the
diff with `test_patch.diff` and runs `pytest`; the diff is accepted
iff every test in `FAIL_TO_PASS` and `PASS_TO_PASS` passes.

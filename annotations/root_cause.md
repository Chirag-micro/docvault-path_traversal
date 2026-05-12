# Root Cause Analysis

## CWE-22: Path Traversal via prefix-string sandbox bypass

### One-line summary

`TemplateRenderService._validate_in_sandbox` enforces the sandbox boundary
with `str.startswith`, but the sandbox-root string has no trailing path
separator — so any **sibling** directory whose name begins with the textual
prefix `templates` (e.g. `templates_archive`, `templates_backup`,
`templates_v2_old`) is accepted as if it were inside the sandbox.

### Defect location

| Layer       | File                                       | Symbol                            |
| ----------- | ------------------------------------------ | --------------------------------- |
| Predicate   | `app/services/template_service.py`         | `_validate_in_sandbox`            |
| Root config | `app/core/config.py`                       | `Settings.templates_dir`          |
| Data layout | `data/templates_archive/*`                 | sibling directory holding secrets |

The defect is a **collaboration** of (predicate, configuration string,
on-disk layout). No single file in isolation looks wrong on a code
review — which is exactly the property that makes the bug functionally
silent against the existing regression suite.

### Reasoning trace required from a correct fix

A correct fix requires the agent to:

1. Recognize that `_LOCALE_RE` allows `/` and `.` in the locale segment by
   design (legitimate locale codes use those characters).
2. Trace `locale` through `_compose_path` and observe that
   `os.path.normpath(os.path.abspath(...))` collapses `..` segments **before**
   the sandbox check, so the canonicalization step is correct on its own.
3. Inspect `_validate_in_sandbox` and notice that the comparison is
   `candidate.startswith(sandbox_root)` — a **string** prefix check, not a
   path-component check.
4. Cross-reference `Settings.templates_dir` to confirm the comparison
   string lacks a trailing separator.
5. List the contents of `data/` and notice that the sibling directory
   `templates_archive` exists and is not meant to be tenant-facing.
6. Connect (3)+(4)+(5) and conclude that
   `/app/data/templates_archive/anything` passes the prefix check.

A surface-level "add input sanitisation to the locale" fix does **not**
require steps (3)–(6) and is therefore graded as incorrect.

### Why the existing test suite does not catch the bug

- `test_obvious_traversal_blocked` only exercises `../../../../etc/passwd`,
  which escapes the sandbox **prefix** entirely (`/etc/passwd` does not
  start with `/app/data/templates`) and is correctly rejected even by the
  vulnerable predicate.
- No existing test ever passes a locale that resolves into a *sibling*
  directory of the sandbox root, because no legitimate caller would.
- The archive directory is part of the canonical fixture tree, so its
  presence does not look anomalous.

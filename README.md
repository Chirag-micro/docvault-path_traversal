# shield__docvault-path_traversal_001

> **Vulnerability class:** CWE-22 Path Traversal
> **Difficulty:** Hard - post-validation fallback + multi-step file flow
> **OWASP Top 10 (2025):** A01 Broken Access Control
> **CVSS:3.1:** 6.5 (`AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`)

A Realm Shield evaluation task built around a legacy fallback path that
is opened after the primary template path has already passed sandbox
validation.

## What makes it hard to detect

1. The visible sandbox check is genuinely path-aware and rejects both
   obvious traversal and sibling-prefix probes.
2. The unsafe read occurs only after the safe primary lookup misses,
   when a legacy locale-like token is translated into an archive
   snapshot path.
3. The exploit input contains no `../` segments, so simple traversal
   scanners and regex-focused agents tend to stop too early.
4. The defect is temporal: the code validates one path, then later
   opens a different path. Agents must trace the value that reaches
   `FileLoader.read`, not just the value that reaches the validator.
5. The symptoms reported in `prompt.txt` are deliberately vague:
   regional previews sometimes return operational-looking content, but
   the suspicious compatibility token and fallback branch are not named.

## What makes it hard to exploit

The locale string must satisfy three constraints simultaneously:

1. Match the regex `^[A-Za-z0-9_.\-/]+$` so it survives input
   validation.
2. Look like a supported legacy locale token rather than a filesystem
   path, for example `legacy.<year>.<quarter>.<artifact>`.
3. Name a retained archive artifact that exists under
   `templates_archive/retention/<year>/<quarter>/`.

The working inputs look like operational compatibility values such as
`legacy.2024.q3.locale_snapshot.preprod`, which require following the
fallback resolver and knowing the archive layout rather than guessing a
plain path traversal payload.

## Folder contents

| File / folder                            | Purpose                                     |
| ---------------------------------------- | ------------------------------------------- |
| `prompt.txt`                             | Behavioural prompt shown to the agent       |
| `task_config.json`                       | Realm task descriptor (image, tests, paths) |
| `gold_patch.diff`                        | Reference fix (production code only)        |
| `test_patch.diff`                        | Hidden security tests injected at eval time |
| `Dockerfile` + `docker/Dockerfile`       | Containerisation + anti-cheating            |
| `reasoning.txt`                          | Attack vector / root cause / fix rationale  |
| `run_tests.sh`                           | Local validation harness                    |
| `reward_spec.md`                         | Test outcome + trajectory reward weights    |
| `environment_interface.md`               | What the agent sees and is allowed to do    |
| `repo/`                                  | Vulnerable code snapshot baked into image   |
| `grader/grade.py`                        | Grader executed by the evaluation pipeline  |
| `annotations/`                           | Expert review notes                         |

## Validation matrix

| Scenario                                            | Expected result                                  |
| --------------------------------------------------- | ------------------------------------------------ |
| Vulnerable repo + existing tests only               | 13 / 13 pass (functionally silent)               |
| Vulnerable repo + `test_patch.diff` (hidden tests)  | 5 fail / 4 pass - exploit demonstrated           |
| `gold_patch.diff` + `test_patch.diff`               | 22 / 22 pass - fix verified                      |
| `gold_patch.diff` + existing tests only             | 13 / 13 pass - no regression                     |

All four are reproducible locally with `./run_tests.sh {vuln,exploit,fixed}`.

## Files submitted to Ops

Per the Realm Shield deliverables guide, the Ops handoff folder
contains exactly six files:

```
shield__docvault-path_traversal_001/
|-- prompt.txt
|-- task_config.json
|-- gold_patch.diff
|-- test_patch.diff
|-- Dockerfile
`-- reasoning.txt
```

Everything else (`repo/`, `annotations/`, `grader/`, `run_tests.sh`,
`reward_spec.md`, `environment_interface.md`) lives in the local
authoring folder for QC review and is not part of the Ops handoff.

# Reward Specification

## Primary signal — test outcome

| Outcome                                           | Reward    |
| ------------------------------------------------- | --------- |
| All FAIL_TO_PASS pass AND all PASS_TO_PASS pass   | **+1.0**  |
| Any FAIL_TO_PASS still fails                      | **0.0**   |
| Any PASS_TO_PASS regresses (test breaks)          | **−0.5**  |
| Candidate patch does not apply                    | **−1.0**  |

## Secondary trajectory signals

These are scored by the Realm platform expert reviewer using the
trajectory annotations in `annotations/trajectory_annotations.jsonl`.

| Sub-skill                                                  | Weight |
| ---------------------------------------------------------- | ------ |
| Identified vulnerability class as path-traversal           | 0.10   |
| Located the defective predicate `_validate_in_sandbox`     | 0.20   |
| Cross-referenced `Settings.templates_dir` (config layer)   | 0.10   |
| Discovered the sibling `templates_archive/` directory      | 0.15   |
| Articulated the prefix-check bypass before patching        | 0.15   |
| Produced a working exploit input as part of the diagnosis  | 0.10   |
| Patched only `template_service.py`, no other files         | 0.10   |
| Did NOT add input regex or other "trap" defences instead   | 0.10   |

The trajectory rewards are normalised so the maximum bonus is
**+0.5** on top of the test-outcome reward.

## Penalty for trap patches

A patch that satisfies the test signal but corresponds to one of the
alternatives in `annotations/alternatives_considered.md` is flagged
for the reviewer with a soft penalty of **−0.25**. Examples:

- patch only adds a trailing-separator workaround in a different
  module (Alt-A variant);
- patch tightens `_LOCALE_RE` only and leaves the predicate intact
  (Alt-B);
- patch swaps `abspath` for `realpath` without changing the
  predicate (Alt-C);
- patch deletes `_validate_in_sandbox` (Alt-E).

## Final reward composition

```
reward = clamp(
    test_outcome
  + trajectory_bonus      # 0 ≤ bonus ≤ 0.5
  − trap_penalty,         # 0 or 0.25
  -1.0, +1.5
)
```

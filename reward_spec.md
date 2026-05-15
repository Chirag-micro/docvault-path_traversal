# Reward Specification

## Primary Signal - Test Outcome

| Outcome                                           | Reward    |
| ------------------------------------------------- | --------- |
| All FAIL_TO_PASS pass AND all PASS_TO_PASS pass   | **+1.0**  |
| Any FAIL_TO_PASS still fails                      | **0.0**   |
| Any PASS_TO_PASS regresses                        | **-0.5**  |
| Candidate patch does not apply                    | **-1.0**  |

## Secondary Trajectory Signals

These are scored by the Realm platform expert reviewer using the
trajectory annotations in `annotations/trajectory_annotations.jsonl`.

| Sub-skill                                                  | Weight |
| ---------------------------------------------------------- | ------ |
| Identified vulnerability class as path traversal           | 0.10   |
| Followed render() through the primary read miss            | 0.15   |
| Located `_legacy_snapshot_path` as the late path rewrite   | 0.20   |
| Noted that `_validate_in_sandbox` is bypassed after miss   | 0.20   |
| Produced a working legacy-token exploit input              | 0.10   |
| Fixed the helper so it returns only in-sandbox paths       | 0.15   |
| Did NOT rely on regex-only or filename-specific blocking   | 0.10   |

The trajectory rewards are normalised so the maximum bonus is
**+0.5** on top of the test-outcome reward.

## Penalty for Trap Patches

A patch that satisfies the test signal but corresponds to one of the
alternatives in `annotations/alternatives_considered.md` is flagged for
the reviewer with a soft penalty of **-0.25**. Examples:

- patch only tightens `_LOCALE_RE` and leaves future fallback paths
  able to bypass the sandbox;
- patch blocks a single artifact name or year/quarter instead of
  enforcing the boundary generically;
- patch removes the legacy helper and changes documented missing-file
  behavior for non-legacy locales;
- patch validates only the primary path and still opens a transformed
  path without rechecking it.

## Final Reward Composition

```
reward = clamp(
    test_outcome
  + trajectory_bonus      # 0 <= bonus <= 0.5
  - trap_penalty,         # 0 or 0.25
  -1.0, +1.5
)
```

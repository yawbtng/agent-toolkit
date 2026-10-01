# Scoring rubric

A simplified, single-pass version of `desloppify`'s stateful strict-score loop — this skill runs once per invocation rather than maintaining scan/rescan state across sessions, so the score is a snapshot to gauge severity, not a tracked metric.

## Method

For the reviewed scope (diff or files), count flagged instances per category from `patterns.md`, weighted by how much the category tends to matter:

| Category | Weight per instance |
|---|---|
| Defensive overdose | 3 |
| Type bypass | 3 |
| Duplicate/parallel implementations | 3 |
| Over-engineering | 2 |
| Test slop | 2 |
| Dead code | 2 |
| Deep nesting | 1 |
| Comment noise | 1 |
| Naming/style fingerprints | 1 |

Defensive overdose (broad `except: pass` / bare `catch {}` swallow-patterns) and duplicate/parallel implementations are the two categories current research most consistently flags as the highest-impact AI-code smells — hence the top weight. Architectural-fingerprint and process/workflow smells (see `patterns.md`) aren't scored per-instance; they're qualitative signals, not counted defects.

**Score = 100 − (sum of weighted instances), floor at 0.** A clean diff with nothing flagged scores 100. Treat this the same direction as `desloppify`'s convention — higher is cleaner.

## Interpreting the score

- **90-100** — minor or no issues. Spot-fix only what's flagged, if anything.
- **70-89** — a normal amount of AI-assisted-code roughness. Fix flagged issues individually; don't restructure beyond what's flagged.
- **Below 70** — enough issues that fixing them one at a time may leave the code inconsistent. Still default to minimal-diff fixes, but flag to the user that the volume suggests the code may be worth a deeper pass (ambitious-restructuring mode, see `modes.md`) rather than many small patches.

Don't let a low score justify a rewrite the user didn't ask for — report the score and the findings, let the user decide how far to go, unless they already asked for aggressive cleanup.

## Caveat

Weights are a heuristic, not a precise defect-severity model — a single defensive-overdose instance that's actually masking a real bug matters more than the weight suggests, and a single comment-noise instance in an otherwise pristine diff matters less. Use judgment on individual findings; use the score only as a rough "how much is here" signal.

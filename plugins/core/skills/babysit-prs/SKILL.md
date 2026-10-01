---
name: babysit-prs
description: >
  Babysit a GitHub pull request by continuously polling CI checks, review comments,
  and mergeability state. Diagnoses failures, retries flaky checks (up to 3x),
  auto-fixes branch-related issues, addresses actionable review comments, and stops
  only when the PR is ready to merge or needs human help. Use when asked to monitor,
  watch, or babysit a PR.
---

# PR Babysitter

## Objective

Babysit a PR persistently until one of these terminal outcomes:

- The PR is merged or closed.
- CI is successful, no unaddressed review comments, not blocked on review approval, and mergeable (no conflict risk).
- A situation requires human help (CI infra issues, exhausted flaky retries, permission problems, or ambiguity).

Do not stop merely because a single snapshot returns `idle` while checks are still pending.

## Inputs

Accept any of the following:

- No PR argument: infer the PR from the current branch (`--pr auto`)
- PR number (e.g. `/babysit-prs 42`)
- PR URL

## Core Workflow

1. When the user asks to "monitor"/"watch"/"babysit" a PR, start with the watcher's continuous mode (`--watch`) unless doing a one-shot diagnostic.
2. Run the watcher script to snapshot PR/CI/review state (or consume each streamed snapshot from `--watch`).
3. Inspect the `actions` list in the JSON response.
4. If `diagnose_ci_failure` is present, inspect failed run logs and classify the failure.
5. If the failure is likely caused by the current branch, patch code locally, commit, and push.
6. If `process_review_comment` is present, inspect surfaced review items and decide whether to address them.
7. If a review item is actionable and correct, patch code locally, commit, and push.
8. If the failure is likely flaky/unrelated and `retry_failed_checks` is present, rerun failed jobs with `--retry-failed-now`.
9. If both actionable review feedback and `retry_failed_checks` are present, prioritize review feedback first — a new commit will retrigger CI, so avoid rerunning flaky checks on the old SHA.
10. On every loop, verify mergeability / merge-conflict status via `gh pr view`.
11. After any push or rerun action, immediately return to step 1 and continue polling on the updated SHA.
12. If you had been using `--watch` before pausing to patch/commit/push, relaunch `--watch` yourself in the same turn immediately after the push.
13. Repeat until PR is green + review-clean + mergeable, `stop_pr_closed` appears, or a blocker is reached.

## Commands

### One-shot snapshot

```bash
python3 ~/.claude/skills/babysit-prs/scripts/gh_pr_watch.py --pr auto --once
```

### Continuous watch (JSONL)

```bash
python3 ~/.claude/skills/babysit-prs/scripts/gh_pr_watch.py --pr auto --watch
```

### Trigger flaky retry cycle

```bash
python3 ~/.claude/skills/babysit-prs/scripts/gh_pr_watch.py --pr auto --retry-failed-now
```

### Explicit PR target

```bash
python3 ~/.claude/skills/babysit-prs/scripts/gh_pr_watch.py --pr <number-or-url> --once
```

## CI Failure Classification

Use `gh` commands to inspect failed runs before deciding:

- `gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha`
- `gh run view <run-id> --log-failed`

**Branch-related** (fix locally):
- Compile/typecheck/lint failures in files touched by the PR
- Deterministic test failures in changed areas
- Snapshot changes caused by UI/text changes in the branch
- Static analysis violations introduced by latest push

**Flaky/unrelated** (rerun):
- DNS/network/registry timeouts
- Runner provisioning or startup failures
- GitHub Actions infrastructure errors
- Rate limits or transient API outages

If ambiguous, perform one manual diagnosis attempt before choosing rerun.

Read `~/.claude/skills/babysit-prs/references/heuristics.md` for the full checklist.

## Review Comment Handling

The watcher surfaces review items from:
- PR issue comments
- Inline review comments
- Review submissions (COMMENT / APPROVED / CHANGES_REQUESTED)

It surfaces both human reviewer feedback (OWNER/MEMBER/COLLABORATOR + the authenticated user) and approved review bot feedback (e.g. Claude code review bot).

On a fresh watcher state file, existing pending review feedback is surfaced immediately — not only comments that arrive after monitoring starts.

**When you agree with a comment and it is actionable:**

1. Patch code locally.
2. Commit with `fix: address PR review feedback (#<n>)`.
3. Push to the PR head branch.
4. Resume watching on the new SHA immediately — do NOT stop after pushing.
5. If monitoring was running in `--watch` mode, restart `--watch` immediately after the push.

**When you disagree or the comment is non-actionable:**
- Continue the watcher loop. The script de-duplicates surfaced items via state.
- If a review thread is already marked as resolved in GitHub, treat it as non-actionable.

## Git Safety Rules

- Work only on the PR head branch.
- Avoid destructive git commands (`--force`, `reset --hard`, etc.).
- Before editing, check for unrelated uncommitted changes. If present, stop and ask the user.
- After each fix, commit and `git push`, then re-run the watcher.
- Do not run multiple concurrent `--watch` processes for the same PR.
- A push is NOT a terminal outcome — continue the monitoring loop.

**Commit message conventions:**
- CI fix: `fix: resolve CI failure on PR #<n>`
- Review feedback: `fix: address PR review feedback (#<n>)`

## Polling Cadence

Adaptive polling — continues monitoring even after CI turns green:

- **CI not green** (pending/running/failing): poll every **1 minute**
- **CI green**: start at 1min, then backoff exponentially (1m→2m→4m→8m→16m→32m), cap at **1 hour**
- **State changes** (new commit, check status change, new review comment, mergeability change): reset to 1min
- **PR merged/closed**: stop immediately

## Stop Conditions (Strict)

Stop ONLY when:
- PR merged or closed
- PR ready to merge: CI passed, no unaddressed reviews, not blocked on approval, no merge conflicts
- User intervention required and cannot safely proceed alone

Keep polling when:
- `actions` contains only `idle` but checks are still pending
- CI is still running/queued
- CI is green but mergeability is unknown/pending
- CI is green but blocked on review approval — continue watching for new comments

## Output

Provide concise progress updates while monitoring. Final summary includes:
- Final PR SHA
- CI status summary
- Mergeability / conflict status
- Fixes pushed (list)
- Flaky retry cycles used
- Remaining unresolved failures or review comments

When CI first goes all green: `CI is all green! X/Y passed. Still on watch for review approval.`

## References

- Heuristics: `~/.claude/skills/babysit-prs/references/heuristics.md`
- GitHub CLI notes: `~/.claude/skills/babysit-prs/references/github-api-notes.md`

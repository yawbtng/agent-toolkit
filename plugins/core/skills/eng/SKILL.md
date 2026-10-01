---
name: eng
version: 1.0.0
description: |
  Unified engineering workflow orchestrator. Auto-detects your current phase
  (discover, plan, build, verify, ship, learn) and runs the right tools.
  Just type /eng and it figures out what to do next.
  Requires the "gstack" CLI/plugin and the "Compound Engineering" plugin to
  be installed — this skill routes to their sub-skills (/gstack:*,
  /workflows:*) and will fail mid-phase without them.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - Skill

---

# /eng — Unified Engineering Workflow Orchestrator

You are an engineering workflow orchestrator. When the user invokes `/eng`, you
detect where they are in the development lifecycle and drive the next phase
automatically. The user should never have to remember which sub-skill to call.

## Requirements

This skill is an orchestrator, not a standalone tool — it routes to two other plugins:

- **[gstack](https://github.com/search?q=gstack+cli)** — provides `/gstack:plan-ceo-review`, `/gstack:plan-eng-review`, `/gstack:review`, `/gstack:ship`, `/gstack:retro`
- **Compound Engineering** — provides `/workflows:brainstorm`, `/workflows:plan`, `/workflows:work`, `/workflows:review`, `/workflows:compound`

Without both installed, phases that invoke their sub-skills will fail. If you don't have them, treat this file as a reference architecture for building your own phase-detecting orchestrator around whatever workflow skills you do have — the phase-detection logic and decision tree below are the reusable part.

## Phase Detection

Run this diagnostic FIRST every time `/eng` is invoked:

```bash
echo "=== PHASE DETECTION ==="

# 1. What branch are we on?
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "no-git")
echo "branch: $BRANCH"

# 2. Is there a diff against main?
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ] && [ "$BRANCH" != "no-git" ]; then
  DIFF_STAT=$(git diff origin/main --stat 2>/dev/null | tail -1)
  DIFF_FILES=$(git diff origin/main --name-only 2>/dev/null | wc -l | tr -d ' ')
  COMMIT_COUNT=$(git log origin/main..HEAD --oneline 2>/dev/null | wc -l | tr -d ' ')
  echo "diff: $DIFF_STAT"
  echo "changed_files: $DIFF_FILES"
  echo "commits_ahead: $COMMIT_COUNT"
else
  DIFF_FILES=0
  COMMIT_COUNT=0
  echo "diff: (on main or no git)"
fi

# 3. Recent brainstorm docs?
echo "--- brainstorms (last 14 days) ---"
find docs/brainstorms -name "*.md" -mtime -14 2>/dev/null || echo "(none)"

# 4. Recent plan docs?
echo "--- plans (last 14 days) ---"
find docs/plans -name "*.md" -mtime -14 2>/dev/null || echo "(none)"

# 5. Open todos from review?
echo "--- review todos ---"
ls todos/*-pending-*.md 2>/dev/null | head -5 || echo "(none)"

# 6. Uncommitted changes?
echo "--- working tree ---"
git status --porcelain 2>/dev/null | head -10 || echo "(clean)"

# 7. PR exists for this branch?
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ] && [ "$BRANCH" != "no-git" ]; then
  echo "--- pr status ---"
  gh pr view --json state,url 2>/dev/null || echo "(no PR)"
fi
```

## Phase Decision Tree

Based on the diagnostic, determine the phase:

```
Is the user's message about a NEW idea or feature?
  YES → PHASE 1: DISCOVER

Does a recent brainstorm exist but NO plan yet?
  YES → PHASE 2A: PLAN

Does a recent plan exist but branch is on main (no work started)?
  YES → PHASE 2B: PLAN REVIEW, then PHASE 3: BUILD

Is there a feature branch with uncommitted changes or recent commits?
  Are there pending review todos?
    YES → Fix todos, then re-verify
  Is the diff small (<3 commits) and still in progress?
    YES → PHASE 3: BUILD (continue)
  Is there a meaningful diff with no review yet?
    YES → PHASE 4: VERIFY

Has the branch been reviewed (no pending P1 todos) and tests pass?
  YES → PHASE 5: SHIP

Did the user just fix a tricky bug or solve a hard problem?
  YES → PHASE 6A: COMPOUND

Is it end of week or user asks for reflection?
  YES → PHASE 6B: RETRO

Nothing detected?
  → Ask the user: "What are you working on?" with options:
    A) Start a new feature
    B) Continue work on current branch
    C) Review my changes
    D) Ship what I have
    E) Weekly retro
```

## Phase Execution

### PHASE 1: DISCOVER

Tell the user:
> Starting discovery phase. I'll explore your idea through a structured brainstorm.

Then invoke: `/workflows:brainstorm`

When brainstorm completes, automatically suggest:
> Brainstorm captured. Ready to create an implementation plan? (Y/n)

If yes, proceed to PHASE 2A.

### PHASE 2A: PLAN

Tell the user:
> Creating implementation plan. I'll research your codebase and document the approach.

Then invoke: `/workflows:plan`

When plan completes, ask:
> Plan ready. How do you want to stress-test it?
> A) CEO review — challenge the vision, find the 10x opportunity
> B) Eng review — lock in execution details
> C) Skip review, start building

If A: invoke `/gstack:plan-ceo-review`
If B: invoke `/gstack:plan-eng-review`
If C: proceed to PHASE 3.

After plan review completes:
> Plan reviewed. Ready to start building? (Y/n)

If yes, proceed to PHASE 3.

### PHASE 2B: PLAN REVIEW (if plan exists but no review happened)

Ask:
> I found a recent plan. Want to review it before building?
> A) CEO review
> B) Eng review
> C) Skip, start building

### PHASE 3: BUILD

Tell the user:
> Starting implementation. I'll set up the branch, break the work into tasks, and execute.

Then invoke: `/workflows:work`

The work skill handles branching, task breakdown, implementation, testing, and incremental commits internally.

When work completes (PR created by workflows:work), proceed to PHASE 4.

If work was NOT invoked via the skill (user was coding manually), and there's a diff, ask:
> You have changes on this branch. Ready for review?
> A) Quick review (pre-push sanity check)
> B) Full review (multi-agent, thorough)
> C) Not yet, still working

### PHASE 4: VERIFY

Determine review depth by the size of the change:

- If diff < 100 lines changed OR < 3 files: start with quick review
- If diff >= 100 lines OR touches auth/payments/migrations/security: recommend thorough

**Quick review:**
Tell the user:
> Running quick pre-push review.

Invoke: `/gstack:review`

After quick review, if no CRITICAL findings:
> Clean review. Want a thorough multi-agent review before merge, or ship it?
> A) Thorough review
> B) Ship it

**Thorough review:**
Tell the user:
> Running thorough multi-agent review. This spawns 10+ specialist agents in parallel.

Invoke: `/workflows:review`

After thorough review:
- If P1 findings exist: tell the user what needs fixing. After fixes, re-run verify.
- If no P1 findings: proceed to PHASE 5.

### PHASE 5: SHIP

Tell the user:
> Shipping. This will merge main, run tests, bump version, generate changelog, and create a PR.

Invoke: `/gstack:ship`

After ship completes, output the PR URL and ask:
> Shipped! Did you solve any tricky problems during this feature worth documenting? (y/N)

If yes, proceed to PHASE 6A.

### PHASE 6A: COMPOUND (learning capture)

Tell the user:
> Capturing what you learned. This documents the solution for future reference.

Invoke: `/workflows:compound`

After compound completes:
> Solution documented. This will automatically surface in future planning via the learnings researcher.

### PHASE 6B: RETRO (weekly reflection)

Tell the user:
> Running weekly retrospective.

Invoke: `/gstack:retro`

If previous retro data exists, automatically use `compare` mode:

```bash
ls .context/retros/*.json 2>/dev/null | wc -l
```

If > 0: `/gstack:retro compare`
Else: `/gstack:retro`

## Arguments

The user can shortcut to a specific phase:

- `/eng` — Auto-detect phase
- `/eng discover` or `/eng brainstorm` — Jump to Phase 1
- `/eng plan` — Jump to Phase 2A
- `/eng build` or `/eng work` — Jump to Phase 3
- `/eng review` — Jump to Phase 4 (auto-picks quick vs thorough)
- `/eng review quick` — Force quick review
- `/eng review thorough` — Force thorough review
- `/eng ship` — Jump to Phase 5
- `/eng compound` or `/eng learn` — Jump to Phase 6A
- `/eng retro` — Jump to Phase 6B
- `/eng status` — Just run phase detection, show where we are, suggest next step

## Rules

1. ALWAYS run phase detection first (even with arguments — use it to provide context).
2. ALWAYS tell the user which phase you detected and why before executing.
3. After each phase completes, ALWAYS suggest the next phase. Don't stop.
4. Use `AskUserQuestion` for phase transitions — let the user confirm or redirect.
5. If the user describes what they want to build in the same message as `/eng`, treat it as Phase 1 input and pass it to `/workflows:brainstorm`.
6. Never skip verify (Phase 4) before ship (Phase 5) unless the user explicitly says to.
7. For quick decisions, offer A/B/C options. Don't make the user type long answers.
8. Keep phase transition messages to 1-2 lines. Don't explain the whole workflow every time.

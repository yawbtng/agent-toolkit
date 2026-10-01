---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Directory Selection Process

Follow this priority order:

### 1. Check Existing Directories

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

**If found:** Use that directory. If both exist, `.worktrees` wins.

### 2. Check CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

**If preference specified:** Use it without asking.

### 3. Ask User

If no directory exists and no CLAUDE.md preference:

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ~/.config/superpowers/worktrees/<project-name>/ (global location)

Which would you prefer?
```

## Safety Verification

### For Project-Local Directories (.worktrees or worktrees)

**MUST verify directory is ignored before creating worktree:**

```bash
# Check if directory is ignored (respects local, global, and system gitignore)
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If NOT ignored:**

Per Jesse's rule "Fix broken things immediately":
1. Add appropriate line to .gitignore
2. Commit the change
3. Proceed with worktree creation

**Why critical:** Prevents accidentally committing worktree contents to repository.

### For Global Directory (~/.config/superpowers/worktrees)

No .gitignore verification needed - outside project entirely.

## Creation Steps

### 1. Detect Project Name

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 2. Create Worktree

```bash
# Determine full path
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/.config/superpowers/worktrees/*)
    path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"
    ;;
esac

# Create worktree with new branch
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. Copy Environment Files

**CRITICAL:** Copy .env files from the source branch/main repo to the new worktree:

```bash
# Get path to main repo
main_repo=$(git rev-parse --show-toplevel)

# Copy environment files if they exist
for env_file in .env .env.local .env.development .env.development.local; do
  if [ -f "$main_repo/$env_file" ]; then
    cp "$main_repo/$env_file" "$path/$env_file"
    echo "Copied $env_file"
  fi
done

# For monorepos, also check subdirectories
for subdir in frontend backend; do
  for env_file in .env .env.local; do
    if [ -f "$main_repo/$subdir/$env_file" ]; then
      mkdir -p "$path/$subdir"
      cp "$main_repo/$subdir/$env_file" "$path/$subdir/$env_file"
      echo "Copied $subdir/$env_file"
    fi
  done
done
```

**Why critical:** Worktrees don't share untracked files - without this, the new workspace will be missing API keys, database URLs, and other secrets needed to run.

### 4. Run Project Setup

Auto-detect and run appropriate setup:

```bash
# Node.js (detect package manager)
if [ -f pnpm-lock.yaml ]; then pnpm install
elif [ -f yarn.lock ]; then yarn install
elif [ -f package-lock.json ]; then npm install
elif [ -f package.json ]; then npm install
fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python (detect package manager)
if [ -f uv.lock ] || [ -f pyproject.toml ] && grep -q "uv" pyproject.toml 2>/dev/null; then uv sync
elif [ -f poetry.lock ]; then poetry install
elif [ -f Pipfile.lock ]; then pipenv install
elif [ -f requirements.txt ]; then pip install -r requirements.txt
elif [ -f pyproject.toml ]; then pip install -e .
fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

**For monorepos:** Run setup in each subdirectory that has dependencies:

```bash
# Example for frontend/backend monorepo
for subdir in frontend backend; do
  if [ -d "$subdir" ]; then
    cd "$subdir"
    # Run appropriate install command based on files present
    cd ..
  fi
done
```

### 5. Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
# Examples - use project-appropriate command
npm test
cargo test
pytest
go test ./...
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### 6. Report Location

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md → Ask user |
| Directory not ignored | Add to .gitignore + commit |
| .env files in source repo | Copy to new worktree |
| Monorepo with frontend/backend | Copy .env from each subdir |
| pnpm-lock.yaml present | Use `pnpm install` |
| uv.lock or uv in pyproject | Use `uv sync` |
| Tests fail during baseline | Report failures + ask |
| No package.json/Cargo.toml | Skip dependency install |

## Common Mistakes

### Skipping ignore verification

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always use `git check-ignore` before creating project-local worktree

### Assuming directory location

- **Problem:** Creates inconsistency, violates project conventions
- **Fix:** Follow priority: existing > CLAUDE.md > ask

### Proceeding with failing tests

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

### Hardcoding setup commands

- **Problem:** Breaks on projects using different tools
- **Fix:** Auto-detect from project files (package.json, etc.)

## Example Workflow

```
You: I'm using the using-git-worktrees skill to set up an isolated workspace.

[Check .worktrees/ - exists]
[Verify ignored - git check-ignore confirms .worktrees/ is ignored]
[Create worktree: git worktree add .worktrees/auth -b feature/auth]
[Copy .env.local from main repo]
[Copy frontend/.env.local from main repo]
[Copy backend/.env.local from main repo]
[Run pnpm install in frontend/]
[Run uv sync in backend/]
[Run tests - 47 passing]

Worktree ready at /Users/jesse/myproject/.worktrees/auth
Environment files copied: .env.local, frontend/.env.local, backend/.env.local
Dependencies installed: frontend (pnpm), backend (uv)
Tests passing (47 tests, 0 failures)
Ready to implement auth feature
```

## Red Flags

**Never:**
- Create worktree without verifying it's ignored (project-local)
- Skip copying .env files from source repo
- Skip baseline test verification
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Skip CLAUDE.md check
- Assume npm when pnpm-lock.yaml exists
- Assume pip when uv.lock exists

**Always:**
- Follow directory priority: existing > CLAUDE.md > ask
- Verify directory is ignored for project-local
- Copy .env and .env.local files from source branch
- Auto-detect package manager (pnpm > yarn > npm, uv > poetry > pip)
- Auto-detect and run project setup
- Verify clean test baseline

## Integration

**Called by:**
- **brainstorming** (Phase 4) - REQUIRED when design is approved and implementation follows
- Any skill needing isolated workspace

**Pairs with:**
- **finishing-a-development-branch** - REQUIRED for cleanup after work complete
- **executing-plans** or **subagent-driven-development** - Work happens in this worktree

---
name: ralphy
description: Set up, plan, and run Ralphy loops (OpenCode, Claude Code, Cursor). Use when the user says "/ralphy", "ralphy", "ralphy loop", "plan ralphy tasks", "run ralphy", "ralphy init", or wants to create YAML task lists and commands for the Ralphy autonomous AI loop. Docs: https://github.com/michaelshimeles/ralphy
---

# Ralphy Setup, Plan & Run

Helps you configure Ralphy, turn PRDs/plans into YAML task files, and get copy-pasteable commands. When the user is **unsure** about parallel execution, branch-per-task, or create/draft PRs, **suggest** a workflow and **explain why** that suggestion fits their context.

## Phase 1 — Detect and Setup

1. **Check for `.ralphy/`** (and `.ralphy/config.yaml`) in the project root.
2. **If missing or empty:**
   - Run: `ralphy --init`
   - Then: `ralphy --config` to confirm
   - Add rules by editing `.ralphy/config.yaml` or: `ralphy --add-rule "your rule"`
   - If the user attaches `@.ralphy/config.yaml`, propose concrete edits (rules, boundaries, commands).
3. **If present:** Confirm setup and ask if they want to adjust rules or proceed to plan/run.

### Config format (from Ralphy README)

`.ralphy/config.yaml` should follow this structure:

```yaml
project:
  name: "my-app"
  language: "TypeScript"
  framework: "Next.js"

commands:
  test: "npm test"
  lint: "npm run lint"
  build: "npm run build"

rules:
  - "use server actions not API routes"
  - "follow error pattern in src/utils/errors.ts"

boundaries:
  never_touch:
    - "src/legacy/**"
    - "*.lock"
```

Optional: `capabilities.browser: "auto"`, `notifications.discord_webhook`, etc. See [reference.md](reference.md).

## Phase 2 — Identify Feature and Task Source

- **Attached PRD/plan** (e.g. `refactor-api-routes.md`, `.plan.md`): Parse tasks and phases; map phases to `parallel_group` (Phase 1 → 1, Phase 2 → 2, etc.).
- **No attachment:** Ask for a short feature description or path to a PRD; draft a minimal task list and convert to Ralphy YAML.

## Phase 3 — Emit or Write YAML

Use the Ralphy YAML format. **Minimal example** (like `.ralphy/test-tasks.yaml`):

```yaml
# Test YAML for Ralphy - Minimal case
tasks:
  - title: Task 1
    completed: false
    description: First task

  - title: Task 2
    completed: false
    description: Second task

  - title: Task 3
    completed: false
    description: Third task
```

**With parallel groups** (from README):

```yaml
tasks:
  - title: Create User model
    parallel_group: 1
  - title: Create Post model
    parallel_group: 1   # same group = runs together
  - title: Add relationships
    parallel_group: 2  # runs after group 1
```

Each task: `title` (required, unique), `completed` (default `false`), optional `parallel_group`, optional `description`. Write to `.ralphy/<feature-slug>.yaml` or output in a block and tell the user where to save it.

## Phase 4 — Workflow Suggestion and Commands

**When the user is unsure** whether to use parallel execution, branch-per-task, or create/draft PRs:

1. **Suggest** a concrete workflow (e.g. "use serial runs first" or "use `--parallel --branch-per-task --draft-pr`").
2. **Explain why:** e.g. "Serial is suggested because the tasks depend on each other and share files; parallel is better when tasks are independent and grouped by `parallel_group`."

### Suggestion rules

| User context | Suggest | Why |
|--------------|--------|-----|
| Few tasks (<5), shared codebase, order matters | Serial, no `--parallel` | Avoids merge conflicts and preserves dependency order. |
| Many tasks, clear phases in YAML (`parallel_group`) | `--parallel --max-parallel 3` (or N) | Speeds up work; groups run in order, tasks in same group run together. |
| Need review before merging | `--branch-per-task --create-pr` or `--draft-pr` | Each task gets a branch and PR so humans can review. |
| Quick iteration, trust auto-merge | `--branch-per-task` without `--create-pr` | Branches keep history; Ralphy auto-merges when possible. |
| Very large repo (e.g. big `node_modules`) | Add `--sandbox` with `--parallel` | Uses symlinked deps instead of worktrees for faster setup. |
| First time / validation | `--dry-run` first | Previews tasks and flow without running agents. |

Always output both **(a) the suggested command** and **(b) a one- or two-sentence rationale** for that suggestion.

### Engines (user choice)

- **OpenCode:** `ralphy --opencode ...`
- **Claude Code:** `ralphy` or `ralphy --claude ...`
- **Cursor:** `ralphy --cursor ...`

### Example commands

**Serial, YAML, OpenCode (single run):**
```bash
ralphy --yaml .ralphy/refactor-api-routes.yaml --opencode
```

**Parallel, branches, draft PRs, Claude Code:**
```bash
ralphy --yaml .ralphy/refactor-api-routes.yaml --claude --parallel --branch-per-task --draft-pr --base-branch main
```

**Preview only:**
```bash
ralphy --yaml .ralphy/my-feature.yaml --dry-run
```

**Using Markdown PRD instead of YAML:**
```bash
ralphy --prd .ralphy/refactor-api-routes.md --opencode
```

## Quick reference

- **Task sources:** `--prd PATH`, `--yaml FILE`, `--json FILE`, `--github owner/repo`
- **Execution:** `--parallel`, `--max-parallel N`, `--sandbox`, `--no-merge`
- **Branches/PRs:** `--branch-per-task`, `--base-branch NAME`, `--create-pr`, `--draft-pr`
- **Safety/speed:** `--dry-run`, `--fast` (skip tests+lint), `--max-iterations N`

Full flag list and details: [reference.md](reference.md).

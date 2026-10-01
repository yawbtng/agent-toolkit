# Ralphy Reference

Condensed from [Ralphy README](https://github.com/michaelshimeles/ralphy). Use for flag lookup and task-source details.

## Task sources

| Flag | Usage | Format |
|------|--------|--------|
| `--prd PATH` | Markdown task file or folder | `- [ ] task` or `- [x] done` |
| `--yaml FILE` | YAML task file | `tasks:` list with `title`, `completed`, optional `parallel_group`, `description` |
| `--json FILE` | JSON task file | `{ "tasks": [{ "title", "completed", "parallel_group?", "description?" }] }` |
| `--github REPO` | GitHub issues | Optional `--github-label TAG` |

YAML/JSON: titles must be unique. `parallel_group` controls order when using `--parallel` (same group = run together; higher number = later).

## Options (flags)

| Flag | What it does |
|------|----------------|
| `--prd PATH` | Task file or folder (default PRD.md) |
| `--yaml FILE` | YAML task file |
| `--json FILE` | JSON task file |
| `--github REPO` | Use GitHub issues |
| `--github-label TAG` | Filter issues by label |
| `--sync-issue N` | Sync PRD progress to GitHub issue #N |
| `--model NAME` | Override model for any engine |
| `--sonnet` | Shortcut for `--claude --model sonnet` |
| `--parallel` | Run parallel agents |
| `--max-parallel N` | Max agents (default 3) |
| `--sandbox` | Lightweight sandboxes instead of git worktrees (faster for large node_modules) |
| `--no-merge` | Skip auto-merge in parallel mode |
| `--branch-per-task` | One branch per task |
| `--base-branch NAME` | Branch from this (e.g. main) |
| `--create-pr` | Create PRs per task/branch |
| `--draft-pr` | Create draft PRs |
| `--no-tests` | Skip tests |
| `--no-lint` | Skip lint |
| `--fast` | Skip tests + lint |
| `--no-commit` | Don’t auto-commit |
| `--max-iterations N` | Stop after N tasks |
| `--max-retries N` | Retries per task (default 3) |
| `--retry-delay N` | Seconds between retries |
| `--dry-run` | Preview only |
| `--browser` | Enable browser automation (agent-browser) |
| `--no-browser` | Disable browser automation |
| `-v, --verbose` | Debug output |
| `--init` | Setup .ralphy/ config |
| `--config` | Show config |
| `--add-rule "rule"` | Add rule to config |

## Engines

| Engine | Flag | CLI |
|--------|------|-----|
| Claude Code | (default) or `--claude` | claude |
| OpenCode | `--opencode` | opencode |
| Cursor | `--cursor` | agent |
| Codex | `--codex` | codex |
| Qwen | `--qwen` | qwen |
| Droid | `--droid` | droid exec |
| Copilot | `--copilot` | copilot |
| Gemini | `--gemini` | gemini |

## Config (.ralphy/config.yaml)

Beyond the README example in SKILL.md, you can add:

```yaml
capabilities:
  browser: "auto"   # "auto" | "true" | "false"

notifications:
  discord_webhook: "https://discord.com/api/webhooks/..."
  slack_webhook: "https://hooks.slack.com/services/..."
  custom_webhook: "https://your-api.com/webhook"
```

## YAML schema (reminder)

```yaml
tasks:
  - title: string      # required, unique
    completed: bool   # default false
    parallel_group: 1 # optional; same number = same wave
    description: |    # optional
      Multiline text.
```

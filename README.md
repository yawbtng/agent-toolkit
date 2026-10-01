# Agent Toolkit

Private, canonical skill collection for Devin, Claude Code, Codex, Cursor, and agents that support the open `SKILL.md` format.

Installing the root Devin plugin loads a lean-to-mid baseline of 48 broadly useful skills. Five specialist plugins remain available as optional installs:

| Plugin | Purpose | Skills |
| --- | --- | ---: |
| `agent-toolkit` | Cross-cutting engineering, design, frontend, and agent-quality baseline | 48 |
| `agent-core` | Specialized planning, debugging, review, verification, and delivery workflows | 94 |
| `agent-design` | Specialized visual direction, typography, motion, and design QA | 32 |
| `agent-frontend` | Framework, component, performance, and platform-specific frontend guidance | 15 |
| `agent-knowledge` | Research, documentation, memory, context reconstruction, and synthesis | 23 |
| `agent-productivity` | Automation, communication, planning, and personal workflows | 15 |

## Install

Local linked install for development:

```bash
devin plugins install --local .
```

Personal install synchronized to Devin Cloud:

```bash
devin plugins install yawbtng/agent-toolkit
```

Skills are then available as namespaced commands such as:

```text
/agent-toolkit:frontend-design
/agent-toolkit:systematic-debugging
/agent-toolkit:next-best-practices
```

## Maintain

Rebuild the local inventory:

```bash
python3 scripts/inventory_skills.py --output inventory/skills.json
```

Import canonical local skills into an empty plugin tree:

```bash
python3 scripts/import_skills.py --inventory inventory/skills.json --repo .
```

Validate manifests, skill metadata, duplicate names, local paths, and secret-like values:

```bash
python3 scripts/validate.py
```

Existing agent installations remain independent. Do not replace them with links to this repository until local and cloud plugin verification succeeds.

## Provenance

The local inventory records each selected source and content hash. Reviewed external additions are listed in `inventory/external-sources.json`; required licenses are preserved in `THIRD_PARTY_NOTICES.md`.

MCP servers are intentionally excluded from this phase.

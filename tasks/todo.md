# Agent Toolkit Plan

- [x] Inventory all local skill sources and identify exact and semantic duplicates.
- [x] Define plugin boundaries and selection criteria.
- [x] Create the meta-plugin and subplugin manifests.
- [x] Import canonical skills without modifying source installations.
- [x] Validate frontmatter, names, links, scripts, and agent-specific assumptions.
- [x] Research additional high-value skills, emphasizing design quality.
- [x] Review third-party skill licenses and supply-chain risk before inclusion.
- [ ] Install the plugin locally and verify skill discovery.
- [ ] Push the private repository and install it into the Devin personal manifest.
- [ ] Verify discovery in a fresh Devin Cloud session.

## Boundaries

- Skills only in this phase; MCP configuration and credentials remain untouched.
- Existing skill directories remain unchanged until the canonical repository is verified.
- Never copy secrets, machine-specific tokens, generated caches, or private synced skill payloads blindly.
- Prefer one canonical copy of each skill and preserve upstream attribution.

## Verification

- `python3 scripts/validate.py`: passed with 227 unique skills, 48 in the baseline, and no errors or warnings.
- `python3 -m py_compile scripts/*.py`: passed for all toolkit scripts.
- Repository-wide secret-pattern scan: no matches after replacing a bundled bearer value with an environment variable.
- Repository-wide absolute-home scan: only the validator's detection pattern remains.

## Review

- The root plugin now exposes a lean-to-mid baseline instead of auto-installing every specialist plugin.
- Five optional plugins retain specialist skills without polluting default skill selection.
- Four externally discovered skills passed published security audits and MIT license review before import.
- Local-only, overlapping, and runtime-dependent skills remain optional and are listed in `inventory/curation.json` for further pruning.
- Local and cloud installation remain blocked on Devin CLI authentication.

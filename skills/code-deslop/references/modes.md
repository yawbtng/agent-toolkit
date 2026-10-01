# Fix modes: minimal-diff vs. ambitious-restructuring

## Minimal-diff (default)

Every source in this skill except `thermo-nuclear-code-quality-review` converges on this stance, and it's the safer default for a skill that runs on someone else's diff or codebase:

- One flagged issue → one focused fix, at the site of the issue.
- Don't touch adjacent code that wasn't flagged, even if it could arguably be improved too.
- Preserve existing structure, naming conventions, and style choices that weren't themselves flagged.
- Preserve behavior — a fix should never change what the code does, only how it's written.
- Summarize what changed and why, so the change is auditable in a normal code-review sense.

Use this mode unless the user explicitly asks for more.

## Ambitious-restructuring (opt-in only)

`thermo-nuclear-code-quality-review`'s contribution: sometimes the right fix isn't a local patch but a structural change — collapsing a bad abstraction, merging near-duplicate functions, reorganizing a module. This mode is more invasive and changes more surface area than the flagged issues alone would require.

**Only switch to this mode when the user explicitly asks for it** — phrases like "restructure this," "this needs a real refactor," "make this actually good, not just cleaned up," or after a low score (see `scoring-rubric.md`) when the user confirms they want the deeper pass. Do not infer this mode from a low score alone.

When in this mode:
- Still preserve external behavior (same inputs → same outputs), even though internal structure may change substantially.
- Call out the restructuring decisions explicitly (what moved/merged/was removed and why) — a bigger diff needs a clearer explanation, not less of one.
- If the restructuring is large, consider proposing it before executing, so the user can confirm the direction rather than reviewing a fait accompli.

# Code slop pattern catalog

Synthesized from the diff-review checklists shared across the `deslop` (brianlovin/poteto/davila7) cluster, `desloppify`'s mechanical + subjective checks, `code-slop`'s 6-category taxonomy, and current (2025-2026) research on AI-code tells (McKelvey's "9 Tells" writeup, arXiv 2605.02741 on AI-generated code smells, and duplicate-code studies including GitClear's 2025 report). Organized by category, most commonly-seen first within each.

## Architectural fingerprint (check first)

The single highest-confidence tell, and the one to check before anything else — the inverse of how human code tends to look:

- **AI code is line-by-line uniform but architecturally inconsistent.** Every comment follows the same format, every function has the same documentation style, formatting is mechanically consistent within a block — but zoom out and each function/module solves a similar problem its own way, because each generation session started fresh without full context of what came before.
- **Human code is the opposite:** locally inconsistent (comment style drifts, formatting has personality) but architecturally consistent (the same problem gets solved the same way everywhere, because one person's mental model stays applied across the whole codebase).

**Confidence rule:** any single tell in this catalog, on its own, is a hunch — plenty of legitimate human code trips one pattern. Treat 4-5 co-occurring tells across different categories as a reliable diagnosis. Don't declare code "AI-generated" or flag it aggressively off one hit; this rule matters most when the user asks "does this look AI-written?" (Detect mode) rather than when fixing an already-flagged issue.

## Comment noise

- A comment that restates what the next line already says (`// increment counter` above `counter++`).
- A comment explaining *what* the code does instead of *why* — the code itself already says what; a comment only earns its place by covering something the code can't (a non-obvious constraint, a workaround, a gotcha).
- Comments left over from an earlier version of the code that no longer match what's there (stale, not just redundant).
- Section-header comments inside a short function (`// --- validation ---` / `// --- processing ---`) that just chunk up something that didn't need chunking.

**Fix:** delete restating/stale comments outright. Keep only comments that explain a non-obvious *why*.

## Defensive overdose

- try/catch around a call that can only throw for a state already ruled out earlier in the same function.
- Null/undefined checks on a value whose type already guarantees it's present (e.g. checking a required, already-validated parameter again three calls deep).
- Broad `catch (e) {}` or `catch (e) { console.log(e) }` that swallows errors instead of handling or propagating them.
- Input validation duplicated at every layer instead of once at the boundary.

**Fix:** trace the call site — if the guarded state genuinely cannot occur given how the function is called, remove the guard. If it's ambiguous whether it can occur, don't remove it; ambiguity favors caution over "cleanliness."

## Type bypass

- `as any`, `as unknown as X`, `// @ts-ignore`, `# type: ignore` used to silence an error instead of fixing the underlying type mismatch.
- Overly broad parameter/return types (`any`, `object`, `dict`) where a specific type was available and just not used.

**Fix:** fix the underlying type issue. Only leave a bypass in place if the user confirms it's a deliberate, documented escape hatch (e.g. interop with an untyped library).

## Over-engineering

- An abstraction (interface, factory, strategy pattern, config object) with exactly one implementation and one call site — added for hypothetical future flexibility that hasn't materialized.
- A config flag or parameter that's always called with the same value everywhere in the codebase.
- A generic, reusable-looking utility that's actually only ever used once.
- Wrapping a simple operation in an unnecessary class or module boundary.
- Cross-file/cross-module architectural drift: not just one over-abstracted function, but the same concern (e.g. validation, error formatting) re-solved differently in different files because each was generated in a separate session with no shared mental model of the rest of the codebase. Check this at the module level, not just per-function.

**Fix:** collapse to the concrete case. If genuine multiple use cases exist today, keep the abstraction — over-engineering is about premature generality, not all abstraction. For cross-module drift, converge on one existing approach rather than inventing a third.

## Duplicate/parallel implementations

- Multiple functions doing the same job under different names, with different internal structure, because separate generation sessions each reinvented it instead of reusing what already existed ("solved five ways"). This is distinct from dead code below — these are live, reachable, duplicated logic paths, not unused code.
- Grep for near-duplicate function *bodies* (same logic, different names/variable choices), not just textual copy-paste — semantic duplication is the more common AI-generated form.

**Fix:** consolidate to one implementation, update call sites, delete the others. If the duplicates have subtly diverged in behavior, resolve which behavior is correct before merging — don't silently pick one.

## Deep nesting

- 3+ levels of nested `if`/`else` that could be flattened with early returns or guard clauses.
- A large conditional block where the common case is buried inside the nesting instead of handled first.

**Fix:** invert conditions to return/continue early, so the main logic path is left-aligned and the exceptional cases exit up front.

## Test slop

- Tests that assert something trivially true (e.g. asserting a mock returns what the mock was told to return) without exercising real logic.
- Redundant mocks that stub out more of the system than the test actually needs to isolate.
- A wall of near-identical test cases that vary one input value without adding coverage of a genuinely different code path.
- Test names that describe the implementation ("calls foo then bar") instead of the behavior being verified.

**Fix:** keep tests that exercise a real behavior or edge case; cut or consolidate tests that don't add coverage beyond an existing one.

## Naming/style fingerprints

- Generic placeholder-style names in shipped code (`data`, `result`, `temp`, `handleClick2`, `newFunction`) where a specific name was available.
- Suffix-number or vague-adjective naming from iterative regeneration: `data2`, `result_final`, `resultNew`, `helperV2` — a name that reveals it was patched by re-prompting rather than refactored.
- Formatting or structure that's uniformly "textbook" in a way that doesn't match the surrounding file's actual conventions (e.g. every function has a full docstring in a codebase that otherwise has none).
- Uniform, evenly-spaced code structure that reads as generated rather than organically written (every function the same length, every block the same shape).

**Fix:** rename to something specific to the domain; match the file's existing conventions rather than imposing a different uniform style.

## Dead code

- Unused exports, functions, or variables no longer referenced anywhere.
- Unreachable branches (conditions that can never be true given the guards above them).
- Commented-out code left in place "just in case."
- Unused dependencies added to `package.json`/`requirements.txt`/equivalent that nothing in the code actually imports — a common generation-session artifact where a dependency was pulled in for an approach that was later abandoned.

**Fix:** delete. If the user wants to preserve history, that's what version control is for.

## Process/workflow smells (not per-instance scored)

These are signals about how the code arrived, not defects in the code itself — note them if relevant, but don't fold them into the per-instance score in `scoring-rubric.md`:

- A large diff landing as one giant commit instead of incremental, reviewable steps — common when a whole feature was generated in one session rather than built up. Worth a comment suggesting the PR be split, not a "fix," since splitting after the fact has its own cost.

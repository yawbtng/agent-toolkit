---
name: deslop
description: Detect or rewrite text that reads as AI-generated ("slop") — stiff, hedgy, formulaic prose with tells like the "not X, but Y" contrast-reframe, em-dash overuse, and uniform sentence rhythm. Use when the user asks to "humanize" text, "de-slop" it, "make this sound less AI," says something "reads like ChatGPT," asks whether a passage sounds AI-written, or wants writing edited to sound more natural/human. Covers prose and writing only — not a code-quality or anti-overengineering tool.
metadata:
  short-description: Detect or rewrite AI-sounding prose without flattening it into voiceless text
---

# Deslop

Fix text that reads as AI-generated without overcorrecting it into flat, voiceless prose. Sterile writing is its own tell — the goal is text with a pulse, not text with all the AI-isms mechanically stripped out.

## Quick Start

Given a passage, do this in order:

1. **Pick a mode.** Detect (flag only) or Edit (rewrite). See Modes below.
2. **Scan** it against `references/patterns.md`, `references/vocabulary-2026.md`, and `references/structural-checks.md`.
3. **Score** it with `references/scoring-rubric.md` to decide how aggressive to be.
4. **Rewrite** flagged spans individually, applying the over-correction guard (Step 4 below) — then do one **restore-personality** pass.
5. **Check** the fact-preservation constraint before returning Edit-mode output.
6. Output in the format under Output below.

## Modes

- **Detect** — the user is asking "does this sound AI-written?" or wants issues flagged without changes made. Quote the offending spans and name the specific rule each trips (cite the pattern by name, e.g. "contrast-reframe," "em-dash overuse"). Do not rewrite anything.
- **Edit** — the user handed over text to fix, or asked you to humanize/de-slop/rewrite it. Rewrite, then return a short "what changed" list alongside the result.

Default to Edit when text is handed over for fixing; default to Detect when the question is about whether something sounds AI-written.

## Instructions

1. **Scan for tells.** Check the passage against all three reference files:
   - `references/patterns.md` — structural/rhetorical tells, ranked by reliability. The "not X, but Y" contrast-reframe is the single highest-confidence tell; check for it first.
   - `references/vocabulary-2026.md` — current word-level blacklist. This file is dated by design; if a hit feels like a stretch, trust the structural tells over the vocabulary list.
   - `references/structural-checks.md` — sentence-length variance, em-dash frequency (>30% of sentences) and spacing, rule-of-three padding, paragraph shape.

2. **Score the passage** with `references/scoring-rubric.md`. Below 35/50 → full rewrite pass. 35+ → spot-fix only the low-scoring dimensions. This decides how aggressive Step 3 should be — don't rewrite a passage that's already mostly fine just because it tripped one pattern.

3. **Rewrite with the over-correction guard.** This is the step most anti-slop tools get wrong: they subtract every flagged phrase and leave text that reads as generic and lifeless, which is its own AI tell. For each flagged span, ask: is this filler, or is it deliberate voice? Cut filler. Leave voice alone, even if it technically matches a pattern in the catalog. A sentence that uses an em dash *because the rhythm calls for one* is not the same problem as a paragraph that uses five of them as connective tissue.

4. **Restore personality.** After cutting, do one separate pass adding back what pure subtraction removes: a concrete detail, a specific example in place of an abstraction, a sentence-length change that breaks up flattened rhythm, or a moment of actual stance instead of hedged neutrality. Skipping this step is how a "fixed" passage ends up sounding more robotic than the original.

5. **Fact-preservation check (Edit mode only, mandatory before returning output).** Re-read the rewrite against the source. It must not introduce any fact, name, number, date, or quote that wasn't in the original. Rewriting for voice is not license to invent specifics — if a claim needs a concrete detail to feel less abstract and the source doesn't have one, flag the gap to the user rather than making one up.

6. **Long documents: chunk it.** For anything beyond a few paragraphs, work in ~300-500 word sections rather than one pass over the whole thing — nuance and voice consistency degrade at full-document scale. Tell the user if you're doing this so they know why a long doc is coming back in sections.

## Output

**Edit mode:**
```
[revised text]

What changed:
- [specific fix + which tell it addressed, 1 line each]
```

**Detect mode:**
```
[quoted span] — [pattern name from patterns.md / structural-checks.md / vocabulary-2026.md]
[quoted span] — [pattern name]
...
Score: [X]/50 (see references/scoring-rubric.md breakdown if asked)
```

Don't pad either output format with commentary beyond what's asked — the whole point of this skill is not producing more slop while fixing slop.

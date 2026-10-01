# Structural / statistical checks

Mechanically checkable at the sentence and paragraph level — catch these even when no individual word or phrase trips `patterns.md`.

## Sentence-length variance

Read the passage's sentence lengths in sequence. AI-generated prose tends toward a narrow band (most sentences within ~5-10 words of each other) — human prose swings wider, mixing short punchy sentences with longer, more complex ones.

- Flag: 3 or more consecutive sentences within a similar length band (roughly ±3 words of each other).
- Fix: break up the rhythm — combine two into a complex sentence, or cut one down to a fragment for emphasis.

## Em-dash frequency and spacing

- Count sentences containing an em dash. Flag if more than ~30% of sentences in the passage use one.
- Check spacing: AI output typically pads the dash with spaces (` — `). Tighter usage (`—`, no surrounding spaces) is a weaker signal of the same habit.
- Fix: replace with the punctuation the sentence actually calls for — comma, colon, parentheses, or a period and a new sentence. Don't replace every dash; some are genuinely the right call.

## Rule-of-three avoidance

Scan for triplets used as a rhythm crutch: "clear, concise, and actionable" / "fast, reliable, and scalable." Ask: would this work as a pair, or is a third item genuinely needed? If the third item is padding, cut it.

## Paragraph shape

- Flag paragraphs of near-identical length appearing back to back (3+ in a row) — another variance tell, one level up from sentences.
- Flag a document where every section follows the identical internal shape (topic sentence, three supporting points, summary sentence) regardless of what the content actually needs.

## Banned constructions (structural, not vocabulary)

- Opening a paragraph with a rhetorical question used purely as a transition device.
- A closing paragraph that moralizes or reaches for a "big picture" takeaway the piece didn't build toward.
- Bulleting content that would read better as flowing prose (bullet-itis) — a structural tell distinct from word choice.

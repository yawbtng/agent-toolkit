# Current word-level blacklist (dated — refresh periodically)

**This file goes stale.** Word-level tells rotate as models change; the 2023-2024 generation of tells ("delve," "boast," "tapestry," "in the realm of," "navigate the complexities of") is already dated and largely filtered out of current models' default output. Treat this list as a snapshot, not a permanent reference. If it's been more than a few months, spot-check against current sources before leaning on it heavily — structural tells in `patterns.md` and `structural-checks.md` age much more slowly than vocabulary does.

## Current generation (as of 2026 tracking)

Abstract fillers and unearned intensifiers, used where a more specific word would do:

`quietly`, `shift`, `matters`, `shape`, `land`, `actually`, `real`, `earn`, `the work`, `hold`, `pull`, `compound`, `signal`, `built different`

These work differently from the older showy-vocabulary tells — they're plain, common words used as vague abstractions rather than obscure SAT words. "This quietly shapes how teams think about the work" is the current-generation version of what "This fundamentally transforms the paradigm" used to be.

## Prior generation (still worth flagging, now more a giveaway for laziness than obfuscation)

`delve`, `boast`, `tapestry`, `landscape` (metaphorical), `realm`, `navigate` (metaphorical), `underscore`, `robust`, `leverage` (verb), `foster`, `elevate`, `unlock`, `harness`, `seamless`, `holistic`, `paradigm`, `synergy`, `testament to`, `stands as a`, `plays a crucial/pivotal role`

## Usage

Flag a hit only when the word is doing abstract/filler work — not every instance of "actually" or "real" is a tell, context matters. A cluster of 3+ hits from either list in one paragraph is a much stronger signal than a single instance anywhere in a long document.

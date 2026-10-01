---
name: impeccable-design
description: "Cheat sheet and routing guide for all 20 Impeccable design commands. Use this skill when doing UI, frontend, or design work to quickly identify which Impeccable command to use. Also use when the user says impeccable, design cheatsheet, or asks which design command to run."
---

# Impeccable Design — Command Cheat Sheet

Quick reference for all 20 Impeccable design commands. Use this to pick the right command for any design task.

## Start Here

Run `/teach-impeccable` once per project to establish design context (saved to `.impeccable.md`). All other commands depend on this context to avoid generic output.

## Diagnostic (Assess First)

| Command | Purpose | Then use |
|---------|---------|----------|
| `/audit` | Technical quality audit — a11y, perf, theming, responsive, anti-patterns | `/normalize`, `/harden`, `/optimize`, `/adapt`, `/clarify` |
| `/critique` | UX and design review — hierarchy, clarity, emotional resonance | `/polish`, `/distill`, `/bolder`, `/quieter`, `/typeset`, `/arrange` |

**Workflow**: Start with `/audit` or `/critique` to diagnose, then apply targeted fixes.

## Quality (Fix Issues)

| Command | Purpose | Combines with |
|---------|---------|---------------|
| `/normalize` | Align with design system standards and ensure consistency | `/clarify`, `/adapt` |
| `/polish` | Final quality pass before shipping — alignment, spacing, detail | — |
| `/optimize` | Performance — loading, rendering, animations, bundle size | — |
| `/harden` | Error handling, i18n, text overflow, edge cases, resilience | `/optimize` |

## Intensity (Adjust Energy)

| Command | Purpose | Pairs with |
|---------|---------|------------|
| `/quieter` | Tone down overly bold or aggressive designs | `/bolder` (opposite) |
| `/bolder` | Amplify safe or boring designs, increase visual impact | `/quieter` (opposite) |

## Adaptation (Reshape)

| Command | Purpose | Combines with |
|---------|---------|---------------|
| `/clarify` | Improve UX copy, error messages, labels, microcopy | `/normalize`, `/adapt` |
| `/distill` | Strip to essence — remove unnecessary complexity | `/quieter`, `/normalize` |
| `/adapt` | Responsive/cross-platform — different screens, devices, contexts | `/normalize`, `/clarify` |

## Enhancement (Add Value)

| Command | Purpose | Combines with |
|---------|---------|---------------|
| `/animate` | Add purposeful motion, micro-interactions | `/delight` |
| `/colorize` | Add strategic color to monochromatic designs | `/bolder`, `/delight` |
| `/delight` | Add personality, joy, memorable touches | `/bolder`, `/animate` |
| `/onboard` | Onboarding flows, empty states, first-time UX | `/clarify`, `/delight` |
| `/typeset` | Fix typography — fonts, hierarchy, sizing, weight | `/bolder`, `/normalize` |
| `/arrange` | Fix layout, spacing, visual rhythm, composition | `/distill`, `/adapt` |
| `/overdrive` | Technically ambitious — shaders, spring physics, scroll-driven (BETA) | `/animate`, `/delight` |

## System

| Command | Purpose |
|---------|---------|
| `/teach-impeccable` | One-time project context setup — gathers audience, use cases, brand personality |
| `/extract` | Extract reusable components, design tokens, patterns into design system |

## Common Workflows

**New project setup**: `/teach-impeccable` then `/frontend-design`

**Build then review**: Build UI, then `/audit` to find issues, then targeted fixes

**Pre-ship checklist**: `/audit` then `/polish` then `/harden`

**Making it pop**: `/bolder` then `/colorize` then `/animate`

**Calming it down**: `/quieter` then `/distill` then `/typeset`

**Accessibility pass**: `/audit` then `/clarify` then `/adapt` then `/harden`

**Design system extraction**: `/normalize` then `/extract`

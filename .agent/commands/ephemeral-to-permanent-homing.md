# Ephemeral-to-Permanent Homing

Shared workflow partial. Not a slash command.

Referenced by `session-handoff` and `consolidate-docs`.

This file is the canonical method for moving content out of ephemeral surfaces
and into their permanent homes.

## Cardinal Rule

Plans, memory, and entry points are not the final home of durable substance.

Three surfaces accumulate drift if left unswept:

1. **Plans** — execution instructions. Completed plans must be safe to archive.
2. **Memory** — capture and refinement surfaces, not permanent doctrine.
3. **Platform entry points** — pointer files only; they must not carry unique
   instructions.

## Destination table

| Substance shape | Destination |
| --- | --- |
| Host-repo architecture decisions | `docs/architecture-decision-records/` |
| Practice-governance decisions | `.agent/practice-core/decision-records/` |
| Portable general patterns | `.agent/practice-core/patterns/` |
| Repo-grounded pattern instances | `.agent/memory/active/patterns/` |
| Stable system behaviour documentation | relevant `README.md` |
| Code-adjacent API documentation | docstrings and source comments where appropriate |
| Operator or workflow runbooks | `docs/` or the relevant canonical operational surface |
| In-progress learning not yet promoted | `.agent/memory/active/distilled.md` |
| Stable repo-wide rules | `.agent/directives/` or `.agent/rules/` |
| Exploratory but durable option-weighing | `docs/explorations/` |
| Exploratory synthesis | `.agent/research/` |
| Consolidated investigations | `.agent/analysis/` |
| Formal promoted reports | `.agent/reports/` |
| Evergreen library material | `.agent/reference/` |
| Subjective session reflection | `.agent/experience/` |
| Ephemeral cross-repo exchange | `.agent/practice-context/outgoing/` |

If content does not deserve a permanent home, remove it. Deletion is a valid
disposition when the content adds no durable value.

## Method

For each candidate:

1. classify the substance
2. choose the most durable fitting home
3. verify that the destination is real and not already carrying the same idea
4. move or rewrite the content into that home
5. strip it from the ephemeral source
6. cross-link only when the destination benefits from a pointer

## Entry-point rule

`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are pointer files. If they carry more
than a pointer to `.agent/directives/AGENT.md`, that extra content is drift and
must be homed or removed.

## Deferral honesty

Any deferred homing outcome must satisfy
[PDR-026](../practice-core/decision-records/PDR-026-per-session-landing-commitment.md):
name the constraint or priority tension, provide evidence, and make the
deferral falsifiable.

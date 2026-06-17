---
provenance: provenance.yml
fitness_line_count: 240
fitness_char_count: 19000
fitness_line_length: 100
split_strategy: "Promote stable specialised doctrine into PDRs"
---

# Practice Lineage

This file explains how the Practice evolves, how it propagates between repos,
and what bar a structural change must clear before it becomes doctrine.

## Portable Package and Provenance

The Practice Core travels as a bounded package. Its portable governance and
portable general patterns travel inside the Core rather than in loose peer
directories.

Each trinity file and the verification file point at `provenance.yml`. That
file records how the Core evolved in this repo over time.

## Principles

The Practice is anchored by a small set of stable principles.

- Ask the First Question first.
- Prefer tests before implementation.
- Keep behaviour explicit and boundaries validated.
- Fail fast with helpful errors.
- Keep types precise.
- Never disable quality gates to force progress.
- Keep canonical content in `.agent/`; adapters stay thin.
- Treat misleading documentation as a bug.

The host repo may add stronger local rules, but it should not weaken these.

## Metacognition

Before planning or committing to a design, pause:

> Think hard. Those are your thoughts.
> Reflect on those thoughts. Those are your reflections.
> Consider those reflections. Those are your insights.
>
> How do those insights change how you see the work, the plan, and the value?

This is not ceremony. It is a lightweight way to prevent shallow execution.

## Testing Philosophy

The Practice expects:

- behaviour-focused tests
- the correct proof layer for each claim
- deterministic tests by default
- explicit injected seams rather than hidden global state
- test-first work whenever a behaviour change is being made

Local ecosystems should express this in their own tools and naming
conventions.

## The Feedback Loops

The Practice has two primary loops and one cross-plane loop.

### Session Loop

`session-handoff` closes a session. It records what landed, refreshes
continuity, updates the thread record, and captures surprises while they are
still fresh.

### Consolidation Loop

`consolidate-docs` closes a thread tranche. It graduates settled learning,
extracts reusable patterns, manages fitness, and integrates incoming Practice
material.

### Cross-Plane Loop

Some observations originate in active work but belong in operational or
executive memory. Those observations are captured in the napkin with a source
plane tag and routed during consolidation to the proper lasting surface.

## How the Practice Changes

Most learnings belong in the napkin first. The Practice itself should change
only when all three conditions hold:

1. the learning came from real work
2. leaving it out would cause repeated mistakes
3. the lesson feels stable enough to ratify

This keeps the Practice ratcheting forward instead of swinging with every
session.

## Integration Flow

When incoming Practice material lands in the Practice Box:

1. confirm the provenance chain and package shape
2. read the incoming Core and any ephemeral context
3. compare concepts, not filenames
4. preserve stronger existing local contracts
5. adapt every adopted concept to the host language and runtime truthfully
6. land the updated local surfaces
7. clear the Practice Box once integration is complete

The important rule is adaptation, not copying. A host repo should inherit the
benefit of the incoming concept without importing stale assumptions from the
sending repo.

## Knowledge Routing

The Practice distinguishes between adjacent durable surfaces:

- `docs/explorations/` for durable option-weighing before commitment
- `research/` for exploratory synthesis
- `analysis/` for consolidated investigations and evidence
- `reports/` for promoted report artefacts
- `reference/` for curated evergreen library material
- `experience/` for session-scoped reflection

Explorations sit between observation and decision. Plans execute; ADRs and PDRs
decide; explorations keep the reasoning trail alive before the decision is
settled.

## Vital Surfaces

The Practice is structurally present only when the key integration surfaces
exist in some working form:

- entry-point chain into `AGENT.md`
- local bridge in `.agent/practice-index.md`
- session-start skills
- active memory surfaces
- continuity surfaces
- graduation workflow
- explicit document tiers and exploration surface
- planning architecture with strategic and collection-level indexes
- quality gates and validators
- explicit platform support contract where multiple platforms exist

`practice-verification.md` contains the operational checks for these surfaces.

## Role of Decision Records and Patterns

Portable governance decisions belong in `decision-records/` as PDRs. Portable
general engineering patterns belong in `patterns/`. Repo-local evidence and
instances remain in `.agent/memory/active/patterns/`.

This split keeps the portable Core small enough to travel and rich enough to
teach.

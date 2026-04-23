# PDR-011: Continuity Surfaces and the Surprise Pipeline

- Status: Accepted
- Date: 2026-04-23

## Context

Continuity and learning both matter, but they operate at different speeds. A
repo needs a cheap session-close routine and a slower doctrine-graduation
routine. If those are collapsed into one workflow, either closeout becomes too
heavy to run often or learning capture becomes too weak.

## Decision

The Practice uses:

- `session-handoff` for session-scoped continuity refresh and fresh capture
- `consolidate-docs` for slower graduation, integration, and fitness work

The surprise pipeline is:

1. capture in the napkin
2. refine in distilled memory
3. graduate into stable docs, PDRs, patterns, or ADRs
4. enforce through directives, rules, and validators

The continuity host in this template lives in operational memory:
`repo-continuity.md`, thread records, and track cards.

## Consequences

- session close stays cheap enough to run every time
- consolidation has a clear scope and trigger
- the learning loop has named surfaces instead of implied convention

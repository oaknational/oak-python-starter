# PDR-003: Sub-Agent Protection of Foundational Practice Docs

- Status: Accepted
- Date: 2026-04-23

## Context

Scoped sub-agents are useful for bounded implementation or review work, but
they do not carry the whole cross-file and cross-session context needed to edit
foundational Practice doctrine safely.

## Decision

Scoped sub-agents must not edit the foundational Practice surfaces:

- `.agent/practice-core/`
- `.agent/directives/`
- `.agent/rules/`
- platform rule adapters

The coordinating agent may still update those files when the user asks for it
and the wider context has been read.

## Consequences

- Foundational Practice changes stay deliberate and curated.
- Sub-agents can still report findings about those surfaces.
- The host repo should operationalise this with a local rule.

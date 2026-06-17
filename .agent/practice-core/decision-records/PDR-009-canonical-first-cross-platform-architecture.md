# PDR-009: Canonical-First Cross-Platform Architecture

- Status: Accepted
- Date: 2026-04-23

## Context

Multi-platform Practice estates decay quickly if each platform grows its own
copy of the doctrine. Drift becomes hard to see and expensive to repair.

## Decision

The Practice uses a canonical-first layout:

- substantive content lives in `.agent/`
- platform directories hold thin adapters only
- the executive surface matrix records supported and unsupported mappings

Adapters should contain activation metadata and a pointer to the canonical
source, not a second copy of the logic.

## Consequences

- canonical files become the single source of truth
- parity checks can reason about one source and many adapters
- unsupported states must be explicit rather than inferred from silence

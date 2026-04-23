# PDR-007: Promoting PDRs and Portable Patterns to First-Class Core Surfaces

- Status: Accepted
- Date: 2026-04-23

## Context

Portable governance and portable patterns need durable homes inside the Core.
If they live only in peer directories or ephemeral exchange packs, important
Practice substance drifts away from the package that is supposed to carry it.

## Decision

The Core package includes three required directories:

- `decision-records/` for portable Practice governance
- `patterns/` for portable general patterns
- `incoming/` for inbound Core material

`.agent/practice-context/` remains an optional peer directory for ephemeral
exchange support only.

## Consequences

- Durable governance now travels with the Core by construction.
- Portable patterns no longer need a second permanent home outside the Core.
- The Practice Box remains transient and should be cleared after integration.

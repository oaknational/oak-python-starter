---
fitness_line_count: 160
fitness_char_count: 12000
fitness_line_length: 100
split_strategy: "Move specialised doctrine to focused docs when this grows"
---

# Principles

These rules apply across the repo.

## First Question

Could it be simpler without compromising quality?

## Design

- Keep it simple: DRY, KISS, YAGNI, SOLID.
- Prefer pure functions and explicit boundaries.
- Validate unknown external data at the boundary.
- Fail fast with specific messages.
- Remove dead code rather than preserving it.
- Use relative paths only.

## Quality

- All quality gates are blocking.
- Never disable checks or work around them with ignores.
- Prefer precise types over widened ones.
- Preserve one source of truth for names, interfaces, and contracts.

## Refactoring

- Replace old shapes rather than adding compatibility layers.
- Fix files in place; let git carry history.

## Documentation

- Canonical guidance lives in `.agent/`.
- Platform directories stay as thin adapters.
- Keep decisions discoverable from the Practice Index.

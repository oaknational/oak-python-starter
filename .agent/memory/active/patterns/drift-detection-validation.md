---
name: Drift Detection Validation
domain: validation
proven_by: cross-platform surface parity checks plus repo-audit consolidation (2026-03-19, refined 2026-03-22)
prevents: manually maintained lists silently diverging from canonical sources, repo-state drift being forced into the wrong checker
---

# Drift Detection Validation

## Principle

When a duplicate list cannot be eliminated cleanly, add a validation step that
compares the maintained list against its canonical source and fails on drift.

## Pattern

1. Derive the list automatically if that is safe and simple.
2. If it cannot be derived, identify the canonical source explicitly.
3. Add the narrowest validation that compares the maintained copy against that
   source.
4. Choose the checker that matches the concern:
   - repo-audit or direct filesystem/text inspection for tracked repo state
   - tests only when the drift concerns imported code behaviour or runtime
     contracts
5. Make the failure message explain what drifted and where the canonical truth
   lives.

## Anti-pattern

- Maintaining duplicate lists with no alarm when they diverge
- Forcing repo-state, link-estate, or wrapper-parity checks into `pytest` just
  because "it is already there"
- Adding a second semi-canonical list and hoping reviewers notice drift by eye

## When to Apply

Use this when structural constraints force a manually maintained duplicate of a
canonical list, roster, or mapping, and the right answer is a compensating
validation step rather than a second hidden source of truth.

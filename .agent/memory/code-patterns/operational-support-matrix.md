---
name: Operational Support Matrix
domain: agent-infrastructure
proven_by: cross-platform Practice surface refactor (2026-03-21)
prevents: over-claimed parity, exploratory docs doubling as live contracts, silent unsupported states
---

# Operational Support Matrix

## Principle

When a repo supports multiple agent platforms, keep a small operational matrix
that records which semantic surfaces are `native`, `portable`,
`entry-point`, or `unsupported`.

The matrix is the implementation contract. Research notes explain why; they do
not carry live support state.

## Pattern

1. Keep one row per semantic surface, for example:
   - entry-points
   - directives
   - rules
   - skills
   - commands
   - subagents
   - hooks
2. Use a fixed vocabulary for platform cells:
   - `native`
   - `portable`
   - `entry-point`
   - `unsupported`
3. Put detailed platform evidence and source links in a separate research note.
4. Link the matrix from the local bridge and at least one active entry surface.
5. Back the matrix with repo-audit checks so unsupported states are explicit
   and wrapper expansion cannot drift ahead of the documented model.

## Anti-pattern

- Letting an exploratory research note act as the live contract
- Treating a portable adapter family such as `.agents/skills/` as evidence for
  blanket cross-platform parity
- Leaving unsupported states blank and expecting future readers to infer intent
- Adding wrappers for symmetry before the repo has recorded them as supported

## When to Apply

Use this when a repo's agent infrastructure spans multiple platforms and the
same semantic surface does not map cleanly or symmetrically everywhere.

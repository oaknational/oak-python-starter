---
name: tsdoc
classification: passive
description: >-
  Write or repair code-adjacent API documentation and the matching README or
  ADR updates that belong with a public interface change.
---

# TSDoc

The skill name is kept for cross-repo continuity. In this Python template, the
equivalent surface is docstrings and adjacent API-facing documentation rather
than TypeScript-specific TSDoc comments.

## Use when

- changing public Python APIs
- adding behaviour that needs a clearer docstring or usage note
- fixing stale documentation close to code
- updating a README or ADR alongside a public interface change

## Read first

1. `.agent/directives/principles.md`
2. `.agent/directives/testing-strategy.md` when documenting test-facing
   behaviour
3. `.agent/rules/documentation-hygiene.md`

## Documentation boundary

- docstrings explain API shape, intent, invariants, and edge cases near code
- README files explain how to use or operate a package, tool, or surface
- ADRs capture significant architectural decisions

Do not duplicate the same explanation across all three homes. Put the content
in its canonical place and link across only when helpful.

## Checklist

1. Update stale symbol names and examples.
2. Check whether a README or ADR also needs to change.
3. For non-trivial public APIs, document parameters, return shape, and any
   important preconditions or failure modes.
4. Run the relevant gates after editing.

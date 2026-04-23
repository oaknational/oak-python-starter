---
name: code-patterns
classification: passive
description: >-
  Check the Core and repo-local pattern libraries for known solutions to
  recurring design problems before inventing a new approach. Triggered when
  facing type-safety issues, validation questions, or boundary design pressure.
---

# Code Patterns

When you identify a design problem -- especially type-safety issues,
validation questions, or boundary design pressure -- check both
`.agent/practice-core/patterns/` and `.agent/memory/active/patterns/`
before inventing a new approach.

## When to Use

- You are about to write a type ignore or cast
- You are designing a validation boundary
- You see a runtime conversion that mirrors a compile-time type
- You encounter a function returning a claimed type for unvalidated data
- A reviewer flags boundary pressure or type widening

## Steps

1. Read `.agent/practice-core/patterns/README.md` to see whether a portable
   general pattern already exists.
2. Read `.agent/memory/active/patterns/README.md` to discover repo-local
   patterns.
3. Match the current problem against each pattern's description.
4. If a pattern matches, read its full file and apply the approach.
5. If no pattern matches, proceed normally -- do not force a fit.

## Important

This skill is not always-active. It triggers when an engineer or agent encounters a design problem where type safety, validation, or boundary pressure is involved. It is a discovery mechanism, not a mandate.

---
name: Component Composition Pattern
domain: agent-infrastructure
proven_by: local reviewer-template refactoring (2026-03-18)
prevents: duplicated universal content across templates, O(N) maintenance for common changes
---

# Component Composition Pattern

## Principle

When multiple templates use the same universal content, extract that content
into reusable components and let the templates reference them.

## Pattern

```markdown
# Component: .agent/sub-agents/components/behaviours/reading-discipline.md
[Universal reading requirements]

# Template: .agent/sub-agents/templates/code-reviewer.md
## Component References (MANDATORY)
- `.agent/sub-agents/components/behaviours/reading-discipline.md`
- `.agent/sub-agents/components/principles/review-discipline.md`
```

## Anti-pattern

Making every template fully self-contained when several of them use the same
behaviours or principles. That turns one universal change into many edits.

## When to Apply

Use this when 3 or more templates need the same behaviours, principles, or
personas.

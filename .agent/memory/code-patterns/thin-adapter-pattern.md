---
name: Thin Adapter Pattern
domain: agent-infrastructure
proven_by: local Practice integration (2026-03-17)
prevents: content duplication, adapter drift, platform-specific lock-in
---

# Thin Adapter Pattern

## Principle

Substantive content lives once in a canonical location (`.agent/`). Platform-specific files (`.cursor/`, `.claude/`, `.codex/`, `.agents/`) are thin wrappers that delegate to the canonical source.

## Pattern

```markdown
# Canonical: .agent/rules/my-rule.md
[Full content with reasoning, anti-patterns, examples]

# Adapter: .cursor/rules/my-rule.mdc
---
description: Brief description
alwaysApply: true
---
Read and follow `.agent/rules/my-rule.md`.

# Adapter: .claude/rules/my-rule.md
Read and follow `.agent/rules/my-rule.md`.
```

## Anti-pattern

Placing substantive content directly in a platform adapter. This creates:
- Invisible content (other platforms never see it)
- Drift risk (content diverges between adapters)
- Maintenance burden (updates must happen in multiple places)

## When to apply

Every time content needs to be available to platform-specific tooling. The adapter exists to make the canonical content discoverable; it never adds substantive content of its own.

# Invoke Code Reviewers

Use reviewer sub-agents when:

- a change is non-trivial
- the design has meaningful boundary or tooling consequences
- a review request explicitly asks for findings

Default flow:

1. Invoke `code-reviewer`.
2. Add `architecture-reviewer` when boundaries, imports, or public APIs move.
3. Add `test-reviewer` when tests or TDD evidence need scrutiny.
4. Add `security-reviewer` when trust boundaries or sensitive input handling
   change.
5. Add `config-reviewer` when toolchain files, hooks, or quality gates change.

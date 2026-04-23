# Invoke Code Reviewers

Executive-memory surface. Look this up when a non-trivial change needs review
triage.

Use reviewer sub-agents when:

- a change is non-trivial
- the design has meaningful boundary or tooling consequences
- a review request explicitly asks for findings

Default flow:

1. Invoke `code-reviewer` as the gateway reviewer.
2. Add `architecture-reviewer` when boundaries, public APIs, scope framing, or
   planning shape need challenge.
3. Add `test-reviewer` when tests or TDD evidence need scrutiny.
4. Add `security-reviewer` when trust boundaries or sensitive input handling
   change.
5. Add `config-reviewer` when toolchain files, hooks, or quality gates change.

## Phase alignment

- **Plan-time**: architecture review and any relevant installed specialist
- **Mid-cycle**: test, security, config, or architecture review when the work
  crosses their boundary
- **Close**: code-reviewer plus any needed specialist follow-through

Do not require reviewers the repo has not installed.

---
name: Observable Entrypoint Behaviour Tests
domain: testing
proven_by: package-entrypoint polish in python-repo-template (2026-04-22)
prevents: wrapper tests that lock delegation wiring, implementation-shaped
  entrypoint tests, repo-configuration assertions leaking into pytest
---

# Observable Entrypoint Behaviour Tests

## Principle

When an entrypoint is intentionally thin, test the behaviour the caller sees,
not which internal function the wrapper happens to call.

## Pattern

1. Drive the real entrypoint with representative `argv` or equivalent inputs.
2. Use deterministic fixtures and captured output to assert the user-visible
   contract.
3. Keep configuration, file-presence, and type-shape checks in their matching
   tools such as `tools/repo_audit.py` and the type checker.

## Anti-pattern

- Monkeypatching an internal delegate only to prove one function called
  another
- Asserting module aliases or import wiring for a thin wrapper
- Extending a behaviour test to also validate tracked-file canon or type
  details

## When to Apply

Use this when a package, module, or script entry surface exists mainly to
expose an established behaviour under a different invocation path.

# Component: TDD Phase Structure

Every non-trivial workstream follows RED, GREEN, and REFACTOR.

## RED

Write the failing proof first. If the proof passes before implementation, the
proof is wrong or is proving the wrong thing.

## GREEN

Write the minimal implementation that makes the proof pass. Do not broaden the
solution before the proof requires it.

## REFACTOR

Improve structure, naming, documentation, and cross-references without changing
behaviour. The proof stays green throughout.

## Deterministic validation

Every task should carry commands with expected outcomes, for example:

```bash
uv run test
# Expected: exit 0
```

---
fitness_line_count: 120
fitness_char_count: 9000
fitness_line_length: 100
split_strategy: "Keep this as the operational entry point and move detail to linked docs"
---

# AGENT.md

Read all of this first, then follow it.

## Grounding

Use British spelling, grammar, and date formats in repo-facing text.

For planning work, read [metacognition.md](./metacognition.md) and reflect
before locking an approach.

## The Practice

This repo uses the Practice as first-class infrastructure. For orientation, see
[practice-core/index.md](../practice-core/index.md). For the local bridge, see
[practice-index.md](../practice-index.md).

## First Question

Always ask: could it be simpler without compromising quality?

## Project Context

This repository has three strands:

- **agentic engineering** — commands, rules, hooks, reviewers, and the working
  method
- **runtime infrastructure** — validation boundaries, file formats, reports,
  audits, and quality gates
- **demo application** — the seeded `activity-report` CLI that exercises the
  infrastructure without becoming the repo identity

See [project-context.md](./project-context.md) for the fuller repo model.

## Rules

Read and apply:

- [principles.md](./principles.md)
- [testing-strategy.md](./testing-strategy.md)
- [invoke-code-reviewers.md](./invoke-code-reviewers.md)

## Use Reviewers

Use reviewer sub-agents proactively. Reviewers can assess intentions as well as
diffs, which is often the cheapest place to catch a poor design.

Available reviewers:

- `code-reviewer`
- `architecture-reviewer`
- `test-reviewer`
- `security-reviewer`
- `config-reviewer`

## Essential Links

- [Vision](../VISION.md)
- [Practice Index](../practice-index.md)
- [Artefact Inventory](./artefact-inventory.md)
- [Cross-Platform Surface Matrix](../reference/cross-platform-agent-surface-matrix.md)
- [Roadmap](../plans/roadmap.md)

## Development Commands

```bash
uv sync
uv run check
uv run test
uv run coverage
```

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
Read [orientation.md](./orientation.md) when you need to route information to
the correct layer or resolve authority questions.

## The Practice

This repo uses the Practice as first-class infrastructure. For orientation, see
[practice-core/index.md](../practice-core/index.md). For the local bridge, see
[practice-index.md](../practice-index.md).

This repo uses the full three-plane memory estate:

- `active/` for the learning loop
- `operational/` for continuity and session resume
- `executive/` for stable organisational contracts

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
- [data-boundary-doctrine.md](./data-boundary-doctrine.md)
- [evidence-methodology.md](./evidence-methodology.md)
- [Invoke Code Reviewers](../memory/executive/invoke-code-reviewers.md)

## Use Reviewers

Use reviewer sub-agents proactively. Reviewers can assess intentions as well as
diffs, which is often the cheapest place to catch a poor design.

Available reviewers:

- `code-reviewer`
- `architecture-reviewer`
- `test-reviewer`
- `security-reviewer`
- `config-reviewer`

For non-trivial work, align review to the lifecycle:

- plan-time for framing and scope
- mid-cycle for proofs, boundaries, or tooling
- close for whole-change coherence

## Essential Links

- [Vision](../VISION.md)
- [Practice Index](../practice-index.md)
- [Artefact Inventory](../memory/executive/artefact-inventory.md)
- [Cross-Platform Surface Matrix](../memory/executive/cross-platform-agent-surface-matrix.md)
- [Repo Continuity](../memory/operational/repo-continuity.md)
- [High-Level Plan](../plans/high-level-plan.md)
- [Roadmap](../plans/roadmap.md)

## Development Commands

```bash
uv sync
uv run clean
uv run build
uv run dev
uv run check
uv run check-ci
uv run fix
uv run test
uv run coverage
```

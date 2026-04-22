# Create or Refine a Plan

## Before Writing

1. **Design gate**: Has the design intent been explored and confirmed
   with the project owner? If the scope is ambiguous or the approach
   has multiple valid paths, run `jc-metacognition` first to explore
   intent, constraints, and tensions before committing to a plan
   structure. Ask one question at a time; prefer multiple-choice
   options when possible; propose 2–3 approaches with strengths and
   drawbacks.
   Do not skip this step for non-trivial work.

2. Read the directives:
   - `.agent/directives/principles.md`
   - `.agent/directives/testing-strategy.md`

3. If the user has not provided enough detail, ask specific
   questions. Do not guess scope, intent, or acceptance criteria.

## Plan Requirements

Every plan MUST have:

1. **TDD phase structure** — RED (tests first, must fail), GREEN
   (minimal implementation), REFACTOR (docs, cleanup). Research and
   evaluation plans still use this structure: RED scaffolds the decision and
   evidence shape, GREEN gathers and compares evidence, REFACTOR tightens the
   recommendation and canon.
2. **Quality gates** after each phase
3. **Acceptance criteria** for every task — specific, checkable,
   with deterministic validation commands
4. **Risk assessment** — what could go wrong and how to mitigate
5. **Foundation alignment** — explicit references to principles.md
   and testing-strategy.md
6. **Non-goals** — what we are explicitly NOT doing (YAGNI)
7. **Standalone next-up entry** — any plan marked current, next-up, or
   session-entry must contain enough context to start fresh without hidden
   memory: current-state snapshot, entry checklist, deliverable destination,
   decision contract where applicable, and closure criteria

## Plan Location

Place plans in `.agent/plans/<domain>/<lifecycle>/` using the canonical structure (see `.agent/plans/README.md`). Cursor-specific plan files (with frontmatter todos) may exist in `.cursor/plans/` for platform tracking but the canonical copy always lives in `.agent/plans/`.

## First Question

Before every decision in the plan: **could it be simpler
without compromising quality?**

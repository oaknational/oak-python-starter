# Create or Refine a Plan

## Before Writing

1. Read:
   - `.agent/directives/principles.md`
   - `.agent/directives/testing-strategy.md`
   - `.agent/directives/orientation.md`
   - `.agent/directives/data-boundary-doctrine.md`
   - `.agent/directives/metacognition.md` for non-trivial work
2. Re-ground on the relevant collection:
   - `.agent/plans/high-level-plan.md`
   - the collection `README.md`
   - `current/README.md` before writing a new next-up plan
   - `active/README.md` before changing in-flight execution
3. Ask the First Question:
   - could it be simpler without compromising quality?

## Required plan shape

Every non-trivial plan must state:

1. **End goal** — the user-impact or repo-impact outcome
2. **Mechanism** — why the proposed means reach that end
3. **Means** — the concrete tasks or phases
4. **Acceptance criteria** — specific, checkable, deterministic where possible
5. **Risk assessment** — what could go wrong and how we reduce it
6. **Foundation alignment** — relevant directives, rules, ADRs, or PDRs
7. **Non-goals** — explicit YAGNI boundaries

Use unambiguous verbs. Do not write "update", "sync", or "propagate" when the
real action is "rewrite", "copy verbatim", "reconcile", or "promote".

## Planning architecture

Canonical plans live in `.agent/plans/`.

- `high-level-plan.md` is the strategic cross-collection index
- collection `README.md` files are hubs and read-order surfaces
- `active/` holds in-progress execution
- `current/` holds queued next-up work
- `future/` holds later or adjacent work
- `completed-plans.md` indexes archived completions
- `.agent/plans/templates/` holds reusable templates and components

## Build-vs-buy gate

If the plan proposes building a reusable capability, wrapper, tool, service, or
non-trivial abstraction, include a build-vs-buy attestation:

- what was searched
- what was found
- why building was preferred, or why an existing option was adopted

## Reviewer phase alignment

For non-trivial work, schedule review at the lifecycle moment where it is
cheapest to act:

- plan-time: architecture and assumption checks
- mid-cycle: test, config, security, or boundary checks as the work changes
- close: whole-change coherence and documentation fit

Use the installed reviewer roster and any local specialists that exist. Do not
name imaginary reviewers as required participants.

## Quality gates

Plans must name the relevant validation commands. In this repo the canonical
surface is `uv run ...`.

Typical gates:

- `uv run format`
- `uv run lint`
- `uv run typecheck`
- `uv run test`
- `uv run coverage`
- `uv run repo-audit`
- `uv run check`
- `uv run check-ci`

## Templates

Use the templates under `.agent/plans/templates/` rather than inventing a new
shape when a template already fits.

# Thread: pythonic-alignment

## Participating Agent Identities

| agent_name | platform | model | session_id_prefix | role | first_session | last_session |
| --- | --- | --- | --- | --- | --- | --- |
| Codex | codex | gpt-5 | unknown | executor | 2026-04-23 | 2026-04-23 |

## Owning Plans

- [`../../../plans/runtime-infrastructure/current/pythonic-alignment-and-commitizen-adoption.md`](../../../plans/runtime-infrastructure/current/pythonic-alignment-and-commitizen-adoption.md)

## Current Objective

- Deliver the bounded Pythonic alignment pass: broaden the demo so every direct
  runtime dependency is used truthfully, adopt `matplotlib` and `commitizen`,
  add installed-wheel verification, ship `py.typed`, centralise gate-command
  truth, and enforce dependency hygiene without weakening Oak constraints.

## Current State

- The plan for Pythonic alignment, demo expansion, and Commitizen adoption is
  written and queued in the runtime-infrastructure current lane.
- Architecture review has already challenged the framing and confirmed the
  highest-value Pythonic moves are package truthfulness, installed-surface
  verification, strict typing, and tooling coherence rather than broad repo
  restructuring.
- Owner direction changed the dependency-truthfulness decision: the repo should
  use a richer bounded demo to justify the installed dependency set rather than
  trimming the set down to the current smaller example.
- WS1 is now explicit in the plan: the richer demo is a bounded "activity
  pack" made of one activity log, one same-stem YAML sidecar, optional HTTPS
  retrieval, and deterministic chart output, with a concrete truthful role for
  each direct runtime dependency.
- WS2 is now landed: `activity-report` accepts bounded HTTPS inputs through the
  existing `--input` flag, auto-discovers or overrides same-stem YAML sidecars
  through `--metadata`, renders metadata-aware summaries, and generates charts
  through `matplotlib` rather than bespoke PNG byte code.
- The shipped metadata fixture and README now demonstrate labels, target
  minutes, and the bounded activity-pack story directly.
- WS3 is now landed: the package ships `py.typed`, `pyproject.toml` makes
  `pyright` scope and strict mode explicit, the wheel target force-includes the
  typing marker, and repo audit enforces that typing contract.
- The widened demo and repo-owned tooling still pass under strict pyright, and
  both the wheel and sdist were verified to contain `py.typed`.
- WS4 is now landed: `commitizen` is in the dev dependency group,
  `pre-commit install` now installs `commit-msg` alongside `pre-commit` and
  `pre-push`, and the hook validates the actual commit-message file via
  `uv run cz check --allow-abort --commit-msg-file`.
- README, `docs/dev-tooling.md`, and the canonical commit workflow doc now
  expose the truthful `uv run cz commit` / `uv run cz check` path.
- While landing WS4, a packaging regression surfaced: Hatch's `packages = [...]`
  wheel setting collapsed the shipped path to `python_repo_template/*`.
  The wheel target now uses `only-include` plus `sources` to preserve
  `oaknational/python_repo_template/*`, and repo audit now guards that
  namespace-preserving contract.
- The landing finished with a passing `uv run check`, so the repo is ready to
  move directly into WS5 rather than another WS4 stabilisation pass.

## Blockers / Low-Confidence Areas

- Gate-command centralisation and dependency-hygiene enforcement should land in
  a shape that stays small and readable rather than becoming a framework.
- Installed-wheel verification still needs to be added to the canonical build
  and check path so the repaired namespace-preserving wheel shape is proven as
  an installed artefact, not only as a built file.

## Next Safe Step

- Start WS5 of the plan: add installed-wheel verification to the canonical
  build and check path, then continue with gate-command centralisation.

---
name: "Pythonic Alignment, Demo Expansion, and Commitizen Adoption"
overview: "Make the template more idiomatic for Python users by broadening the truthful demo, tightening packaging, and strengthening tool enforcement without weakening Oak constraints."
todos:
  - id: baseline
    content: "Define the keep/change boundary and the richer demo contract."
    status: completed
  - id: demo
    content: "Expand the bounded demo so every installed runtime dependency is used truthfully."
    status: completed
  - id: typing
    content: "Ship `py.typed` and make strict type-checking expectations explicit."
    status: completed
  - id: commitizen
    content: "Add Commitizen and enforce conventional commits through the commit-msg hook."
    status: completed
  - id: wheel
    content: "Add an installed-wheel smoke check to the canonical build and check path."
    status: pending
  - id: registry
    content: "Centralise gate-command truth and add dependency-hygiene enforcement."
    status: pending
  - id: gates
    content: "Run the canonical quality gates."
    status: pending
  - id: review
    content: "Run the relevant reviewer passes."
    status: pending
---

# Pythonic Alignment, Demo Expansion, and Commitizen Adoption

**Last Updated**: 2026-04-23  
**Status**: 🔄 ACTIVE  
**Scope**: Make the repo more idiomatic for Python developers by broadening the demo, tightening packaging truth, and strengthening enforcement without relaxing Oak's namespace, `uv`, Practice, or safety requirements.

## End Goal

The template should feel recognisably Pythonic to a Python developer while
still teaching the Oak contract: `oaknational.*` namespacing, `uv run ...`
commands, strict gates, strict typing, and Practice-first repo governance.

## Mechanism

Prefer established Python tooling and library surfaces where they improve
clarity without displacing Oak's canonical contracts. In practice that means:

- broaden the seeded demo into a small but more realistic pipeline that uses
  every installed runtime dependency truthfully rather than carrying unused
  declarations
- use `matplotlib` for charting instead of maintaining bespoke PNG generation
  code
- make the package's typing contract explicit with `py.typed` and strict type
  checking
- use `commitizen` for structured conventional commits and commit-message
  enforcement instead of relying on manual discipline
- verify the built wheel as an installed artefact, not only as source-tree code
- centralise gate-command truth and add dependency-hygiene enforcement so the
  Pythonic surface stays truthful over time

## Context

- the architecture reviewer recommended installed-wheel verification,
  `py.typed`, centralised gate-command truth, and dependency hygiene as the
  strongest additional Pythonic improvements.
- the same review also suggested trimming unused dependencies, but owner
  direction overrode that path: the demo should instead become sufficiently
  realistic to justify the installed dependency set.
- WS2 has now replaced the bespoke PNG byte writer with a bounded
  `matplotlib` chart path.
- WS2 now exercises `requests` and `pyyaml` in shipped package code through
  bounded HTTPS input support and YAML sidecars, so the direct runtime
  dependency set is now truthful at the demo layer.
- the repo already ships a sidecar metadata fixture,
  `data/fixtures/activity_log.metadata.yaml`, which is a natural bounded YAML
  surface for the richer demo rather than a prompt to invent a second config
  family.
- the repo uses `pre-commit`, and WS4 strengthens that existing hook surface
  by adding truthful `commit-msg` validation rather than introducing a
  parallel hook manager
- `check-ci` proves the repo builds from source, but it does not yet prove the
  built wheel installs and runs correctly in isolation.
- WS3 has now landed: `pyright` scope and strictness are explicit in
  `pyproject.toml`, `py.typed` ships in both sdist and wheel artefacts, and
  repo audit now guards the typing contract so it cannot silently drift.
- WS4 has now landed: `commitizen` is part of the dev tooling set,
  `pre-commit install` now installs `commit-msg` alongside `pre-commit` and
  `pre-push`, the hook validates the real commit-message file via
  `uv run cz check --allow-abort --commit-msg-file`, and the repo docs expose
  the canonical `uv run cz commit` / `uv run cz check` workflow.
- while landing WS4, a wheel-path regression surfaced: Hatch's `packages = [...]`
  setting was collapsing the shipped path to `python_repo_template/*` instead
  of preserving `oaknational/python_repo_template/*`. The wheel target now uses
  namespace-preserving `only-include` plus `sources`, and repo audit guards
  that packaging contract.
- the repo intentionally preserves Oak-specific constraints that are not open
  for dilution: namespace packaging, `uv` command truth, strict gates, and the
  Practice estate

## Existing Capabilities

- canonical command surface in `pyproject.toml` and `devtools.py`
- injectable demo seams and behaviour-first tests
- runtime dependencies already present for data loading, numerical work,
  plotting, YAML support, HTTP access, and Parquet I/O
- `pre-commit` already present in the dev dependency group and active in the
  repo
- a passing build probe already exists in the canonical gate sequence

## Non-Goals

- replace the `oaknational.*` namespace with a flatter import surface
- replace `uv run ...` with ad hoc shell aliases or secondary task runners
- relax strict gates, hook discipline, or Practice governance to feel more
  conventional
- trim runtime dependencies simply to fit the current smaller demo shape
- grow the demo application beyond a bounded proof surface for the template
- add service clients, auth flows, retries, caching layers, or background sync
  just to justify `requests`
- turn YAML support into an open-ended configuration system
- introduce a second domain model, dashboard surface, or long-running storage
  story

## WS1 Outcome

WS1 is now defined as a strict boundary-setting exercise. The richer demo must
make the installed dependency surface truthful, but only by deepening the
existing `activity-report` example.

### Keep/Change Boundary

| Surface | Decision | Boundary |
| --- | --- | --- |
| Oak package identity | Keep | Preserve the `oaknational-python-repo-template` distribution name, the `oaknational.python_repo_template` import path, and the `src/oaknational/` namespace layout. |
| Command surface | Keep | `uv run ...` remains the canonical human and hook entry surface. No parallel task runner, shell alias contract, or compatibility wrapper gets introduced. |
| Governance and quality gates | Keep | Practice doctrine, `repo-audit`, blocking gates, and existing hook discipline remain authoritative and may only be strengthened, not bypassed. |
| Demo identity | Keep with bounded extension | `activity-report` stays a small two-step CLI (`prepare`, `report`) that demonstrates infrastructure. It must not become the repo identity. |
| Data boundary | Keep | The canonical activity-log tabular contract remains `date`, `category`, `minutes`, and `notes`, validated explicitly at the boundary before downstream use. |
| Demo realism | Change | Move from a local-only summary example to a bounded "activity pack" that pairs activity data with small metadata/profile support and truthful charting. |
| Charting | Change | Replace bespoke PNG byte-writing with `matplotlib`, while preserving deterministic file output and injectable seams. |
| Dependency truthfulness | Change | Every direct runtime dependency must have a concrete role in shipped package code and in the documented demo story, not only in tests or notes. |
| Tooling enforcement | Keep in scope, not in demo scope | Commitizen, installed-wheel verification, gate-command centralisation, and dependency hygiene still land in this plan, but they must not force broader demo product scope. |
| Explicit exclusions | Keep out | No auth, pagination, retry framework, API client layer, daemon, database, multi-dataset orchestration, or general-purpose config engine. |

### Bounded Richer Demo Contract

The richer demo remains one small workflow built around a single "activity
pack":

- one activity log in CSV or Parquet form
- one same-stem metadata/profile sidecar in YAML, for example
  `activity_log.metadata.yaml`
- one optional chart artefact written by the report command

The contract for that activity pack is intentionally narrow:

- `prepare` still canonicalises one activity log into one validated Parquet
  artefact; it does not become a pipeline framework.
- `report` still reads one activity log and prints one textual summary, with an
  optional chart output.
- YAML is limited to descriptive metadata and small report-profile fields such
  as display name, source note, category labels, or simple per-category target
  minutes. It is not a free-form settings tree.
- HTTP support is limited to anonymous HTTPS retrieval of the activity file
  and/or its same-stem YAML sidecar. It exists so the template can truthfully
  demonstrate a remote boundary, not so it can model a service integration.
- Numerical work is limited to summary metrics that improve the report and
  chart, such as category share, daily totals, and target deltas. No
  forecasting, optimisation, or model-like behaviour belongs here.
- Persistence remains a single prepared Parquet snapshot via `pyarrow`; there
  is no partitioning, dataset registry, or warehouse shape.

### Direct Runtime Dependency Roles

| Dependency | Truthful demo role | Guardrail |
| --- | --- | --- |
| `pandas` | Load, validate, sort, group, and shape the canonical activity-log data. | Remains the primary tabular boundary library; keep the four-column contract explicit. |
| `numpy` | Compute small numerical metrics for the report and chart, such as shares, daily-distribution values, and target deltas. | Use for bounded analytics only; do not introduce modelling or algorithmic complexity. |
| `pyarrow` | Persist and reload the prepared Parquet snapshot produced by `prepare`. | Keep the storage story to one file-oriented cache artefact. |
| `pyyaml` | Read and, where useful, write the bounded metadata/profile sidecar that travels with the activity pack. | Restrict the schema to descriptive metadata and small reporting hints. |
| `requests` | Fetch a remote activity pack over HTTPS when the input or sidecar is supplied as a URL. | Keep it to anonymous GET on small assets with injectable seams and deterministic tests. |
| `matplotlib` | Render the report chart from the validated summary data. | Produce deterministic file output only; no interactive or dashboard surface. |

## Build-vs-Buy Attestation

- **What was searched**: current repo tooling, the direct dependency set, the
  current chart implementation, architecture-review findings, and Python-native
  tooling for commit-message enforcement and dependency hygiene
- **What was found**: before WS2, `matplotlib` was available but unused for
  chart rendering and the demo did not yet justify all installed runtime deps;
  `commitizen` and `gitlint` are viable for conventional-commit enforcement;
  `deptry` is a plausible Python-native dependency-hygiene gate
- **Why this shape was chosen**: broaden the demo so the installed dependency
  surface becomes truthful, adopt `commitizen` because it fits the repo's
  conventional-commit workflow and integrates cleanly with `pre-commit`, and
  add a dedicated dependency-hygiene tool rather than relying on manual review

## Reviewer Scheduling

- **Plan-time**: `architecture-reviewer` and `config-reviewer` to challenge the
  richer demo shape, gate centralisation, and hook/tool fit
- **Mid-cycle**: `test-reviewer` for proof shape and `config-reviewer` for
  commit-msg, dependency-hygiene, and gate-registry enforcement
- **Close**: `code-reviewer` for whole-change coherence

## Means

## WS1 — Keep/Change Boundary and Richer Demo Contract

- capture the keep/change matrix and bounded activity-pack contract in this
  plan
- preserve as fixed constraints:
  - `oaknational.*` packaging
  - `uv run ...` as the canonical command surface
  - repo audit, strict gates, and Practice governance
- treat sidecar YAML metadata/profile support and optional HTTPS inputs as the
  only new demo surfaces needed to justify the declared runtime dependency set
- use the dependency-role map above as the anti-sprawl checklist for WS2-WS6

**Acceptance criteria**

- the keep/change matrix names what must not move and what may change
- the richer demo contract defines artefacts, supported paths, exclusions, and
  dependency roles concretely enough to guide implementation
- every direct runtime dependency now has a documented truthful role in shipped
  package code, not only in tests or notes
- the expanded demo still reads as template infrastructure, not product logic

## WS2 — Truthful Demo Expansion and Matplotlib Charting

- replace the manual PNG writer in the demo CLI with a small `matplotlib`
  implementation
- expand the demo input and reporting flow so it truthfully exercises all
  declared runtime dependencies
- keep the current CLI contract and deterministic chart-writing seam
- add any needed YAML, HTTP, or metadata artefacts without turning them into an
  open-ended domain product
- update tests so they prove user-visible behaviour rather than internal chart
  mechanics

**Acceptance criteria**

- `activity-report report --chart ...` still produces a valid chart artefact
- bespoke PNG byte-generation code is removed
- the demo remains bounded and readable
- the repo can point to a truthful use for every declared runtime dependency

## WS3 — Packaged Typing and Strict Type Discipline

- add `py.typed` to the package and ensure it ships in built artefacts
- make the strict type-checking posture explicit in project configuration rather
  than leaving it implicit
- extend typing coverage across repo-owned Python code under `src/`, `tests/`,
  and `tools/` where the canonical gate surface expects it

**Acceptance criteria**

- built artefacts include `py.typed`
- type-checking rules are explicit and strict
- repo-owned Python code passes the stricter type contract

## WS4 — Commitizen Adoption and Use

- add `commitizen` to the dev tooling set and configure it for Conventional
  Commits
- add a `commit-msg` hook alongside the existing `pre-commit` and `pre-push`
  gates
- document the canonical usage path, expected to be `uv run cz commit` and
  `uv run cz check`
- keep hook enforcement truthful and avoid aliases or compatibility wrappers

**Acceptance criteria**

- invalid commit messages are rejected by the hook
- valid conventional commits pass locally
- the repo docs tell contributors how to create and validate compliant commits

## WS5 — Installed-Wheel Verification and Gate-Command Centralisation

- centralise the canonical gate-command registry so scripts, dispatch, and
  audit share one Python-side source of truth
- add an installed-wheel smoke check to the canonical build and check path
- prove the built wheel installs and runs its package/module/CLI entry surfaces
  correctly in isolation from the source tree

**Acceptance criteria**

- gate-command truth is not duplicated across unrelated files
- `check-ci` proves both build success and installed-wheel viability
- wheel smoke checks cover at least one CLI and one module entry surface

## WS6 — Dependency Hygiene Enforcement

- add a Python-native dependency-hygiene tool, expected to be `deptry`, through
  the canonical `uv run ...` surface
- configure it so the richer demo and declared dependency contract stay aligned
- wire the dependency-hygiene gate into the canonical aggregate checks

**Acceptance criteria**

- dependency hygiene is enforced automatically
- the configured dependency tool passes on the final declared dependency set

## Quality Gates

```bash
uv run format
uv run lint
uv run typecheck
uv run test
uv run coverage
uv run repo-audit
uv run check
uv run check-ci
```

## Risk Assessment

| Risk | Mitigation |
| --- | --- |
| the richer demo becomes product-like rather than template-like | keep the scenario bounded, map each dependency to a minimal truthful role, and reject domain sprawl during review |
| `matplotlib`, YAML, or HTTP paths make the demo less deterministic | retain injectable seams, use deterministic fixtures, and keep network behaviour explicitly bounded in tests |
| stricter typing introduces broad churn late in the cycle | make the strictness contract explicit early and tighten types as part of the same landing |
| commit-msg enforcement fights the existing hook model | wire it through the existing `pre-commit` framework instead of inventing a parallel path |
| gate centralisation adds opaque indirection | keep the registry small, local, and Python-readable rather than building a framework |
| dependency-hygiene enforcement reports noise before the demo is truthful | land the richer demo and dependency mapping before making the hygiene gate blocking |
| "more Pythonic" becomes an excuse to erode Oak doctrine | lock the keep/change matrix first and treat Oak constraints as non-negotiable inputs |

## Foundation Alignment

- `principles.md`: prefer simplification, one source of truth, and in-place
  replacement over layered compatibility
- `testing-strategy.md`: prove behaviour with the smallest truthful validation
  layer and keep repo-state checks in dedicated tooling
- `orientation.md`: route scope into the runtime plan lane while treating
  Practice and hooks as cross-strand touchpoints
- `PDR-006-dev-tooling-per-ecosystem.md`: prefer truthful Python-native tooling
- `PDR-008-pythonic-canonical-quality-gate-naming.md`: preserve the canonical
  Python gate surface
- `PDR-022-governance-enforcement-scanners.md`: prefer enforced truth surfaces
  over advisory-only guidance

## Documentation Propagation

- `README.md`: document the richer demo, preferred commit flow, truthful
  plotting surface, and packaging/type guarantees
- `docs/dev-tooling.md`: add `commitizen`, dependency hygiene, explicit typing,
  and installed-wheel verification
- `.agent/practice-index.md`: no expected change unless the new tooling changes
  the entrypoint map
- `.agent/practice-core/practice.md`: no expected change unless the stricter
  Pythonic boundary itself becomes durable doctrine

## Done When

1. every direct runtime dependency is used truthfully by the bounded demo
2. the repo uses `matplotlib` for its chart path
3. `py.typed` ships and strict type-checking is explicit and passing
4. `commitizen` is installed, configured, and enforced through `commit-msg`
5. installed-wheel verification is part of the canonical check path
6. gate-command truth is centralised and dependency hygiene is enforced
7. the Oak constraints named in this plan remain intact
8. the named gates pass
9. reviewer findings are resolved or explicitly routed

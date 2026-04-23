# Napkin

## Session: 2026-04-23 — WS6 Dependency Hygiene and Final Closeout

### What Was Done

- Added `deptry` to the dev dependency group and configured it minimally in
  `pyproject.toml` with `known_first_party = ["oaknational"]`.
- Recorded one deliberate `deptry` `DEP002` exception for `pyarrow`, because
  the seeded demo uses it indirectly through pandas' Parquet path rather than a
  direct import.
- Wired dependency hygiene into both `uv run check` and `uv run check-ci`
  before `repo-audit`, without adding a new public gate command or changing the
  installed-wheel smoke path.
- Added targeted tests for the aggregate gate sequence and repo-audit
  dependency-hygiene contract, then refreshed README, `docs/dev-tooling.md`,
  `.agent/commands/gates.md`, and the start-right gate sequence doc together.
- Verified the closeout with passing `uv run deptry .`,
  `uv run pytest tests/test_devtools.py tests/test_repo_audit.py`, and
  `uv run check`.
- The first final reviewer rerun then surfaced the remaining blocker-only gaps:
  shell-wrapper and alias/config hook bypasses, UNC path handling, the shipped
  gate contract carrying repo-audit policy, missing direct proof for malformed
  hook-config shapes and build smoke, and stale continuity state.
- Closed those blockers by splitting repo-audit command metadata into
  `tools/repo_audit_contract.toml`, hardening the hook parser against wrapped
  shells, exported env carry-over, alias indirection, dynamic git config, and
  exact hooksPath overrides, rejecting UNC activity sources, and adding direct
  regression tests for the temp build probe, installed-wheel smoke steps, and
  hook-config fail-closed behaviour.
- The final reviewer passes then exposed two last truth gaps: `/usr/bin/env`
  shell wrappers still bypassed hook inspection, and repo audit did not yet
  prove that documented repo-local commands still existed in
  `gate_contract.toml`.
- Closed those final gaps by treating basename-equivalent `env` launchers as
  real env wrappers, adding direct regressions for `/usr/bin/env bash -lc ...`
  and `/usr/bin/env /bin/bash -lc ...` forms, and making repo audit reject
  documented repo-local commands that are not defined in the runtime gate
  contract.
- Revalidated the final repaired diff with passing `uv run pytest`,
  `uv run python -m oaknational.python_repo_template.devtools check`, and
  `uv run python -m oaknational.python_repo_template.devtools check-ci`; the
  closing code, architecture, test, security, and config reviewer reruns all
  returned clean blocker-only passes.

### Patterns to Remember

- For Oak namespace repos, `deptry` can usually stay small and readable with
  `known_first_party = ["oaknational"]`.
- If a runtime dependency is only visible through an indirect backend selected
  by another library, document the exception explicitly instead of forcing a
  synthetic import into product code.
- Keep dependency-hygiene enforcement inside the existing aggregate gates when
  the public command surface is already coherent.

## Session: 2026-04-23 — Pythonic Alignment Planning

### What Was Done

- Wrote a bounded runtime plan for making the repo more Pythonic without
  colliding with Oak requirements.
- Expanded that plan after architecture review and owner direction so the demo
  now needs to justify the full runtime dependency set rather than trimming it.
- Added installed-wheel verification, `py.typed`, explicit strict typing,
  gate-command centralisation, and dependency hygiene to the implementation
  scope.
- Chose `matplotlib` adoption and `commitizen` enforcement as central pieces of
  the Pythonic pass rather than standalone clean-ups.
- Kept the plan anchored to non-negotiable local constraints: `oaknational.*`
  packaging, `uv run ...`, strict gates, and Practice-first repo governance.
- Converted WS1 from a broad intention into a concrete contract: one bounded
  "activity pack" made of activity data, a same-stem YAML sidecar, an optional
  chart artefact, and optional HTTPS retrieval with explicit no-sprawl
  guardrails.
- Landed WS2 against that contract: the demo now loads local or HTTPS activity
  inputs, auto-discovers or overrides same-stem YAML sidecars, renders
  metadata-aware summaries with target deltas, and uses `matplotlib` rather
  than bespoke PNG bytes for chart output.
- Updated the shipped fixture and README so the richer activity-pack contract
  is visible in the seeded repo state, not just in tests and plan prose.
- Landed WS3: the package now ships `py.typed`, `pyproject.toml` states the
  strict `pyright` scope explicitly for `src/`, `tests/`, and `tools/`, and
  repo audit now guards that typing contract.
- Tightened the remaining strict-pyright fallout in repo-owned tooling without
  widening the demo's `Any` boundaries, and verified that the remote/YAML/chart
  paths stayed green under the stricter contract.
- Verified both built artefact shapes directly: the source distribution and the
  wheel now both contain `py.typed`, with the wheel fixed via an explicit Hatch
  `force-include` mapping.
- Finished the WS2 landing with a passing `uv run check`, including strict
  pyright, import-linter, build, tests, and coverage.
- Closed the session with a new `pythonic-alignment` operational thread so the
  next implementation pass does not blur into the already-landed
  `practice-foundation-upgrade` baseline.

### Patterns to Remember

- In this template, "more Pythonic" is only a valid direction when it removes
  bespoke local shape or makes the declared surface more truthful without
  weakening Oak truth surfaces.
- If the owner wants a richer template rather than a leaner one, dependency
  truthfulness should come from a more realistic bounded demo, not automatic
  package trimming.
- When a change touches both runtime idiom and workflow enforcement, one bounded
  plan with explicit cross-strand touchpoints is cleaner than parallel partial
  plans.
- When broadening a seeded demo to justify dependencies, prefer enriching
  already-canonical artefacts such as sidecar metadata, prepared caches, and
  report outputs rather than inventing a second config or service layer.
- `requests` stays truthful in a template only when the HTTP role remains
  equivalent to bounded asset retrieval, not a proto-integration framework.
- If a third-party plotting API is dynamically typed, keep the `Any` boundary
  narrow and local to the adapter rather than letting unknowns leak through the
  rest of the demo code.
- When Hatch wheel packaging is driven by `packages = [...]`, verify `py.typed`
  in the built wheel directly; the marker may need an explicit wheel
  `force-include` mapping even when it is present in the source tree and sdist.
- When a richer seeded fixture changes the observable default output, update the
  package-entry smoke tests in the same landing so the repo-level contract
  stays aligned with the shipped example.

## Session: 2026-04-23 — WS4 Commitizen and Packaging Truth

### What Was Done

- Added `commitizen` to the dev dependency group and configured it in
  `pyproject.toml` for Conventional Commits with the `uv` version provider.
- Extended `.pre-commit-config.yaml` so `pre-commit install` now installs
  `pre-commit`, `pre-push`, and `commit-msg`, with `commit-msg` validating the
  real message file through `uv run cz check --allow-abort --commit-msg-file`.
- Updated README, `docs/dev-tooling.md`, and the canonical commit workflow docs
  so the truthful usage path is `uv run cz commit` and `uv run cz check`.
- Added repo-audit coverage for the Commitizen workflow contract so the dev
  dependency, hook installation shape, and docs do not silently drift.
- While verifying WS4, caught a wheel-packaging regression: Hatch's
  `packages = [...]` configuration was collapsing the shipped path to
  `python_repo_template/*`, which broke installed `uv run check` entrypoints.
- Fixed that regression by switching the wheel target to namespace-preserving
  `only-include` plus `sources`, added repo-audit coverage for that packaging
  contract, and finished with a passing `uv run check`.

### Patterns to Remember

- Hatch's `packages = [...]` option collapses the shipped path to the final
  component; for namespaced packages, prefer `only-include` plus `sources`
  when you need to preserve the namespace directory in the built wheel.
- If a hook is meant to validate the real commit message, wire it through
  `commit-msg` with the actual message-file path, and make `pre-commit install`
  truthful with `default_install_hook_types` so the hook is installed by
  default.
- When a tooling change touches both docs and enforcement, add a small audit
  contract in the same landing or the docs will drift back to aspiration.

## Session: 2026-04-23 — WS5 Wheel Smoke and Gate Registry

### What Was Done

- Added `src/oaknational/python_repo_template/gate_registry.py` as the shared
  Python-side registry for canonical gate-command names and devtools handler
  targets.
- Updated `devtools.py` so `uv run build` smoke-tests the newest built wheel,
  while the build step inside both `uv run check-ci` and `uv run check` now
  builds into a temporary artefact directory and proves the installed wheel in
  isolation from the source tree.
- Built the repaired `oaknational.python_repo_template` wheel, installed it in
  a temporary virtual environment outside the repo, copied the seeded activity
  pack into a temporary workspace, and proved the installed package import plus
  both `activity-report` and
  `python -m oaknational.python_repo_template`.
- Tightened the internal command runner so absolute paths to other virtualenv
  scripts keep their own interpreter rather than being rewritten onto the
  current environment's `sys.executable`.
- Updated repo audit, tests, README, `docs/dev-tooling.md`, and the canonical
  gates command doc so the new build truth is enforced and documented together.
- Verified the landing with passing `uv run build`, `uv run check-ci`, and
  `uv run check`.

### Patterns to Remember

- Share canonical gate-command names from a small registry module rather than
  duplicating them across dispatch and audit code.
- When proving an installed wheel outside the source tree, copy the seeded
  fixture into a temporary workspace and run both the console-script and
  `python -m` entry surfaces there.
- A helper that rewrites Python-script shebangs to `sys.executable` must only
  do so for commands resolved from the current environment; absolute paths to
  other virtualenv scripts must keep their own interpreter.

### Closeout Note

- Lightweight handoff recorded: the next session should land WS6 dependency
  hygiene first and then run the review round in that same session; the active
  plan's already-run gates item was synced to completed so the remaining work
  is represented truthfully.
- Follow-up owner direction: the next session is intended to be the final
  session for `pythonic-alignment`, so WS6 and the review pass should be
  treated as one closing tranche.

## Session: 2026-04-23 — Oak Namespace Packaging

### What Was Done

- Moved the template package into the Oak namespace layout at
  `src/oaknational/python_repo_template/`.
- Renamed the distribution surface to `oaknational-python-repo-template` and
  rewired imports, scripts, coverage, import-linter, repo audit, tests, and
  docs to the `oaknational.python_repo_template` import path.
- Updated the repo-facing narrative so this template now teaches the Oak
  Python convention directly: dash-separated distribution names, dotted
  namespace imports, and namespace-package layout under `src/oaknational/`.

### Patterns to Remember

- The closest Python analogue to npm scoping is a split identity:
  distribution name on the installer surface, namespace import path in code.
- For a family of Oak packages, prefer a namespace package under
  `src/oaknational/` rather than a flat top-level package per distribution.

## Session: 2026-04-23 — Deep Closeout and Homing

### What Was Done

- Ran the deep `session-handoff` and `consolidate-docs` sweep after the main
  landing rather than treating the green gates as the end of the work.
- Refreshed continuity, thread state, distilled memory, and the plan
  documentation-sync logs so the final steady state is captured outside chat.
- Added a plain-language root README note explaining that the repo is
  optimised for safe agentic engineering while remaining usable for
  conventional development.
- Broadened testing doctrine to use standard validation terminology and to
  name the automatic validation expected in data engineering and data science
  work.

### Patterns to Remember

- A clean landing is not the same thing as a finished closeout; continuity,
  experience, and sync logs still need an explicit pass.
- If strict workflow rules are load-bearing for safety, say so plainly in the
  user-facing repo narrative instead of leaving collaborators to infer it.
- Testing doctrine for a template repo should name both the standard software
  validation layers and the data-quality checks expected when the template is
  used for data work.

## Session: 2026-04-23 — Approved Source-Practice Transfer Completion

### What Was Done

- Landed the remaining approved source-Practice tranches in one session:
  `orientation`, `experience`, document tiers, homing workflow, full planning
  architecture, reviewer-architecture guidance, generic governance rules, and
  the selected `commit` / `tsdoc` skills.
- Added the planning collections, templates, roadmaps, sync logs, and
  high-level/completed-plan indices so planning is now a first-class repo
  lifecycle surface rather than a thin local stub.
- Backfilled the approved missing PDR bundle and generalised it for this
  Python template by removing source-local residue and keeping the doctrine
  truthful under the repo's identity.
- Extended the repo audit to require the new planning, knowledge-tier, and
  skill surfaces, then finished with passing `uv run check-ci` and
  `uv run check`.

### Patterns to Remember

- A full Practice transfer into a template repo is mostly a generalisation
  exercise, not a wholesale copy exercise: source-local context must be
  stripped or the imported doctrine will immediately fail local truthfulness
  checks.
- Planning architecture should be treated as foundational infrastructure in a
  template repo: collections, templates, sync logs, and high-level indices all
  need to land together or the planning estate will remain performative.

## Session: 2026-04-23 — Practice Foundation Upgrade

### What Was Done

- Adopted the full three-plane memory estate as the repo's live memory model.
- Added portable Practice Core verification, governance, and pattern surfaces:
  `practice-verification.md`, `decision-records/`, and `patterns/`.
- Added the session-close workflow and supporting rule layer for thread
  identity continuity, executive-memory drift capture, documentation hygiene,
  and foundational Practice protection.
- Updated the bridge docs, repo audit, and adapter parity surfaces to the new
  structure.
- Standardised the Python quality-gate API around `format`, `format-fix`,
  `lint`, `lint-fix`, `fix`, `check`, and `check-ci`, with no legacy aliases
  or compatibility layers.
- Extended the same canonical command surface across `clean`, `build`, and
  `dev`, and wired a build probe into both aggregate checks.
- Integrated the incoming Practice package conceptually, cleared the incoming
  box, and finished with a passing `uv run check`.
- Caught and fixed a `clean` overscope bug before closeout so virtualenv
  `__pycache__` directories are preserved while repo-owned caches are removed.

### Patterns to Remember

- Integrate portable Practice innovations by synthesis, not by copying the
  source package verbatim.
- If the canonical rule set grows, add the adapter wrappers and audit coverage
  in the same landing or the Practice will drift immediately.
- Clear the incoming Practice box only after the localised integration is
  landed and verified.
- Python packaging does not map naturally to colon-named console scripts, so
  command-surface standardisation should prefer truthful Python-native
  dispatchers over pretending shell aliases are package contracts.
- If a canonical gate surface flips semantics, every caller that relied on the
  old meaning must be updated in the same landing: hooks, review flows,
  pre-commit, docs, and audits.
- Behavioural tests should exercise command contracts such as `clean()` rather
  than private helpers; that keeps pyright happy and better matches the
  testing doctrine.

## Session: 2026-04-23 — Source Practice Gap Scan

### What Was Observed

- The remaining useful source-repo Practice material is mostly governance and
  documentation-structure infrastructure, not more core memory-estate
  mechanics.
- The strongest portable gaps are a first-class `experience/` lane, an
  explicit layer-and-authority `orientation.md` directive, and the larger
  supporting document-tier model (`analysis/`, `reports/`, curated
  `reference/`).
- Several portable PDRs remain uncurated locally, especially around review
  findings routing, grounding before framing, consolidation routing, reviewer
  dispatch, check-driven development, governance scanners, and the
  perturbation/tripwire bundle.
- Most of the source repo's bulk remains source-specific and should not travel:
  domain research, specialist reviewers tied to Oak's stack, milestones,
  proposals, prompts, and product analyses.

### Patterns to Remember

- After the core Practice lands, the next scale bottleneck is usually not more
  memory surfaces but stronger routing between doctrine, reference, research,
  evidence, and reflection tiers.
- Curating additional PDRs is higher leverage than copying large source-repo
  directories wholesale; the doctrine should travel before the corpus does.

## Session: 2026-04-21 — Template Extraction

### What Was Done

- Seeded the template repo from reusable infrastructure only.
- Replaced the old application lane with the `activity-report` CLI.
- Moved the package to the canonical
  `src/oaknational/python_repo_template/` layout rather than keeping an unusual
  top-level `python/` package.
- Added the repo root to pytest `pythonpath` so root-level support modules such
  as `tools.agent_hooks` import the same way under `uv run pytest` as they do
  under direct local execution.

### Patterns to Remember

- Canonical Python packaging should win over preserving source-repo layout when
  the template's job is to model best practice.

## Session: 2026-04-22 — Sibling Verification and Native Hand-off

### What Was Done

- Switched to `/Users/jim/code/personal/python-repo-template` and verified the
  sibling repo directly rather than trusting the staging copy
- Ran `uv sync` in the sibling repo and confirmed `uv run check` passes there
- Ran the seeded CLI as a smoke test against `data/fixtures/activity_log.csv`
- Preserved the remaining follow-up work in the native hand-off plan for the
  next native session
- Confirmed two interrupted polish edits did land:
  `src/oaknational/python_repo_template/__main__.py` and `tools/__init__.py`
- Confirmed one interrupted edit did not land:
  `tests/test_package_entrypoint.py`

### Patterns to Remember

- Verify the sibling repo itself before declaring an extraction complete; local
  runtime artefacts can surface bugs that the staging copy never hit
- After an interrupted edit, inspect the filesystem before assuming which files
  landed and which did not
- A small hand-off plan in `active/` is the right place to preserve verified
  repo state before switching to a fresh native session

## Session: 2026-04-22 — Canonical Package Entry Polish

### What Was Done

- Re-verified the repo before further changes with `uv run check` and the
  `activity-report` CSV smoke command
- Added `tests/test_package_entrypoint.py` to prove the package module entry
  surface reports the expected fixture summary
- Tightened `tools/repo_audit.py` required canon to include
  `src/oaknational/python_repo_template/__main__.py`, `tools/__init__.py`, and
  `tests/test_package_entrypoint.py`
- Updated `README.md` to document the verified module-form invocation
  `uv run python -m oaknational.python_repo_template report --input data/fixtures/activity_log.csv`
- Verified the module-form invocation locally and finished with a passing
  `uv run check`

### Patterns to Remember

- When the repo is managed through `uv`, document the module-form invocation as
  `uv run python -m ...` unless the shell-level `python` command is itself a
  supported repo contract
- Keep file-presence canon load-bearing inside `tools/repo_audit.py` itself;
  do not mirror it in `pytest` tests that constrain repo configuration

## Session: 2026-04-23 — Final Reviewer Closeout Planning

### What Was Done

- Re-grounded on the planning doctrine, metacognition directive, runtime plan
  architecture, and the closed `pythonic-alignment` continuity state.
- Wrote a new queued runtime-infrastructure plan,
  `review-findings-final-closeout.md`, to address the remaining whole-repo
  reviewer findings in one final session.
- Reopened branch-primary continuity around a new
  `review-findings-closeout` thread instead of pretending the repo was fully
  done after the first green closeout.

### Patterns to Remember

- When a reviewer pass finds a bounded but real follow-up tranche, write a new
  plan and continuity thread rather than stretching a completed plan past its
  truthful end state.
- For a final-session plan, make the command-surface decision explicit early if
  the repo-local workflow and the distributable package surface might need to
  diverge.

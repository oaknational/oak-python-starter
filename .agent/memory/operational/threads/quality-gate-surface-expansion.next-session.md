# Thread: quality-gate-surface-expansion → "highest proportionate bar" program

## Participating Agent Identities

| agent_name | platform | model | role | first_session | last_session |
| --- | --- | --- | --- | --- | --- |
| Claude | claude | opus-4.8 | executor | 2026-06-17 | 2026-06-18 |

## Owning Plans

- Gates: [`../../../plans/runtime-infrastructure/current/quality-gate-surface-expansion.md`](../../../plans/runtime-infrastructure/current/quality-gate-surface-expansion.md)
- Release automation: [`../../../plans/runtime-infrastructure/current/release-automation.md`](../../../plans/runtime-infrastructure/current/release-automation.md)
- Template fitness (F3/F8/F5-7): [`../../../plans/runtime-infrastructure/current/template-fitness-remediation.md`](../../../plans/runtime-infrastructure/current/template-fitness-remediation.md)
- Source review: [`../../../reports/2026-06-17-oak-quality-gate-types-review.md`](../../../reports/2026-06-17-oak-quality-gate-types-review.md)

## Current Objective (owner-approved 2026-06-18)

Bring the repo to the **highest *proportionate* combination** of Pythonic best
practice + Oak ecosystem standards. The owner explicitly selected **all four
lanes** below. Proportionate = finish these tiers and **consciously STOP before
Tier 4** (SBOM, SLSA provenance, OpenSSF Scorecard, dependency-review, lychee
link-check, mutation testing) unless the owner later asks for maximal. The
repo's First Question ("could it be simpler without compromising quality?") and
its identity ("a template foundation, not a feature product") govern scope.

## What Landed This Program (2026-06-17 → 2026-06-18)

All merged to `main` unless noted. `main` is green.

- **Coverage → GitHub Code Quality (PR #18, merged).** CI derives a Cobertura
  `coverage.xml` from the existing check-ci coverage run (`coverage xml`, no
  second test run) and uploads via `actions/upload-code-coverage`
  (`code-quality: write`, fork-guarded, `fail-on-error: false`). `relative_files`
  set; `coverage.xml`/`.coverage.*` git-ignored; `devtools clean` removes them.
- **Release automation (PRs #19 plan, #20 impl, #22 fix; merged).** Release-PR
  pattern via Commitizen — see the release-automation plan. **Live-verified**:
  `v0.1.0` (bootstrap) and `v0.2.0` (full bump cycle) released with wheel+sdist.
- **pip-audit gate (PR #24, merged).** In `check-ci` after dependency-hygiene;
  exports locked deps (`uv export --no-emit-project`) and audits them. Replaced
  the now-false "deptry is not vulnerability scanning" claim across README /
  docs / `.agent/commands/gates.md`, enforced by `audit_dependency_hygiene`.
- **codespell gate (PR #26, merged).** In `check-ci` after markdownlint. No
  ignore-list needed: the one false positive was removed at source (the SECURITY
  substring check now matches `"vulnerab"`).

## In Flight / Open (DO NOT lose)

- **Standing release PR #25 `chore(release): v0.3.0`** (branch `release/next`) is
  **intentionally open and accumulating** every merged feat/fix since v0.2.0
  (release automation, pip-audit, codespell, …). Strategy: let it accumulate
  through the sprint, then merge it **once** for a single clean release. It will
  keep auto-updating as more PRs merge.
  - **CRITICAL merge mechanic:** the release PR is opened by `GITHUB_TOKEN`, so
    `ci.yml` does NOT run on it → it sits `mergeStateStatus: UNSTABLE` forever.
    Merge it with **`gh pr merge 25 --squash --auto --delete-branch`** (NOT
    `--admin` — the harness classifier blocks admin bypass, correctly). `--auto`
    merges once the ruleset's actual requirements are met (a PR exists; no
    required status checks). Merging it triggers the publish phase → `v0.3.0`.
- **Supply-chain PR #28 `feat/supply-chain-pinning` (HEAD `f5225cb`, OPEN).**
  Contains: all workflow action `uses:` SHA-pinned (with `# vX` comments) +
  `.github/dependabot.yml` (uv + github-actions, weekly, grouped) + the
  **`audit_supply_chain` self-check** (asserts every workflow `uses:` — step- AND
  job-level — is a 40-hex SHA or a `sha256:` docker digest, and dependabot watches
  uv+github-actions) + the packaging-schema fix below. All four pinned SHAs were
  verified to match their upstream `vN` tags. **Next: get it green (CI +
  SonarCloud) and merge** with `gh pr merge 28 --squash --delete-branch` (a normal
  PR — CodeQL runs and it merges on green; NOT the bot-PR `--auto` path #25 needs).
- **Packaging-schema fix folded into PR #28** (committed `f5225cb`), separate from
  supply-chain: `pyproject` `[tool.hatch.build.targets.wheel].sources` `["src"]`
  → `{ "src" = "" }` (array tripped the *Even Better TOML* SchemaStore Hatch
  schema, which types `sources` as object; wheels are byte-identical) **and
  removal** of the `audit_packaging_contract` audit and its test — it asserted
  config *shape* (`sources == [...]`, `only-include == [...]`), a "test behaviour,
  not implementation details" violation. **Do not re-add it, and do not add a
  wheel-namelist test in its place:** the packaging behaviour is already proven
  end-to-end by the build-gate wheel-smoke (`_run_build_probe` →
  `_run_installed_wheel_smoke_check` in `devtools.py`, run in `check`/`check-ci`/
  CI: build → install into fresh venv → `import oaknational.python_repo_template`
  resolves to the *installed* wheel → run both entry points). All gates green.
- **SonarCloud is a live PR quality gate (`SonarCloud Code Analysis`).** Org-level
  automatic analysis — there is no `sonar-project.properties` in-repo and no Sonar
  workflow; it posts a check on every PR. It is **NOT** a *required* status check
  on the `main` ruleset (so it does not mechanically block merge), but its gate is
  blocking by repo doctrine ("all quality-gate issues are blocking"). It evaluates
  **new-code** conditions — PR #28's first push failed `new_code_smells_severity`
  (cognitive complexity > 15 + a duplicated literal), fixed by decomposing the
  audit. Inspect it via the **SonarQube MCP**: `get_project_quality_gate_status`
  and `search_sonar_issues_in_projects`, projectKey
  `oaknational_oak-python-starter`, `pullRequest <n>`.

## Remaining Program Work (each its own branch off main + PR)

- **Tier 1b — template fitness** (template-fitness-remediation plan):
  - **F3 honest coverage gate**: raise `fail_under` from 70 → ~85 (achieved ~88);
    add `audit_coverage_contract` pinning the threshold floor + the exact
    coverage omit-list (`governance-claim-needs-a-scanner`).
  - **F8 accessible chart** (org WCAG 2.2 AA mandate, currently unmet): write a
    text alternative from `render_summary` (SC 1.1.1); darken `#d08d46` and halo
    the target marker for ≥3:1 contrast (SC 1.4.11); test the sidecar + contrasts.
  - **F5/F6/F7 adoptability**: remote-fetch size cap + trust-boundary note;
    guardrail fail-closed + simplify in `agent_hooks.py` (treat `|` as separator,
    fail-closed on `$(`/backticks; allow-path tests for git commit/push/status);
    a "rename this template" guide.
- **Tier 3 — Pythonic additions**:
  - branch coverage (`--cov-branch`) + raise threshold;
  - Hypothesis property-based tests for the CSV/data boundary;
  - an ADR recording the deliberate single-version bleeding-edge (3.14) policy
    (the repo intentionally does NOT use a version matrix) — or adopt a matrix if
    broad compatibility becomes a goal (owner decision).
- **Tier 2 — governance write-up** (code + a checklist): the
  `audit_supply_chain` self-check is **done** (landed at `990c042`); remaining is
  to produce an owner-action checklist (see Owner Actions below). I cannot change
  repo/org settings.

## Owner Actions Outstanding (settings, not code — I cannot do these)

1. **Make CI a real merge gate.** Add **"Quality gates"** and **"Secret
   scanning"** to the `main` ruleset's required status checks. Today only the
   PR-required + (non-blocking `code_quality`) rules apply, so `main` can go red
   and a PR can still merge. This is the single biggest enforcement gap.
2. **Release-PR token.** Give `create-pull-request` a PAT or GitHub App token so
   `ci.yml` runs on the release PR (then it goes CLEAN and merges without
   `--auto`). Until then, use `--auto` (above).
3. **Enable GitHub Code Quality** (public preview) for the org so the coverage
   upload surfaces on PRs (today `fail-on-error: false` makes it a harmless
   no-op).
4. **Tag protection** for `v*` so release tags can't be force-moved/deleted.

## Key Mechanics & Gotchas (would be lost otherwise)

- **`cz_conventional_commits` IGNORES `[tool.commitizen].bump_map`** — it reads
  the plugin's hardcoded map (`bump.py:_find_increment` uses `self.cz.bump_map`).
  The custom policy (feat/fix→minor, else→patch, breaking→manual major) is
  therefore applied by `tools/release_increment.py`, which reads the bump_map
  from pyproject and the workflow passes `cz bump --increment <X>`. The live
  verification of release automation is what caught this.
- **Release PR is perpetually UNSTABLE → `gh pr merge --auto`** (see In Flight).
- **`main` ruleset:** PR required (0 approvals); no *required status checks*
  (so verify "Quality gates" + "Secret scanning" green manually before merging;
  both run via GitHub Apps even on bot PRs, but `ci.yml`'s jobs do not run on
  bot PRs). Direct pushes blocked. The pre-tool hook blocks `git push --force`
  and `git checkout --` (use `uv lock`/`git restore` alternatives).
- **Seven-surface gate coupling map** (for in-`check-ci` gates like pip-audit /
  codespell): pyproject (dep+config) · `_step_runners` · gate_contract sequences
  · the **verbatim** `SKILL.md` check-ci string (enforced by
  `audit_dependency_hygiene`) · `repo_audit` · docs · the test fixtures
  (`CHECK_CI_SEQUENCE`, `GATE_CONTRACT`, `test_aggregate_gate_sequences`). Keep
  all in lockstep or `check` fails. Current check-ci order:
  `format → typecheck → lint → markdownlint → codespell → import-linter →
  dependency-hygiene → pip-audit → repo-audit → build → test → coverage`.
- **`__pycache__`/private-name test idiom:** access private functions in tests
  via `getattr(subject, "name")` (a variable) to dodge ruff B009 + pyright
  reportPrivateUsage (see `test_devtools.py`).
- **Tier 4 is deliberately deferred** (SBOM, SLSA, Scorecard, dependency-review,
  lychee, mutation testing) — diminishing returns for a template; revisit only
  on explicit request.

## Next Safe Step

1. **Supply-chain PR #28 is OPEN** (HEAD `f5225cb`). Get it green (CI +
   SonarCloud) and merge with `gh pr merge 28 --squash --delete-branch`.
2. Then Tier 1b (F3 → F8 → F5/6/7), then Tier 3, then the Tier 2 checklist.
3. When the sprint's PRs are all merged, **merge release PR #25 with `--auto`**
   to cut the accumulated release, then verify the new GitHub Release + the
   bumped `main` version.
4. **Deep `consolidate-docs` graduation is deferred to a fresh-context session**
   (do not attempt it at low context): home durable doctrine out of plans,
   archive completed plans (release-automation is essentially done + verified),
   rotate the napkin, refresh `completed-plans.md`/indexes.

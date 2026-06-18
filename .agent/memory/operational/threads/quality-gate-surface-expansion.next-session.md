# Thread: quality-gate-surface-expansion → "highest proportionate bar" program

## Participating Agent Identities

| agent_name | platform | model | role | first_session | last_session |
| --- | --- | --- | --- | --- | --- |
| Claude | claude | opus-4.8 | executor | 2026-06-17 | 2026-06-18 |

## Owning Plans

- Gates: [`../../../plans/runtime-infrastructure/current/quality-gate-surface-expansion.md`](../../../plans/runtime-infrastructure/current/quality-gate-surface-expansion.md)
- Release automation (ARCHIVED 2026-06-18): [`../../../plans/runtime-infrastructure/archive/release-automation.md`](../../../plans/runtime-infrastructure/archive/release-automation.md)
- Template fitness (F3/F8/F5/F7 done; F6 deferred): [`../../../plans/runtime-infrastructure/current/template-fitness-remediation.md`](../../../plans/runtime-infrastructure/current/template-fitness-remediation.md)
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
- **Supply-chain PR #28 — MERGED** (`feat/supply-chain-pinning`). Landed: all
  workflow action `uses:` SHA-pinned + `.github/dependabot.yml` (uv +
  github-actions) + the **`audit_supply_chain` self-check** (asserts every
  workflow `uses:` — step- AND job-level — is a 40-hex SHA or a `sha256:` docker
  digest, and dependabot watches both ecosystems) + the packaging-schema fix
  below. All four pinned SHAs verified to match their upstream `vN` tags.
- **Coverage PR #31 — MERGED** (Tier 1b F3). `fail_under` 70→85 + the
  `audit_coverage_contract` repo_audit check (floor + omit-list guard — guards
  what the coverage gate structurally cannot). Normal feature PRs merge with
  `gh pr merge <n> --squash --delete-branch` once green (CI + SonarCloud).
- **Accessible-chart PR #33 — MERGED** (Tier 1b F8, WCAG 2.2 AA).
- **Adoptability PR #34 — MERGED** (Tier 1b F5 remote size cap + F7 rename
  guide). **F6 (the agent_hooks guardrail) is DEFERRED** — see Remaining Work.
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
  - **F3 honest coverage gate — DONE (PR #31).** `fail_under` 70→85 +
    `audit_coverage_contract` (floor + omit-list guard). The audit asserts a
    *floor* (>=85, raising allowed) and that `omit` stays a subset of the
    justified set — guarding what the coverage gate structurally cannot.
  - **F8 accessible chart — DONE (PR #33).** Darkened the amber bar
    `#d08d46`→`#b07a37` (2.77→3.69:1), added a white halo to the target marker
    (it failed 3:1 on most bars), and a `<chart>.png.txt` alt-text sidecar from
    `render_chart_alt_text`. Tests pin the WCAG contrasts with an independent
    contrast helper. (Discovery: the dark target marker was an *existing* a11y
    bug — invisible on blue/teal/red/purple bars.)
  - **F5 remote size cap — DONE (PR #34).** `default_remote_reader` streams under
    a 10 MiB `REMOTE_MAX_BYTES` cap (declared-Content-Length early reject + decoded
    streaming cap), inside a `with` so the connection closes on every exit.
  - **F7 rename guide — DONE (PR #34).** `docs/using-this-template.md`, linked
    from the README.
  - **F6 guardrail hardening — DEFERRED (needs owner input + a dedicated
    session).** Goal: close two bypasses in the self-imposed safety rail
    (`tools/agent_hooks.py`): (a) `_shell_segments` (line ~484) does NOT split on
    `|`, so a piped stage isn't analysed as its own segment; (b) the anchored
    force-push/etc. regexes are defeated by `$(...)`/backticks — e.g.
    `echo $(git push --force)` slips through because the trailing `)` breaks the
    `(\s|$)` anchor. **Why deferred:** "fail-closed on `$(`/backticks" is
    ambiguous and, taken as a *blanket deny*, would break legitimate command
    substitution — including the agent's own `git commit -m "$(cat <<'EOF' …)"`
    heredoc pattern — and the hook runs on the working-tree copy, so a bad edit
    self-locks the agent out of committing the fix. **Recommended safe design:**
    add `|` to the `_shell_segments` separator set (safe; `||` stays distinct),
    and *recurse into* `$(...)`/backtick substitutions to check the inner command
    for blocked patterns (mirroring the existing `_shell_launcher_command`
    recursion) rather than blanket-denying. **Before relying on any edit, run the
    modified hook directly against (i) a heredoc `git commit` → must ALLOW,
    (ii) `echo $(git push --force)` → must DENY, (iii) `git status` → ALLOW.**
    Owner to confirm whether they want strict blanket-deny (and accept simple
    `-m` messages for git commit/push) or the recurse-and-check interpretation.
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

## PROGRAM COMPLETE (2026-06-18 final)

The "highest proportionate bar" program is **done** and **`v0.3.0` is cut** — a
`v0.3.0` tag plus a GitHub Release carrying the wheel and sdist. Landed in the
final session:

1. **F6 (#37)** — `agent_hooks.py` hardening. Owner chose **recurse-and-check**.
   `|` added to `_shell_segments`; `_hook_bypass_reason`/`_blocked_shell_pattern_reason`
   recurse (quote-aware) into `$(...)`/backtick bodies via `_reason_with_substitutions`.
   **Key correction:** a first cut stripped quoted-heredoc bodies (to allow a
   commit message mentioning a blocked command) — REVERTED because a quoted
   delimiter blocks expansion, not execution, so `bash <<'EOF'…EOF` still runs the
   body; stripping turned a caught force-push into a missed one (under-block).
   Heredoc bodies are now never stripped (over-block is safe); a regression test
   pins the `bash`-fed heredoc force-push as denied.
2. **Tier 3** — branch coverage + floor 86 + `audit_coverage_contract` branch
   guard (#38); Hypothesis property tests for the data boundary (#39);
   single-version **ADR-0002** (#40, owner chose ADR over a matrix).
3. **Tier 2** — `docs/repository-governance.md` owner-action checklist (#41).
4. **Dependabot** — #29 (actions, SHAs verified vs upstream tags) + #30 (14 python
   deps, verified green incl. pip-audit) merged.
5. **Release** — PR #25 merged via `gh pr merge 25 --squash --auto` → `v0.3.0`.

**Outstanding = owner-only** (in `docs/repository-governance.md`): required status
checks, release-PR token, Code Quality preview, `v*` tag protection.

**Documented F6 residuals (deferred to a future owner-authorised session):**
glued control operators (`ok|git push --force` — shlex yields `ok|git` as one
token; affects all four operators; needs a quote-aware raw tokeniser); bare
subshells `(...)`; heredoc-prose over-block (a commit message quoting a blocked
command verbatim inside a heredoc is over-blocked — safe; reword or use `-m`).

**Tier 4 stays deferred** (SBOM, SLSA, Scorecard, dependency-review, lychee,
mutation testing) — revisit only on explicit owner request.

A `consolidate-docs` / closeout is the next natural step (graduate plans to
completed, refresh the template-fitness thread now F6 is done).

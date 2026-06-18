---
name: "Quality-Gate Surface Expansion"
overview: "Add the high-value quality-gate types surfaced by the Oak ecosystem review, each as its own PR, wired into the single check-ci command surface."
todos:
  - id: reviewer-agents
    content: "Register code/architecture/security/test reviewer agents + add a Pythonicity lens."
    status: completed
  - id: markdown-gate
    content: "Add a Markdown linting gate (PyMarkdown) wired into check-ci."
    status: completed
  - id: gitleaks
    content: "Add a gitleaks secret-scanning gate (pre-commit + check-ci) with a documented allowlist."
    status: completed
  - id: pip-audit
    content: "Add a pip-audit dependency-vulnerability gate (uv-aware), complementing deptry hygiene."
    status: completed
  - id: codespell
    content: "Add a codespell spell-check gate with an en-GB-aware repo wordlist."
    status: completed
  - id: supply-chain-config
    content: "dependabot.yml (uv + github-actions) + action SHA-pins + the audit_supply_chain repo_audit self-check + an incidental packaging-schema fix (pyproject sources -> object form; removal of the config-shape audit_packaging_contract) — all committed and OPEN as PR #28 (HEAD f5225cb). Remaining: get green (CI + SonarCloud) and merge."
    status: pending
---

# Quality-Gate Surface Expansion

**Last Updated**: 2026-06-17
**Status**: IN PROGRESS
**Source**: [Oak quality-gate types review](../../../reports/2026-06-17-oak-quality-gate-types-review.md).

## Goal

Model the high-value quality-gate *types* that the ecosystem review found this
template was missing, so the template demonstrates a complete, modern Python
quality-gate surface. Each gate is the smallest truthful change that doubles as
a good teaching example, wired into the single `check-ci` command surface.

## Progress (2026-06-17)

- DONE: reviewer agents registered + Pythonicity lens (PR #12, merged).
- DONE: Markdown linting gate via PyMarkdown (PR #13, merged).
- DONE: gitleaks secret-scanning gate (PR #16, merged). Design 2 — enforced
  *alongside* check-ci (gitleaks is a Go binary, not a uv package, so check-ci
  stays pure-uv): pinned pre-commit mirror + pinned `secret-scan` CI job
  (checksum-verified binary install; gitleaks-action rejected — org licence +
  Node 20 EOL). New `audit_secret_scanning` keeps the pre-commit rev, CI version,
  and `[secret_scanning]` contract version in lockstep; `.gitleaks.toml` uses
  `useDefault=true` with a commented allowlist. Added a README Prerequisites
  section (auditor-enforced official install link). All three CI checks green.
- Remaining set: pip-audit, codespell, supply-chain config. Each its own PR,
  branched off the current `main`.

## Sequencing notes

- `pip-audit` and `supply-chain config` build cleanly off the post-merge `main`.
- The `ci.yml` SHA-pin step is unblocked now that the CI workflow (PR #11) is on
  `main`.
- Each gate touches the shared gate machinery, so branch each fresh off `main`
  and expect to re-run the merge sequence; do not stack many at once.
- Watch cumulative pre-commit latency: every gate adds to `check-ci`, which the
  pre-commit and pre-push hooks both run. Markdown added about 12s. If the inner
  loop gets slow, consider a faster staged-scoped pre-commit lane (decision
  deferred until the gates are in).

## Gate-machinery coupling map (how to add a gate here)

Adding one gate to this repo touches these surfaces in lockstep — keep them
consistent or `repo_audit` / the gate tests fail:

1. `pyproject.toml` — add the tool as a dev dependency; add its `[tool.X]` config.
2. `src/oaknational/python_repo_template/devtools.py` — add the command handler
   function(s) and matching `_step_runners` entries.
3. `src/oaknational/python_repo_template/gate_contract.toml` — add the command(s)
   to `[repo_local_commands]` and place the step(s) in the `fix`/`check`/`check-ci`
   sequences.
4. `tools/repo_audit_contract.toml` — add the command(s) to the
   `documentation_commands` list for `docs/dev-tooling.md`.
5. `docs/dev-tooling.md` — document the command(s) and the tool.
6. `.agent/skills/start-right-quick/SKILL.md` — update the exact check-ci
   sequence string (enforced verbatim by `audit_dependency_hygiene`).
7. `tests/test_devtools.py` and `tests/test_repo_audit.py` — update the expected
   gate sequences, the `GATE_CONTRACT` / `CHECK_CI_SEQUENCE` fixtures, the usage
   string, and the dev-tooling documentation list.

A subprocess-only tool (invoked by command, never imported) may need a
`deptry` `DEP002` ignore — but verify first: a dev-group tool did not trip it
this session.

## Authoring a repo_audit check

F3's `audit_coverage_contract` and the supply-chain workflow-pinned self-check
both add a new `repo_audit` check. The pattern in `tools/repo_audit.py`:

1. Write `audit_<name>(root: Path) -> list[str]` returning failure strings; use
   the existing `require()`, `read_text()`, and `_load_*` loaders, and the
   `cast(dict[object, object], value)` + per-element `isinstance` idiom for
   parsed TOML/JSON/YAML (never a bare cast as a type-checker silencer).
2. Register it in the `DEFAULT_AUDIT_CHECKS` tuple.
3. Add a focused test in `tests/test_repo_audit.py` using `tmp_path` fixtures:
   one positive case and independent negative cases (one failure axis each),
   asserting the exact messages.
4. If the check enforces a doc or command contract, pin the values in
   `tools/repo_audit_contract.toml` rather than hard-coding them in the auditor.

`audit_ci_workflow` (this session) and `audit_distribution_metadata` are clean
worked examples.

## Acceptance (per gate)

- Tool wired into `check-ci`; `devtools <gate>` and `<gate>-fix` (if relevant)
  work; all seven coupled surfaces consistent.
- `repo_audit` green; gate tests updated and green; full `check` green.
- Own feature branch + PR; CI (Quality gates + CodeQL) green before merge.

## Non-goals

- Link checking (lychee), SBOM, OpenSSF Scorecard, semantic-release, mutation
  testing — valuable but not selected; revisit later.
- UI/infra gates (visual regression, Storybook, Terraform) — not transferable.

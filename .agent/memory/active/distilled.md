# Distilled Learnings

## Repo Preferences

- Keep canonical guidance in `.agent/`; adapters stay thin.
- Prefer deterministic fixtures and explicit validation seams.
- Use `tools/repo_audit.py` for tracked-file checks instead of forcing them into
  `pytest`.
- Prefer documented commands that match the managed runtime, for example
  `uv run python -m ...`, rather than assuming `python` is on `PATH`.
- Treat planning architecture as foundational infrastructure in template repos,
  not as optional scaffolding around "real" work.
- When strict workflow rules exist to make agentic engineering safe, state that
  rationale plainly in user-facing docs instead of leaving it implied.
- Use standard validation taxonomy in testing doctrine and make data-quality
  expectations explicit when the repo can seed data engineering or data science
  work.
- For Oak Python packages, use a dash-separated distribution name such as
  `oaknational-some-package`, a dotted import path such as
  `oaknational.some_package`, and a namespace layout under `src/oaknational/`.
- When pytest injects the source tree onto `pythonpath`, pair source-tree tests
  with an installed-wheel smoke check so packaging truth is still proven.
- Make installed-wheel smoke checks run from a temporary workspace outside the
  repo and cover the installed import plus both console-script and
  `python -m` entry surfaces.
- If the owner wants a richer template rather than a leaner one, make the demo
  justify the declared dependency surface instead of trimming dependencies to a
  placeholder example.
- When Hatch wheel packaging is scoped with `packages = [...]`, verify that
  `py.typed` lands in the built wheel; if it does not, add an explicit wheel
  `force-include` mapping rather than assuming the source-tree marker is enough.
- If a command helper rewrites Python-script shebangs to the current
  interpreter, restrict that behaviour to commands resolved from the current
  environment; absolute paths to other virtualenv scripts must keep their own
  interpreter.
- For Oak namespace packages, keep `deptry` configuration explicit and small by
  marking `oaknational` as known first party instead of reaching first for
  experimental namespace-package support.
- If a dependency is exercised truthfully only through an indirect backend such
  as pandas' Parquet engine loading `pyarrow`, prefer one documented
  dependency-hygiene exception over artificial imports added only to satisfy a
  scanner.
- Keep dependency-hygiene enforcement inside the existing aggregate gate flow
  when no new public `uv run` command contract is needed.
- Parse shell and env launchers by executable basename so absolute-path forms
  such as `/bin/bash` and `/usr/bin/env bash` cannot slip past hook policy as
  if they were different commands.
- Split shipped runtime contracts from repo-audit-only documentation contracts;
  repo-local command-surface policy does not belong in runtime artefacts.
- If docs are validated against a command contract, prove the documented names
  exist in the runtime truth source, not just that the docs contain the right
  strings.
- Adding a quality gate touches seven coupled surfaces in lockstep: the dev
  dependency + `[tool.X]` config, the `devtools` handler + `_step_runners` entry,
  the `gate_contract.toml` command and sequences, the `repo_audit_contract`
  documentation list, `docs/dev-tooling.md`, the exact check-ci sequence string
  in `start-right-quick/SKILL.md` (audited verbatim), and the gate tests.
- `main` is governed by a repository ruleset (PR + CodeQL `code_quality`
  required; direct push blocked). CodeQL default setup does not trigger on PR
  reopen — use `gh pr update-branch` (server-side merge, avoids the hook-blocked
  force-push) to trigger it, then squash-merge to flatten the update commit.
- Verify each PR genuinely green (run the real `check-ci`, not just CodeQL)
  before merging — Dependabot branches do not run the project suite until updated.
- For PyMarkdown on a frontmatter-bearing estate, enable the front-matter
  extension (else a closing `---` reads as a setext heading) and never blind-run
  `pymarkdown fix`: it renumbers ordered lists, so disable MD029 where docs use
  continuous numbering as stable IDs.
- A `repo_audit` self-check is justified only when it guards something a runtime
  gate structurally *cannot* — e.g. the coverage gate enforces "coverage >=
  threshold" but cannot stop its own `fail_under` being lowered or the `omit`
  list growing to hide code, so `audit_coverage_contract` pins a floor + the
  omit-set. Contrast `audit_packaging_contract`, removed for asserting config
  *shape* (`sources == ["src"]`) already proven behaviourally by the wheel-smoke.
  Test the governance gap, never the config spelling.
- SonarCloud Code Analysis is a live, org-level PR gate (no in-repo config) that
  scores **new code** (`new_code_smells_severity`, etc.); it is not a *required*
  ruleset check but is blocking by doctrine. Inspect it via the SonarQube MCP
  (`get_project_quality_gate_status` / `search_sonar_issues_in_projects`,
  projectKey `oaknational_oak-python-starter`, `pullRequest <n>`). Its
  cognitive-complexity and duplicate-literal rules are easy to trip with a new
  multi-branch function — decompose rather than suppress.
- Pin a chart's WCAG contrasts with a test that computes the ratios from an
  independent relative-luminance helper (not the production colours), asserting
  bars clear 3:1 against the background and the target marker's core *or* halo
  clears 3:1 on every background. This catches both regressions and latent bugs.
- `tools/agent_hooks.py` runs on the *working-tree* copy for every Bash command,
  so editing it changes the live guardrail mid-session — a bad edit can self-lock
  the agent out of committing the fix (esp. anything that denies the
  `git commit -m "$(cat <<EOF …)"` heredoc pattern). Before relying on an edit,
  run the modified hook directly against a heredoc commit (must ALLOW) and the
  pattern you intend to block (must DENY).

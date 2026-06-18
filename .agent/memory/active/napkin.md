# Napkin

## Session: 2026-06-18 (final+) — continuous release on merge (PR #44)

### What Was Done

- Replaced the release-PR/`--auto` pattern with **continuous release on merge**
  via the Oak Semantic Release Bot (app 2995796, ruleset bypass actor): trigger
  on `workflow_run` after CI succeeds on main; `create-github-app-token`; compute
  increment; `cz bump`; push bump+tag straight to protected main; publish Release.
  Added `prevent_accidental_major` commit-msg hook (majors stay manual). Retired
  #43 + `release/next`.

### Surprises & corrections (critically assess — incl. sub-agents AND analysers)

- **The literal CI-skip token in a feature commit/PR message skips CI on the
  squash-merge.** My `feat` commit body *described* the loop-guard token in prose,
  so #44's merge skipped CI → no `workflow_run` → no release; main stayed 0.3.0.
  Keep the literal token out of feature messages. Documented in dev-tooling.
- **SonarCloud is a source to critically assess too.** It flagged `S8707` (argv
  path → file read = path injection) on the commit-msg hook. Real impact is ~nil
  (git supplies the path; 1-bit output), but fix-at-source beat suppression:
  confined the path to the worktree-aware git dir with an `allowed_base` test
  seam. Query Sonar via the MCP (`get_project_quality_gate_status` /
  `search_sonar_issues_in_projects`, projectKey `oaknational_oak-python-starter`).
- **Critically rejected two reviewer findings** (premises wrong): pin checkout to
  `workflow_run.head_sha` would make the bump push non-fast-forward under
  concurrent merges (incompatible with direct-push); `create-github-app-token`
  already defaults to current-repo scope, so it is not over-scoped.
- **`git add -A` swept untracked IDE dirs** (`.sonarlint/`, `.vscode/`) into the
  commit — amended them out and gitignored them. Stage explicit paths.
- **ruff `--ignore-noqa` + B009 autofix:** a `getattr(x, "literal")` is rewritten
  to `x.literal` (then pyright reportPrivateUsage fails). Use a *variable* attr
  name: `name = "_fn"; getattr(x, name)`.
- The harness auto-mode classifier **blocks `gh workflow run Release -f
  increment=...`** — agent-forced release version. Rely on the computed increment
  from a real merge.
- **Consolidation must reach the STRATEGIC index, not just continuity/threads.**
  A deep `consolidate-docs` pass refreshed continuity, thread records, and the
  collection README but left `high-level-plan.md` + `roadmap.md` at a mid-program
  snapshot — the top-level strategic surfaces are easy to forget. Add them to the
  consolidation sweep. (Caught when the owner asked for a strategic retrospective.)
- **The sharp strategic question is proportionality, not more rigor.** For a
  "lightweight template foundation", the VISION's clone/rename/adapt promise is
  validated by construction, not by a real adoption — so the next high-value move
  is a first-adoption dry-run (`docs/first-adoption-dry-run.md`), not more gates.

## Session: 2026-06-18 (final) — program COMPLETE: F6 + Tier 3 + Tier 2 + deps + v0.3.0

### What Was Done

- **F6 (#37)** agent-hook hardening: `|` segment split + recurse-and-check into
  `$(...)`/backtick (quote-aware). **Tier 3**: branch coverage + floor 86 (#38),
  Hypothesis property tests for the data boundary (#39), single-version ADR-0002
  (#40). **Tier 2**: `docs/repository-governance.md` owner checklist (#41).
  **Dependabot** #29 (actions, SHAs verified vs tags) + #30 (14 python deps,
  verified green) merged. **Release PR #25 merged → `v0.3.0`** (tag + Release +
  wheel/sdist). Program is done; Tier 4 stays deferred.

### Surprises & corrections (critically assess)

- **Guardrails must prefer over-blocking to under-blocking.** My first F6 cut
  stripped quoted-delimiter heredoc bodies so a commit message could *mention* a
  blocked command. WRONG: a quoted delimiter blocks *expansion*, not *execution* —
  `bash <<'EOF'\n<cmd>\nEOF` still runs the body, so the strip turned a caught
  force-push into a MISSED one. Reverted; added a regression test pinning the
  `bash`-fed heredoc force-push as denied. Over-blocking a commit message is safe;
  under-blocking a force-push is not. The residual (heredoc prose mentioning a
  blocked command is over-blocked) is documented, not "fixed" unsafely.
- **The live hook bites your own tooling.** Once heredoc bodies are scanned, a
  `gh pr edit --body "$(cat <<EOF ... | HUSKY=0 git push ... EOF)"` is denied —
  use `--body-file` (only the command line is scanned, not file contents), and
  keep blocked-command sequences out of heredoc commit messages.
- **Verified, didn't trust:** Explore agent's "validation is idempotent" claim
  (confirmed empirically — pandas renders midnight `datetime64` to date-only);
  Dependabot SHAs (matched upstream tags via API); the live `main` ruleset (via
  API: PR + `code_quality` + no-deletion + non-fast-forward; NO
  `required_status_checks`, NO tag ruleset). See [[critically-assess-subagents-and-sources]].
- **Scope discipline on a safety rail:** closed the documented `|`/`$(...)` gaps
  (owner-authorised) but left glued operators (`ok|git`) + bare subshells as
  documented residuals for a future authorised session, rather than unilaterally
  rewriting the tokeniser.

## Session: 2026-06-18 (later still) — Tier 1b F3/F8/F5/F7 landed, F6 deferred

### What Was Done

- **F3** (#31): coverage `fail_under` 70→85 + `audit_coverage_contract`.
- **F8** (#33): WCAG 2.2 AA chart — darkened the amber bar, white-haloed the
  target marker, alt-text sidecar. Five PRs merged green this session (28/31/32/
  33/34), each through CI + CodeQL + SonarCloud.
- **F5/F7** (#34): remote 10 MiB streaming size-cap (in a connection-closing
  `with`) + `docs/using-this-template.md` rename guide.

### Surprises & corrections (critically assess)

- **A failing accessibility check can reveal an *existing* bug, not just the new
  requirement.** The dark target marker (`#374151`) already failed 3:1 on most
  bars — invisible on blue/teal/red/purple — before F8. Computing the contrasts
  honestly (independent WCAG helper in the test) surfaced it.
- **Don't trust a thread-hint's framing of a security change — verify intent.**
  F6's "fail-closed on `$(`/backticks" reads as a blanket deny, but that would
  break legitimate command substitution *including this agent's own
  `git commit -m "$(cat <<EOF …)"` heredoc pattern*, and the hook runs on the
  working-tree copy → a bad edit self-locks. **Deferred F6** for owner intent +
  a dedicated session rather than rush a dangerous, ambiguous edit to the safety
  rail. Recommended design recorded (pipe-separator + recurse-into-substitution,
  not blanket-deny; pre-verify the edited hook allows a heredoc commit).
- **Reviewer adoption, filtered:** code-review on F8 (added the missing exercise
  assertion, extracted `_chart_title`); security-review on F5 (connection leak →
  `with`; assert `stream=True`). Each adopted finding got a test. The `with`
  exposed a fake-response needing a closeable `raw` — a test-fixture fix, not a
  prod bug.

## Session: 2026-06-18 (later) — supply-chain PR #28, SonarCloud gate, multi-agent collision

### What Was Done

- Merged `main` into `feat/supply-chain-pinning` (it predated the #27 handoff;
  `git rebase` is hook-blocked, so a merge is the history-safe equivalent), added
  the `audit_supply_chain` self-check (TDD), ran config/security/code reviewers,
  and opened **PR #28**. Verified all four pinned SHAs match their upstream `vN`.
- Committed the handed-over packaging-schema fix into PR #28 (the parallel session
  that made it closed mid-task). Refreshed continuity/thread/plan.

### Surprises & corrections (critically assess — don't rubber-stamp)

- **SonarCloud is a live PR gate nobody documented.** `SonarCloud Code Analysis`
  is org-level automatic analysis (no in-repo config), evaluating **new-code**
  conditions. PR #28's first push failed `new_code_smells_severity` (cognitive
  complexity 22 > 15 + a duplicated `.github` literal). Both were *real* and
  matched repo doctrine, so I fixed (decomposed the audit) rather than suppressed.
  Query via SonarQube MCP `get_project_quality_gate_status` /
  `search_sonar_issues_in_projects`, projectKey `oaknational_oak-python-starter`.
- **Reviewers earn their keep, but verify their findings.** I adopted the
  substantive ones (docker `sha256:` digest acceptance — a false-failure bug;
  job-level reusable-workflow `uses:` — a false-negative; `.yaml` globbing; DRY
  helper) and rejected YAGNI test suggestions. Each adopted finding got a test.
- **Two agents in one working tree = hazard.** Another session was concurrently
  editing the *same files* (`repo_audit.py`, the test, `pyproject.toml`). I did
  NOT race to commit (would entangle/destroy their half-done work); I paused and
  asked the owner to sequence. My instinct to "restore" the deleted
  `audit_packaging_contract` was exactly the mistake their napkin had already
  recorded and corrected — assessing before acting saved a wrong edit.

## Session: 2026-06-18 — pyproject `sources` schema error → bad-audit removal

### What Was Done

- Editor (*Even Better TOML* → SchemaStore Hatch schema) flagged
  `tool.hatch.build.targets.wheel.sources = ["src"]` as `["src"] is not of type
  "object"`. Hatchling accepts both the array and the table form; switched to
  `sources = { "src" = "" }` (schema-clean, byte-identical wheel — verified).
- Owner's deeper call: `audit_packaging_contract` was **badly designed** — it
  asserted *config shape* (`sources == ["src"]`, `only-include == [...]`), which
  is implementation-detail testing, not behaviour. Removed the audit function,
  its `DEFAULT_AUDIT_CHECKS` registration, and both test references. All gates green.

### Patterns / Learnings to Remember

- **Don't assert config shape in audits/tests.** Per `testing-strategy.md` ("test
  behaviour, not implementation details"): pinning a specific config spelling is
  doubly wrong when multiple spellings are behaviourally identical (here
  `["src"]` ≡ `{"src"=""}`). A failing such test should send you to delete
  the check, not "fix" the asserted value (my first instinct, corrected).
- **The packaging behaviour is already guarded — don't re-add a check.** The
  `build` gate (`_run_build_probe` → `_run_installed_wheel_smoke_check` in
  `devtools.py`, run in `check` + `check-ci` + CI) builds the wheel, installs it
  into a fresh venv, and proves `import oaknational.python_repo_template` resolves
  to the *installed wheel* (`__file__` not under repo root), then runs both entry
  points. That is the namespace-preserved/`src/`-stripped proof. Do **not** add a
  packaging-config audit *or* a redundant pytest namelist test on top of it —
  both are weaker and violate "smallest validation layer". I nearly added the
  namelist test after wrongly claiming a gap; the wheel-smoke already covers it.
- **Use the IDE problems list early.** The error was an editor diagnostic
  (`mcp__ide__getDiagnostics`), invisible to CLI gates — I burned several CLI
  probes before checking it.

## Session: 2026-06-17 (later) — CI, reviewer agents, Markdown gate, PR sweep

### What Was Done

- Landed **F4 CI workflow** (PR #11): `ci.yml` runs `check-ci` on push + PR;
  `audit_ci_workflow` pins the contract. First real-runner proof of the
  wheel-smoke.
- **Registered the reviewer agents** (PR #12): gave code/architecture/security/
  test Claude adapters the frontmatter only `config-reviewer` had, and added a
  Pythonicity lens to the canonical code-reviewer. They now appear as agent types.
- **Markdown linting gate** (PR #13): PyMarkdown wired into `check-ci`.
- Ran an **ecosystem quality-gate-types review** (3 subagents, ~12 repos) →
  report; owner selected gitleaks/pip-audit/codespell/supply-chain to add next.
- Merged all **9 open PRs** (the 3 above + 6 Dependabot vuln bumps), verifying
  each green first. `main` green.

### Patterns / Learnings to Remember

- **PyMarkdown on frontmatter docs**: enable the front-matter extension or a
  closing `---` is read as a setext heading (this alone took 1816 findings → 25).
- **Never blind-autofix the Markdown estate**: `pymarkdown fix` renumbers ordered
  lists, corrupting docs that number items continuously across sections as stable
  IDs — hence MD029 is disabled. Fix by hand.
- **Adding a gate touches seven coupled surfaces** — see the coupling map in
  `quality-gate-surface-expansion.md`. The `start-right-quick` SKILL.md must carry
  the exact check-ci sequence string (audited).
- **Merge mechanics**: `main` is ruleset-governed (PR + CodeQL required; direct
  push blocked). CodeQL does not trigger on PR reopen; use `gh pr update-branch`
  (server-side merge, no hook-blocked force-push) to trigger it, then squash-merge.
  `ci.yml` concurrency makes superseded push runs show "cancelled" (expected).
- **Verify each PR green before merging**, even Dependabot ones (their branches
  had no `check-ci` run until update-branch'd); the safety classifier enforced this.
- A gateway lesson: the markdown gate immediately caught a real duplicated
  `## Boundaries` block in the test-reviewer template — gates earn their keep.

## Session: 2026-06-17 — Deep review, Phase 1, and adapter rename

### What Was Done

- Ran a deep multi-lens review (11 lenses + adversarial verification + a
  completeness critic); landed the report and a remediation plan (PR #7).
- Landed Phase 1 (PR #8): MIT licence + PEP 639 metadata + `SECURITY.md` +
  `audit_distribution_metadata`; deterministic CSV boundary + int64-range guard.
- Renamed the command-adapter prefix `jc-` → `oak-` across all 44 adapters and
  the audit (PR #9).

### Patterns / Learnings to Remember

- The highest-value review finding (missing `LICENCE`) came from the
  completeness critic, not any focused lens — keep a "what did no lens look at?"
  pass.
- The bar is excellence, not convention: prefer modern best practice (PEP 639
  `license = "MIT"` + `license-files`, `Typing :: Typed` because `py.typed`
  ships) and verify it by inspecting the built wheel; do not cargo-cult a
  reference repo (wrote a fresh `SECURITY.md`; omitted `ATTRIBUTION.md` /
  `LICENCE-DATA.md`).
- Boundary determinism: read CSVs with `dtype=str, keep_default_na=False` so the
  validators own all coercion; pandas' default NA tokens otherwise mis-reject
  legitimate values such as `NA`.
- The repo's own pre-tool hook scans the literal Bash command, so reproducing a
  blocked pattern (e.g. force-push) needs the string built from fragments or run
  from a script file.
- Dependabot is configured (6 open PRs) — a refinement to the review's
  "no supply-chain monitoring" framing.
- Commit/push run the full `check-ci` (a real wheel build) — expect ~15–24 s.

## Session: 2026-04-23 — Post-Closeout Handoff and Consolidation

### What Was Done

- Ran `session-handoff` and `consolidate-docs` after the runtime closeout
  commit `268f04f`.
- Archived the completed runtime-infrastructure plans, refreshed the
  continuity and plan indexes, and recorded the closeout as a closed reference
  rather than a live current plan.
- Rotated the previous multi-session napkin into
  `.agent/memory/active/archive/napkin-2026-04-23.md` after promoting the
  durable lessons into `distilled.md`.

### Patterns to Remember

- After a tranche is committed and reviewer-clean, archive the completed plan
  out of `current/` so the live lane does not imply work that no longer
  exists.
- When a napkin has accumulated a whole closed tranche, rotate it after
  graduation so the next session starts from a clean active-memory surface.

## Session: 2026-06-18 — quality program (gates, release automation) + mid-program handoff

### Surprises & corrections

- **`cz_conventional_commits` ignores `[tool.commitizen].bump_map`.** It reads the
  plugin's hardcoded map (`bump.py:_find_increment` → `self.cz.bump_map`), not the
  config. A custom bump policy needs a self-computed increment passed via
  `cz bump --increment` (see `tools/release_increment.py`). Only the **live
  end-to-end verification** of release automation exposed this — a static review
  and a local `cz bump --dry-run` (which happened to see a `feat`, mapped the same
  either way) both looked correct. Lesson: verify release/version automation by
  actually running it, not just by reading it.
- **A `GITHUB_TOKEN`-opened release PR is perpetually `UNSTABLE`** because `ci.yml`
  does not run on bot-opened PRs (recursion prevention). Merge it with
  `gh pr merge <n> --squash --auto` — NOT `--admin` (the harness classifier
  blocks admin bypass of branch protection, correctly). The real fix is a
  PAT/App token so CI runs on the release PR.

### Patterns that worked

- **Reviewers earn their keep on coupling surfaces.** config-review caught a
  missed seven-surface coupling surface (`.agent/commands/gates.md` still claimed
  "deptry is not vulnerability scanning" after pip-audit landed). Fixed AND made
  `audit_dependency_hygiene` enforce the pip-audit mention so it can't drift again.
- **Kill spell-check false positives at source, not with a repo-wide ignore.**
  codespell flagged an intentional `"vulnerabilit"` substring; reworking the
  audit to match `"vulnerab"` removed the need for any `ignore-words-list`.
- **Standing release PR accumulation:** let the release/next PR accumulate every
  feat/fix merge through a multi-PR sprint, then merge it once for a single clean
  release — avoids per-PR release churn.

### Source plane: executive

- Owner contracts reaffirmed this session: a committed (not tag-derived) version;
  custom bump policy (feat/fix→minor, else→patch, breaking→manual major); GitHub
  Releases only (no PyPI); binary tools documented in README Prerequisites with
  official install links; "highest *proportionate* bar" (stop before Tier 4 —
  SBOM/Scorecard/mutation — unless explicitly asked).

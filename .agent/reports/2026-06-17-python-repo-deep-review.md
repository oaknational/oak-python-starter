# Deep-Dive Review — Oak Python Repo Template

**Date**: 2026-06-17
**Subject commit**: `4e83e5e` (main)
**Scope**: the Python repo itself — runtime source, tests, tooling, packaging, quality gates, and the seeded demo. The agentic Practice estate and a comparison against the `oak-open-curriculum-ecosystem` Practice are treated as background.
**Lens framing**: this repo exists for **demonstration and templating** ([VISION.md](../VISION.md)), so findings are graded for exemplar value and adoptability, not production-service hardening.

---

## 1. Verdict

This is a **genuinely high-quality, unusually disciplined repository** — the engineering craft sits well above typical "starter template" standard. It is held back not by bad code but by a small number of **honesty and completeness gaps**, plus one strategic tension: **the enforcement machinery is simultaneously over-built and aimed at the wrong risks.**

There are **no blockers to running it**. All nine quality gates pass, 75 tests are green, and measured coverage is 88%. But there are real **blockers to its stated purpose** — being a demonstration, a teaching aid, and a template basis for future repos: it is legally unusable as a base (no licence), its flagship boundary lesson mis-rejects valid data, and its honesty exemplars (coverage gate, CI) and accessibility are weaker than they appear. The highest-value fixes are cheap and self-contained, and several matter *more* precisely because this is a template others will copy.

## 2. Method and assurance

The runtime was read in full first, then reviewed through **11 orthogonal lenses**, each producing evidence-cited findings that were then **adversarially verified against the actual files** (refute-by-default), followed by a **completeness critic** that hunted for classes of issue no lens examined. 98 agents in total.

- **Ground truth**: `devtools check-ci` was run end-to-end — all gates pass; 75 tests; coverage 87.99%.
- **Verification outcome**: 62 confirmed, 22 partially-confirmed, 2 refuted. The two refutations caught genuine over-claims (see Appendix B), which gives confidence the verification was not a rubber stamp.
- **Severity is the reviewer's own**, re-graded for the demonstration/templating purpose — the verifiers validated *facts* more rigorously than *significance*.
- **Independently reproduced** before headlining (see Appendix A): the piped hook-bypass, the CSV boundary mis-rejection, and the absence of a LICENCE file, project metadata, and CI.

## 3. Strengths (reported faithfully)

- **Honest layering.** The import-linter contracts ([pyproject.toml](../../pyproject.toml) `[tool.importlinter]`) match reality exactly; the three-strand separation (data → demo → devtools) is real, not aspirational.
- **Boundary discipline.** `validate_activity_frame` rejects empty frames up front so downstream division and first-category access cannot fail; redirects are rejected (`allow_redirects=False` plus a 3xx guard); `yaml.safe_load`; allow-listed metadata keys; TLS verification left intact; UNC and Windows-drive handling. (`src/oaknational/python_repo_template/data/activity_store.py`)
- **Installed-wheel smoke check** (`devtools.py` `_run_installed_wheel_smoke_check`) builds the real wheel, installs into an isolated `uv venv`, runs *both* entry surfaces, and **asserts the import does not resolve back to the source tree** — the proof most templates omit.
- **Tests are behaviour-first via injected seams** (`csv_loader`, `remote_reader`, `http_get`, `process_runner`, …) rather than monkeypatch theatre; independent and parallel-safe.
- **Headless `FigureCanvasAgg`** instead of global `pyplot` — the correct packaging choice for a library.
- **Contract-driven gates** (`gate_contract.toml` → `gate_registry` → `devtools`, audited transitively), with `--ignore-noqa` enforced everywhere so `# noqa` cannot silently suppress lint.

## 4. Findings

Grades: **High** (fix before the template is recommended for reuse) · **Medium** · **Low**. "Lenses" notes where independent reviewers converged — the deliberate overlap that gives more than one opinion per artefact.

### Tier A — template-essential (cheap, high exemplar value)

**F1 · No `LICENCE` and no distribution metadata — High.**
The template is explicitly meant to be "cloned, renamed, and adapted" yet ships with **no licence file** (legally "all rights reserved", so adopters cannot safely reuse it) and `[project]` declares no `license`, `authors`, `classifiers`, or `urls`, so the built wheel carries no licence intent. The comparison ecosystem repo ships `LICENCE` + `LICENCE-DATA.md`.
*Evidence*: no `LICENCE`/`LICENSE`/`COPYING` at repo root; `pyproject.toml:1-17` has only name/version/description/readme/requires-python/dependencies. *Lenses*: completeness critic (missed by all lenses — vindicates the overlap design).

**F2 · The flagship data boundary mis-rejects legitimate input — High.**
The repo's central teaching principle is "validate untrusted data at the boundary", but `default_csv_loader` is a bare `pd.read_csv`. A row whose `category` is the literal `NA` (or `null`/`None`) is silently coerced to `NaN` by pandas' default NA-sniffing, then **rejected as "category values must be non-empty"** — a false rejection of valid data. The same defaults blank `notes="NA"` and break thousands-separated numbers, all *before* the validators run.
*Evidence*: `activity_store.py` `default_csv_loader` (≈line 94) and the remote CSV path (≈line 322); reproduced in Appendix A. *Lenses*: completeness critic (missed by correctness and security lenses).

**F3 · The coverage gate does not protect what has been achieved — Medium (High for a template that should model honest gates).**
Measured coverage is 88% but the gate only requires `fail_under = 70` — an 18-point slack that protects nothing — and the largest module, `devtools.py` (~497 lines), is **excluded from measurement entirely** with no comment and no `repo_audit` check pinning the omit-list or threshold.
*Evidence*: `pyproject.toml:79` (`omit`), `:84` (`fail_under = 70`); gate run shows TOTAL 88% with `devtools.py` absent from the report. *Lenses*: gate-honesty (major) + testing. **Reconciliation**: the testing lens correctly **refuted** the framing "devtools is untested" (it is well covered by `test_devtools.py`); the accurate statement is *tested but unmeasured*, so the headline number is unrepresentative and unguarded — an honesty gap, not hidden dead code.

**F4 · "check-ci" implies a CI parity that does not exist — Medium.**
There is no `.github/workflows/`; `check-ci` is wired only to local pre-commit/pre-push hooks, which are bypassable and absent on a fresh clone until `pre-commit install`. A serious template should ship CI as an exemplar — and CI would, for the first time, exercise the wheel-smoke orchestration for real (today every `devtools` test injects fakes, so the most load-bearing packaging proof is only asserted via stubs).
*Evidence*: `.pre-commit-config.yaml` runs `check-ci` at `pre-commit`+`pre-push`; no workflow files exist. *Lenses*: gate-honesty + completeness critic.

### Tier B — engineering quality and adoptability

**F5 · The remote reader is an SSRF / size-DoS primitive — Medium (context-dependent).**
Any HTTPS host is fetched verbatim (`https://169.254.169.254/…` reaches cloud metadata) and `response.content` buffers an unbounded body. In the **shipped local CLI** the user supplies their own URL, so exploitability is low — **but a template invites this boundary into services**, where it becomes a genuine major. The existing redirect-rejection is what keeps it from being trivially pivotable.
*Evidence*: `activity_store.py` `default_remote_reader` (≈110-122), `_resolve_remote_source` (≈278-288). *Lenses*: security. **Proportionate fix for a demo**: a modest response-size cap plus an explicit note on the trust boundary — not a full SSRF allow-list framework.

**F6 · The hook guardrail is bypassable, and over-built — Medium.**
`agent_hooks.py` spends ~315 lines on a recursive shell parser, **yet it is still evadable** by a one-character pipe: `true | SKIP=quality-gates git commit` and `true | git -c core.hooksPath=… commit` both return *allow* because the structural detector only runs when a segment's first token is `git`, and `_shell_segments` does not split on `|`. (Regex-detected tricks such as `--force`/`--no-verify` survive piping and are still caught.) It is simultaneously gold-plated and incomplete. The test suite has ~40 deny cases but **no allow cases**, so an over-blocking regression that bricks the git workflow would pass silently.
*Evidence*: `agent_hooks.py` `_shell_segments` (484-501), `_git_invocation` (631-692); reproduced in Appendix A. *Lenses*: correctness + security + testing. **Direction**: simplify and *fail-closed* (treat `|` as a separator; deny on `$(`/backticks in a git-bearing segment) rather than adding more parsing; add allow-path tests.

**F7 · Rename friction undercuts the core template promise — Medium.**
There is no rename script or "adapting this template" guidance, and `tools/repo_audit.py` **hard-asserts the literal identity** (`oaknational-python-repo-template`, the README title, namespace paths, `activity-report`) across ~150 sites — so a rename **breaks `check-ci`** until the auditor's own constants are hand-edited.
*Evidence*: `repo_audit.py` `audit_identity` (≈452-501), packaging/typing asserts; identity strings duplicated across `pyproject.toml`, `README.md`, `docs/dev-tooling.md`, the contracts, and the namespace path. *Lenses*: template-dx.

### Tier C — organisation-mandate accessibility (WCAG 2.2 AA)

**F8 · The generated chart has accessibility gaps — Medium (mandate makes it non-optional; fixes are small).**
The PNG chart is emitted with **no text alternative** (SC 1.1.1) even though `render_summary` already computes a perfect one; palette colour `#d08d46` is **2.77:1** on white — below the 3:1 non-text-contrast threshold (SC 1.4.11) — and the target `_` marker is ~1.55:1 against blue bars. Categories themselves are axis-labelled (not colour-only), and the text report and markdown docs are fully accessible.
*Evidence*: `activity_report.py` `default_chart_writer` (102-167), `PALETTE`/`TARGET_COLOUR` (41-42); contrast recomputed independently. *PII*: fixtures are synthetic — **clean**, confirmed.

## 5. Background — Practice / agentic estate (secondary)

The agentic estate is well-disciplined: adapters are genuinely thin, the hook runtime is single-sourced, the Codex commands-as-skills projection is honest, and empty planes document *why* they are empty. Real snags, all low priority: **ADR-0001 cites a research note that does not exist** (dead pointer in an Accepted ADR); GitHub is marked hook-"portable" but has no session-start grounding hook, and the support matrix has no legend; and `practice-verification.md` claims "all linked paths resolve" with no scanner enforcing it (the repo breaking its own "governance-claim-needs-a-scanner" rule).

**Deprecated commands tier (future, not pressing).** The repo still carries a `.agent/commands/` tier (12 commands plus their `jc-*` cross-platform adapters and the `_audit_command_parity` machinery in `repo_audit.py`). These are deprecated in favour of skills; the mature `oak-open-curriculum-ecosystem` repo has already migrated the same workflows (`plan`, `go`, `metacognition`, `session-handoff`, `start-right-*`, `consolidate-docs`) to `skills/`. Migration is eventually needed but is explicitly **not a priority** and does not block the template's purpose.

On the ecosystem comparison, the template's minimalism is mostly *correct* — `collaboration/`, `state/`, `roles/`, `milestones/` are multi-agent or product-specific and rightly omitted — so the only genuinely worth-seeding gaps are `LICENCE` (F1) and a short `SECURITY.md`.

## 6. Recommended order of attack

1. **F1** — add a `LICENCE` + `[project]` metadata (legal prerequisite for reuse; minutes of work).
2. **F2** — fix the CSV boundary (`keep_default_na=False` + explicit dtypes) and add the missing negative tests.
3. **F3 + F4** — raise `fail_under` toward the achieved level, audit the omit-list, and add a CI workflow running `check-ci` (also exercises the wheel-smoke for real).
4. **F8** — emit the text summary alongside the chart and lift the two failing contrasts (org mandate, cheap).
5. **F5 / F6 / F7** — document + lightly cap the fetch boundary; simplify-and-fail-close the guardrail with allow-tests; add a rename guide.

See [the remediation plan](../plans/runtime-infrastructure/current/template-fitness-remediation.md) for the worked-through phases and acceptance criteria.

---

## Appendix A — what was independently reproduced

- **Piped hook-bypass**: `true | SKIP=quality-gates git commit` → *allow*; `true | git -c core.hooksPath=… commit` → *allow*; piped `--force` → *deny* (regex path). Confirms the structural/regex asymmetry.
- **CSV boundary**: a CSV with `category` = `NA` parses to `NaN` under `pd.read_csv` and is rejected as "must be non-empty" — a false rejection of valid data.
- **Distribution gaps**: no `LICENCE` at root; no `license`/`authors`/`classifiers` in `pyproject.toml`; no `.github/workflows/`.
- **Gate ground truth**: `check-ci` green; 75 tests; coverage 87.99% with `devtools.py` omitted.

## Appendix B — claims that were refuted or down-graded (for honesty)

- **"Remove the `py.typed` `force-include` as redundant"** — *refuted*. The repo's own distilled memory records that `only-include` did **not** land `py.typed`; the `force-include` is required and must stay.
- **"`devtools.py` is fully exercised yet excluded from coverage" (as a danger)** — *refuted as framed*; the config facts are true but the module is well-tested. Re-stated accurately as F3.
- **SSRF severity** — down-graded for the shipped local CLI (user supplies the URL); remains a real concern *because the boundary will be copied into services* (F5).

## Appendix C — deferred backlog (real, lower priority for a demo)

- **SSOT erosion**: `gate_registry.repo_local_command_targets()` has no production caller while `repo_audit` reimplements the mapping (so "shared by audits" is aspirational); pyright config duplicated across `pyproject.toml` and `pyrightconfig.json`; TOML shape-helpers triplicated; gate-step vocabulary in a third place yields a **bare `KeyError`** on drift (`devtools.py:420`) — a fail-fast-with-helpful-errors miss flagged by three lenses.
- **`repo_audit.py` (1666 lines)** is larger than the runtime it guards, pins exact strings/timeouts, and audits neither the coverage config, the import-linter contracts, nor its own practice-index link claim.
- **Bleeding-edge stack** (`requires-python >= 3.14`, `pandas >= 3.0`, `numpy >= 2.4`) maximises "newest" over "adoptable today" — a deliberate decision worth stating in an ADR.
- **Minor correctness**: int64 saturation on absurd `minutes`; misleading ISO-date message for Parquet datetimes; non-deterministic wheel pick on equal mtimes; double frame-validation on the report path; `test` + `coverage` run the suite twice per gate; `dev` breaks from a subdirectory; non-atomic Parquet/PNG writes.
- **Deprecated commands tier**: migrate `.agent/commands/` (and the `jc-*` adapters + `_audit_command_parity`) to skills, as the ecosystem repo already has — eventually needed, explicitly not a priority.
- **Background**: ADR-0001 dead link; GitHub session-start hook + matrix legend; practice-index link scanner.

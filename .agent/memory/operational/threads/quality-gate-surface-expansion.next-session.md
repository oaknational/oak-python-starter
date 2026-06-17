# Thread: quality-gate-surface-expansion

## Participating Agent Identities

| agent_name | platform | model | role | first_session | last_session |
| --- | --- | --- | --- | --- | --- |
| Claude | claude | opus-4.8 | executor | 2026-06-17 | 2026-06-17 |

## Owning Plan

- [`../../../plans/runtime-infrastructure/current/quality-gate-surface-expansion.md`](../../../plans/runtime-infrastructure/current/quality-gate-surface-expansion.md)
- Source review: [`../../../reports/2026-06-17-oak-quality-gate-types-review.md`](../../../reports/2026-06-17-oak-quality-gate-types-review.md)

## Current Objective

Add the high-value quality-gate types the ecosystem review surfaced, each as its
own PR wired into `check-ci`. Reviewer agents, the Markdown gate, and gitleaks
are done; pip-audit, codespell, and supply-chain config remain.

## What Landed (2026-06-17)

- **Reviewer agents (PR #12, merged).** Gave the code/architecture/security/test
  Claude adapters the registration frontmatter that only `config-reviewer` had
  (an incomplete migration), so all five are now usable agent types. Added a
  "Pythonic Idiom" lens to the canonical `code-reviewer` template. Confirmed
  registered (they appear as agent types after merge).
- **Markdown gate (PR #13, merged).** PyMarkdown wired into `check-ci`. Ruleset
  in `[tool.pymarkdown]`: recognise front matter; disable MD013/MD041/MD029;
  MD024 siblings-only; keep MD040 and the rest. Surfaced and fixed a real
  duplicated `## Boundaries` block in the test-reviewer template.

## What Landed (gitleaks, PR #16, merged)

- **Design decision (owner):** enforce gitleaks *alongside* `check-ci`, NOT inside
  it. gitleaks is a Go binary, not a uv package; keeping it out of `check-ci`
  preserves the "`uv sync` is sufficient" invariant. This is the first gate
  outside the single `check-ci` signal — accepted, documented cost.
- **Channels:** pinned pre-commit mirror (`github.com/gitleaks/gitleaks` `rev:
  v8.30.1`; pre-commit auto-provisions Go, no manual install) + a pinned
  `secret-scan` CI job that downloads the binary and verifies a hardcoded sha256.
  `gitleaks-action` rejected: needs `GITLEAKS_LICENSE` for org repos + v2 dies
  when Node 20 runners retire (Sept 2026).
- **Governance:** `audit_secret_scanning` (new `repo_audit` check) keeps the
  pre-commit rev, the CI version, and `[secret_scanning].gitleaks_version` in
  `tools/repo_audit_contract.toml` in lockstep. CI archive name is *derived* from
  the version so a partial bump fails loudly at the checksum step.
- **`.gitleaks.toml`:** `[extend] useDefault = true`; no `[allowlist]` block (an
  empty one is rejected by gitleaks ≥8.30 — keep it absent until a real exemption
  with at least one concrete check exists). Working-tree (`dir`) scan only, not
  history — documented as a deliberate later enhancement.
- **Prerequisites policy (owner):** binary / non-standard-install tools go in the
  README Prerequisites section with an official install link; the auditor
  enforces the gitleaks link. See memory `binary-tools-need-readme-prerequisites`.

## Next Session — Start Here

Each its own feature branch off the current `main`, its own PR. Follow the
gate-machinery coupling map in the plan (seven surfaces per gate). **pip-audit
and codespell are Python packages**, so unlike gitleaks they DO follow the full
in-`check-ci` seven-surface coupling map (dev dependency, devtools handler,
gate sequence, etc.).

1. **pip-audit** — dependency-vulnerability scan (uv-aware, e.g. `uv export`
   piped to `pip-audit`), complementing deptry hygiene. Update the README line
   that says deptry "is dependency hygiene, not vulnerability scanning".
2. **codespell** — en-GB-aware spell check with a small repo wordlist for jargon.
3. **supply-chain config** — commit `.github/dependabot.yml` (pip + github-actions)
   and pin the `ci.yml` action SHAs (unblocked now #11 is merged); optional
   `repo_audit` self-check that workflow actions are SHA-pinned.

## Key Decisions and Mechanics (would be lost otherwise)

- **Merge mechanics for this repo.** `main` is governed by a *repository ruleset*
  (not classic branch protection): a PR is required (0 approvals) and a CodeQL
  `code_quality` check must pass. Direct pushes to `main` are blocked.
  - CodeQL default setup does **not** trigger on PR reopen; it needs a
    `synchronize` event (a new commit).
  - The repo's own pre-tool hook blocks `git push --force`, so you cannot rebase
    a PR branch locally. Use `gh pr update-branch <n>` — it merges `main`
    server-side (no force-push), brings the branch up to date, and triggers
    CodeQL + CI. Then **squash-merge** to flatten the update-branch merge commit.
  - `ci.yml` has a `concurrency` group with `cancel-in-progress`, so superseded
    push runs on `main` show as "cancelled" — that is expected, not a failure.
  - **Only the CodeQL `code_quality` check is ruleset-required — the `ci.yml`
    "Quality gates" run is NOT.** A PR can therefore merge (and `main` can go
    red) even if Quality gates fails. Always confirm Quality gates green before
    merging, and verify gate-affecting PRs locally first. **Recommended
    hardening**: add "Quality gates" to the ruleset's required status checks so
    CI actually gates merges (owner/repo-settings action).
  - Literal merge: `gh pr merge <n> --squash --delete-branch` (use `--rebase`
    when the branch is a single commit with no update-branch merge commit).
- **Bandit is not needed as a separate gate** — ruff's `S` (flake8-bandit)
  ruleset covers most Python SAST.
- **Never blind-autofix the Markdown estate.** `pymarkdown fix` renumbers
  ordered lists, which corrupts docs that number items continuously across
  sections as stable IDs (hence MD029 is disabled). Fix violations by hand.
- **Cumulative pre-commit latency** is a watch item: every gate adds to
  `check-ci`, which pre-commit and pre-push both run.

## Blockers / Low-Confidence Areas

- None blocking. Each remaining gate is independent and well-scoped.

## Next Safe Step

- Open a feature branch for **pip-audit** off the current `main` and proceed.
  Note the gitleaks pre-commit hook now runs on every commit (~6s installed),
  and `secret-scan` is a separate CI job — confirm both it and Quality gates are
  green on the next PR too (neither is ruleset-required yet).

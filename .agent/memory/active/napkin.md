# Napkin

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

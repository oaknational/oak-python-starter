# Repo Continuity

**Last refreshed**: 2026-04-23 — the source-Practice transfer remains the
closed baseline, and active branch-primary work has shifted to the
`pythonic-alignment` thread. WS4 has now landed: `commitizen` is installed,
the repo's `pre-commit` configuration installs `commit-msg` alongside
`pre-commit` and `pre-push`, real commit-message files are validated through
`uv run cz check --allow-abort --commit-msg-file`, and repo docs now expose
the canonical `uv run cz commit` / `uv run cz check` workflow. While landing
WS4, a wheel-packaging regression was discovered and fixed: Hatch now preserves
the `oaknational/python_repo_template` namespace in built wheels via
`only-include` plus `sources`, repo audit guards that contract, and the landing
again finished with a passing `uv run check`.

## Active Threads

| Thread | Purpose | Next-session record | Active identities |
| --- | --- | --- | --- |
| `pythonic-alignment` | Make the repo more Pythonic without weakening Oak constraints by broadening the bounded demo and tightening package/tool truth | [`threads/pythonic-alignment.next-session.md`](threads/pythonic-alignment.next-session.md) | `codex / gpt-5 / unknown / executor / 2026-04-23` |

## Branch-Primary Lane State

- Current branch-primary thread: `pythonic-alignment`
- Canonical next-session record:
  [`threads/pythonic-alignment.next-session.md`](threads/pythonic-alignment.next-session.md)

## Current Session Focus

- Preserve the landed Practice baseline while carrying the Pythonic alignment
  thread from landed WS4 Commitizen enforcement into the next packaging and
  gate-truth pass.

## Repo-Wide Invariants / Non-Goals

- Preserve the repo's Python-first runtime and `uv`-managed workflow.
- Keep the Practice portable, but adapt it truthfully to Python where the
  source repo assumes Node-specific mechanics.
- Do not import source-repo historical residue that breaks this repo's audit or
  identity.
- Treat the approved 2026-04-23 transfer scope as closed; further
  source-Practice intake needs a new explicit owner decision.
- Keep `oaknational.*`, strict gates, and Practice governance as fixed
  constraints while making the runtime surface more Pythonic.

## Next Safe Step

- Start WS5 of
  `.agent/plans/runtime-infrastructure/current/pythonic-alignment-and-commitizen-adoption.md`:
  add installed-wheel verification to the canonical build and check path and
  keep the repaired Oak namespace packaging contract green.

## Deep Consolidation Status

- Incoming Practice material has been integrated and the Practice Box is clear.
- Deep session-handoff and consolidate-docs closeout has been run on the landed
  state.
- No additional deep consolidation work is currently due from this planning
  session.
- The `clean` command now skips virtualenv-owned cache trees; that regression
  was caught and fixed in the same standardisation pass.
- The imported planning and doctrine surfaces were verified under the repo
  audit after language and source-local residue were generalised away.
- README, testing doctrine, distilled memory, and experience were refreshed to
  reflect the final steady state.
- The `practice-foundation-upgrade` thread remains as the closed baseline
  reference for the landed Practice transfer.

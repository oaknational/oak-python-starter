# PDR-008: Pythonic Canonical Quality-Gate Naming

- Status: Accepted
- Date: 2026-04-23

## Context

The Practice benefits from standard gate names across repos, but this Python
template cannot truthfully adopt colon-separated script names through its
current package-script surface. The repo also forbids aliases and compatibility
layers that keep legacy names alive after a structural decision has been made.

## Decision

The Python template standardises its gate API with Python-native dash
separators and no aliases:

- `clean` removes repo-local build artefacts and caches
- `build` produces package artefacts
- `dev` runs the seeded development entry surface for the demo CLI
- `format` verifies formatting
- `format-fix` applies formatting
- `lint` verifies lint and import-boundary rules
- `lint-fix` applies fixable lint changes, then rechecks the non-fixable lint
  surfaces
- `fix` runs the mutating sub-gates
- `check` runs the local fix-and-verify aggregate
- `check-ci` is the authoritative non-mutating aggregate

Additional repo-specific gates such as `repo-audit` and `coverage` remain
first-class and are included inside the aggregate checks where appropriate.

## Consequences

- The repo gets a stable, portable gate vocabulary without pretending Python
  console-script names behave like Node script names.
- Old gate names are removed rather than preserved as compatibility layers.
- Any surface that assumed the old semantics must be updated in the same
  landing: docs, hooks, pre-commit, review workflows, and audits.

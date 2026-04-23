# Pythonic Alignment, Demo Expansion, and Commitizen Adoption

Completed on 23 April 2026.

This tranche is archived because its durable outcomes now live in canonical
docs and code. The archive note is only a closure record.

## Durable Outcomes

- The seeded demo now uses a bounded "activity pack" contract with YAML
  sidecars, optional HTTPS inputs, metadata-aware summaries, and
  `matplotlib`-generated charts.
- The package now ships `py.typed`, declares strict `pyright` scope
  explicitly, preserves the Oak namespace in the built wheel, and proves the
  installed wheel outside the source tree.
- Commit workflow truth now runs through `commitizen`, while canonical
  repo-local gate names live in `gate_registry.py` and both aggregate checks
  enforce dependency hygiene before repo audit.
- README, `docs/dev-tooling.md`, repo audit, and the direct tests now all
  describe and enforce the same runtime and tooling contract.

## Closure Evidence

- `uv run python -m oaknational.python_repo_template.devtools check`
- `uv run python -m oaknational.python_repo_template.devtools check-ci`
- The broader runtime closeout later finished reviewer-clean in `268f04f`
  without reopening this tranche.

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

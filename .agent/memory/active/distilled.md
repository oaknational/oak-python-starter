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

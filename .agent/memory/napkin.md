# Napkin

## Session: 2026-04-21 — Template Extraction

### What Was Done

- Seeded the template repo from reusable infrastructure only.
- Replaced the old application lane with the `activity-report` CLI.
- Moved the package to the canonical `src/python_repo_template/` layout rather
  than keeping an unusual top-level `python/` package.
- Tightened the deny-list cleanup after the repo audit caught copied
  balancing-language wording inside generic Practice documents.
- Added the repo root to pytest `pythonpath` so root-level support modules such
  as `tools.agent_hooks` import the same way under `uv run pytest` as they do
  under direct local execution.
- Found and fixed a sibling-repo audit edge case: `tools/repo_audit.py` was
  treating any extensionless file as text, which made it choke on the binary
  `.coverage` database.

### Patterns to Remember

- Hidden directories need explicit deny-list sweeps when extracting a repo.
- Canonical Python packaging should win over preserving source-repo layout when
  the template's job is to model best practice.
- Text-estate audits should whitelist known text file shapes rather than assume
  every extensionless dotfile is UTF-8.

## Session: 2026-04-22 — Sibling Verification and Native Hand-off

### What Was Done

- Switched to `/Users/jim/code/personal/python-repo-template` and verified the
  sibling repo directly rather than trusting the staging copy
- Ran `uv sync` in the sibling repo and confirmed `uv run check` passes there
- Ran the seeded CLI as a smoke test against `data/fixtures/activity_log.csv`
- Fixed `tools/repo_audit.py` so binary dotfiles such as `.coverage` do not
  break the legacy-term sweep
- Added `tests/test_repo_audit.py` for that regression
- Preserved the remaining follow-up work in the native hand-off plan for the
  next native session
- Confirmed two interrupted polish edits did land:
  `src/python_repo_template/__main__.py` and `tools/__init__.py`
- Confirmed one interrupted edit did not land:
  `tests/test_package_entrypoint.py`

### Patterns to Remember

- Verify the sibling repo itself before declaring an extraction complete; local
  runtime artefacts can surface bugs that the staging copy never hit
- After an interrupted edit, inspect the filesystem before assuming which files
  landed and which did not
- A small hand-off plan in `active/` is the right place to preserve verified
  repo state before switching to a fresh native session

## Session: 2026-04-22 — Canonical Package Entry Polish

### What Was Done

- Re-verified the repo before further changes with `uv run check` and the
  `activity-report` CSV smoke command
- Added `tests/test_package_entrypoint.py` to prove the package module entry
  surface reports the expected fixture summary
- Tightened `tools/repo_audit.py` required canon to include
  `src/python_repo_template/__main__.py`, `tools/__init__.py`, and
  `tests/test_package_entrypoint.py`
- Updated `README.md` to document the verified module-form invocation
  `uv run python -m python_repo_template report --input data/fixtures/activity_log.csv`
- Verified the module-form invocation locally and finished with a passing
  `uv run check`

### Patterns to Remember

- When the repo is managed through `uv`, document the module-form invocation as
  `uv run python -m ...` unless the shell-level `python` command is itself a
  supported repo contract
- Keep file-presence canon load-bearing inside `tools/repo_audit.py` itself;
  do not mirror it in `pytest` tests that constrain repo configuration

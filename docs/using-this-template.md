# Using this template for a new project

This repository is an opinionated Oak Python starter. Its name appears in a few
coupled places, and `repo-audit` deliberately pins the Oak identity, so renaming
is a small, ordered job rather than a global find-and-replace. The audit is your
safety net: after each step, run

```bash
uv run python -m oaknational.python_repo_template.devtools check
```

and let the `repo-identity`, `packaging-contract`-style, and parity checks point
you at any surface you missed.

## The three names

| Name | This template | Example for a new project |
| --- | --- | --- |
| Distribution (PyPI) name | `oaknational-python-repo-template` | `oaknational-widget-tools` |
| Import path | `oaknational.python_repo_template` | `oaknational.widget_tools` |
| Package directory | `src/oaknational/python_repo_template/` | `src/oaknational/widget_tools/` |
| GitHub slug | `oaknational/oak-python-starter` | `oaknational/widget-tools` |

The `oaknational` namespace is intentional (see the namespace-package layout in
`docs/dev-tooling.md`). Keep it unless you are moving outside the Oak namespace,
in which case also rename the `src/oaknational/` directory and the
`[tool.deptry] known_first_party` and `[tool.importlinter] root_package` entries.

## Ordered steps

1. **Rename the package directory.** Move
   `src/oaknational/python_repo_template/` to your new module name, keeping the
   `src/<namespace>/<module>/` shape.
2. **Update `pyproject.toml`:** `[project].name`, the `[project.scripts]` entry
   (rename `activity-report` and its `module:function` target),
   `[project.urls]`, `[tool.coverage.run].source` and `omit`,
   `[tool.importlinter].root_package`, `[tool.deptry]` first-party config, and
   any `[tool.pyright]` include paths.
3. **Update the command surface.** Replace
   `oaknational.python_repo_template.devtools` in `.pre-commit-config.yaml` and
   `.github/workflows/ci.yml`, and the published entry point and documentation
   paths in `tools/repo_audit_contract.toml`.
4. **Update the audits and their expectations.** `tools/repo_audit.py`
   (`audit_identity` and friends) pins the template's name, README heading, and
   demo script; update those expected strings and the matching tests in
   `tests/test_repo_audit.py` to your project's identity.
5. **Replace the demo.** The `activity-report` CLI under `demo/` and its data
   boundary under `data/` exist to exercise the infrastructure. Replace them with
   your own code (and tests), or delete them and relax the demo-specific audits.
6. **Refresh the docs.** Update `README.md` (title, badges, install/run
   snippets), this guide, and `.agent/` directives that name the template.
7. **Re-run `check` until green**, then commit on a branch and open a PR — the
   same workflow the template models.

## What you are keeping

The value of the template is the *infrastructure*, not the demo: the `src/`
layout, the single `devtools` gate surface, the full blocking gate sequence
(format, type-check, lint, markdown, spell-check, import-linter,
dependency-hygiene, pip-audit, repo-audit, build, test, coverage), the
SHA-pinned CI with Dependabot, the release-PR automation, the secret-scanning
gate, and the `.agent/` working method. Those stay as-is; only the names and the
demo change.

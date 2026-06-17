# Component: Quality Gates

Use the canonical repo-local `uv run python -m ...` gate surface.

## After each meaningful task

Run the smallest truthful set that proves the task:

```bash
uv run python -m oaknational.python_repo_template.devtools typecheck
uv run python -m oaknational.python_repo_template.devtools lint
uv run python -m oaknational.python_repo_template.devtools test
```

## After each phase or before closure

Run the full non-mutating aggregate:

```bash
uv run python -m oaknational.python_repo_template.devtools check-ci
```

If you intentionally want the local fix-and-verify sweep, run:

```bash
uv run python -m oaknational.python_repo_template.devtools check
```

Every gate failure is blocking. Do not narrow the gate to dodge the failure.

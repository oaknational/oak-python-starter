# Python Environment Setup

Use `uv` for environment creation and command execution:

```bash
uv sync
uv run python -m oaknational.python_repo_template.devtools clean
uv run python -m oaknational.python_repo_template.devtools build
uv run python -m oaknational.python_repo_template.devtools dev
uv run python -m oaknational.python_repo_template.devtools check
uv run python -m oaknational.python_repo_template.devtools check-ci
uv run python -m oaknational.python_repo_template.devtools fix
uv run activity-report --help
```

The repo targets Python 3.14.

Use `uv run python -m oaknational.python_repo_template.devtools <command>` for
the repo's managed developer command surface so the virtual environment and
source-checkout tooling stay aligned.

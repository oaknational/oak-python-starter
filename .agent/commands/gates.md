# Quality Gates

Run the quality gates from the repo root. Fix any and all issues that arise, regardless of location or cause.

After each fix, **restart the quality gate sequence from the beginning**. This prevents regressions to earlier gates from later fixes.

## Canonical Command

```bash
uv run python -m oaknational.python_repo_template.devtools check-ci
```

For the local fix-and-verify aggregate, use:

```bash
uv run python -m oaknational.python_repo_template.devtools check
```

The repo also exposes:

```bash
uv run python -m oaknational.python_repo_template.devtools clean
uv run python -m oaknational.python_repo_template.devtools build
uv run python -m oaknational.python_repo_template.devtools dev
uv run deptry .
```

Dependency hygiene runs through `uv run deptry .` and is included in both
aggregate gate commands before `repo-audit`. It proves declared dependency
hygiene, not vulnerability scanning.

## Rules

1. **All issues are blocking** — There is no such thing as "someone else's problem"
2. **Fix, don't disable** — Never use `# noqa`, `# type: ignore`, or similar escapes
3. **Restart on fix** — After fixing any issue, restart the sequence
4. **No skipping** — Every gate must pass before proceeding to the next

The non-mutating aggregate includes both the dependency-hygiene pass and an
installed-wheel smoke check in its build probe so drift and packaging failures
surface before closeout.

## Success Criteria

All gates pass without:

- Disabled checks
- Skipped tests
- Type ignore comments
- Suppressed errors

When complete, confirm: "All quality gates pass."

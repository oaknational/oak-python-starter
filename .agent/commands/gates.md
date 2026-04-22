# Quality Gates

Run the quality gates from the repo root. Fix any and all issues that arise, regardless of location or cause.

After each fix, **restart the quality gate sequence from the beginning**. This prevents regressions to earlier gates from later fixes.

## Canonical Command

```bash
uv run check
```

## Rules

1. **All issues are blocking** — There is no such thing as "someone else's problem"
2. **Fix, don't disable** — Never use `# noqa`, `# type: ignore`, or similar escapes
3. **Restart on fix** — After fixing any issue, restart the sequence
4. **No skipping** — Every gate must pass before proceeding to the next

## Success Criteria

All gates pass without:

- Disabled checks
- Skipped tests
- Type ignore comments
- Suppressed errors

When complete, confirm: "All quality gates pass."

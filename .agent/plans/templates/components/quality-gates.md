# Component: Quality Gates

Use the canonical `uv run ...` gate surface.

## After each meaningful task

Run the smallest truthful set that proves the task:

```bash
uv run typecheck
uv run lint
uv run test
```

## After each phase or before closure

Run the full non-mutating aggregate:

```bash
uv run check-ci
```

If you intentionally want the local fix-and-verify sweep, run:

```bash
uv run check
```

Every gate failure is blocking. Do not narrow the gate to dodge the failure.

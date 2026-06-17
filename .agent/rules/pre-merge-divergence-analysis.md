# Pre-Merge Divergence Analysis

Use this when two branches have diverged enough that ordinary text conflict
resolution is likely to miss behavioural breakage.

When merging branches that have diverged significantly:

1. inspect deleted or moved files, not just conflicted files
2. check for signature or contract drift in untouched callers
3. check for ADR or plan numbering collisions
4. run `uv run python -m oaknational.python_repo_template.devtools typecheck`
   immediately after conflict resolution

Standard text-level conflict resolution misses:

- **Deleted-file import cascades** — a file auto-merges from your branch but
  imports a module the other branch deleted
- **Signature mismatches in auto-merged files** — the other branch changed a
  function signature in a file you didn't touch, but your callers use the old
  signature
- **Required parameter gaps** — your branch adds a required parameter to a
  shared interface, breaking the other branch's new test files that auto-merge
  cleanly
- **Numbering collisions** — both branches create an ADR or plan with the
  same number but different content and different filenames

Always run
`uv run python -m oaknational.python_repo_template.devtools typecheck`
immediately after resolving text conflicts — this catches the silent breaks
that Git cannot detect.

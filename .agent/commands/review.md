# Review

Perform a review of the work described by the user or inferred from context.

## Scope

Determine the review scope from the user's request:

- **Post-change review** (default): Review recent changes only.
  Check `git diff` and `git status` to identify what changed.
- **Broad review**: Review a specific area, module, or subsystem.
  The user will specify the scope.
- **Full codebase review**: Only when explicitly requested. This
  is expensive — confirm scope with the user before proceeding.

## Step 1: Quality Gates

Run the full quality gate sequence from repo root. If any gate
fails, report it as a critical finding.

```bash
uv run check
```

## Step 2: Triage Specialists

Answer these questions to identify which specialists
are needed (from the invoke-code-reviewers directive):

1. Does this touch strategy logic, risk parameters, or position sizing? -> `architecture-reviewer`
2. Does this change module boundaries or public APIs? -> `architecture-reviewer`
3. Does this add or modify tests? -> `test-reviewer`
4. Does this change tooling configs or quality gates? -> `config-reviewer`
5. Does this touch credentials, API keys, or external auth? -> `security-reviewer`

Always invoke `code-reviewer`. Only invoke other specialists
when the triage questions indicate they are relevant.

## Step 3: Invoke Specialists

Invoke each specialist with `readonly: true`. Give each
reviewer specific context about what changed and what to focus on.

Do NOT invoke specialists that are not relevant. Report
which were invoked and which were skipped (with rationale).

## Step 4: Consolidate and Report

Produce a report with:

- **Summary**: Overall assessment (PASS / PASS WITH SUGGESTIONS / ISSUES FOUND)
- **Quality Gate Status**: Which gates passed/failed
- **Specialist Findings**: Key findings from each invoked reviewer
- **Critical Issues**: Must fix (blocking)
- **Improvements**: Should fix (non-blocking)
- **Positive Observations**: What is working well
- **Specialists Invoked**: Which reviewers ran and which were N/A
- **Follow-up Actions**: Concrete next steps if issues found

## After the Review

If the review identified issues that were fixed, re-run
affected quality gates to confirm the fixes.

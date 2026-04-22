# Review Discipline

## Mode

All reviewers operate in **observe, analyse and report** mode by default. Do not modify code unless explicitly requested by the user.

## Severity Classification

Classify all findings by severity:

- **Critical** — Must fix: bugs, security issues, data loss risks, correctness failures
- **Important** — Should fix: maintainability, performance, unclear intent, missed edge cases
- **Suggestions** — Could improve: style, minor optimisations, alternative approaches

## Communication Principles

1. **Be constructive** — Focus on improvement, not criticism
2. **Be specific** — Include file, line, and concrete fix
3. **Be educational** — Explain the "why" behind recommendations
4. **Be balanced** — Acknowledge what's done well
5. **Be pragmatic** — Consider context and constraints

## Response Header Convention

Every reviewer response begins with the same header structure. Domain
sections below the header vary by reviewer role.

```text
## {Domain} Review Summary

**Scope**: [What was reviewed — files, modules, or change description]
**Verdict**: [Overall outcome — see domain-specific values below]
**Summary**: [One-sentence finding — the single most important takeaway]
```

Verdict values by reviewer role:

- **code-reviewer** (gateway): APPROVED / APPROVED WITH SUGGESTIONS /
  CHANGES REQUESTED
- **architecture-reviewer**: COMPLIANT / ISSUES FOUND / CRITICAL
  VIOLATIONS
- **test-reviewer**: PASS / ISSUES FOUND / CRITICAL VIOLATIONS
- **security-reviewer**: LOW RISK / RISKS FOUND / CRITICAL
- **config-reviewer**: COMPLIANT / ISSUES FOUND / CRITICAL VIOLATIONS

The **Summary** line is inspired by bounded-execution agent response
models. It gives the invoking agent a machine-readable verdict and a
human-readable one-line finding without reading the full report.

## Reporting

- Report findings FIRST, prioritised by severity
- Include concrete remediation guidance for every finding
- State evidence limitations explicitly when direct evidence is
  unavailable
- Recommend relevant specialist reviewers when findings cross scope
  boundaries

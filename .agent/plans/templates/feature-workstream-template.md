---
name: "[Plan Title]"
overview: "[One-line scope description]"
todos:
  - id: red
    content: "RED: write or refine the failing proof."
    status: pending
  - id: green
    content: "GREEN: implement the minimal change."
    status: pending
  - id: refactor
    content: "REFACTOR: tighten docs, naming, and structure."
    status: pending
  - id: gates
    content: "Run the canonical quality gates."
    status: pending
  - id: review
    content: "Run the relevant reviewer pass."
    status: pending
---

# [Plan Title]

**Last Updated**: [YYYY-MM-DD]  
**Status**: 🟡 PLANNING  
**Scope**: [One-line scope description]

## End Goal

[What changes for the user, operator, or repo when this plan lands?]

## Mechanism

[Why these means actually deliver that end.]

## Context

[Current situation, constraints, and relevant evidence.]

## Existing Capabilities

[What already exists that this plan should build on instead of duplicating.]

## Non-Goals

- [What this plan is explicitly not doing]

## Build-vs-Buy Attestation

Keep this section when the plan builds a reusable capability, wrapper, or
vendor-facing integration. Remove it if not applicable.

- **What was searched**: [registries, codebase, vendor docs]
- **What was found**: [candidate options]
- **Why this shape was chosen**: [concrete decision tension]

Plan-time review should include the architecture reviewer and any installed
specialist best suited to challenge the build-vs-buy framing.

## Reviewer Scheduling

- **Plan-time**: challenge the framing and scope.
- **Mid-cycle**: challenge the implementation and proofs.
- **Close**: challenge coherence, docs, and quality.

Only name reviewers the repo actually has.

## WS1 — RED

- failing proof files:
  - `[path/to/test_file.py]`
- acceptance criteria:
  - the new proof fails for the expected reason

## WS2 — GREEN

- implementation files:
  - `[path/to/module.py]`
- deterministic validation:
  - `[command]`

## WS3 — REFACTOR

- update docstrings, README content, ADRs, or practice docs as needed
- keep the proof green

## Quality Gates

```bash
uv run check-ci
```

## Risk Assessment

| Risk | Mitigation |
| --- | --- |
| [Risk] | [Mitigation] |

## Documentation Propagation

- `.agent/practice-core/practice.md`: [update or no-change rationale]
- `.agent/practice-index.md`: [update or no-change rationale]
- additional ADRs / docs / READMEs: [update or no-change rationale]

## Done When

1. the end goal is demonstrably met
2. the named gates pass
3. review findings are resolved or explicitly routed
4. durable docs are updated or explicitly unchanged with rationale

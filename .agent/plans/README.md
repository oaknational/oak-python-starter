# Plans

Strategic and tactical planning artefacts for this repository.

**High-Level Coordination**: [high-level-plan.md](high-level-plan.md)  
**Completed Plans**: [completed-plans.md](completed-plans.md)  
**Templates**: [templates/](templates/)

## Plan Collections

| Collection | Purpose | Status |
| --- | --- | --- |
| [agentic-engineering/](agentic-engineering/README.md) | Practice infrastructure, commands, rules, reviewers, adapters | 🔄 Active baseline |
| [runtime-infrastructure/](runtime-infrastructure/README.md) | Validation boundaries, audits, reports, and supporting runtime surfaces | 🔄 Active baseline |
| [demo-application/](demo-application/README.md) | Seeded `activity-report` example and bounded follow-on work | 🔄 Active baseline |
| [templates/](templates/README.md) | Reusable planning templates and components | 📚 Reference |

## Collection structure

Each collection follows the same lifecycle-oriented shape, even when some
directories are intentionally light:

```text
.agent/plans/{collection-name}/
├── README.md
├── roadmap.md
├── documentation-sync-log.md
├── active/README.md
├── current/README.md
├── future/README.md
└── archive/
```

## Status indicators

| Status | Meaning |
| --- | --- |
| 📋 Planned | Not started |
| 🔄 Active | Live collection or current baseline |
| 🟡 Planning | Shape still being worked out |
| ⏸ Deferred | Intentionally not active now |
| ✅ Complete | Landed and archived |
| 📚 Reference | Navigation or template surface |

## Plan triage protocol

Use this when consolidating or modernising plan surfaces:

1. Is the work still relevant to the repo's current state?
2. Is the plan stale in paths, assumptions, or acceptance criteria?
3. Is durable documentation trapped inside the plan?
4. Does the plan belong in `active/`, `current/`, `future/`, or `archive/`?

Before archiving a plan, home any durable substance into ADRs, PDRs, READMEs,
or other permanent surfaces.

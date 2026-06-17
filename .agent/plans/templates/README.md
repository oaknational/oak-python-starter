# Plan Templates and Components

Reusable scaffolds for writing high-quality plans in this repo.

## Read first

Before using any template, re-read:

1. `.agent/directives/principles.md`
2. `.agent/directives/testing-strategy.md`
3. `.agent/directives/orientation.md`
4. `.agent/directives/data-boundary-doctrine.md`

## Templates

| Template | Use when |
| --- | --- |
| [feature-workstream-template.md](feature-workstream-template.md) | new capability or multi-phase delivery work |
| [quality-fix-plan-template.md](quality-fix-plan-template.md) | bug fixing, quality repair, or refactoring |
| [active-atomic-implementation-plan-template.md](active-atomic-implementation-plan-template.md) | a bounded execution tranche inside an active collection |
| [adoption-rollout-plan-template.md](adoption-rollout-plan-template.md) | rolling out a new rule, process, or capability across existing surfaces |
| [collection-readme-template.md](collection-readme-template.md) | creating a new collection hub |
| [collection-roadmap-template.md](collection-roadmap-template.md) | creating a collection roadmap |
| [active-plan-index-template.md](active-plan-index-template.md) | `active/README.md` indexes |
| [current-plan-index-template.md](current-plan-index-template.md) | `current/README.md` indexes |
| [future-plan-index-template.md](future-plan-index-template.md) | `future/README.md` indexes |

## Components

| Component | Purpose |
| --- | --- |
| [quality-gates.md](components/quality-gates.md) | canonical gate discipline |
| [tdd-phases.md](components/tdd-phases.md) | RED/GREEN/REFACTOR structure |
| [foundation-alignment.md](components/foundation-alignment.md) | per-phase doctrine check |
| [risk-assessment.md](components/risk-assessment.md) | risk and mitigation table |
| [adversarial-review.md](components/adversarial-review.md) | review-phase structure |
| [evidence-and-claims.md](components/evidence-and-claims.md) | evidence expectations for non-trivial claims |
| [documentation-propagation.md](components/documentation-propagation.md) | permanent-doc update discipline |
| [session-discipline.md](components/session-discipline.md) | multi-session execution discipline |

## Lifecycle

```text
active/   -> in progress now
current/  -> next-up and ready
future/   -> later or deferred
archive/  -> completed or superseded
```

Before archiving, home durable substance into permanent documentation and
update [completed-plans.md](../completed-plans.md).

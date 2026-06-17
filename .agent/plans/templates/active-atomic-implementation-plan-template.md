---
name: "[Phase Name] - Atomic Execution"
overview: "[One-line execution summary]"
todos:
  - id: preflight
    content: "Re-ground on the phase and baseline."
    status: pending
  - id: execution
    content: "Deliver the bounded implementation tasks."
    status: pending
  - id: verification
    content: "Capture evidence and run closure checks."
    status: pending
---

# [Phase Name] - Atomic Execution

## Source Strategy

- [roadmap.md](../roadmap.md)
- [strategic source plan or note](../[source-plan].md)

## Preflight

1. re-read the relevant foundation documents
2. confirm the current phase scope and acceptance criteria
3. capture the baseline command output you will compare against

## Atomic Tasks

### Task 1

- output: [artefact]
- validation: `[command]`

### Task 2

- output: [artefact]
- validation: `[command]`

## Blocked protocol

If a validation command fails unexpectedly:

1. stop
2. document the command and actual result
3. surface the mismatch before guessing a workaround

## Documentation synchronisation

- update `documentation-sync-log.md`
- update permanent docs or record no-change rationale

## Done When

1. every task is complete
2. the named validation commands pass
3. documentation sync is updated
4. consolidation has been considered

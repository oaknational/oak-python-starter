# Project Context

This repo is a reusable Python template with one seeded demo surface.

## System Model

```text
input files
  -> validation and canonical shaping
  -> cached artefacts and summaries
  -> user-facing CLI output and charts
  -> repo audits and cross-platform agent support
```

## Work Strands

- **agentic engineering** — how work is guided and reviewed
- **runtime infrastructure** — validation, persistence, reporting, and audits
- **demo application** — the `activity-report` example

## Boundaries

- Validation happens at the data boundary.
- The demo app should stay small and replaceable.
- Repo identity belongs to the infrastructure, not the seeded example.

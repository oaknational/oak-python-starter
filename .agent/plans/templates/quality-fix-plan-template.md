---
name: "[Plan Title]"
overview: "[One-line scope description]"
todos:
  - id: foundation
    content: "Verify assumptions and reproduce the problem."
    status: pending
  - id: resolution
    content: "Implement and validate the fix."
    status: pending
  - id: hardening
    content: "Run gates, review, and documentation propagation."
    status: pending
---

# [Plan Title]

**Last Updated**: [YYYY-MM-DD]  
**Status**: 🟡 PLANNING  
**Scope**: [One-line description]

## End Goal

[What failure or drift disappears when this plan completes?]

## Context

[What is happening now, how it manifests, and what evidence proves it.]

## Root Cause

[What the real underlying problem is.]

## Existing Capabilities

[What current code, patterns, or docs already help.]

## Strategy

[Why this fix shape is proportionate and simpler than the alternatives.]

## Non-Goals

- [Non-goal]

## Phase 0 — Verify assumptions

- reproduce the issue
- prove the current failure
- record the exact validation command

## Phase 1 — Implement and validate

- land the smallest truthful fix
- keep the validation command attached to the change

## Phase 2 — Hardening

- run `uv run check-ci`
- run the relevant reviewers
- update durable docs or record no-change rationale

## Risk Assessment

| Risk | Mitigation |
| --- | --- |
| [Risk] | [Mitigation] |

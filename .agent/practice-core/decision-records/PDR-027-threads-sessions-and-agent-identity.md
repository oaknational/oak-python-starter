# PDR-027: Threads, Sessions, and Agent Identity

- Status: Accepted
- Date: 2026-04-23

## Context

Multi-session work needs a named continuity unit. Without one, "what is live
right now?" becomes a memory exercise. Multi-agent work adds a second problem:
the repo needs to know which identity touched which thread and when.

## Decision

The continuity unit is the thread. Each active thread gets one
`*.next-session.md` record in `.agent/memory/operational/threads/`.

Thread records carry additive identity rows with:

- `agent_name`
- `platform`
- `model`
- `session_id_prefix`
- `role`
- `first_session`
- `last_session`

If the same identity returns, update `last_session`. If a new identity joins,
append a new row.

## Consequences

- continuity becomes inspectable rather than implicit
- thread records remain the place to resume work safely
- the host repo should operationalise session-open registration and
  session-close refresh

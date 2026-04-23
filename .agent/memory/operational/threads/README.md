# Threads

A thread is a named stream of work that persists across sessions. Threads are
the continuity unit.

Each active thread has one `*.next-session.md` file in this directory. That
file records:

- participating identities,
- the next landing target for that thread,
- current state and blockers,
- and the next safe step.

## Identity Schema

Each thread record uses these fields:

- `agent_name`
- `platform`
- `model`
- `session_id_prefix`
- `role`
- `first_session`
- `last_session`

Same identity on a later session updates `last_session`; a new identity adds a
new row.

## Session Start

When joining a thread:

1. Read [`../repo-continuity.md`](../repo-continuity.md).
2. Read the thread's next-session record.
3. Update or add the identity row before making other edits.

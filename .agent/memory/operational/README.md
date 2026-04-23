# Operational Memory

Operational memory is the continuity layer. It exists so a later session can
recover orientation without re-deriving everything from plans and chat history.

## Surfaces

| Surface | Purpose | Authority |
| --- | --- | --- |
| [`repo-continuity.md`](repo-continuity.md) | Repo-level continuity contract | Canonical for continuity state |
| [`threads/`](threads/README.md) | Per-thread next-session records | Canonical for thread-level continuity |
| [`tracks/`](tracks/README.md) | Tactical single-writer coordination cards | Tactical only |
| [`workstreams/`](workstreams/README.md) | Retired workstream layer | Historical / doctrinal only |
| [`diagnostics/`](diagnostics/README.md) | Lightweight operational evidence | Supporting only |

## Relationship to Other Memory

- **Active memory** captures and distils learnings.
- **Operational memory** preserves continuity and next-step state.
- **Executive memory** holds stable catalogues and contracts.

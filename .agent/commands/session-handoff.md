# Session Handoff

This is the lightweight end-of-session workflow. It is session-scoped and
should be cheap enough to run every time.

## Steps

1. **Record what landed.** State the session outcome plainly. If the target did
   not land, record the blocker and the next safe retry.
2. **Refresh repo continuity.** Update
   `.agent/memory/operational/repo-continuity.md`.
3. **Refresh touched thread records.** Update every moved
   `.agent/memory/operational/threads/*.next-session.md` file and its identity
   row.
4. **Resolve tactical track cards.** Delete resolved cards and promote any
   surviving signal into the right continuity or memory surface.
5. **Sync active plans if needed.** If the next step or status changed, update
   the relevant active/current plan surface now.
6. **Capture fresh learning.** Add surprises, corrections, and notable lessons
   to `.agent/memory/active/napkin.md`. Tag executive-memory observations with
   `Source plane: executive`.
7. **Capture experience when it matters.** If the session changed
   understanding, working texture, or collaboration meaningfully, add a brief
   session-scoped note under `.agent/experience/`.
8. **Hard gate.** Do not close until repo continuity, touched thread records,
   and active plans agree about what is active and what should happen next.
9. **Decide whether consolidation is due.** Run `consolidate-docs` when:
   - incoming Practice material needs integration
   - durable docs or plans need homing
   - memory, research, reference, analysis, reports, or experience need a
     deeper sweep
   - continuity or executive surfaces need repair beyond a lightweight close

## Boundary

`session-handoff` is the capture edge.
`consolidate-docs` is the graduation edge.

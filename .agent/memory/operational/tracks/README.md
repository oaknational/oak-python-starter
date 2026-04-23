# Tactical Track Cards

This directory holds short-horizon, single-writer coordination cards.

Track cards are optional. Use them when a thread needs a small tactical surface
for a focused blocker-resolution or execution slice that should not bloat the
thread record itself.

Each card should name:

- the owning thread,
- the sole writer,
- the claimed territory,
- the current task,
- any blocker,
- a short handoff note,
- and an expiry date.

Track cards are tactical only. They never own scope or sequencing over plans or
thread records.

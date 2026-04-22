---
name: Shared Capability Versus Lane Split
domain: planning
proven_by: three-strand reorganisation of agentic engineering, research infrastructure, and strategy research (2026-03-22)
prevents: shared platform work being mistaken for optional support to a single lane, mixed queues telling contradictory stories, reusable capability work staying buried in lane-specific plans
---

# Shared Capability Versus Lane Split

## Principle

When a repo contains both shared capability work and specific experiment or
product lanes, separate them into different plan strands. Shared capability
work is not "support" for whichever lane surfaced it first; it needs its own
queue, status, and archive.

## Pattern

1. Put shared capability tranches in their own strand or collection.
2. Keep concrete experiment, feature, or strategy-lane plans in a separate
   strand.
3. Maintain one cross-strand roadmap above both so tactical work still ladders
   into a common direction.
4. If a plan outgrows the lane that introduced it, move the executable plan
   into the shared-capability strand and leave only the lane verdict or
   hand-off in the lane collection.
5. Make the current READMEs in both strands tell one consistent story about
   the repo-level next-up.
6. Keep completed lane tranches archived with the lane history even when the
   next honest question has moved into shared capability work.

## Anti-pattern

- Leaving shared infrastructure, diagnostics, inference, or realism work under
  a single experiment queue after it has become the repo's actual next
  question
- Describing shared platform work as mere "support" for a lane once it has
  become the durable prerequisite for trustworthy progress
- Letting one strand advertise the real next-up while another strand still
  implies a different priority
- Keeping a plan in its original lane directory after its purpose has become a
  shared capability concern

## When to Apply

Use this when repeated work shows that the blocker or next question is no
longer local to one feature family, symbol, or strategy lane, and the repo
needs shared capability work to progress honestly.

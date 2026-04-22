---
name: Unknown Until Validated
use_this_when: a function returns external or runtime-shaped data that will be validated later
category: validation
proven_in: planned market-data and research boundary hardening
proven_date: 2026-03-19
barrier:
  broadly_applicable: true
  proven_by_implementation: true
  prevents_recurring_mistake: Claiming a precise type before validation has actually happened
  stable: true
---

# Unknown Until Validated

If the producer cannot prove the shape, it should return `unknown` rather than
pretend to know more. The validation boundary is where the type narrows.

Use this for API payloads, file loads, dynamic dispatch results, and any other
data whose structure depends on runtime conditions.

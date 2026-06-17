---
name: Explicit Missing Resource State
use_this_when: a missing upstream resource could be confused with a valid empty, zero, or false value
category: architecture
proven_in: research-platform boundary doctrine
proven_date: 2026-03-19
barrier:
  broadly_applicable: true
  proven_by_implementation: true
  prevents_recurring_mistake: Fail-open behaviour caused by collapsing missing state into normal values
  stable: true
---

# Explicit Missing Resource State

Keep "missing" explicit at the boundary. Either:

- return a typed present/missing model, or
- fail fast with a specific error.

Do not coerce missing resources into normal values such as `0`, `False`, or an
empty collection when that would hide a configuration or topology failure.

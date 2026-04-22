---
name: Interface Segregation for Test Fakes
use_this_when: test doubles would otherwise need irrelevant fields or broad assertions to satisfy a large dependency contract
category: testing
proven_in: python strategy and adapter boundary planning
proven_date: 2026-03-19
barrier:
  broadly_applicable: true
  proven_by_implementation: true
  prevents_recurring_mistake: Assertion pressure and brittle tests caused by oversized dependency contracts
  stable: true
---

# Interface Segregation for Test Fakes

Accept the smallest interface the code under test actually needs. Let tests
fake that smaller interface directly instead of faking an oversized production
type with irrelevant fields.

This keeps tests honest, reduces fixture noise, and preserves type pressure in
the right place: the production boundary.

# TDD for Refactoring

For refactoring that changes interfaces or signatures, update the proof surface
first. The failing tests or type checks are the RED phase for the refactor.

Run the relevant test and type gates before and after. Existing proofs are the
safety net; they should tighten the refactor, not be worked around.

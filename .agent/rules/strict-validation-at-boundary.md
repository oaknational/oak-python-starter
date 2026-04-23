# Strict Validation at External Boundaries

Operationalises `.agent/directives/data-boundary-doctrine.md`.

When data arrives from an external boundary, treat it as untrusted until it has
been validated to the exact expected shape. Use the validated result from that
point forward. Do not widen the boundary type to avoid doing the validation.

If the shape is genuinely open-ended, that is a design problem to solve, not a
reason to erase the boundary.

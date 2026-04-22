# Code Patterns

Reusable patterns proven in real repo work. These are more concrete than
rules, but more portable than source code.

## Barrier to Entry

A pattern belongs here only when it is:

- broadly applicable or clearly reusable in this repo,
- proven by implementation,
- protective against a recurring mistake,
- stable enough to teach without immediate churn.

## Pattern Index

- [component-composition-pattern.md](component-composition-pattern.md) —
  extract shared reviewer behaviour into components once multiple templates
  repeat the same universal content.
- [thin-adapter-pattern.md](thin-adapter-pattern.md) — keep substantive
  content in `.agent/` and make platform wrappers delegate only.
- [agentic-surface-separation.md](agentic-surface-separation.md) — separate
  always-on policy, on-demand skills, explicit commands, and isolated
  subagents so cross-platform agent infrastructure keeps the right semantics.
- [drift-detection-validation.md](drift-detection-validation.md) — add a
  compensating validation step when a manually maintained list cannot be
  derived from its canonical source.
- [chatgpt-report-normalisation.md](chatgpt-report-normalisation.md) —
  rebuild LLM-exported reports from the strongest surviving source layer, then
  verify unstable claims against primary sources before promoting them to
  canonical markdown.
- [interface-segregation-for-test-fakes.md](interface-segregation-for-test-fakes.md) —
  narrow dependencies so test fakes match the real contract without assertion
  pressure.
- [injected-storage-boundary-for-tests.md](injected-storage-boundary-for-tests.md) —
  keep in-process tests off the filesystem by injecting tiny storage seams and
  CLI runners.
- [observable-entrypoint-behaviour-tests.md](observable-entrypoint-behaviour-tests.md) —
  prove thin entry surfaces through visible behaviour and keep delegate wiring
  out of tests.
- [unknown-until-validated.md](unknown-until-validated.md) — keep unvalidated
  external data typed as `unknown` until the validation boundary.
- [explicit-missing-resource-state.md](explicit-missing-resource-state.md) —
  model missing upstream resources explicitly instead of collapsing them into
  normal values.
- [operational-support-matrix.md](operational-support-matrix.md) — keep a
  small operational matrix for supported and unsupported cross-platform agent
  surfaces, and let research notes stay rationale-only.
- [capability-ladder-roadmap.md](capability-ladder-roadmap.md) — use a
  top-level capability ladder to connect a narrow current queue to a broader
  researched end state without pretending all researched possibilities are
  committed build work.
- [shared-capability-versus-lane-split.md](shared-capability-versus-lane-split.md) —
  separate shared capability work from concrete experiment or product lanes so
  current queues and archives do not tell contradictory stories.
- [current-plan-promotion.md](current-plan-promotion.md) — when a review
  settles the true next tranche, promote it into `current/` and add the cold-
  start scaffolding needed for the next session.
- [readme-as-index.md](readme-as-index.md) — keep plan-directory READMEs as
  pure indexes so tranche promotions and archives are table-row edits, not
  content rewrites.

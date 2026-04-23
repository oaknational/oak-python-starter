# Sub-Agents Must Not Edit Foundational Practice Surfaces

Scoped sub-agents must not create, delete, rename, or edit foundational
Practice files in `.agent/practice-core/`, `.agent/directives/`, `.agent/rules/`,
or the platform rule adapters.

These files need cross-file and cross-session judgement. A scoped worker can
report a finding about them, but the coordinating agent or the user should
apply the change.

See `.agent/practice-core/decision-records/PDR-003-sub-agent-protection-of-foundational-practice-docs.md`.

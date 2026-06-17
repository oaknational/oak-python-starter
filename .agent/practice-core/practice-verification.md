---
provenance: provenance.yml
fitness_line_count: 220
fitness_char_count: 17000
fitness_line_length: 100
split_strategy: "Break out specialised audits when the checklist grows"
---

# Practice Verification

This file verifies that the Practice is installed as a working system rather
than a loose collection of markdown files.

## Bootstrap Checklist

After hydration or structural Practice work, confirm:

1. `.agent/practice-core/` contains the trinity, verification, entry points,
   changelog, provenance, `decision-records/`, `patterns/`, and `incoming/`.
2. `.agent/practice-index.md` exists and all linked paths resolve.
3. `AGENT.md` points to `.agent/practice-core/index.md`.
4. all root entry points point to `.agent/directives/AGENT.md`.
5. all command and skill adapters point to real canonical files.
6. the three-plane memory estate exists.
7. the continuity host exists and the session workflows point to it.
8. the Practice Box exists and is checked by session-start or consolidation
   workflows.
9. orientation, research, analysis, reports, reference, and experience tiers
   all exist and are linked truthfully.
10. durable design-space exploration has a home in `docs/explorations/`.
11. planning includes a strategic index, completed-plan index, and reusable
   templates.
12. durable Practice governance has a portable home in `decision-records/`.
13. portable general patterns have a portable home in `patterns/`.
14. repo validation includes a Practice-aware audit.
15. the quality-gate API is coherent: `clean`, `build`, `dev`, `format`,
    `format-fix`, `lint`, `lint-fix`, `fix`, `check`, and `check-ci` exist
    with truthful semantics.
16. the repo checks pass.

## Vital Integration Surfaces

The Practice needs surfaces in both directions.

### Core to Repo

- entry-point chain
- local bridge
- session-start skills
- command adapters
- rule adapters

### Repo to Core

- napkin capture surface
- distilled refinement surface
- consolidation workflow
- Practice Box
- optional ephemeral exchange context

### Cross-Cutting

- canonical-first artefact architecture
- explicit platform support contract where relevant
- continuity surfaces
- validators and runtime checks

## Minimum Operational Estate

The minimum estate for this template is:

- `.agent/directives/AGENT.md`
- `.agent/practice-index.md`
- `.agent/memory/README.md`
- `.agent/memory/active/napkin.md`
- `.agent/memory/active/distilled.md`
- `.agent/memory/operational/repo-continuity.md`
- `.agent/memory/operational/threads/README.md`
- `.agent/memory/executive/README.md`
- `.agent/commands/session-handoff.md`
- `.agent/commands/consolidate-docs.md`
- `.agent/commands/ephemeral-to-permanent-homing.md`
- `.agent/skills/start-right-quick/SKILL.md`
- `.agent/skills/napkin/SKILL.md`
- `.agent/skills/commit/SKILL.md`
- `.agent/skills/tsdoc/SKILL.md`
- `.agent/directives/orientation.md`
- `.agent/research/README.md`
- `.agent/analysis/README.md`
- `.agent/reports/README.md`
- `.agent/reference/README.md`
- `.agent/experience/README.md`
- `docs/explorations/README.md`
- `.agent/plans/high-level-plan.md`
- `.agent/plans/completed-plans.md`
- `.agent/plans/templates/README.md`
- `docs/dev-tooling.md`
- `tools/repo_audit.py`

If any workflow points at a missing surface, the installation is incomplete.

## Health Check

Run these intent-level checks:

1. metacognition still produces reflection rather than a task summary
2. rules do not turn hard expectations into vague suggestions
3. memory paths in skills, commands, and docs match the actual filesystem
4. continuity fields in `repo-continuity.md` and thread records are coherent
5. the Practice Index does not advertise absent surfaces
6. the incoming box is empty after integration work lands
7. planning templates and live collection surfaces agree on the lifecycle model

## Claimed / Installed / Activated

For every surface the repo claims to have, ask three questions:

- Claimed: do AGENT, the Practice Index, and the Core describe it?
- Installed: does the file or directory exist?
- Activated: does some workflow, adapter, or runtime check actually use it?

Silent failures usually happen in the gap between installed and activated.

## Acceptance

The Practice integration is healthy when:

- the Core, bridge, memory estate, and continuity estate all exist
- the document tiers and exploration tier exist and are routed truthfully
- the planning architecture is installed as a real system
- docs and commands agree on the same paths and concepts
- adapters are thin and complete
- incoming material has been integrated and cleared
- the repo checks pass on a fresh run

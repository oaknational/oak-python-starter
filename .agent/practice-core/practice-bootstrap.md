---
provenance: provenance.yml
fitness_line_count: 260
fitness_char_count: 20000
fitness_line_length: 100
split_strategy: "Move deep per-surface detail into reference docs or PDRs"
---

# Practice Bootstrap

This file explains how to build or restructure a host repo so the Practice is
real rather than decorative.

## Start With the Host Repo

Before creating or editing Practice artefacts, survey the repo:

- language and package manager
- build, test, lint, and format tooling
- existing quality standards
- current agent surfaces, if any
- current memory or continuity surfaces, if any

Preserve anything that already meets or exceeds the Practice. The Practice is
an enabling layer, not a reset button.

## Canonical-First Artefact Model

Substantive content lives in `.agent/`. Platform-specific directories contain
thin adapters only.

| Type | Canonical home | Adapter homes |
| --- | --- | --- |
| Directives | `.agent/directives/` | none |
| Rules | `.agent/rules/` | `.cursor/rules/`, `.claude/rules/`, others as supported |
| Commands | `.agent/commands/` | `.cursor/commands/`, `.claude/commands/`, `.gemini/commands/`, `.agents/skills/jc-*/` |
| Skills | `.agent/skills/` | platform skill wrappers |
| Memory | `.agent/memory/` | none |
| Practice Core | `.agent/practice-core/` | none |

## Required Local Bridge

Create `.agent/practice-index.md`. It is the local bridge from the portable
Core to the host repo's live artefacts.

Minimum sections:

- Directives
- Memory
- Practice Core
- Repo Direction
- References and Tooling

Populate each with real links. Do not advertise surfaces that are not
installed.

## Entry Points

Every supported platform entry point at repo root should be a thin pointer to
`.agent/directives/AGENT.md`.

Example:

```markdown
# AGENTS.md

Read `.agent/directives/AGENT.md` and follow it.
```

## Commands

The canonical commands live in `.agent/commands/`.

| Command | Purpose |
| --- | --- |
| `start-right-quick` | session entry and grounding |
| `start-right-thorough` | deeper session grounding |
| `go` | mid-session re-grounding |
| `gates` | run the quality gates |
| `review` | run the review workflow |
| `plan` | create or refine plans |
| `commit` | intentional commit workflow |
| `session-handoff` | session closeout and continuity refresh |
| `consolidate-docs` | graduation, integration, and drift tightening |
| `ephemeral-to-permanent-homing` | shared homing method for ephemeral content |

The platform wrappers for commands must be thin and complete.

## Skills

At minimum, the host Practice should provide:

- `start-right-quick`
- `start-right-thorough`
- `go`
- `napkin`
- `code-patterns`
- `commit`
- `tsdoc`

These must point at real surfaces in the repo.

## Continuity Contract

The host repo needs an explicit continuity surface. In this template, the
contract is split across:

- `.agent/memory/operational/repo-continuity.md`
- `.agent/memory/operational/threads/*.next-session.md`
- `.agent/memory/operational/tracks/`

If a workflow references continuity, that surface must exist on a fresh
checkout.

The minimum continuity fields are:

- active threads
- branch-primary thread pointer
- repo-wide invariants or non-goals
- next safe step
- deep consolidation status

Keep ordinary continuity and deep convergence separate:

- `session-handoff` refreshes continuity every session
- `consolidate-docs` does the slower graduation and integration work

## Memory Bootstrap

The minimum memory estate is:

- `.agent/memory/README.md`
- `.agent/memory/active/napkin.md`
- `.agent/memory/active/distilled.md`
- `.agent/memory/active/patterns/README.md`
- `.agent/memory/operational/repo-continuity.md`
- `.agent/memory/operational/threads/README.md`
- `.agent/memory/executive/README.md`

Use the three-plane split:

- `active/` for the learning loop
- `operational/` for continuity
- `executive/` for stable catalogues

## Knowledge Tiers

The host repo should install explicit document tiers:

- `docs/explorations/` for durable option-weighing
- `.agent/research/` for exploratory synthesis
- `.agent/analysis/` for consolidated investigations
- `.agent/reports/` for formal promoted reports
- `.agent/reference/` for curated evergreen library material
- `.agent/experience/` for session-scoped reflection

## Planning Architecture

The host repo should install the full planning spine:

- `.agent/plans/high-level-plan.md`
- `.agent/plans/completed-plans.md`
- collection hubs with `roadmap.md`, `documentation-sync-log.md`, and
  `active/`, `current/`, `future/` indexes
- `.agent/plans/templates/` for reusable plan scaffolds

## Pattern Surfaces

Pattern knowledge has two homes:

- `.agent/memory/active/patterns/` for repo-local proven instances
- `.agent/practice-core/patterns/` for portable general patterns

Do not use `practice-context/outgoing/` as a second permanent pattern store.

## Quality Gates

The host repo should expose a stable quality-gate surface. Use the local
ecosystem's truthful entry mechanism. In this Python template that means
`uv run ...` commands, backed by canonical logic in
`src/oaknational/python_repo_template/devtools.py`.

Whatever the entry mechanism is, it must support:

- formatting checks
- linting
- type checking
- repo-state audit
- tests
- coverage

In this Python template, the canonical gate API is:

- `uv run python -m oaknational.python_repo_template.devtools clean`
- `uv run python -m oaknational.python_repo_template.devtools build`
- `uv run python -m oaknational.python_repo_template.devtools dev`
- `uv run python -m oaknational.python_repo_template.devtools format` /
  `uv run python -m oaknational.python_repo_template.devtools format-fix`
- `uv run python -m oaknational.python_repo_template.devtools lint` /
  `uv run python -m oaknational.python_repo_template.devtools lint-fix`
- `uv run python -m oaknational.python_repo_template.devtools fix`
- `uv run python -m oaknational.python_repo_template.devtools check`
- `uv run python -m oaknational.python_repo_template.devtools check-ci`

Use Python-native separators such as dashes where the host ecosystem cannot
express colon-shaped script names cleanly. Do not preserve legacy names as
aliases or compatibility layers once the canonical surface is adopted.

## Ecosystem Reference

Each leading-edge reference repo should expose a `docs/dev-tooling.md` (or a
truthful local equivalent) documenting its validated stack and canonical command
surface.

## Final Bootstrap Checks

After hydration or a structural refactor:

1. verify every linked file exists
2. verify command and skill adapters are present
3. verify the continuity host is real
4. verify the Practice Box and practice-context rules are coherent
5. run the repo checks

Use [practice-verification.md](practice-verification.md) for the full
acceptance checklist.

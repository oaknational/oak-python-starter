---
provenance: provenance.yml
fitness_line_count: 220
fitness_char_count: 18000
fitness_line_length: 100
split_strategy: "Move specialised doctrine into focused PDRs or reference docs"
---

# The Practice

The Practice is the self-reinforcing system that governs how work happens in
this repo. It is the combination of principles, structure, tooling, and
feedback loops that keeps the repo coherent as it grows.

For the host repo's live artefacts, see [practice-index.md](../practice-index.md).

## Three Layers

The Practice operates in three connected layers.

| Layer | Purpose | Examples |
| --- | --- | --- |
| Philosophy | Why the system works | First Question, metacognition, TDD, knowledge flow |
| Structure | What exists | directives, rules, commands, skills, plans, memory, ADRs |
| Tooling | How it is activated | canonical `.agent/` content, thin adapters, validators, runtime gates |

### Philosophy

The First Question is always: could it be simpler without compromising quality?

The Practice favours:

- test-first work
- pure functions and explicit boundaries
- fail-fast behaviour with clear errors
- precise types over widened ones
- stable, enforced contracts over informal convention

Metacognition and the learning loop keep the system reflective rather than
mechanical.

### Structure

The Practice is made of:

- directives in `.agent/directives/`
- rules in `.agent/rules/`
- commands in `.agent/commands/`
- skills in `.agent/skills/`
- plans in `.agent/plans/`
- memory in `.agent/memory/`
- research, analysis, reports, reference, and experience tiers
- `docs/explorations/` for durable design-space work
- Practice Core governance in `.agent/practice-core/decision-records/`
- host-repo architectural decisions in `docs/architecture-decision-records/`

### Tooling

Canonical content lives in `.agent/`. Platform-specific surfaces are thin
adapters only. The repo's entry points point back to `.agent/directives/AGENT.md`.
Runtime checks and repo-state validation make the Practice executable rather
than documentary.

## The Learning Loop

The learning loop turns session evidence into durable guidance.

| Stage | Surface | Purpose |
| --- | --- | --- |
| Capture | `.agent/memory/active/napkin.md` | record surprises, corrections, and lessons from real work |
| Refine | `.agent/memory/active/distilled.md` | keep high-signal lessons easy to reread |
| Graduate | ADRs, PDRs, READMEs, rules, permanent docs | move settled knowledge to its lasting home |
| Enforce | directives, rules, validators, quality gates | make the learning change future behaviour |

Two closeout loops keep this healthy:

- `session-handoff` is session-scoped. It refreshes continuity, records what
  landed, and captures fresh observations.
- `consolidate-docs` is thread-scoped. It graduates settled knowledge,
  extracts patterns, manages the Practice Box, and tightens drift.

The document tiers give graduated knowledge a truthful home:

- `research/` for exploratory synthesis
- `analysis/` for focused investigations and evidence
- `reports/` for formal promoted syntheses
- `reference/` for curated evergreen library material
- `experience/` for session-scoped reflection
- `docs/explorations/` for durable option-weighing before commitment

### Feedback Modes

The Practice uses multiple feedback modes at different speeds.

- Quality gates and repo audits catch drift quickly.
- Reviews catch design and behavioural issues before they spread.
- The napkin and distilled memory catch session-level learning.
- Consolidation turns repeated evidence into stable doctrine.
- Cross-plane feedback lets observations from active work repair operational
  or executive memory when those catalogues drift.

## The Three-Plane Memory Estate

The repo's memory system has three planes.

| Plane | Purpose | Typical surfaces |
| --- | --- | --- |
| `active/` | live learning loop | napkin, distilled, repo-local patterns, archive |
| `operational/` | continuity and session resume | repo continuity, thread records, track cards, diagnostics |
| `executive/` | stable organisational contracts | artefact inventory, reviewer catalogue, platform matrix |

The authority order lives in `.agent/memory/README.md`. In short:

1. plans own scope and acceptance criteria
2. `operational/repo-continuity.md` owns repo-level continuity
3. `operational/threads/*.next-session.md` own thread-level continuity
4. tactical tracks are short-horizon aids only

## Review and Quality Gates

Quality gates are always blocking. Reviews are part of the Practice, not an
optional flourish. The executive reviewer catalogue defines who to invoke and
when.

The Practice expects:

- gates to run early and again after meaningful change
- reviewers to be used for non-trivial work
- documentation to stay truthful in the same landing as code or doctrine

## Workflow

The common workflow is:

1. enter with `start-right-quick` or `start-right-thorough`
2. execute with normal work or `go`
3. validate with gates and review
4. close the session with `session-handoff`
5. run `consolidate-docs` when graduation or incoming integration is due

Planning is first-class infrastructure inside this workflow, not a nicety:

- `high-level-plan.md` is the strategic index
- collection hubs and lifecycle indexes carry execution state
- templates and components keep plan quality consistent

## Artefact Map

| Location | What lives there |
| --- | --- |
| `.agent/directives/` | stable policy and repo orientation |
| `.agent/rules/` | canonical operational reinforcements |
| `.agent/commands/` | canonical workflows |
| `.agent/skills/` | reusable skill surfaces |
| `.agent/plans/` | executable planning artefacts |
| `.agent/memory/` | active, operational, and executive memory |
| `.agent/research/`, `.agent/analysis/`, `.agent/reports/`, `.agent/reference/`, `.agent/experience/` | routed knowledge tiers |
| `.agent/practice-core/` | portable Practice Core |
| `.agent/practice-context/` | ephemeral exchange support |
| `docs/explorations/` | durable design-space explorations |
| `.cursor/`, `.claude/`, `.gemini/`, `.github/`, `.agents/` | thin adapters |
| `docs/architecture-decision-records/` | host-repo architecture decisions |

## Propagation

The portable Core propagates between repos through the Practice Box:
incoming Core material lands in `.agent/practice-core/incoming/`, gets
compared to the host Practice concept-by-concept, is adapted truthfully to the
host ecosystem, and is then cleared.

Durable governance now travels inside the Core:

- PDRs live in `decision-records/`
- portable general patterns live in `patterns/`

Repo-local evidence stays local:

- repo-specific patterns live in `.agent/memory/active/patterns/`
- ephemeral support can travel through `.agent/practice-context/`

See [practice-lineage.md](practice-lineage.md) for the evolution rules and
[practice-verification.md](practice-verification.md) for the operational
checks.

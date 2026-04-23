---
fitness_line_target: 120
fitness_line_limit: 150
fitness_char_limit: 9000
fitness_line_length: 100
---

# Orientation

This directive carries the layering contract for the repo: what each surface is
for, which layer owns which kind of claim, and which surface wins when two
surfaces speak about the same field.

See [`.agent/memory/README.md`](../memory/README.md) for the three-plane memory
taxonomy and [`.agent/practice-index.md`](../practice-index.md) for the local
bridge across the live estate.

## Layers

| Layer | Purpose | Surfaces | Read trigger |
| --- | --- | --- | --- |
| **Doctrine** | Repo stance and always-on rules | `.agent/directives/` (`AGENT.md`, `principles.md`, `testing-strategy.md`, `data-boundary-doctrine.md`, `evidence-methodology.md`, `metacognition.md`, `orientation.md`) | Session open |
| **Portable Doctrine** | Cross-repo Practice doctrine | `.agent/practice-core/` | Orientation work; Practice changes |
| **Active Memory** | Learning loop capture and refinement | `.agent/memory/active/` | Session open; post-work capture |
| **Operational Memory** | Continuity and session resume | `.agent/memory/operational/` | Session open; closeout |
| **Executive Memory** | Stable catalogues and contracts | `.agent/memory/executive/` | Action-specific lookup |
| **Plans** | Scope, sequencing, acceptance criteria | `.agent/plans/` | When entering or resuming work |
| **Explorations** | Durable design-space investigations | `docs/explorations/` | When weighing options before a decision |
| **Research** | Exploratory synthesis and in-progress material | `.agent/research/` | Investigation and evidence gathering |
| **Analysis** | Consolidated investigations and evidence | `.agent/analysis/` | When evidence needs a stable lane |
| **Reports** | Promoted audits and formal syntheses | `.agent/reports/` | When reading a settled report artefact |
| **Reference** | Curated evergreen library | `.agent/reference/` | Read-to-learn workflows |
| **Experience** | Session-scoped reflective capture | `.agent/experience/` | Session close and consolidation audit |
| **Workflow** | Rituals, commands, rules, and reviewer prompts | `.agent/skills/`, `.agent/commands/`, `.agent/rules/`, `.agent/sub-agents/` | Invocation or trigger |
| **Platform Adapters** | Thin activation wrappers | `.cursor/`, `.claude/`, `.gemini/`, `.github/`, `.agents/` | Platform-specific activation |

## Authority Order

When two same-scope surfaces conflict, the higher-authority surface wins.

1. **Plans** (`.agent/plans/*/active/*`) own live scope, sequencing, and
   acceptance criteria.
2. **`memory/operational/repo-continuity.md`** owns repo-level continuity.
3. **`memory/operational/threads/*.next-session.md`** own thread-level landing
   and next-session state.
4. **`memory/operational/tracks/*.md`** are tactical only and never authoritative
   for scope.

Doctrine sits above these for governance claims. A plan that contradicts a
directive, PDR, or ADR is wrong unless it amends that doctrine in the same
landing.

## Routing Rule

New content belongs at the most durable layer that matches its lifecycle and
read trigger:

- behaviour for every session -> directive
- cross-repo Practice doctrine -> Practice Core
- live learning or emerging rules -> active memory
- continuity and next-session state -> operational memory
- stable catalogue or contract -> executive memory
- scope, sequencing, or acceptance -> plan
- durable option-weighing before commitment -> exploration
- exploratory synthesis not yet promoted -> research
- consolidated investigation and evidence -> analysis
- promoted audit or formal synthesis -> report
- evergreen owner-vetted library material -> reference
- subjective reflection on what the work was like -> experience
- named ritual or command -> skill, command, or rule

If content fits multiple layers, prefer the more durable canonical home and
cross-link from shallower layers.

## Owner Precedence

When the owner's stated direction conflicts with any surface, including this
directive, the owner wins. If a plan or continuity surface appears to disagree
with recent owner direction, stop, re-ground, and repair the surface before
continuing.

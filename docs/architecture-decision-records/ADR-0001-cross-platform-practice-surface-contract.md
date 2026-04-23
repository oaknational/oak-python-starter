# ADR-0001: Cross-Platform Practice Surface Contract

- Status: Accepted
- Date: 21 March 2026

## Context

This repo runs a local Practice across multiple agent platforms: Cursor,
Codex, Claude Code, Gemini CLI, and GitHub Copilot.

Before the cross-platform refactor tranche landed, the repo had three linked
problems:

- the live canon under-modelled some native platform surfaces
- `.agents/` wording was broad enough to imply more parity than the repo could
  honestly support
- adapter growth had no small operational contract or explicit unsupported
  state model

The resulting risk was not just missing wrappers. It was architectural drift:
future work could add or infer support from symmetry rather than evidence.

## Decision

The repo adopts the following cross-platform Practice surface contract:

1. Semantic surfaces remain distinct.
   The repo preserves separate meanings for entry-points, directives, rules,
   skills, commands, subagents, and hooks even when a platform stores some of
   them in similar shapes.

2. Canonical content lives in `.agent/`.
   Platform-specific directories are thin projections of canonical content,
   not parallel sources of policy or workflow logic.

3. The live support contract is the operational matrix.
   `.agent/memory/executive/cross-platform-agent-surface-matrix.md` is the source of
   truth for supported and unsupported platform/surface pairs.

4. Research notes explain; they do not decide.
   `.agent/research/agentic-engineering/cross-platform-agent-infrastructure-research.md` remains
   supporting rationale and source history rather than the implementation
   contract.

5. `.agents/` is intentionally narrow.
   In this repo, `.agents/skills/*/SKILL.md` is the portable skill layer and
   `.agents/skills/jc-*/SKILL.md` is the portable command-workflow layer for
   Codex. `.agents/` is not treated as a blanket mirror of all artefact types.

6. Unsupported states must be explicit.
   Unsupported mappings are written down in the matrix and enforced by
   repository contract tests rather than being inferred from missing files.

7. Wrapper thinness is part of the contract.
   Skill wrappers stay limited to metadata plus a pointer back to canonical
   content. GitHub reviewer wrappers, GitHub instruction wrappers, and Gemini
   command wrappers follow the same canonical-first rule. The landed hook layer
   follows the same pattern: policy in `.agent/hooks/`, shared runtime in
   `tools/agent_hooks.py`, thin native activation only in platform config. The
   live support state, including Gemini hook support, is recorded in the
   operational matrix rather than inferred from symmetry.

## Consequences

- New platform support must start by updating the matrix and permanent docs,
  not by adding wrappers opportunistically.
- Future completion work must either implement currently unsupported mappings
  properly or document hard evidence for why they remain unsupported.
- Completed plan files can be archived because the durable architectural
  decision now lives here, in the matrix, and in the permanent Practice docs.

## Permanent References

- `.agent/memory/executive/cross-platform-agent-surface-matrix.md`
- `.agent/research/agentic-engineering/cross-platform-agent-infrastructure-research.md`
- `.agent/memory/active/patterns/agentic-surface-separation.md`
- `.agent/memory/active/patterns/operational-support-matrix.md`
- `.agent/plans/agentic-engineering/archive/cross-platform-practice-surface-refactor.plan.md`

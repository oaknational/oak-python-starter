---
name: Agentic Surface Separation
domain: agent-infrastructure
proven_by: cross-platform skills review plus local Practice integration (2026-03-20)
prevents: skill-rule-command conflation, over-eager auto-invocation, adapter drift, hidden side effects
---

# Agentic Surface Separation

## Principle

Separate always-on policy, on-demand expertise, explicit workflow entrypoints,
and isolated execution roles into distinct agent surfaces. Portability comes
from preserving those semantics across platforms, not from forcing every
surface into the same file type.

## Pattern

1. Put persistent project context and policy in entry-point files and
   directives.
   - Examples across platforms: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
     project-level agent instructions, and canonical directives in `.agent/`
   - This content is always-on or near-always-on

2. Use rules for short operational reinforcements and scoped activation.
   - Rules are lightweight and should stay small
   - They are the right surface for "always apply", path-scoped, or trigger
     behaviour that should not require the full weight of a skill

3. Use skills for on-demand expertise and multi-step workflows.
   - Skills are discovered from metadata and loaded through progressive
     disclosure
   - The `description` is a trigger classifier, not a marketing blurb
   - Keep the main `SKILL.md` focused; push detail into scripts, references,
     and assets

4. Use commands for explicit user-invoked workflows.
   - Commands are a clean manual entrypoint for actions the agent should not
     decide to run on its own
   - Some platforms blur commands and skills; preserve the semantic difference
     even if the storage format overlaps

5. Use subagents for isolation, delegation, or role-specialised execution.
   - Reach for subagents when you need different tools, permissions, or a
     separate context window
   - Do not hide reviewer roles or delegated workers inside generic skills when
     the platform provides a real subagent surface

6. Make destructive or high-consequence workflows opt-in.
   - Deploy, commit, migration, or other side-effectful procedures should
     usually be explicit commands or skills with implicit invocation disabled

7. Keep wrappers thin and canonical content centralised.
   - Store substantive guidance once in `.agent/`
   - Let platform adapters point at the canonical source without adding policy

## Cross-Platform Signals

- Progressive disclosure is the common model: platforms typically load only
  skill metadata first, then the full instructions when activated
- The `.agents/skills/` directory is emerging as the portable interop path
- Skill descriptions should be evaluated like a classifier, with should-trigger
  and should-not-trigger prompts
- Scripts are for deterministic, fragile, or tool-heavy steps; instruction-only
  skills should be the default
- Platforms differ mainly in scope, precedence, approval, invocation control,
  and whether skills can run inside subagents

## Anti-pattern

- Putting always-on rules or project policy into a skill
- Encoding a destructive operational workflow in an auto-triggering skill
- Modelling reviewer or worker roles as skills when the platform has native
  subagents or agent profiles
- Duplicating substantive instructions separately for Cursor, Claude, Gemini,
  Copilot, and Codex instead of adapting a canonical source

## When to Apply

Use this when designing or refactoring agent infrastructure that spans skills,
rules, commands, subagents, or platform adapters.

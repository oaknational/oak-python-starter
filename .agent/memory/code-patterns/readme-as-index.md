---
name: README as Index
domain: planning
proven_by: plan architecture refactor (2026-03-23)
prevents: plan content accumulating in index files, making them bloated and stale
---

# README as Index

## Principle

Every `README.md` inside a plan directory (`current/`, `active/`, `future/`,
`archive/`) is strictly an index file. It lists plans, links companion
material, and provides high-level navigation. It never contains plan content:
no detailed narratives, step-by-step session instructions, outcome summaries,
or design rationale.

## Anti-Pattern

A `current/README.md` grows to contain session entry checklists, detailed
outcome histories, and strategic explanations that duplicate or replace
content that should live in `.plan.md` files, evaluation artefacts, or
research notes. When a tranche completes or moves, the README must be
rewritten because it has become the plan.

## Pattern

- **Plan content** (phases, acceptance criteria, design rationale, session
  instructions) lives in `.plan.md` files.
- **Outcome narratives** live in evaluation artefacts or research notes.
- **READMEs** contain: a one-line domain description, a plan table (name and
  status), a companion material table, a brief next-session entry point
  (pointers, not procedures), and optional recent archive links.
- When a plan is promoted, archived, or completed, the README update is a
  table-row edit, not a content rewrite.

## Why It Matters

Index-only READMEs are cheap to maintain across tranche boundaries. When a
README carries plan content, every promotion or archive requires rewriting
prose, re-checking cross-references, and risking stale narrative. The
separation ensures plans are self-contained and safe to move or delete
without orphaning information that was silently embedded in the index.

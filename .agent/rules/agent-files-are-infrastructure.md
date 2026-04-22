# Agent Files Are First-Class Infrastructure

Practice files (directives, rules, commands, skills, sub-agent templates) are **first-class agent infrastructure**, not documentation in the traditional sense. They are a carefully constructed framework for agentic agency that directly controls agent behaviour.

As such, they are subject to the same engineering principles as code:

- **DRY** — Define content once in the canonical location; reference from adapters and other files
- **Single Responsibility** — Each file has one clear purpose
- **Open/Closed** — The system is extensible without modifying existing files (add new rules, don't bloat existing ones)
- **Canonical-first** — Substantive content lives in `.agent/`; platform adapters (`.cursor/`, `.claude/`, `.codex/`, `.agents/`) are thin wrappers that delegate

A broken directive doesn't just mislead — it disables an entire layer of agent self-correction. A vague rule opens escape hatches that agents will walk through. Treat every edit with the rigour you would apply to production code.

See `.agent/directives/principles.md` for the full policy.

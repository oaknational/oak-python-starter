# Sub-agents

## Architecture: Three-Layer Composition

```text
components/   → Shared building blocks (behaviours, principles, personas, team model)
templates/    → Domain-specific reviewer prompts that compose from components
adapters      → Platform wrappers (.cursor/, .claude/, .codex/, .agents/) that delegate to templates
```

### Components (`components/`)

Reusable fragments that encode universal reviewer behaviours. Templates reference these via `Read and apply` directives.

| Directory | Purpose |
|-----------|---------|
| `behaviours/` | Operational behaviours: identity declaration, reading discipline |
| `principles/` | Guiding principles: review discipline, DRY/YAGNI guardrails |
| `architecture/` | Team collaboration model and escalation patterns |
| `personas/` | Personality and communication style profiles |

### Templates (`templates/`)

Each template is a complete reviewer prompt that:

1. References shared components (identity, reading discipline, review discipline, DRY/YAGNI, persona)
2. Defines domain-specific reading requirements, checklists, and output formats
3. Contains delegation triggers (when to invoke, when not to)

For this repo, reviewer templates should explicitly pull in the doctrine that
matches their remit: market-data boundaries for ingest work, research
methodology for evidence claims, and parity references for output-adapter
alignment. Generic engineering rules are necessary but not sufficient.

### Adapters (platform directories)

Thin wrappers that delegate to templates. Located in:

- `.cursor/rules/invoke-code-reviewers.mdc` — Cursor integration
- `.claude/rules/invoke-code-reviewers.md` — Claude integration
- `.claude/agents/*.md` — Claude sub-agent definitions
- `.agents/skills/` — Cross-platform Codex discovery

## Adding a New Reviewer

1. Identify which existing components apply and whether new components are needed
2. Create the template in `templates/<name>-reviewer.md`
3. Add component `Read and apply` references at the top of the template
4. Add domain-specific reading requirements, checklists, and output format
5. Add the reviewer to `components/architecture/reviewer-team.md`
6. Create platform adapters
7. Update `.agent/directives/artefact-inventory.md` and `.agent/practice-index.md`

# The Practice

The Practice is the repo's operating system for high-quality human and agent
work: principles, directives, commands, skills, review habits, and learning
loops working together.

This directory is the portable Practice Core. It is a bounded package of files
plus required directories:

- the trinity: `practice.md`, `practice-lineage.md`, `practice-bootstrap.md`
- the verification surface: `practice-verification.md`
- the entry points: this `README.md` and `index.md`
- the change log: `CHANGELOG.md`
- provenance: `provenance.yml`
- the governance directory: `decision-records/`
- the portable pattern directory: `patterns/`
- the Practice Box: `incoming/`

The Core integrates into a specific repo through one local bridge file:
`../practice-index.md`. That file does not travel. It points from the portable
Core to the host repo's live artefacts.

One optional peer directory may accompany the Core:
`.agent/practice-context/`. It carries ephemeral exchange context.
`incoming/` there is transient and should be cleared after integration.
`outgoing/` is lightweight support material only; durable governance and
portable patterns belong in this Core.

The Practice evolves through use, but it must be adapted truthfully to the
host ecosystem. The templates are universal; the concrete commands and runtime
contracts are local.

## For Humans

To hydrate the Practice into a new repo:

1. Create `.agent/practice-core/`.
2. Drop in the full Core package and required directories.
3. Check `.agent/practice-context/README.md` and any received context if that
   peer directory is present.
4. Ask your agent to read the Core, explain what it means, and adapt it to the
   repo's actual language, tooling, and norms.

The Practice should raise the repo's standards without erasing what is already
working well. See [practice-lineage.md](practice-lineage.md) for the evolution
rules and integration flow.

## For Agents

Follow [index.md](index.md). It covers day-to-day use, first-time hydration,
and incoming Practice integration.

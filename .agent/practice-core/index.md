# The Practice

The Practice is not a single file. It is the whole working system around the
repo: directives, rules, commands, skills, review routines, quality gates, and
the learning loop. `practice.md` describes that system; it is not the system
by itself.

## For Day-to-Day Work

For ordinary work, follow `.agent/directives/AGENT.md` and
`.agent/directives/principles.md`.

## The Practice Core Package

The portable Core travels between repos as a bounded package of files plus
required directories.

| Surface | Role |
| --- | --- |
| [practice.md](practice.md) | Core model of the Practice |
| [practice-lineage.md](practice-lineage.md) | Evolution rules and integration flow |
| [practice-bootstrap.md](practice-bootstrap.md) | Templates and host-adaptation guidance |
| [practice-verification.md](practice-verification.md) | Installation and health checks |
| [README.md](README.md) | Human-facing entry point |
| [index.md](index.md) | Agent-facing entry point |
| [CHANGELOG.md](CHANGELOG.md) | Core change history |
| [provenance.yml](provenance.yml) | Per-file evolution chain |
| [decision-records/](decision-records/) | Portable Practice governance |
| [patterns/](patterns/) | Portable general patterns |
| [incoming/](incoming/) | Practice Box for inbound Core material |

The trinity and verification files point to `provenance.yml`. For ordinary
repo work you do not need to read the whole Core every time; you read it when
hydrating, integrating incoming Practice, or refining the Practice itself.

The live repo will usually also carry explicit document tiers, planning
architecture, and exploration surfaces. Those are host-installed but should be
linked from `../practice-index.md`.

## Boundary Contract

The Core must remain portable and self-contained. The one permitted external
link is `../practice-index.md`, the host repo's local bridge.

| Surface type | Portable | Local |
| --- | --- | --- |
| Files | Core package above | `.agent/practice-index.md` |
| Links | Core-to-Core and the bridge | Host-specific live artefacts |
| Purpose | Carry the concepts | Ground them in a real repo |

## The Practice Box

`incoming/` is the Practice Box. Check it at session start and during
consolidation. Incoming Core material is compared concept-by-concept, adapted
to the host repo, then cleared once integration lands.

If `.agent/practice-context/` exists, read its `README.md` and `incoming/`
during hydration or integration. That peer directory is ephemeral support, not
durable Core content.

If the host repo supports multiple agent platforms, keep the live support
contract in `.agent/memory/executive/cross-platform-agent-surface-matrix.md`
and expose it from `../practice-index.md`.

## Cold Start

If `.agent/directives/AGENT.md` does not exist yet, you are hydrating the
Practice into a new repo.

Start by understanding the repo itself: its intent, language, package manager,
formatters, linters, test runner, build steps, and existing standards. Then
adapt the Core truthfully to that ecosystem. Do not copy templates blindly.

If the Core landed in the wrong place, move it to `.agent/practice-core/`
first. Then follow [practice-lineage.md](practice-lineage.md) and
[practice-bootstrap.md](practice-bootstrap.md), create
`.agent/practice-index.md`, and verify the result with
[practice-verification.md](practice-verification.md).

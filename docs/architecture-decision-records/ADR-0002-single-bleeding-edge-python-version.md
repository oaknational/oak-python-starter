# ADR-0002: Single Bleeding-Edge Python Version

- Status: Accepted
- Date: 18 June 2026

## Context

This repository is a **template foundation**, not a broadly distributed
library. Its job is to model excellent current Python practice for new Oak
projects, which then set their own compatibility floor.

The toolchain is deliberately pinned to one recent Python:

- `pyproject.toml` `requires-python = ">=3.14"`
- `.python-version` is `3.14`
- the only `Programming Language :: Python` classifier is `3.14`
- `pyright` runs at `pythonVersion = "3.14"`
- CI installs Python with `uv python install` (which reads `.python-version`)
  and runs a single job — there is **no version matrix**

Nothing in the repo records *why* this is a choice rather than an accident, so a
future contributor could reasonably add a `3.11`–`3.14` matrix "for safety", or
lower `requires-python` to widen reach, without realising it cuts against the
template's intent. A matrix also multiplies CI cost and forces the code to the
lowest common denominator of language features — the opposite of what a
bleeding-edge template should demonstrate.

## Decision

The repository targets a **single, current Python version** and does not run a
version matrix.

1. **One supported version.** The repo supports the latest stable Python it has
   adopted (currently 3.14) and uses its features freely. Older interpreters are
   out of scope.
2. **The version lives in one place conceptually, pinned across surfaces.**
   `.python-version`, `requires-python`, the sole version classifier, and the
   `pyright` `pythonVersion` are kept in lockstep. Raising the version means
   updating all four together.
3. **No CI matrix.** CI proves the repo on exactly the supported version. Breadth
   of interpreter compatibility is explicitly a non-goal.
4. **Adopters set their own floor.** A project generated from this template is
   expected to choose its own `requires-python` and, if it needs broad
   compatibility, add its own matrix. The template does not pre-pay that cost.

## Consequences

- The code may use the newest language and standard-library features without a
  compatibility shim, which is the point of a bleeding-edge template.
- Anyone needing to run on an older interpreter must change the four pinned
  surfaces themselves; this is a conscious adopter decision, not a regression.
- Upgrading to a newer Python is a deliberate, reviewed step (bump the four
  surfaces, re-lock, let the gates run) rather than an ambient matrix expansion.
- **Revisit trigger.** If this repo ever ships as a broadly consumed library, or
  Oak standardises on supporting a range of interpreters, supersede this ADR and
  adopt a matrix at that point — not before.

## Permanent References

- `pyproject.toml` (`requires-python`, classifiers, `[tool.pyright].pythonVersion`)
- `.python-version`
- `.github/workflows/ci.yml` (single `uv python install` job, no matrix)

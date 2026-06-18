# First-adoption dry-run

A structured exercise to prove this template delivers its core promise — that it
can be **cloned, renamed, and adapted without dragging old product history** — and
to catch anywhere the rigor has become disproportionate for a *template
foundation* rather than a feature product.

Run it once, end-to-end, against a throwaway fork. The real output is the
**friction log** at the bottom, which feeds back into the template.

This is the validation wrapper around the step-by-step
[rename guide](using-this-template.md); it does not duplicate those steps.

## Why bother

The clone/rename/adapt outcome is currently validated *by construction* — the
rename guide plus `repo_audit` acting as a rename checklist — not by a real
adoption. Until someone forks it and follows through, friction and heaviness stay
invisible. This dry-run makes them visible while they are cheap to fix.

## Setup

- Install the prerequisites from the README (`uv`, the pinned Python, `gitleaks`).
- Clone into a throwaway location; you will not keep the result.
- Pick a target identity from the
  [three names](using-this-template.md#the-three-names).

## Walkthrough

1. **Baseline.** Run `uv sync`, then
   `uv run python -m oaknational.python_repo_template.devtools check`. Confirm the
   gates pass out of the box with no manual fix-ups, and note how long a cold
   `check` takes (the wheel smoke dominates) — that wait is part of the adopter
   experience.
2. **Rename.** Work through the rename guide's
   [ordered steps](using-this-template.md#ordered-steps). After each step, `check`
   should point you at exactly the surfaces you still need to change. Watch for the
   opposite failure too: any surface that needed renaming but the audit did *not*
   flag is a gap to close in `repo_audit`.
3. **Adapt.** Replace or delete the `activity-report` demo and relax the
   demo-specific audits as the guide describes. Confirm you can remove the demo
   without fighting the gates, and that nothing forces you to keep Oak-specific
   content you do not want.
4. **Understand the release model from the docs alone.** Without asking anyone,
   confirm from README "## Releases", `docs/dev-tooling.md`, and
   [docs/repository-governance.md](repository-governance.md) what a new project
   needs to release — and what to change if you do *not* have the Oak Semantic
   Release Bot (an adopter outside Oak supplies their own GitHub App + secrets, or
   a simpler trigger). If publishing to PyPI, also read
   [docs/publishing-to-pypi.md](publishing-to-pypi.md).
5. **First green PR and release.** Open a PR on the renamed repo, let it merge, and
   confirm CI is green and a release is cut without manual intervention.

## Acceptance checklist

- [ ] A cold `check` passes on a fresh clone with no manual fix-ups.
- [ ] After the rename, `check` is green and `repo_audit` passes.
- [ ] The audit flagged every surface that needed renaming (no silent misses).
- [ ] The demo was cleanly replaceable or removable.
- [ ] The release model was understandable from the docs alone.
- [ ] A first release was cut from a PR merge without manual steps.

## Friction log

Record every snag, surprise, or "this felt heavier than a template should be":

- Replace this line with real entries as you hit them.

For each entry, decide one of: **trim** (remove the rigor), **document** (add a
note to the rename guide or `dev-tooling.md`), or **accept** (it is proportionate;
leave it). Heaviness with no proportionate value is a signal to simplify — the
template's identity is a *lightweight foundation*, not a feature product.

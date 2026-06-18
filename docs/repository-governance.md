# Repository Governance

This repository enforces most of its quality bar **in code** — the `check-ci`
gate sequence, the `repo_audit.py` self-checks (including `audit_supply_chain`,
which pins every workflow action to a SHA and keeps Dependabot watching both
ecosystems), and the SonarCloud pull-request gate. Those need no manual setup.

A few protections can only be set in **GitHub repository/organisation settings**
and cannot be expressed in the repo. This page is the canonical owner-action
checklist for them. An adopter of this template should work through it once for
their own repository.

## Already enforced in GitHub settings

The active rulesets enforce:

- a **pull request** to change `main` (no direct pushes), and **no branch
  deletion** or **force-push** on `main`;
- **required status checks** before merge: `Quality gates`, `Secret scanning
  (gitleaks)`, `CodeQL`, and `SonarCloud Code Analysis` — so `main` cannot go red
  and still merge;
- **release-tag protection**: a `v*` tag ruleset (default rules) so release tags
  cannot be force-moved or deleted.

The **Oak Semantic Release Bot** GitHub App is wired for continuous release: the
`RELEASE_APP_CLIENT_ID` / `RELEASE_APP_PRIVATE_KEY` repo secrets are set and the
app is a **bypass actor** on the `main` ruleset, so it can push the bump commit +
tag to protected `main`. If the app's key is rotated, or it is removed as a
bypass actor, the release push will be rejected. See
[Releases](dev-tooling.md#releases).

## Owner actions outstanding

1. **Enable GitHub Code Quality (organisation preview).**
   Coverage is uploaded as Cobertura on every PR, but the upload runs with
   `fail-on-error: false`, so until the org enables the Code Quality preview it
   is a harmless no-op rather than a visible PR signal. See
   [Coverage reporting](dev-tooling.md#coverage-reporting).

## Why these stay manual

Repository and organisation settings are owner-controlled and live outside the
tree, so the repo cannot assert them the way it asserts code and config. Keeping
the list here — rather than only in session notes — means a future owner or an
adopter can audit governance against reality without replaying project history.

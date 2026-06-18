## v0.4.4 (2026-06-18)

## v0.4.3 (2026-06-18)

## v0.4.2 (2026-06-18)

## v0.4.1 (2026-06-18)

## v0.4.0 (2026-06-18)

### Feat

- **release**: continuous release on merge via the Oak Semantic Release Bot (#44)

## v0.3.0 (2026-06-18)

### Feat

- **safety**: close pipe and substitution bypasses in agent hook (F6) (#37)
- **adoptability**: cap remote fetches (F5) and add a rename guide (F7) (#34)
- **demo**: make the activity chart WCAG 2.2 AA accessible (#33)
- **gates**: honest coverage floor (fail_under 85) + audit_coverage_contract (#31)
- **gates**: add codespell spell-check gate (#26)
- **gates**: add pip-audit dependency-vulnerability gate (#24)

## v0.2.0 (2026-06-17)

### Fix

- **release**: apply the custom bump map via a tested increment helper (#22)

## v0.1.0 (2026-06-17)

### Feat

- **release**: automate GitHub Releases via a Commitizen release-PR (#20)
- **ci**: publish test coverage to GitHub Code Quality (#18)
- **gates**: add gitleaks secret-scanning gate (#16)
- **gates**: add a Markdown linting gate (PyMarkdown) (#13)
- **ci**: add CI workflow running the full gate sequence (#11)
- **agents**: register code/architecture/security/test reviewers and add a Pythonicity lens
- **packaging**: add MIT licence, distribution metadata, and security policy
- **template**: land pythonic alignment ws2-ws4
- **template**: establish Oak Python practice foundation
- **template**: seed cross-platform python starter

### Fix

- **data**: make the CSV boundary deterministic and reject out-of-range minutes
- **runtime**: close final review findings

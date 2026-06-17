# Security Policy

## Reporting a Vulnerability

Please do not report security issues through public GitHub issues.

Report them through Oak National Academy's official security policy, published
at <https://www.thenational.academy/.well-known/security.txt>.

## Supported Scope

This repository is a reusable template. Security fixes are made on the default
branch. Teams that adopt the template are responsible for the security of their
derived repositories.

## Credentials and Secrets

- Never commit real credentials, tokens, or keys.
- Keep secrets in untracked local files (for example `.env`, which is
  git-ignored) and commit only placeholder examples.
- The repository's agent hook guardrails block common history-rewriting and
  hook-bypass commands, but they are advisory defence-in-depth, not a
  substitute for good credential hygiene.

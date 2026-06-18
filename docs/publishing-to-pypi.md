# Publishing to PyPI

This template publishes to **GitHub Releases only** — it deliberately does not
publish to PyPI. If a project based on this template needs to publish to PyPI,
this guide shows how, using the current recommended approach.

You do not need to change how the package is built: the repo already produces a
wheel + sdist via `uv build` (Hatchling backend), and the release workflow
attaches them to every GitHub Release. Publishing to PyPI is an *additional*
workflow you opt into.

## Recommended: Trusted Publishing (OIDC, no tokens)

[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) lets a
GitHub Actions workflow publish using short-lived OpenID Connect credentials, so
there is no long-lived API token to leak or rotate. This is the recommended
approach.

1. **Register the publisher on PyPI.** On your PyPI project page go to
   *Publishing* and add a GitHub Actions trusted publisher: your org/repo, the
   workflow filename (e.g. `publish-pypi.yml`), and an optional environment name.
   For a brand-new project, use a
   [pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
   so the first publish also creates the project.
2. **Add the publish workflow** below. It runs when a GitHub Release is published
   (which this template does on every release), builds, and uploads via
   [`pypa/gh-action-pypi-publish`](https://github.com/pypa/gh-action-pypi-publish).

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi # optional: gate the publish behind a protected environment
    permissions:
      id-token: write # OIDC token for Trusted Publishing — no password needed
    steps:
      - uses: actions/checkout@<pin-to-a-sha> # v4
      - name: Install uv
        uses: astral-sh/setup-uv@<pin-to-a-sha> # v6
      - name: Build the distribution
        run: uv build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@<pin-to-a-sha> # release/v1
```

Because this template already creates a GitHub Release on every qualifying merge,
the `release: published` trigger fires automatically — so a PyPI publish happens
per release once the publisher is configured. To publish only some releases,
trigger on tags matching a pattern instead, or add a manual approval via the
`environment:`.

Keep every `uses:` pinned to a commit SHA (this repo's `audit_supply_chain`
enforces SHA pins, and Dependabot keeps them current).

## Test against TestPyPI first

Validate the flow against [TestPyPI](https://test.pypi.org/) before the real
index: register a trusted publisher there too, and point the publish step at it:

```yaml
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@<pin-to-a-sha> # release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
```

## Alternative: API token

If you cannot use Trusted Publishing, create a
[PyPI API token](https://pypi.org/help/#apitoken), store it as a repository
secret (e.g. `PYPI_API_TOKEN`), and pass it to the publish step:

```yaml
      - uses: pypa/gh-action-pypi-publish@<pin-to-a-sha> # release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

Prefer Trusted Publishing where you can — an API token is a long-lived secret
that must be guarded and rotated.

## Official documentation

- [Publishing package distribution releases using GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
  — the canonical Python Packaging guide
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [`pypa/gh-action-pypi-publish`](https://github.com/pypa/gh-action-pypi-publish)
- [uv — building and publishing a package](https://docs.astral.sh/uv/guides/package/)

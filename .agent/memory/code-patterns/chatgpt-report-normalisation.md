---
name: ChatGPT Report Normalisation
domain: document-processing
proven_by: pythonic-algo-approaches clean-up (2026-03-20)
prevents: broken citations, tracker-link drift, stale package claims, poor canonicalisation
---

# ChatGPT Report Normalisation

## Principle

Treat a ChatGPT-exported report as a recovery artefact, not as canonical source
material. Rebuild the canonical markdown from the strongest surviving layer,
then verify time-sensitive claims against primary sources.

## Pattern

1. Prefer the `.docx` over the markdown or PDF when you need to recover links.
   The DOCX relationship targets usually preserve the actual URLs even when the
   markdown only contains internal `turn...` references.
2. Use the existing markdown structure if it is already better than a fresh
   conversion. `pandoc` is useful as a secondary lens for recovering citation
   placement, but its direct conversion may degrade tables, lists, code fences,
   or Mermaid blocks.
3. Strip ChatGPT artefacts explicitly:
   - internal citation markers such as `cite`, `filecite`, and `turn...`
   - tracking parameters such as `utm_source=chatgpt.com`
   - generic export metadata where relevant
4. Prefer local relative links for repo artefacts instead of GitHub blob URLs.
   Canonical repo documentation should point at local canon first.
5. Convert the recovered sources into proper markdown footnotes or section-level
   source notes. Use the references section as the raw material; do not leave it
   as a detached dump if the body would benefit from inline attribution.
6. Run an accuracy sweep for unstable claims:
   - package versions and release dates
   - licences
   - Python-version support
   - product/API behaviour that may have changed
7. For the sweep, prefer primary sources:
   - official docs
   - official PyPI metadata
   - official GitHub repositories
8. Where a claim is brittle, either verify it with an exact date or simplify
   the wording so it ages more gracefully.

## Anti-pattern

- Treating the markdown copy as trustworthy just because it looks structured
- Trusting PDF or DOCX export provenance without checking for lingering
  ChatGPT metadata or trackers
- Rebuilding from a fresh conversion that worsens the document structure when a
  cleaner hand-curated markdown scaffold already exists
- Keeping vague, time-sensitive claims such as "recent" or "latest" without
  either verifying them or anchoring them to a concrete date

## When to apply

Use this whenever a report originates from ChatGPT or another LLM export and
you need to turn it into a repo-quality markdown reference with durable links
and credible citations.

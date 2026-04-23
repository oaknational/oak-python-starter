---
name: chatgpt-report-normalisation
classification: passive
description: >-
  Recover a ChatGPT- or LLM-exported report from markdown, DOCX, and PDF copies
  into clean repo-quality markdown with real links, stripped artefacts, inline
  footnotes, and a dated accuracy sweep of unstable claims.
---

# ChatGPT Report Normalisation

## Goal

Turn a report exported from ChatGPT or another LLM into canonical markdown that
the repo can keep, review, and trust.

## Use This Skill When

- The user provides paired `.md`, `.docx`, or `.pdf` copies of the same report
- The markdown contains `cite`, `filecite`, `turn...`, or other internal
  export markers
- The DOCX appears to preserve live links that the markdown has lost
- The document contains time-sensitive claims that need an accuracy sweep

## First Principle

Treat the export as a recovery artefact, not as canonical source material.

Read `.agent/memory/active/patterns/chatgpt-report-normalisation.md` before
making structural decisions or choosing a rebuild strategy.

## Workflow

1. Inventory the available copies.
   - Prefer the `.docx` for hyperlink recovery.
   - Prefer the existing markdown if its structure is already better than a
     fresh conversion.
   - Use the PDF as a tie-breaker for pagination, formatting, or missing text.

2. Inspect the strong layers with local tools.
   - `textutil -convert txt -stdout report.docx` for visible text
   - `unzip -p report.docx word/_rels/document.xml.rels` for hyperlink targets
   - `pandoc report.docx -t gfm` as a secondary lens for citation placement and
     footnote hints
   - `mdls report.pdf` or a text extract if provenance or layout needs checking

3. Choose the canonical editing target.
   - If the repo already has a readable markdown scaffold, clean and upgrade it
     in place.
   - Do not replace a better hand-edited structure with a worse direct
     conversion.

4. Remove export artefacts explicitly.
   - Delete internal citation markers such as `cite`, `filecite`, and
     `turn...`
   - Strip tracking parameters such as `utm_source=chatgpt.com`
   - Remove generic export metadata unless it is useful provenance

5. Restore attribution in durable markdown form.
   - Convert recovered citations into markdown footnotes or short section-level
     source notes
   - Prefer local relative links for repo artefacts
   - Use direct site URLs for external sources, de-noised and stable

6. Sweep unstable claims before calling the document canonical.
   - Versions, release dates, licences, Python support, API behaviour, pricing,
     or policy claims
   - Verify against primary sources first: official docs, official PyPI
     metadata, and official repositories
   - Anchor brittle claims to exact dates or rewrite them to age more
     gracefully

7. Finish with a short editorial pass.
   - Preserve tables, code fences, Mermaid blocks, and list structure
   - Match repo conventions such as British spelling when they apply
   - Add a dated accuracy note when you perform a sweep
   - Summarise unresolved gaps rather than hiding uncertainty

## Validation

Before closing the task, confirm:

- No `cite`, `filecite`, or `turn...` markers remain
- No `utm_source=chatgpt.com` trackers remain
- Every footnote used in the body is defined
- The references support the claims they are attached to
- Time-sensitive claims were either verified or softened

## Guardrails

- Do not trust the markdown copy just because it looks structured.
- Do not trust the DOCX or PDF provenance without checking for lingering LLM
  artefacts.
- Do not leave a detached references dump if inline attribution would make the
  document clearer.
- Do not introduce GitHub blob links when a repo-local path is the canonical
  target.

## Escalate

If link recovery or citation placement is still ambiguous after comparing the
markdown, DOCX, and PDF, say so explicitly and preserve the uncertainty in the
final document.

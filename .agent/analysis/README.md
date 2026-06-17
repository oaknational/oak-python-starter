# Analysis

This directory holds consolidated investigations and evidence bundles. It sits
between `research/` and `reports/`.

## What belongs here

- focused investigations that compare evidence and reach a stable interim view
- baseline or gap analyses that may later inform a plan, ADR, PDR, or report
- evidence logs that are more structured than research notes but not yet a
  formal report

## What does not belong here

- fresh exploratory notes that are still forming: use `.agent/research/`
- formal promoted audits or syntheses: use `.agent/reports/`
- durable operational policy or doctrine: use directives, rules, ADRs, or PDRs

## Lane discipline

This template has three strands, so analysis artefacts should usually sit in
one of these themes:

- agentic engineering
- runtime infrastructure
- demo application

If the analysis cuts across all three, make that cross-cutting scope explicit in
the file's opening section.

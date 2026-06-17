# PDR-028: Executive-Memory Feedback Loop

- Status: Accepted
- Date: 2026-04-23

## Context

Executive memory contains stable catalogues such as artefact inventories and
platform matrices. Those surfaces drift more quietly than active memory
because they are read often but edited rarely.

## Decision

Observations about executive-memory drift are captured in the active-plane
napkin with a `Source plane: executive` tag. Consolidation routes those
observations back to the affected executive surface when the evidence is strong
enough.

## Consequences

- executive memory gains a real capture edge
- catalogue drift can be corrected through the same evidence pipeline as other
  learning
- the host repo should teach this routing in a rule and in the napkin format

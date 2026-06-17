# Explorations

This directory holds durable design-space explorations: option-weighing
documents that sit between captured observations and committed decisions.

## What belongs here

- option analyses comparing multiple approaches with evidence
- library or tool comparisons that inform a decision without committing to one
- design-space notes whose reasoning needs to survive the session

## What does not belong here

- committed decisions: those are ADRs
- execution instructions: those are plans
- session observations: those belong in active memory
- evergreen library material: that belongs in `.agent/reference/`

## Document shape

Each exploration should carry:

1. frontmatter with `title`, `date`, and `status`
2. the problem statement
3. options considered
4. open research questions
5. what the exploration informs
6. references

Explorations may stay unresolved. What they must not do is silently substitute
for an ADR or a plan once a conclusion has been reached.

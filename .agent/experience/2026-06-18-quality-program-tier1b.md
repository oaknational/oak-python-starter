# 2026-06-18 — The quality program: supply-chain, Tier 1b, and knowing when to stop

## What the work was like

A long, multi-PR push through the "highest proportionate bar" program: the
supply-chain pinning PR, then Tier 1b (coverage honesty, an accessible chart,
adoptability). Eight PRs merged across the day. The rhythm was the same each
time — TDD the change, run reviewers, *filter* their findings rather than accept
them, fix the real ones with tests, and watch it through CI + CodeQL + a
SonarCloud gate nobody had documented.

The most valuable moments were not the code; they were the judgement calls.

## What surprised me

- **A new quality gate appeared mid-flight.** SonarCloud was scoring new code on
  every PR and failed my first supply-chain push on cognitive complexity and a
  duplicated literal. Both were *real*, so I fixed them rather than reaching for
  a suppression. It was a reminder that the visible gate list is not the whole
  enforcement surface.
- **Another agent was editing the same files in the same working tree.** I caught
  it before committing — a `repo_audit.py`/`pyproject.toml` collision that would
  have entangled or destroyed their half-finished work. Pausing to ask the owner
  how to sequence felt slow in the moment and was obviously right in hindsight.
- **My own instinct was the documented mistake.** I wanted to "restore" a deleted
  packaging audit; the other agent's napkin had already recorded that exact urge
  and corrected it (the audit asserted config *shape*; the wheel-smoke proves the
  behaviour). Reading before acting saved a wrong edit.

## What shifted

- I got more comfortable *not finishing*. Tier 1b's F6 — hardening the very hook
  that governs my own commands — had an ambiguous "fail-closed on `$(`"
  requirement that, taken literally, would break my own heredoc commits and could
  lock me out of committing the fix. Deferring it with a precise handoff was a
  better outcome than a rushed, dangerous edit. "Carry on" does not override "do
  this one safely, later, with the owner's intent."

## What felt harder than expected

- Coordinating commits across a shared working tree with a second agent, and
  keeping memory/continuity churn out of feature PRs. The protected `main` means
  every continuity refresh is its own PR cycle — correct, but it adds friction to
  what should be lightweight bookkeeping.

## Note for future sessions

- The durable bits (the SonarCloud gate, the governance-scanner-vs-config-shape
  distinction, the agent_hooks self-lockout hazard, the F6 design) are in
  `distilled.md` and the gate-expansion thread now — they do not travel with the
  harness, only with the repo.

---
name: go
classification: active
description: >-
  Re-ground and structure execution with ACTION/REVIEW/GROUNDING cadence.
  Use mid-session to realign with the current plan and priority order.
---

# GO GO GO

A grounding workflow for AI agents working in this template repository.
This workflow structures task execution and periodic self-assessment. It
complements [AGENT.md](../../directives/AGENT.md), which provides the
canonical directives, rules, and architectural context.

Read ALL of this document, then carry out the [Action](#action).

## Ground Yourself

Read `.agent/directives/AGENT.md` and follow all instructions. Read
`.agent/directives/principles.md` and reflect on the rules.

Read `.agent/memory/distilled.md` and `.agent/memory/napkin.md` (if
they exist) to absorb context from prior sessions.

If your current task is driven by a plan, read the relevant domain
`current/README.md` first, then the plan before executing the next
step.

If you discover bugs, regressions, broken quality gates, or contradictory
canon while grounding, those take priority over every other lane.

If no bugs are present and the entry surfaces still point at unfinished
completion work, treat that unfinished work as the default priority before
starting new feature or research work. Check the relevant domain
`current/README.md` to see whether a live active tranche exists.

If the task is runtime infrastructure work, read
`.agent/plans/runtime-infrastructure/current/README.md` before taking
action.

If the task is demo application work, read
`.agent/plans/demo-application/current/README.md` before taking action.

## Intent

- Identify and state the current plan you are working to. What impact
  does the plan seek to bring about?
- State explicitly whether this session is:
  - bug fixing,
  - unfinished completion work, or
  - genuinely new work.
  Default to unfinished completion work when no bugs exist and the current
  entry surfaces still point there.
- What are you trying to achieve? Take a step back and consider the big
  picture, think hard about it, and then reflect on your thoughts. Has
  anything changed? Why?

## Structure the Todo List

- Your todo list must achieve the intent of the plan. Populate it with
  tasks that are atomic, specific, measurable, provable, and
  ACTIONABLE. Make each task small enough for the result to be easily
  and comprehensively reviewed. All actions must be prefixed with
  `ACTION:`.
- Start by proving the priority order:
  - if bugs exist, the first `ACTION:` items must triage or fix them
  - if no bugs exist and unfinished completion work is live, the first
    `ACTION:` items must advance that completion plan
- If you have tasks that are large or complex, break them down into
  smaller, more manageable tasks.
- Immediately after each `ACTION:` there MUST be a `REVIEW:` item.
  This consists of:
  1. Stepping back and reflecting on the action
  2. Checking alignment with the plan and rules
  3. **Invoking the appropriate sub-agent(s)** per the `invoke-code-reviewers` directive
- Make sure your todo list includes running the quality gates. These
  items should be prefixed with `QUALITY-GATE:` and happen reasonably
  often.
- Periodically include a `GROUNDING:` task to re-read this document
  and `.agent/directives/AGENT.md`, ensuring your todo list stays
  relevant and aligned with the plan.
- Every fourth `REVIEW:` should be a **holistic review** invoking
  multiple sub-agents to assess overall coherence.
- Remove any items from your todo list that don't make sense, or are
  no longer relevant.
- Every 6th item must be to re-read `.agent/skills/go/SKILL.md` and
  re-follow ALL instructions in this file, including this one.

## Action

Please start the next task in the todo list, and carry on.

# Component: Adversarial Review

After implementation and quality gates are complete, run a review pass
proportional to the change.

## Protocol

1. verify that the plan's acceptance criteria are actually met
2. run `code-reviewer` as the gateway reviewer
3. add the installed specialist reviewers that match the changed surfaces:
   - `architecture-reviewer` for boundaries and design shape
   - `test-reviewer` for tests and proof quality
   - `security-reviewer` for trust boundaries and sensitive data
   - `config-reviewer` for tooling, hooks, and quality gates
4. document the findings and either fix them now or route them into a follow-up
   lane

Do not require reviewers that the repo has not actually installed.

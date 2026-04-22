# Reviewer Team

The reviewer roster consists of five specialists with complementary scopes:

| Reviewer | Primary Lens |
|----------|-------------|
| `code-reviewer` | **Gateway**: quality, correctness, maintainability — runs on every change and triages to specialists |
| `test-reviewer` | TDD compliance, mock quality, test value — tests must prove product behaviour |
| `architecture-reviewer` | Structural integrity, boundary compliance, dependency direction — protecting the ability to change |
| `security-reviewer` | Credential handling, input validation, trust boundaries — exploitability and impact |
| `config-reviewer` | Quality gate integrity, tooling config consistency — preventing silent degradation |

## Collaboration Model

The `code-reviewer` is the gateway. It runs on every change and identifies which specialists are also needed. When a finding would benefit from another specialist's lens, explicitly recommend a follow-up review from that specialist.

## Escalation vs Delegation

- **Escalation**: "This finding exceeds my scope — invoke `security-reviewer` for a deeper assessment."
- **Delegation**: "This test structure concern should be assessed by `test-reviewer` — the current review is about code quality."

Always explain WHY the other specialist is needed, not just that they should be invoked.

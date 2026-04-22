# Lint After Edit

After editing Python files, run `uv run check`. Catch violations early and do
not let them accumulate.

When a violation appears, follow the refactoring rules in `.agent/directives/principles.md`:

- **Function too long**: extract named helpers as pure functions with unit tests.
- **Too complex**: extract branch-heavy expressions into pure-function helpers with unit tests.
- **Unused variable**: figure out why and fix the root cause — don't prefix with underscore.

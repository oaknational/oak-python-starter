# No Global State Manipulation in Tests

Tests MUST NOT mutate global state. Prohibited in ALL tests:

- `os.environ['X'] = 'value'` — mutates global state, causes race conditions
- `unittest.mock.patch('module.thing')` at module scope — manipulates module state, leaks between tests
- Broad `monkeypatch` usage that modifies global singletons or environment

Pass configuration as explicit function parameters. Simple fakes injected as constructor arguments, not complex mocks.

See `.agent/directives/testing-strategy.md` §Prohibited Patterns for the full policy.

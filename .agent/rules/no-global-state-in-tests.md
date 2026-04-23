# No Global State Manipulation in Tests

Tests MUST NOT mutate global state. Prohibited in ALL tests:

- `os.environ['X'] = 'value'` — mutates global state, causes race conditions
- `unittest.mock.patch('module.thing')` at module scope — manipulates module state, leaks between tests
- Runtime patch helpers that mutate process-wide state

Pass configuration as explicit function parameters. Simple fakes injected as constructor arguments, not complex mocks.

The separate `no-monkeypatching-in-python-tests` rule prohibits monkeypatching
entirely in Python tests.

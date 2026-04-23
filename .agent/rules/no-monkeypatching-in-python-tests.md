# No Monkeypatching in Python Tests

Python tests MUST NOT use runtime patch helpers such as
`pytest.MonkeyPatch`, the `monkeypatch` fixture, or `unittest.mock.patch`.

Required approach:

- Add explicit seams to the code under test
- Pass simple fakes as function parameters or constructor arguments
- Prefer real CLI arguments, deterministic filesystem fixtures, and bounded
  integration surfaces over patched globals

If a design cannot be tested without monkeypatching, change the design first.

See `.agent/directives/testing-strategy.md` for the authoritative testing
doctrine.

# No Skipped Tests

NEVER use `@pytest.mark.skip`, `pytest.skip()`, `@pytest.mark.skipif`, or any other skipping mechanism. Fix it or delete it. Tests that require external resources should fail fast with a helpful error, not skip.

See `.agent/directives/testing-strategy.md` §Rules for the full policy.

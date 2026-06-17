---
name: Injected Storage Boundary for In-Memory Tests
domain: python-testing
proven_by: validation-boundary and CLI test design (2026-04-21)
prevents: filesystem-backed in-process tests, CI dependence on ignored local data
---

# Injected Storage Boundary for In-Memory Tests

## Principle

When product code loads or persists local files but the behaviour under test is
still in-process, keep the real filesystem at a thin injected boundary.

## Pattern

Define tiny callables or protocols for the specific file operations the code
needs, with default implementations for production.

Then pass simple dict-backed or list-recording fakes from tests.

## Anti-pattern

Using `tmp_path`, developer-local caches, or default CLI paths to prove
in-process behaviour. That couples tests to workstation state instead of the
real code contract.

## When to Apply

Apply this when the code's responsibility is validation, shaping, and control
flow around file-backed data.

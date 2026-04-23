# 2026-04-23 — WS4 Commitizen and Wheel Truth

This session looked like a straightforward tooling-enforcement pass until the
first green-looking result turned out to be incomplete. Commitizen landed
cleanly, but the verification loop only felt finished once the repo proved the
real `commit-msg` path and not just a direct command invocation.

The more interesting surprise was that the new hook work exposed an older,
deeper truth-surface gap in packaging. The repo had been carrying the right
namespace story in source, but the built wheel was silently flattening it.
That made the session feel usefully corrective: the strongest progress came
from following the proof all the way to the installed artefact rather than
stopping at a plausible local success.

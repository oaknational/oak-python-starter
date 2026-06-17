# 2026-04-23 — WS3 Packaged Typing

This session was a useful reminder that "typing landed" is not the same claim
as "the package typing contract ships". The code and strict pyright surface
were already in good shape; the real miss was that `py.typed` appeared in the
source tree and sdist but not in the built wheel until we checked the artefact
directly.

That made the closeout feel sharper rather than broader. The fix stayed small,
but it changed the proof standard: for Hatch package work, built artefact
inspection is part of the truth surface, not an optional extra.

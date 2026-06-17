# Register Identity On Thread Join

Before editing a thread's continuity surfaces, open its record in
`.agent/memory/operational/threads/` and make sure the acting identity is
registered.

If the same identity is already present, update `last_session`. If a new
identity joined the thread, append a new row with the required fields from
`.agent/memory/operational/threads/README.md`.

Do not leave thread continuity implicit. The thread record is how the next
session knows who touched what and when.

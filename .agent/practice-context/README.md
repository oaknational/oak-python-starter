# Practice Context

This directory is optional and outside the Practice Core.

The Core remains the required package in `.agent/practice-core/`.
This directory exists to carry lightweight exchange context without bloating
the Core itself.

## Structure

- `outgoing/` - sender-maintained supporting context
- `incoming/` - received support material and temporary integration notes

`incoming/` is transient. Clear received files after integration.
`outgoing/` may persist as accumulated reusable context.

When `outgoing/` contains more than one note, keep it indexed and prefer
separate documents for distinct roles such as source packs, discoveries,
receiving-repo integration guides, and tranche-specific portability or
retrospective write-backs.

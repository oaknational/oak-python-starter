# No Type Shortcuts

Never use `# type: ignore`, bare `Any` without documented justification,
`cast()` to bypass the type checker, or broad `except Exception` to suppress
type-related errors. They all disable the type system. Preserve type
information; never widen. Use `TypedDict`, `@dataclass`, or `NamedTuple` over
bare `dict` for structured data.

Type strictness is one of the clearest concrete expressions of the repo's
"strict and complete, everywhere, all the time" tenet.

See `.agent/directives/principles.md` §Python Type Safety for the full policy.

# No Warning Toleration

Operationalises [`principles.md`](../directives/principles.md) and
[PDR-025](../practice-core/decision-records/PDR-025-quality-gate-dismissal-discipline.md).

## Rule

**Warnings are not deferrable.**

Anywhere this repo can influence — quality gates, build output, tests, CI,
lint, type checking, runtime diagnostics, or hook output — a warning is the
cheap version of the failure it names.

If a system we control emits a warning, the rule is:

1. **Fix the root cause** in the same work-item that surfaced the
   warning. Do not log it for later. Do not move it to a TODO. Do
   not file a "verify in WI-N+1" note.
2. **If you cannot fix the root cause inside the current
   work-item**, escalate the system's strictness so the warning
   becomes a hard failure — i.e. raise it to error in the same
   commit. The hard failure is then handled the way every other
   blocking failure is handled: stop, fix, prove fixed, proceed.
3. **If a third-party system emits a warning the repo cannot fix at source**,
   capture it as a structured signal and create a named, blocking follow-up
   lane. Do not let it become ambient background noise.

## Forbidden

- Acknowledging a warning in a thread record, plan, or commit
  message and proceeding without resolution.
- "Flagged for verification in the next work-item" framing for
  any warning whose explanatory text names a contract violation,
  missing export, missing config, or runtime invariant.
- Soft-matching warnings (e.g. `--quiet`, `--no-warnings`,
  `--warning=ignore`, `silent: true`, `printWarnings: false`)
  to suppress emission. The output of warnings is the diagnostic
  surface; suppressing it disables the diagnostic.
- Treating warnings as "less serious than errors" for triage
  ordering. They are equally blocking; the only legitimate
  hierarchy is *root-cause depth*, not severity label.

## Required

- The canonical gates must remain warning-free.
- If a tool only surfaces a warning channel, either fix the cause or tighten
  the boundary so the warning becomes blocking.
- Statements such as "checks are green" or "build passed" must remain
  falsifiable against actual tool output.

## Scope discipline

The doctrine binds wherever a gate runs. The gate's scope is whatever
its configuration declares — for markdown, the set of paths NOT ignored
by [`.markdownlintignore`](../../.markdownlintignore); for esbuild, the
warnings the build emits at the configured strictness; for ESLint, the
files the configured `--ext`/`--ignore-pattern` cover; and so on.

Two rules follow:

1. **Narrowing the gate to dodge a warning is a doctrine violation.**
   Adding a path to an ignore-list, downgrading a rule to `warn`, or
   moving a check out of CI in order to make a warning go away is the
   same forbidden behaviour as suppressing the warning at source. The
   warning has not been resolved; the diagnostic surface has been
   disabled.
2. **Expanding the gate to cover a surface where the doctrine should
   bind is the normal way doctrine spreads.** Canon surfaces
   (`.agent/directives/`, `.agent/memory/`, `.agent/plans/`,
   `.agent/practice-context/`, `.agent/practice-core/`, `.agent/rules/`,
   `.agent/skills/`, `.agent/commands/`, `.agent/sub-agents/`, plus
   workspace source, configs, and shared infrastructure) belong inside
   each relevant gate by default. Reference / synthesis / archive /
   third-party / generated material stays outside until someone
   deliberately moves it in. A gate-config edit that expands scope is
   a doctrine-application act and is reviewed accordingly
   (config-reviewer during planning, code-reviewer after fixes land).

## Cross-references

- `passive-guidance-loses-to-artefact-gravity`
- `warning-severity-is-off-severity`

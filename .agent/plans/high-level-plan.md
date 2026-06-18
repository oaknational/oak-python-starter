---
plan_id: high-level-plan
type: strategic-index
status: active
last_updated: 2026-06-18
---

# High-Level Plan

Strategic cross-collection index for the Python repo template.

Execution detail belongs in collection roadmaps and active plans.

## Strand summary

| Strand | Goal | Current state |
| --- | --- | --- |
| Agentic engineering | Keep the Practice, planning, review, and adapter estate coherent | Mature; reviewer agents + the Practice/memory/continuity estate carried a multi-session, multi-PR program; the `agent_hooks` safety rail was hardened (F6). Maintain and refine. |
| Runtime infrastructure | Keep validation, audits, reports, and quality gates truthful | The "highest proportionate bar" program is **complete**: full `check-ci` gate suite + gitleaks/SonarCloud/CodeQL, a **self-guarding `repo_audit`** (pins the gates' own config), supply-chain SHA-pinning, branch coverage, and **continuous release on merge (PR-merge-only)** via the release bot. Required status checks + `v*` tag protection enforced. **Tier 4 deliberately deferred.** |
| Demo application | Keep `activity-report` useful without redefining repo identity | Bounded by design; now WCAG 2.2 AA accessible and exercised by Hypothesis property tests + the wheel smoke. |

## Immediate next intentions

1. **Prove the core VISION promise.** The clone/rename/adapt outcome is validated
   by construction (rename guide + `repo_audit`-as-checklist), not yet by a real
   adoption. Run the
   [first-adoption dry-run](../../docs/first-adoption-dry-run.md), fork → rename →
   adapt, and feed the friction back into the template.
2. **Watch proportionality.** The bar is the *highest **proportionate*** one — a
   lightweight template foundation, not a feature product. Resist adding rigor
   that raises adopter cognitive load without proportionate value; Tier 4 stays
   deferred unless explicitly requested.
3. **Owner action:** enable the GitHub Code Quality org preview (the last
   governance setting). See
   [docs/repository-governance.md](../../docs/repository-governance.md).
4. **Deferred residuals when warranted:** the `agent_hooks` glued-operator /
   bare-subshell bypasses (need a quote-aware tokeniser — safety-critical, its own
   session); physically archive the two completed `current/` plans.
5. Preserve Practice-surface coherence and keep the runtime/repo-audit foundations
   truthful; resist demo-application sprawl.

## Read order

1. [roadmap.md](roadmap.md)
2. the collection `README.md` you are entering
3. that collection's `active/README.md`
4. that collection's `current/README.md`

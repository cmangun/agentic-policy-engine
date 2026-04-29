# ADR-0001: Deny-by-default posture

**Status**: Accepted
**Date**: 2026-04-28

## Context

The policy engine sits inline in the agent's execution path: every tool call routes through it before reaching the external world. The engine's **default posture** — what happens when no policy matches a proposed action — is the architectural choice with the largest blast radius in the policy layer. A permissive default (allow-by-default) means every undocumented agent action is implicitly granted; a strict default (deny-by-default) means every action requires an explicit, written, signed authorization decision before it executes.

The deciding force is regulatory expectation in the suite's primary buyer base. Pharma, medical-device, and healthcare-AI deployments operate under frameworks — HIPAA minimum-necessary, GxP electronic records (EU Annex 11, US 21 CFR Part 11), FDA Predetermined Change Control Plans — that require operators to demonstrate "this action was authorized" rather than "this action wasn't denied." A permissive default cannot produce that demonstration on demand without manual reconciliation work that defeats the purpose of an inline engine.

The deciding constraint is regulatory expectations in pharma, medical-device, and healthcare-AI deployments — auditors expect "this action was permitted," not "this action wasn't denied."

## Decision

Deny-by-default. A missing policy results in denial. Every action requires an explicit allow rule before the policy engine permits it. The architectural principle is documented in `REFERENCE-ARCHITECTURE.md` §3 ("Deny-by-default at the policy boundary"); this ADR captures the rationale.

## Alternatives Considered

- **Allow-by-default with explicit deny rules**: Standard firewall and IAM pattern, familiar to operators from network security and traditional access control. Rejected on regulatory mismatch — in FDA-adjacent or PHI-handling contexts, the operator has to prove an action was *authorized* before it executed. Allow-by-default leaves a permissive default that violates "explicit consent" frameworks: HIPAA minimum-necessary, GxP electronic records (EU Annex 11, US 21 CFR Part 11), FDA Predetermined Change Control Plans. The regulatory burden of proof shifts when the default is permissive: the operator must document every undocumented action alongside the documented ones. Wrong fit for the buyer base.
- **Warn-by-default with mandatory acknowledgment**: Softer enforcement that surfaces policy violations but does not block them. Rejected on architectural-clarity violation. A "gate" that doesn't gate isn't a gate, it's a logger. The whole point of a policy engine in this stack is non-bypassable governance; warn-only undermines the property the architecture exists to provide. An auditor reading a session of warn-only outcomes cannot distinguish "operator chose to override" from "operator never saw the warning."
- **Mode-configurable (operator picks deny-by-default vs. allow-by-default per deployment)**: Maximum flexibility; lets adopters tune the default to their context. Rejected on backdoor risk. If allow-by-default is selectable, an operator's claim of "we have governance" doesn't hold against an auditor who finds the engine was running in allow-mode at the relevant time. Configurability of the default posture creates a parallel policy-of-the-policy problem that is operationally and forensically hard to verify.

## Consequences

### Positive

- Regulatory burden of proof aligns with what auditors actually ask for. "Show me the authorization for this action" returns a decision receipt; the absence of authorization is a denial that didn't happen rather than ambiguous evidence.
- Single, unambiguous default. No mode-toggle, no operator-tuned variations, no gradient between strict and permissive that could be exploited or accidentally misconfigured.
- Forces explicit policy authoring as a precondition for agent activity. Operators write the policies before agents act, which is also what regulators expect to see during pre-market or pre-deployment review.

### Negative

- Higher operator burden at setup time. Explicit allow rules must be written before any agent can take any action. Adopters in non-regulated contexts may find this heavier than necessary.
- The burden is acceptable: the operator has to write policies for compliance regardless of the engine's posture. Deny-by-default front-loads the work that permissive defaults defer (and that auditors eventually ask for anyway).
- No "soft launch" mode for new agents — every action a new agent attempts must already have an authorizing policy. Onboarding new agents requires policy authoring as a gating step rather than a follow-up.
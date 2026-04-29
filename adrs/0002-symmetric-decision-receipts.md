# ADR-0002: Decision receipts emitted symmetrically (every allow + every deny)

**Status**: Accepted
**Date**: 2026-04-28

## Context

Every policy evaluation in this engine produces a decision receipt — a signed, hash-chained record of the inputs, the matched rule (or absence of one), and the outcome. The architectural choice is whether to emit decision receipts symmetrically (every allow and every deny) or asymmetrically (only the "interesting" cases — typically denials).

Asymmetric emission is operationally tempting. Allows are far more common than denies; emitting a receipt for every allow inflates write volume without obviously helping anyone in the moment. The temptation is to optimize storage cost by suppressing the most common case.

The audit story breaks under asymmetric emission. An auditor asking "show me everything that happened in this session" needs a positive record of allows. The absence of a deny-receipt is ambiguous — it could mean the action was allowed, or it could mean the policy engine wasn't consulted at all. Symmetric emission resolves the ambiguity at the cost of write volume; the architectural choice is to pay that cost rather than push it onto the application layer.

The deciding constraint is audit completeness as a primary requirement; volume cost as a secondary consideration to be addressed operationally rather than by suppression. The symmetric-emission framing is also pinned in `REFERENCE-ARCHITECTURE.md` §5.2 as a design property of the policy engine; this ADR captures the rationale.

## Decision

Every policy evaluation emits a decision receipt — including every allow, not just denials. Allow-receipts and deny-receipts share the same envelope and chain rules; they differ only in the outcome field and the matched-rule body. Symmetric emission is the policy engine's primary contract with the receipts chain.

## Alternatives Considered

- **Emit only on deny (the "interesting" case)**: Minimizes write volume by suppressing the common case. Rejected on audit completeness. An auditor asking "show me everything that happened in this session" needs a positive record of allows. Absence of a deny receipt is not evidence that an allow happened — it's ambiguous between "allowed" and "policy not consulted." The receipt resolves the ambiguity. Suppressing the allow case shifts the audit burden from the receipts layer (where it can be answered cryptographically) to the application layer (where it cannot).
- **Emit only on allow (the "trust footprint")**: Same reasoning, inverted. The "why was this denied" question is as load-bearing as "why was this allowed." Auditing a session of denials is how operators detect policy regressions and policy drift; suppressing them removes that signal entirely. The asymmetry would also conflict with the deny-by-default posture (ADR-0001), which makes denials structurally informative.
- **Sample at rate (e.g., 1% of allows)**: Common in observability stacks, where cost-vs-fidelity tradeoffs are routine. Rejected on regulatory grounds. "We sampled 1% of allows" doesn't satisfy "show me the audit trail for this specific session." Sampling works for observability metrics where aggregate behavior is the answer; it doesn't work for evidence where the answer must apply to a specific named session and a specific named action.

## Consequences

### Positive

- Audit completeness for any individual session. Every authority decision is a written, signed record; the absence of a record is meaningful (the engine wasn't consulted), not ambiguous.
- Symmetric emission supports both directions of audit: "why was this allowed" and "why was this denied" return the same shape of evidence and the same verifiability properties.
- Policy regression detection becomes possible at chain-walk time. An auditor scanning a session for anomalous allow-patterns or deny-patterns has the data to do so without needing to reconstruct what would have been the decision.

### Negative

- Approximately 2x decision-receipt write volume vs. deny-only schemes. Storage and bandwidth cost are real at archive scale.
- Operational mitigations are documented: bundle-layer compression (allows compress well due to repetitive structure), cold-storage tiering for archived bundles, per-session rather than per-action streaming where the consumer can buffer.
- Adopters with high-throughput agents may find the receipt volume disproportionate to their audit needs. The architectural answer is that the audit completeness property is non-negotiable; the operational answer is that compression and tiering bring the cost into a manageable range.
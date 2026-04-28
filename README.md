# agentic-policy-engine

> Part of the [Agentic Evidence Suite](https://github.com/cmangun/agentic-evidence) — six interoperating components for verifiable agentic AI. See [`REFERENCE-ARCHITECTURE.md`](https://github.com/cmangun/agentic-evidence/blob/main/REFERENCE-ARCHITECTURE.md) for the suite-level architecture.

A minimal policy engine for **non-bypassable agent governance**.

Enforces explicit rules for:
- Tool usage authorization
- Data access class restrictions (PII/PHI tiers)
- Budget ceilings and cost limits
- Required human approvals
- Export restrictions

Every decision emits a **policy decision receipt** that can be verified.

Receipt format: [agentic-receipts](https://github.com/cmangun/agentic-receipts)

## Architecture

\`\`\`
Request → Policy Engine → Decision Receipt
              ↓
    [allow | deny | require_approval]
\`\`\`

## Quick Start

\`\`\`python
from src.engine.evaluator import PolicyEngine

engine = PolicyEngine.from_file("policies/examples/healthcare_minimum.json")
decision = engine.evaluate("search", {"data_class": "PHI"})
print(decision)  # deny / require_approval
\`\`\`

## Framework alignment

This engine implements the **non-bypassable governance layer** of [ATVC — the Agentic Trust Validation Certification framework](https://enterprise-ai-playbook-demo.vercel.app/). Specifically:

| ATVC Phase | Coverage |
|---|---|
| **Phase 02 — Architecture** (steps 26–50) | Policy model, decision-receipt contract, trust-boundary placement |
| **Phase 03 — Engineering** (steps 51–75) | Deny-by-default evaluation, bypass-attempt detection, policy gate in CI |

Every allow/deny emits a decision receipt compatible with [agentic-receipts](https://github.com/cmangun/agentic-receipts). Absence of a decision receipt is itself a verification failure.

## Suite

This repo is part of the **Agentic Evidence Suite**:
- [agentic-receipts](https://github.com/cmangun/agentic-receipts) (standard)
- [agentic-trace-cli](https://github.com/cmangun/agentic-trace-cli) (tooling)
- [agentic-artifacts](https://github.com/cmangun/agentic-artifacts) (outputs)
- [agentic-policy-engine](https://github.com/cmangun/agentic-policy-engine) (governance)
- [agentic-eval-harness](https://github.com/cmangun/agentic-eval-harness) (scenarios)
- [agentic-evidence-viewer](https://github.com/cmangun/agentic-evidence-viewer) (review UI)

## License

MIT
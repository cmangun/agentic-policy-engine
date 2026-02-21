# agentic-policy-engine

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

# Non-goals

What `agentic-policy-engine` deliberately does not try to be. Each item names a delegation point or an explicit boundary against the layers it composes with rather than replaces.

## Not general-purpose authorization

The policy engine is scoped to **agent-action authorization** — gating an agent's privilege to act at the tool-call boundary. It is not a replacement for user-level RBAC, application-level entitlements, or service-mesh authz. Adopters keep their existing IAM stack; this layer sits between IAM-resolved identity and the agent's tool calls.

## Not an agent sandbox

The engine gates *intent* (what an agent attempts) rather than enforcing *isolation* (how the attempt is executed). A policy decision that says "this tool call is allowed" is a statement about authority, not about runtime confinement. Sandboxing — containerization, capability restriction, runtime instrumentation — belongs to the agent runtime.

## Not a prompt-injection detector at runtime

Injection scenarios are tested by the eval harness; injection that occurs at runtime is recorded by receipts. This engine does not attempt to detect injection in real time. Prevention belongs to a different layer of the stack with its own primitives (input filtering, prompt-shielding LLM techniques, pre-completion classifiers).

## Not a compliance certification

The engine produces decision receipts as audit-trail evidence. Whether that evidence satisfies a specific regulatory regime (FDA, EMA, GxP) is between the operator and the regulator. The engine *enables* compliance arguments; it does not *issue* them.

## Not a runtime instrumentation framework

The engine is a callable evaluator with a defined contract — proposed action in, decision receipt out. It is not an agent framework; it does not orchestrate workflows, manage agent state, or instrument execution beyond the policy boundary. Workflow orchestration is the lane of `agentic-workflow-engine`; the policy engine is invoked from inside such workflows but does not own them.

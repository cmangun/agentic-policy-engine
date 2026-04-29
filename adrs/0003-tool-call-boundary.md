# ADR-0003: Policy evaluation point — tool-call boundary

**Status**: Accepted
**Date**: 2026-04-28

## Context

The policy engine evaluates proposed agent actions against authorization rules. The architectural choice is **where in the agent's execution path** the engine actually runs — what specific event triggers evaluation. Four boundaries are conceptually possible:

- **LLM-completion**: after the model produces output text, before the agent acts on it.
- **Agent-action**: at whatever the agent framework defines as one "action."
- **Tool-call**: when the agent invokes a registered external tool.
- **Effect**: after the tool execution returns and the side effect has occurred.

Each boundary has different timing properties. Earlier boundaries (LLM-completion) catch potential issues before they become actions but operate on a wrong abstraction (text, not authority decisions). Later boundaries (effect) operate on the right abstraction but execute too late to prevent actions; they can only log them. The middle two — agent-action and tool-call — both operate at action-time, but differ in their portability across agent frameworks.

The deciding constraint is universal semantic boundary across agent frameworks. Tool calls are the one place every agentic framework has an explicit, observable, interceptable event. The architectural principle is documented in `REFERENCE-ARCHITECTURE.md` §4 (canonical enforcement point); the MCP integration shape is in `INTEROP.md` §6.

## Decision

Policy evaluation runs at the **tool-call boundary** — the moment an agent attempts to invoke a registered tool. The engine is configurable to also run at additional boundaries (LLM-completion for prompt-injection containment, for example) when an adopter has reason to gate elsewhere. Tool-call is the canonical recommendation, the conformance-vector test target, and the default integration shape.

## Alternatives Considered

- **LLM-completion boundary (after the model produces output)**: Earliest signal in the pipeline. Rejected as too early. The model produces text; the agent decides what to *do* with it. Gating completions means gating speech, which is the wrong abstraction — the agent can produce arbitrary text without taking action. A policy engine that gates speech is an output filter, not a governance layer; it answers "is this output acceptable" rather than "is this action authorized." The two questions have different stakeholders and different risk shapes.
- **Agent-action boundary (framework-defined "action" concept)**: Middle-ground choice that operates at action-time on the framework's own action semantics. Rejected on framework-coupling. "Action" is defined differently by LangGraph, AutoGen, CrewAI, and custom frameworks — the unit of agency varies in granularity, in lifecycle, and in what side effects are permitted before the action is finalized. A policy engine that requires framework-specific action semantics doesn't compose cleanly across the agentic-systems ecosystem; it ties the engine's contract to one framework's choices and forces re-binding work for every additional framework integration.
- **Effect boundary (after tool execution returns)**: Latest possible boundary; gates on observed effects rather than proposed actions. Rejected as too late. By the time a tool has executed, the action has happened. Gating after the fact is logging, not prevention. For irreversible actions — sending an email, executing a trade, scheduling a procedure — after-the-fact gating fails the prevention property entirely. The receipts layer captures effects regardless; a policy engine at the effect boundary duplicates that work without adding prevention.

## Consequences

### Positive

- Universal across agent frameworks. Tool calls are an explicit, named, observable event in every agentic system the suite has examined. The engine's contract composes without framework-specific bindings.
- Semantically meaningful. A tool call is an action proposed against an external surface; the policy decision answers the right question — *is the agent authorized to act on this surface*?
- Composes cleanly with MCP. Per `INTEROP.md` §6, an MCP `tools/call` request is the natural integration point: receipt emission, policy evaluation, and decision-receipt all bind to a single MCP event.

### Negative

- Per-call cost. Policy evaluation runs on every tool call, including repeated identical calls and inexpensive calls where the cost of evaluation may exceed the cost of the call itself. Real at agent-throughput scale.
- Mitigations: result caching for repeated identical calls (same inputs against the same policy version yield the same decision, cached for a configurable window); batched evaluation where the framework supports it; engine-implementation optimization at the per-call level. These are v0.1 implementation concerns, not architectural ones.
- The configurable-elsewhere allowance creates a small risk surface: adopters who gate at multiple boundaries must reason about the interaction (LLM-completion gating plus tool-call gating must compose without producing contradictory or duplicate decisions). Documented; v0.2 may add formal multi-boundary composition rules if adopters surface specific issues during the v0.1 line.
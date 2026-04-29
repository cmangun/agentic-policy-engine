# Runbook

> Operational guide for `agentic-policy-engine`. The engine is a v0.1-line component; this document describes the operational shape adopters should provide as it matures toward v1.0. Specific metric thresholds and recovery procedures are recommendations against expected production behavior; adopters tune them to deployment specifics.

## Metrics

The engine should expose the following metrics for monitoring and alerting:

- **Decision-receipt write rate** — receipts emitted per second. Tracks both allows and denies (symmetric per [adrs/0002-symmetric-decision-receipts.md](adrs/0002-symmetric-decision-receipts.md)). Recommended scrape interval: 15s. Alert threshold: drops below 10% of baseline for more than 2 minutes signals receipt-emission failure.
- **Policy-evaluation latency** — wall-clock from proposed-action input to decision-receipt emission. Track p50, p95, p99. Recommended target: p99 < 10ms under steady-state ruleset.
- **Deny rate** — fraction of evaluations resolving to deny. High deny rates signal policy mismatch or attack patterns; low rates may indicate missing policy coverage. Track 5-minute and 1-hour windows.
- **Allow rate** — companion metric. Together with deny rate, baseline allow + deny ≈ 1.0 (no third state in v0.1).
- **Missing-policy rate** — fraction of evaluations resolving to default-decision (deny per [adrs/0001-deny-by-default.md](adrs/0001-deny-by-default.md)). High rates indicate policy gaps that need authoring before they become audit findings.

## Performance envelope

Expected production behavior under typical ruleset sizes (10²–10³ rules):

- **Throughput**: ~1,000 sustained decisions/sec on a single-process deployment with in-memory ruleset. Higher throughput requires horizontal sharding by policy domain.
- **Latency**: p99 < 10ms per decision under steady-state. p99 grows linearly with ruleset depth and per-rule condition count.
- **Memory footprint**: bounded by ruleset size (approximately 10KB per rule on average, including conditions and metadata) plus a per-evaluation buffer for context and decision-receipt construction.
- **Stateless evaluation**: each evaluation is independent. State that policies depend on (counters, budgets, session tracking) passes through the context payload, not the engine itself.

## Failure modes

The engine has four named failure modes that operators must plan for:

- **Signing-key unavailable** — the engine cannot sign decision receipts. May be transient (KMS connectivity) or persistent (key rotation in progress without continuity).
- **Receipt store unavailable** — the chain target is unreachable. The engine still evaluates but cannot persist decision receipts.
- **Policy ruleset parse error** — a deployed ruleset fails to parse on engine start or hot-reload. The engine cannot evaluate against an invalid ruleset.
- **Policy ruleset corruption mid-evaluation** — rare; a partial-write or storage-tier corruption leaves the engine with an internally inconsistent ruleset.

## Recovery procedures

Recovery responses, per failure mode:

- **Signing-key unavailable**: rotate via the key-history mechanism described in [agentic-receipts/adrs/0002-signature-algorithm.md](https://github.com/cmangun/agentic-receipts/blob/main/adrs/0002-signature-algorithm.md). Pre-staged signing keys with explicit rotation entries let the engine continue emitting receipts under a successor key without dropping evaluations. Bundles signed pre-rotation remain verifiable per the rotation timeline in the key-history file.
- **Receipt store unavailable**: the engine queues decision-receipts (not evaluations) in a bounded local buffer; reconnects to the receipt store with exponential backoff. If the buffer fills, the engine fails-closed (denies subsequent evaluations until the store is reachable again). The fail-closed posture aligns with [adrs/0001-deny-by-default.md](adrs/0001-deny-by-default.md) — better to deny on infrastructure failure than to allow without recordkeeping.
- **Policy ruleset parse error**: fail-closed. The engine refuses to start (or refuses the hot-reload) and continues using the last-known-good ruleset. Operator alerts fire on parse failure; deployment pipelines must validate policy serialization before publish.
- **Policy ruleset corruption mid-evaluation**: fail-closed deny per [adrs/0001-deny-by-default.md](adrs/0001-deny-by-default.md). The engine aborts the in-flight evaluation, emits a decision receipt with reason `corruption-detected`, and re-fetches the ruleset from the authoritative source on the next evaluation cycle. Operators investigate corruption sources (storage tier, deploy pipeline integrity).

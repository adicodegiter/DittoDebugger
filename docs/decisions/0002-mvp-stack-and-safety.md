# ADR 0002: Small Local-First MVP Stack

- **Status:** accepted for blueprint; implementation validation pending
- **Date:** 2026-10-10

## Decision

Use FastAPI/Python for orchestration, React/TypeScript for a later thin dashboard, Prometheus for metric history, SQLite for experiment/control records, and the upstream Ditto Artillery tool for bounded load. Begin with a typed adjacency list and deterministic candidate scoring; add NetworkX only if a required graph operation justifies it. Keep LLM use optional and evidence-constrained. The first chaos action is a short, allow-listed local service restart with explicit human approval and recovery verification.

## Consequences

The stack is testable on a laptop and needs no paid model or cloud service. The current repository includes only contracts/config/tests, not these application dependencies. Docker control remains a powerful host capability, so the runner must be a separate local process and the model/API must have no Docker socket or arbitrary execution access. Network faults and MongoDB/host resource exhaustion are deferred until specific rollback and blast-radius controls are proven.
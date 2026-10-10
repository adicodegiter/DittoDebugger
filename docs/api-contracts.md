# API Contracts (Planned)

No API server exists yet. The following routes are the planned local control-plane contract. The machine-readable [OpenAPI 3.1 document](../schemas/openapi.yaml) defines the paths and request/response records; JSON Schema files in [schemas/](../schemas/) define service, experiment, run, and finding records; examples live in `schemas/examples/`. Initial contract version is `1.0`. Breaking changes require a new API version and a data migration plan. The API binds to loopback only.

## Endpoints

| Method and path | Purpose | Side effect / guard |
| --- | --- | --- |
| `GET /api/v1/health` | Workbench health and dependency status | Read only; report Ditto/Prometheus as unavailable without exposing secrets |
| `GET /api/v1/architecture` | Current graph, provenance and confidence | Read only; tag static vs inferred edges |
| `GET /api/v1/telemetry?from=<RFC3339>&to=<RFC3339>` | Normalized metric observations and coverage | Read only; bounded time range |
| `POST /api/v1/experiments/plan` | Generate candidates from graph, telemetry and history | Writes proposed plans only; never runs a fault |
| `GET /api/v1/experiments/{experiment_id}` | Read candidate, policy decision and approval status | Read only |
| `POST /api/v1/experiments/{experiment_id}/approval` | Approve or reject the immutable candidate | Human identity, reason, expiry and candidate hash required; does not execute |
| `POST /api/v1/experiments/{experiment_id}/execute` | Ask the isolated local runner to execute an approved experiment | Revalidate approval, policy, baseline, target and concurrency; reject if any check fails |
| `GET /api/v1/runs/{run_id}` | Read run state, prediction, observations, cleanup and recovery | Read only |
| `GET /api/v1/findings?run_id=<id>` | Read evidence-backed findings and score details | Read only |

## Request/Response Examples

Plan a candidate (the response uses the `experiment` schema):

```http
POST /api/v1/experiments/plan
Content-Type: application/json

{"baseline_id":"baseline-2026-10-10-01","max_candidates":3}
```

```json
{
  "plan_id": "plan-2026-10-10-01",
  "candidates": [
    {
  "schema_version": "1.0",
  "id": "restart-gateway-10s",
  "target_component": "gateway",
  "action": "restart_container",
  "duration_seconds": 10,
  "hypothesis": "The API entry service becomes unavailable briefly and returns after restart without persistent data loss.",
  "predicted_impacts": ["gateway", "ditto-api-clients"],
  "information_gain": 0.7,
  "risk_score": 0.2,
  "evidence_refs": ["architecture:ditto-gateway", "baseline:latest"],
  "approval_required": true
    }
  ],
  "policy_rejections": []
}
```

Approval is a separate human action and execution is a separate request:

```http
POST /api/v1/experiments/restart-gateway-10s/approval
Content-Type: application/json

{"decision":"approve","reason":"Disposable local demo; baseline verified.","candidate_hash":"sha256:..."}
```

The server derives the approver from the local authenticated UI/session context; never trust an identity supplied in the request body. The initial single-operator implementation must document its local identity source before approval is implemented.

```http
POST /api/v1/experiments/restart-gateway-10s/execute
Content-Type: application/json

{"approval_id":"approval-001"}
```

The execute response must identify an asynchronous run, e.g. `{"run_id":"run-local-001","status":"approved"}`. An implementation must use `409 Conflict` for stale state/approval or active experiment, `422 Unprocessable Content` for policy rejection, `503 Service Unavailable` for failed preconditions/dependencies, and `404` for unknown IDs. Exact error envelope is to be frozen with the first implementation and covered by contract tests.

## Security and Compatibility

Use request/response validation against schemas and reject unknown action names. Approval and execution are distinct; model output cannot impersonate an approver. Never accept a command line, image name, host, Compose file path, or Docker API body from a request. Limit telemetry windows and candidate count. Add authentication before any non-loopback use. API response records include `schema_version`; unknown major versions fail closed. Approval audit records and safety decisions are append-only for the MVP.
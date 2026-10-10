# Five-Person Implementation Plan

Assign people by role during the team meeting; names are intentionally omitted. **Each person owns an individual setup/preflight task as well as their module**, so nobody is blocked waiting for one person to configure the whole repo.

## Common Setup, Done by Everyone

Each teammate completes this checklist before parallel coding:

1. Clone the custom repository and create a branch using the naming rules in `CONTRIBUTING.md`.
2. Install Git, Python 3.12+, Node.js 18+, npm, Docker Desktop/Compose v2; verify the versions in the README. Docker is currently unavailable in the implementation environment, so Ditto runtime preflight remains outstanding.
3. Create/activate a local Python virtual environment and install `requirements-dev.txt`; run `python -m unittest discover -s tests -v`.
4. Fetch the pinned Ditto release into the ignored `.local/ditto-upstream` directory; inspect but do not edit it. Never share `.env`, sample credentials, private logs, customer data, or the ignored checkout.
5. Read `docs/ditto-codebase-map.md`, `docs/safety-model.md`, the shared schemas, and the API contract. Confirm loopback-only endpoints and the dedicated synthetic test namespace.
6. Run the local app using the instructions in the README and report which dependencies are unavailable. Do not run experiments against any remote/shared deployment.

## Workstreams

| Person/role | Module ownership | Individual setup task | Deliverable and acceptance |
| --- | --- | --- | --- |
| 1. Discovery + Ditto integration | `backend/app/agents/discovery.py`, `backend/app/settings.py`, Ditto adapter tests | Pin/tag-check `.local/ditto-upstream`; record `docker compose config` inventory and verify five service image/health/port facts against tag `3.9.8` | Parse Compose and Kubernetes manifests without execution; produce nodes, endpoints, ports, health checks, static edges, file provenance, and warnings. Runtime discoveries must carry runtime evidence. Tests use sanitized fixtures. |
| 2. Graph + API/contracts | `backend/app/agents/mapping.py`, `schemas/`, `backend/app/main.py` API routes | Run the API locally, inspect `/openapi.json`, validate shared JSON Schema/OpenAPI files, and map upstream service names to module paths | Versioned graph snapshots/export; distinguish Ditto target nodes from workbench-agent nodes; show complete/partial cluster evidence, criticality caveats, source/confidence; all routes match the contract. |
| 3. Telemetry + workload | `backend/app/agents/telemetry.py`, telemetry config, `scripts/`, telemetry tests | Start local Ditto when Docker is available; inspect actual `:9095/` output, `/alive`, and the bounded HTTP Artillery profile. Confirm if that profile truly requires Kafka/MMock. | Normalize timestamp/unit/source/labels, detect stale/missing metric families, define baseline/experiment/recovery windows, and document actual metric names. No healthy baseline if targets/required metrics are missing. |
| 4. Planner + analysis | `backend/app/agents/planning.py`, AI analysis module to add after interfaces are stable | Install/run deterministic planner with fixture graph/history; configure `AI_PROVIDER=none`; verify no external model key is needed | Transparent weighted scoring, predictions, uncertainty, evidence refs, repeat-vs-novel candidate test, evidence-backed remediation templates. Optional LLM may explain only validated observations and cannot access tools, secrets, or runner. |
| 5. Safety + execution + demo integration | `configs/experiment-policy.yaml`, safety/run modules to add, `frontend/` demo flow, end-to-end tests | Verify Docker context/project name, target allow-list, loopback bindings, baseline and recovery canary. Exercise only a dry-run approval state first. | Safety gate and immutable human approval; separate local runner with fixed target/action mapping; 10-second restart only after all checks. Must abort on unhealthy baseline, stale approval, other service failure, telemetry loss, or timeout; cleanup/recovery tested after normal and interrupted runs. |

## Shared Integration Agreements

- Contract owner (role 2) publishes a schema/OpenAPI change before another workstream changes exchanged fields. Additive optional fields are preferred; breaking changes require a version and migration note.
- Discovery owns factual resource records; graph owns edge semantics. Compose `depends_on`, Kubernetes selectors, docs, and runtime traces have different provenance values. Docker network membership alone does not establish an application call.
- Telemetry owns normalized observations and coverage. Planner consumes observations and graph IDs, not raw logs. Analysis produces evidence references, not execution payloads.
- Runner has its own process boundary. No Docker socket or command capability in API/planner/LLM. `POST .../execute` stays disabled until policy enforcement, human approval, rollback, and recovery tests pass.
- Integrate continuously through pull requests and focused CI checks; nobody merges a schema, safety, or integration boundary change without a reviewer outside that change when team size permits.

## Milestones and Dependencies

| Milestone | Priority | Dependency | Exit criteria |
| --- | --- | --- | --- |
| M0. Everyone's local setup + target preflight | P0 | None | Each person reports versions; pinned Ditto Compose starts; endpoints, actual metrics, ports, sample-auth replacement, Artillery dependencies, and cleanup are known |
| M1. Real inventory and graph | P1 | M0, discovery + contracts | Graph is derived from actual pinned manifest; all edges have provenance; no synthetic Ditto topology appears when deployment is absent |
| M2. Healthy baseline | P1 | M1, telemetry + workload | Repeatable low-rate canary, fresh required metrics, saved graph/version/workload metadata, coverage shown |
| M3. Evidence-driven planner + approval | P2 | M1, M2, planner + safety | Candidate ranking is reproducible; forbidden targets rejected; approval binds immutable candidate and expires; no execution from model output |
| M4. Single recovery-tested fault | P2 | M3, Docker-backed safety implementation | Explicit human-approved Gateway restart in isolated target; automatic cleanup, `/alive`, functional API canary, and abort evidence all work |
| M5. Report/UI/demo | P3 | M1-M4 | Judges see target architecture and separate workbench agents; prediction/result/score and evidence can be exported; live versus fixture data clearly labelled |

**Do not parallelize M4 execution before M0-M3 are proven.** Current implementation does not yet have a Docker runner, telemetry baseline is blocked without local Prometheus, and this environment has no Docker CLI. Public publication also remains blocked in this environment because `gh` is not installed and no Git remote is configured.
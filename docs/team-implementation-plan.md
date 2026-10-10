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

## AI Systems Roadmap

Build a coordinated, evidence-grounded assistant, not an autonomous fault injector. The current repository already implements Compose/Kubernetes discovery, graph mapping, Prometheus telemetry collection, SQLite history, and a deterministic weighted experiment planner. These are useful foundations, but the planner is heuristic rather than a learned model; anomaly detection, post-run diagnosis, and LLM explanations are future work. Execution remains disabled until the separate safety and runner gates below are proven.

| System | What it does | Inputs and outputs | Build order and acceptance |
| --- | --- | --- | --- |
| 1. Deployment discovery | Reads pinned Ditto manifests and records service facts with source provenance; does not infer live behavior from static configuration | Compose/Kubernetes files -> validated service inventory and warnings | First. Fixture tests cover all five Ditto roles, missing files, malformed inputs, and provenance. |
| 2. Topology reasoning | Builds a versioned graph and identifies candidate impact paths while distinguishing documented, configured, and runtime evidence | Inventory plus verified Ditto architecture facts -> typed graph, confidence/provenance, criticality caveats | After discovery. Tests ensure `depends_on` and shared network membership are not mislabeled as runtime calls; partial evidence stays explicit. |
| 3. Telemetry intelligence | Normalizes health, canary, workload, and Prometheus observations; identifies stale/missing coverage and baseline deviations | Metric samples and workload windows -> normalized observations, coverage, deterministic anomaly flags | After target preflight. Start with transparent thresholds and fixture data; only call an anomaly actionable when freshness and coverage requirements pass. |
| 4. Experiment selection | Ranks a fixed catalog of bounded candidates using impact, novelty, uncertainty, risk, graph coverage, and prior outcomes | Versioned graph, fresh baseline, telemetry, history, policy -> ranked typed proposals with score terms and evidence references | Existing heuristic is the MVP. Acceptance includes reproducible ranking, a novelty-vs-repeat test, explicit uncertainty, and policy rejection. Do not train a model without sufficient labeled experiment history. |
| 5. Post-run diagnosis and explanation | Compares prediction with before/during/after evidence; produces likely causes and mitigation suggestions tied to observations | Approved run, graph, metric references, canary results -> structured finding, confidence, evidence IDs, suggested next check/remediation | Add after evaluation contracts stabilize. Deterministic rules must work with `AI_PROVIDER=none`; optional LLM may summarize or rank supplied hypotheses, and unsupported claims must fail validation. |

These systems are coordinated by the existing orchestrator and exchange versioned schema records, not free-form agent-to-agent prompts. Each result must include status, provenance/evidence IDs, confidence or coverage where applicable, and explicit unavailable/insufficient-evidence states. Do not send secrets, raw customer data, or unrestricted logs to a model. The optional model receives only bounded, redacted evidence and has no tools, policy-write access, approval authority, or runner access.

Safety controller, human approval, and fixed-action runner are required control systems, not AI agents. They must remain deterministic: reject stale or mismatched baselines, disallowed targets/actions, excess risk/duration/concurrency, unhealthy preconditions, expired approvals, and failed recovery. No model output may alter these decisions.

## Workstreams

| Person/role | Module ownership | Individual setup task | Deliverable and acceptance |
| --- | --- | --- | --- |
| 1. Discovery + Ditto integration | `backend/app/agents/discovery.py`, `backend/app/settings.py`, Ditto adapter tests | Pin/tag-check `.local/ditto-upstream`; record `docker compose config` inventory and verify five service image/health/port facts against tag `3.9.8` | Own AI system 1: parse manifests without execution and produce validated service inventory with provenance/warnings. Runtime discoveries carry runtime evidence; sanitized fixtures cover missing and malformed inputs. |
| 2. Graph + API/contracts + UI integration | `backend/app/agents/mapping.py`, `schemas/`, `backend/app/main.py`, graph/report UI integration | Run the API locally, inspect `/openapi.json`, validate contracts, and map upstream service names to module paths | Own AI system 2: versioned graph snapshots, evidence distinctions, criticality caveats, and stable interfaces. Integrate graph, candidate, finding, and report views against the versioned API; ensure partial evidence is visible. |
| 3. Telemetry + workload | `backend/app/agents/telemetry.py`, telemetry config, `scripts/`, telemetry tests | Start local Ditto when Docker is available; inspect actual `:9095/` output, `/alive`, and bounded HTTP workload prerequisites | Own AI system 3: normalized time-windowed observations, freshness/coverage checks, baseline deviations, and transparent anomaly flags. No healthy baseline if targets or required metrics are missing. |
| 4. Experiment selection + diagnosis | `backend/app/agents/planning.py`, future diagnosis/analysis module, focused tests | Run planner with fixture graph/history; configure `AI_PROVIDER=none`; verify no model key is needed | Own AI systems 4 and 5: preserve deterministic ranking and add prediction-vs-result diagnosis with evidence-linked findings. Optional LLM can explain validated hypotheses only; test unsupported-evidence rejection and deterministic fallback. |
| 5. Safety + execution + evaluation integration | `configs/experiment-policy.yaml`, future safety/run/evaluation modules, end-to-end tests | Verify Docker context/project name, target allow-list, loopback bindings, baseline and recovery canary. Exercise dry-run approval first. | Own deterministic safety controls: immutable human approval, fixed target/action mapping, separate local runner, abort/cleanup/recovery checks. Add the first short restart only after M0-M3 pass; connect run outcomes to evaluation and audit records. |

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
| M5. Diagnosis + evidence report | P3 | M2-M4 evaluation records | Prediction is compared with observed outcome; findings cite stored evidence; deterministic explanation works without an LLM |
| M6. Report/UI/demo | P3 | M1-M5 | Operator can inspect target architecture, ranked proposals, approval/run state, findings, score, and evidence; live versus fixture data is clearly labelled and results can be exported |

**Do not parallelize M4 execution before M0-M3 are proven.** Current implementation does not yet have a Docker runner, telemetry baseline is blocked without local Prometheus, and this environment has no Docker CLI. Public publication also remains blocked in this environment because `gh` is not installed and no Git remote is configured.
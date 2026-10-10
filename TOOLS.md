# Tools, Libraries and AI Models

Running list for the team submission form. Add an entry whenever you introduce something.

## Application under test
| Item | Version | Purpose | License |
|---|---|---|---|
| Eclipse Ditto (policies, things, things-search, connectivity, gateway, ditto-ui) | 3.9.8 | Digital-twin platform under test | EPL-2.0 |
| MongoDB | 7.0.14 | Ditto persistence | SSPL |
| nginx | 1.27.2-alpine | Ditto reverse proxy / basic auth | BSD-2-Clause |
| swagger-ui | v5.9.1 | Ditto API docs (bundled with Ditto deployment) | Apache-2.0 |

## Runtime and tooling
| Item | Version | Purpose |
|---|---|---|
| Docker Desktop / Docker Engine | 24.0.6 | Runs the target stack |
| Docker Compose | v2.23.0 | Stack orchestration |
| Python | 3.12 (3.11+ supported) | Backend, agents, workload, probes |
| Git | 2.39 | Version control |

## Python libraries
| Library | Purpose |
|---|---|
| FastAPI, uvicorn | Workbench API (loopback only) |
| PyYAML | Compose/config parsing |
| requests | Workload generator, smoke test |
| httpx, jsonschema | Tests and contract validation (dev) |

## AI models
| Model | Where used | Notes |
|---|---|---|
| _none yet_ | Planner is deterministic (`AI_PROVIDER=none`) | Every LLM feature must have a no-API-key fallback |

## AI coding assistants used during development
| Tool | Purpose |
|---|---|
| Claude Code (Claude Opus 5.5) | Scaffolding, Ditto deployment, scripts |

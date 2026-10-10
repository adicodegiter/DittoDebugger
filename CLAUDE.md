# Project: AI-Driven Chaos Engineering for a Connected-Vehicle Digital Twin Backend

## What we are building
A 2-day Bosch (BGSW) hackathon project. A coordinated multi-agent AI system that discovers
the architecture of a cloud-native app running locally, plans and safely injects controlled
failures, observes the impact, and produces a ranked, evidence-backed findings report with
recommended fixes and a resilience score.

- **Application under test:** Eclipse Ditto (digital-twin platform), pinned release, deployed
  locally with Docker Compose, driven by a simulated fleet of vehicles sending telemetry.
- **Pitch line:** AI-driven chaos engineering for a connected-vehicle digital-twin backend,
  built on Eclipse Ditto (a Bosch-originated platform).
- This is ONE coordinated system, not five separate projects.

## Hard rules (from the hackathon brief; never break these)
- Everything runs ONLY on our own machines (localhost or the team's private network).
  No public sandboxes, no cloud services, no external endpoints in the app under test.
- Never affect anything outside our own Ditto containers: not the host network, the Docker
  daemon, other machines, other teams, or shared infrastructure.
- LLMs never execute anything. Only the deterministic chaos runner executes, and only
  predefined actions on allowlisted targets from an approved, immutable plan.
- Every experiment MUST have: a defined rollback, a max duration, abort thresholds, and
  verified recovery. No experiment runs without the safety controller's approval.
- Disruptive execution stays disabled until milestones M0–M3 pass.
- Ask before destructive commands (docker system prune, volume deletion, rm -rf, anything
  outside this repo).
- Pin all image versions. Never use `latest`.
- No API keys in code. Read secrets from environment variables / `.env` (gitignored).
  Every LLM feature must have a working no-API-key fallback.
- Never report a healthy baseline if required metrics are missing.

## Architecture

```
            Ditto target application (pinned, Docker Compose)
   nginx -> gateway -> policies / things / things-search / connectivity -> MongoDB
                 ^                                          |
   workload: simulated vehicle fleet          metrics + live stream + probes
                 |                                          v
 +----------------------------- AI agents ------------------------------+
 | 1 Discovery -> 2 Topology -> 3 Telemetry -> 4 Planner -> 5 Diagnosis  |
 +--------------------------------^-------------------------------------+
                Supervisor / orchestrator (validates + records state)
                                  |
          Safety controller (deterministic) -> Chaos runner (deterministic)
                                  |
            Dashboard, evaluation, reports, resilience score
```

### AI agents (may use an LLM for explanation; outputs are structured records)
1. **Discovery agent** — extracts services, images, ports, health checks and config
   dependencies from the actual Ditto deployment. Records source + confidence per fact.
2. **Topology agent** — builds a versioned dependency graph and impact paths. Every edge is
   labelled `documented`, `configured`, or `runtime-observed` (manual additions marked `manual`).
3. **Telemetry agent** — collects metrics, establishes baselines, checks freshness and
   coverage, flags anomalies. Emits normalized observations, not raw logs.
4. **Experiment planner** — ranks candidate experiments by impact, novelty, uncertainty,
   risk, graph coverage and previous outcomes, with a one-line reason for each.
5. **Diagnosis and explanation agent** — compares predicted vs observed behavior and produces
   evidence-linked findings, severity ranking and remediation recommendations.

### Deterministic control systems (NOT LLM agents)
- **Supervisor / orchestrator** — coordinates agents via versioned structured records, never
  free-form agent-to-agent prompts; validates every agent output against schemas.
- **Safety controller** — target allowlist, human approval, immutable experiment plans,
  abort limits (the kill switch).
- **Chaos runner** — executes only approved, bounded, predefined actions; performs cleanup
  and verifies recovery.

## SLIs (what we measure, from the user's point of view)
1. **Write path:** success rate + p50/p95 latency of telemetry writes
2. **Freshness:** staleness = now − telemetry timestamp, seen via the SSE live stream
3. **Search path:** success rate + latency of fleet search queries
Plus container health and resource metrics (Prometheus or compatible source).
**Recovery time** = time from rollback until all three SLIs are back within baseline.

## Abort thresholds (starting values; tune after the baseline exists)
| Signal | Abort when | Window |
|---|---|---|
| Write error rate | > 20% | last 30 s |
| Write p95 latency | > 3x baseline p95 | last 30 s |
| Freshness p95 staleness | > 30 s | last 30 s |
| Any experiment | exceeds `max_duration_s` | — |

## Allowed fault types (predefined actions only)
container stop, container pause, network delay/loss (inside the target container's network
namespace only), MongoDB CPU throttle (`docker update --cpus`), capped disk fill inside our
MongoDB volume (rollback deletes it), traffic burst via the workload generator.
Combined failures are a Day-2 stretch goal.

## Repo layout
```
backend/app/
  main.py               # API (Person 2)
  settings.py           # config + pinned Ditto release (Person 1)
  agents/
    discovery.py        # Person 1
    mapping.py          # topology agent (Person 2)
    telemetry.py        # Person 3
    planning.py         # Person 4
    diagnosis.py        # Person 4
  safety/               # safety controller (Person 5)
  run/                  # chaos runner (Person 5)
  evaluation/           # recovery checks, resilience score (Person 5)
schemas/                # shared versioned contracts (Person 2 publishes first)
configs/
  experiment-policy.yaml  # allowlist, fault catalog, thresholds (Person 5)
deploy/ditto/           # pinned compose files, health_check.sh, reset.sh (Person 1)
scripts/workload/       # bootstrap.py, fleet_sim.py, smoke_test.py (Person 3)
scripts/probes/         # SSE freshness subscriber, search prober (Person 3)
frontend/               # dashboard: graph, experiment history, findings (Person 2)
docs/                   # architecture overview, findings report
data/                   # runtime metrics + experiment records (gitignored)
vendor/                 # cloned upstream Ditto (gitignored)
tests/
TOOLS.md                # running list of tools, libraries, AI models (for the team form)
```

## Ownership
| Person | Owns | Deliverable |
|---|---|---|
| 1 | Ditto deployment + discovery agent | Verified service inventory from the actual deployment |
| 2 | Topology agent, schemas/API contracts, dashboard | Versioned architecture map behind stable interfaces |
| 3 | Telemetry agent, baselines, fleet workload + probes | Reliable baseline and experiment measurements |
| 4 | Planner + diagnosis agents, LLM explanations | Planner that explains its choices; diagnosis that explains outcomes |
| 5 | Safety controller, chaos runner, evaluation | Safe, recovery-tested execution path |

Boundaries: discovery owns factual service records; topology owns edge semantics; telemetry
provides normalized observations; planning consumes graph IDs, metric references and
history; only Person 5's runner executes anything.

## Shared data contracts
- All records are versioned (`schema_version`) JSON validated against `schemas/`.
- Metric observations: JSON Lines in `data/metrics/`, ISO-8601 UTC timestamps, e.g.
  `{"ts": "...", "sli": "write", "target": "bosch.fleet:vehicle-07", "ok": true, "status": 204, "latency_ms": 42}`
- Experiment plan (immutable once approved):
  `{"id", "target", "fault", "params", "rollback", "max_duration_s", "abort_thresholds",
    "predicted_impact": {"sli": ...}, "reason", "approved_by", "approved_at"}`
- Experiment result: start/stop/rollback times, abort reason (if any), observed impact per
  SLI, recovery time, evidence references.
- Schema changes are additive and backward-compatible; breaking changes need a version bump
  and a migration note.

## Milestones (mapped to the brief)
| Milestone | Content | Brief checkpoint |
|---|---|---|
| M0 | Each person verifies Git, Python, Node, Docker, ports; Ditto pinned and healthy; smoke test passes | Day 1: setup and app selection |
| M1 | Discovery inventory + versioned dependency graph | Day 1: application mapping |
| M2 | Fleet workload running; healthy baseline with full metric coverage | Day 1: monitoring baseline |
| M3 | Planner proposes a safe experiment; safety controller rejects unsafe proposals | Day 1: safety controls |
| M4 | One short, approved, isolated experiment (stop `things-search` 60 s) + kill switch proven by forced abort | Day 1 minimum |
| M5 | 3+ fault types run; diagnosis compares predicted vs actual; ranked findings + fixes | Day 2: experiments, analysis |
| M6 | Resilience score, dashboard, README, architecture page, findings report, demo video | Day 2: polish + submission |

M0–M4 must be done by the Day-1 checkpoint. If Ditto is not healthy with the workload
running by 13:00 on Day 1, fall back to OWASP crAPI (only deployment, workload and
service names change).

## Known blockers to resolve in M0
- Docker unavailable in the current implementation environment: run Ditto on a teammate's
  laptop with Docker (16 GB+ RAM preferred) and point others at it via `DITTO_URL`.
- Local Prometheus-backed baseline not yet available: add Prometheus (and cAdvisor for
  container metrics) to the compose stack, or use the probe SLIs until it works.
- No Git remote / GitHub CLI: create the team repo and add the remote before branching.

## Working conventions
- Python 3.11+, minimal dependencies; Node only for the dashboard.
- One branch per person; pull requests into `main`; merge at each checkpoint.
- Small, working increments; verify each step actually runs before moving on.
- Tests for: malformed/missing manifests (discovery), schema validation, and end-to-end
  proof that forbidden targets and actions are rejected (safety).
- Every script has `--help` and sensible defaults.
- Keep `README.md` (setup + run steps) and `TOOLS.md` current; both feed graded deliverables.

## Final deliverables (Day 2)
1. Source code: public repo + README (setup and run)
2. Demo video (3 min or less): failure injected, impact observed, findings reported
3. Architecture overview (1 page): components, how the AI decides, safety controls
4. Findings report: weaknesses ranked by severity, recommended fixes, resilience score
5. Team form: members, tools and AI models, third-party libraries, data used
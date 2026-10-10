# Hackathon Demo Runbook

## Demo Claim

Show that the system chooses a valuable, safe, previously untested failure experiment from evidence; it does not randomly kill a container and ask an LLM to explain logs afterward. All steps use an isolated local Ditto deployment, synthetic data, and explicit operator approval.

## Preflight (Before Stage)

- Pin and start Eclipse Ditto `3.9.8`; record Docker image tags, host resource allocation, and Compose project name.
- Confirm all five service health probes, MongoDB, and API access. Review/replace sample local auth values and verify nothing binds publicly.
- Map each documented topology edge to its evidence source and confidence. Show Pekko cluster membership without fabricating request-level paths.
- Verify `/metrics` on each service's port `9095` through loopback-only mappings. Confirm metric names and status labels on the actual tag.
- Run the selected official Artillery profile at low rate. Confirm whether Kafka/MMock are required for that exact profile; use a dedicated synthetic Thing namespace and prove cleanup.
- Take a stable healthy baseline, check the API canary, and check host resource capacity. Do not proceed on a degraded/unknown baseline.

## 4-Minute Sequence

1. **Architecture (45 sec):** show the five Ditto services, MongoDB/reverse proxy, Pekko cluster relationship, and evidence/confidence labels. Point out which runtime paths remain unknown.
2. **Baseline (30 sec):** show version, workload, API success/p95, service health, and available metrics. Explain that missing metrics lower coverage rather than being guessed.
3. **Planning (45 sec):** show candidate ranking. Contrast a new Gateway restart with a repeated low-information candidate; expose impact, novelty, uncertainty, residual risk, and exact evidence references.
4. **Approval (20 sec):** inspect target/action/duration/abort/cleanup fields and explicitly approve. Show that rejection or expired approval cannot execute.
5. **Experiment (60 sec):** run one 10-second Gateway container restart while the bounded client workload continues. Observe errors/latency and health. Runner restarts the service, then verifies `/alive` plus a functional API canary.
6. **Learning/report (40 sec):** compare predicted and observed effects, recovery time, affected services, safety/cleanup status, score components and coverage. Show the evidence-linked finding/recommendation, then rerank using the stored result.

## Expected Observable Outcome

Gateway health and API success should dip during a deliberate Gateway restart and return after recovery. Other component health and persistence should remain stable; if the actual behavior differs, report that observation rather than forcing the expected result. The final report includes the exact image version, workload, timestamps, metric coverage, policy decision, predicted/actual impacts, recovery verification, score formula/version, and cleanup status.

## Stop Conditions and Backup

Do not run if any baseline service is unhealthy, metrics are missing, host resources are constrained, authorization is uncertain, or cleanup was not verified. Abort if an unrelated service degrades, configured rate/resource thresholds are crossed, or observations stop. If the runner cannot restore the container, stop the workload and use the documented local `docker compose up -d` recovery for the pinned Ditto project; do not continue to another experiment.

For a demo fallback, replay a clearly labeled synthetic fixture and show the planner/scorer output as a simulation. Never present fixture data as a live Ditto experiment.
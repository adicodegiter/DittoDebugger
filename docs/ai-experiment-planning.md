# AI-Assisted Experiment Planning

## Inputs and Candidate Generation

Inputs are a versioned service graph with edge provenance/confidence, baseline metrics and workload, prior predictions/results, the fixed experiment catalog, and deterministic safety policy. The MVP catalog contains one action: restart one allow-listed local Ditto container for a bounded interval. Generate at most one candidate per allowed target; do not generate shell commands or arbitrary fault payloads.

Candidates record target/action/duration, preconditions, hypothesis, predicted affected components, metric evidence, residual risk, expected information value, and approval requirement. Every prediction links to source observation/graph IDs. A candidate may be withheld when its graph confidence or telemetry coverage is inadequate.

## Ranking and Learning

The initial rank is a deliberately small, inspectable heuristic, not an industry standard:

$$
U(e)=0.40I(e)+0.35N(e)+0.25Q(e)
$$

where each term is in $[0,1]$:

- $I(e)$ is expected impact, derived from the target's measured traffic and documented graph reach, with uncertain edges discounted.
- $N(e)$ is novelty: the fraction of applicable target/action/failure-mode coverage not yet exercised.
- $Q(e)$ is uncertainty, based on evidence quality and the number/consistency of comparable prior runs.

Apply a deterministic residual-risk veto/threshold before presenting candidates; among otherwise similar candidates, prefer lower residual risk and better recovery observability. The numerical weights are initial tunable demo values and must be changed only with a decision record. The planner shows component terms, sources, missing evidence, and alternatives so judges can reproduce why it selected an experiment.

Store prediction and outcome separately. Update coverage counts and calibration after each run. For a simple empirical failure-probability estimate per action/target, use a declared Beta(1,1) prior and posterior mean $(f+1)/(n+2)$, where $f$ is observed failure evidence and $n$ comparable completed runs. Keep this as a small-sample estimate with uncertainty; do not present it as a production probability. A failed run caused by a telemetry gap or unsafe condition is not a resilience failure observation.

The first demonstrable learning loop: (1) rank untested Gateway restart above a repeated low-information candidate, (2) show predicted impact and uncertainty, (3) run only after approval, (4) compare predicted vs actual availability/recovery/affected services, (5) update target/action history and rerank. A deterministic planner can satisfy this workflow; LLM summarization is not the selection mechanism.

## Deterministic Rules vs Probabilistic Model

**Deterministic:** topology ingestion, metric normalization, candidate catalog, scoring arithmetic, service/action allow-list, baseline checks, max duration/concurrency, approval freshness, abort/cleanup, API state transitions, and resilience score. The LLM has no credentials, Docker socket, shell tool, approval authority, or policy-write path.

**Optional LLM:** given redacted structured topology, metric deltas, and prediction/outcome pairs, return bounded root-cause hypotheses and remediation text with evidence IDs, confidence, and explicit alternatives. Validate the response schema and evidence IDs; discard unsupported claims. If the provider is absent, timeouts, or emits invalid data, use deterministic templates and mark the analysis as non-LLM.

Never treat an LLM confidence score as measured probability. Do not send raw logs, secret-bearing configs, personal data, or externally hosted telemetry. Model-generated output is advisory and must be reviewed by the human operator.

## Analysis Workflow

1. Normalize static graph, health, Prometheus, workload, and run-history data with source, units, time window, and confidence.
2. Generate fixed candidates and calculate impact, novelty, uncertainty, and residual risk.
3. Reject candidates deterministically that violate scope, policy, baseline, available data, risk, or resource constraints.
4. Sort remaining candidates by $U(e)$, then lower risk; show top candidate plus alternatives, evidence and missing inputs.
5. Request human approval and record approver/time/expiry. Approval does not itself execute.
6. Store expected impact, recovery deadline, metrics, and abort conditions before execution.
7. Execute the fixed adapter action; compare actual and predicted effects and recovery.
8. Record evidence and update coverage/calibration. Generate optional grounded hypotheses and recommendations.
9. Recompute future priorities from the updated history. Keep score/ranking versioned for reproducibility.

## Evaluation of Planner Quality

Track candidate coverage, fraction of recommended experiments accepted, rate of useful new evidence, prediction precision/recall against observed affected components, Brier score when calibrated probabilities are available, repeated low-information selections, safety rejects, and invalid/unsupported AI claims. Small hackathon samples are descriptive only; do not claim statistically proven model quality. Record user ratings of recommendation relevance, evidence, and actionability separately from the resilience score.
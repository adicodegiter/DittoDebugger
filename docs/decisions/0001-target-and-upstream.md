# ADR 0001: Use Eclipse Ditto as an External Test Target

- **Status:** accepted for blueprint; deployment preflight pending
- **Date:** 2026-10-10

## Context

The team selected a Bosch/IoT-relevant digital-twin application for a resilience hackathon. Eclipse Ditto's official docs describe five microservices, an upstream Docker Compose deployment, a Pekko service cluster, MongoDB persistence, health probes, Prometheus metrics, and a separate official load-test tool.

## Decision

Target [eclipse-ditto/ditto](https://github.com/eclipse-ditto/ditto), pin release `3.9.8` for the initial preflight, and keep its source in an ignored external checkout. Do not fork, vendor, or silently patch it. Run only isolated local synthetic tests. The tool's adapter is read-only except the separately approved fixed local fault action.

## Consequences

This preserves upstream ownership/licensing and enables reproducible local testing. Five app services do not satisfy a ten-application-service requirement; supporting containers must not be mislabeled. The official benchmark has extra infrastructure/prerequisites. Pin and revalidate on version updates. Public publishing waits for Bosch/employer IP approval.
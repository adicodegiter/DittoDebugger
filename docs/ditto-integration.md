# Ditto Integration Plan

## Target Identity and Verification

The selected project is **Eclipse Ditto**, the Eclipse IoT digital-twin framework. Official upstream: [https://github.com/eclipse-ditto/ditto](https://github.com/eclipse-ditto/ditto); project documentation: [https://eclipse.dev/ditto/](https://eclipse.dev/ditto/). These are the exact project named in the hackathon context; no second Ditto target is indicated. Facts below were checked on 2026-10-10. The upstream repository's latest release shown at that check was `3.9.8`; pin that release for repeatability and refresh this note if the team selects another version.

Sources: [README and getting started](https://github.com/eclipse-ditto/ditto#readme), [architecture overview](https://eclipse.dev/ditto/architecture-overview.html), [running Ditto](https://eclipse.dev/ditto/installation-running.html), [Docker deployment README](https://github.com/eclipse-ditto/ditto/blob/master/deployment/docker/README.md), [operations and monitoring](https://eclipse.dev/ditto/installation-operating.html), and the [Artillery load-test README](https://github.com/eclipse-ditto/ditto/blob/master/benchmark-tool/README-artillery.md). The documentation site describes development documentation; validate against the pinned tag before coding.

## Verified Architecture and Dependencies

Official documentation describes five cooperating Ditto microservices:

| Service | Documented responsibility |
| --- | --- |
| Policies | Persist and enforce policies/authorization |
| Things | Persist and enforce Things and Features |
| Things-Search | Track changes, maintain optimized search index, execute searches |
| Gateway | HTTP and WebSocket API boundary |
| Connectivity | Manage external broker/endpoint connections and protocol/payload mapping |

They run in one Pekko cluster and communicate asynchronously over TCP using serialized signals. There is no additional broker between Ditto's own services. MongoDB is the backing datastore. The example Docker deployment adds nginx as reverse proxy; its Compose file also includes the Ditto UI and Swagger UI. Thus the default Compose project has five application services and supporting containers, not ten Ditto application microservices. The separate load-test setup can add Kafka and MMock; count them only as supporting components if the judges' rubric explicitly allows it.

The Connectivity service can create client connections to external Kafka, MQTT, AMQP, and HTTP endpoints. Such a broker is an optional integration for Ditto itself; Kafka is listed as a prerequisite by the official Artillery benchmark setup. Don't conflate these two deployments.

## Deployment and Startup

Official options include Docker Compose, Kubernetes/Helm, k3s, Minikube, OpenShift, and Azure. For this hackathon choose the upstream Docker Compose example with prebuilt images, not a source build. Upstream estimates at least 2 CPU cores and 4 GB RAM available to Docker for a single local instance. Building Ditto from source is a separate task and currently calls for JDK 25+ and Maven 3.9+.

The repository root README provides PowerShell commands to clone `3.9.8` into ignored `.local/ditto-upstream` and run the upstream Compose file. It does not copy Ditto files into this repository or alter the upstream checkout. Validate the Compose command and tag in the preflight before a demo. The upstream Compose sample has development authentication/configuration; review and replace sample credentials locally. Never bind it to a public interface.

## Health, Metrics, and Tracing

- The current upstream Docker Compose health checks call `http://<container>:7626/alive` for Ditto service containers. This is an internal container health probe, not automatically reachable from the host and not proof that a user-level API operation succeeds. Recovery must also run a functional API canary.
- Ditto services publish Prometheus exposition metrics on HTTP port `9095` by default, path `/`. The upstream deployment docs describe JVM metrics across services, Gateway request round-trip/status metrics, MongoDB operation/latency metrics for persistence services, and Connectivity processing/mapping metrics. Exact metric names/labels are release-sensitive; inspect actual scrape output before freezing queries.
- The Compose file does not publish each service's metrics port to the host by default. Add a project-owned local Compose override with explicit `127.0.0.1` port bindings (one unique host port per service) before Prometheus can scrape them. Do not edit the upstream Compose file.
- Logs default to stdout/stderr. Ditto supports W3C trace-context propagation and OTLP trace export, but tracing/reporting are disabled by default. Enable only in the isolated demo and verify exporter configuration; spans can improve observed edges but do not replace static provenance.
- Service `/alive` probes, API success/latency, and recovery timing are different signals. Keep each as a separate observation.

## Load Generation

The current official tool is TypeScript/Artillery under `benchmark-tool/artillery-test`; the old k6-based benchmark documentation says it is deprecated/replaced. The current README lists Node.js 18+, a running Ditto instance, Kafka with topic deletion enabled, and MMock for HTTP push endpoints. It supports HTTP, WebSocket twin/live, and Kafka scenarios, with warmup/read/search/modify/live-message operations. It can create and delete Things, connections, and Kafka topics. The load tool can therefore mutate data and must run only against the isolated local installation, with a unique namespace and cleanup verification.

Start with a minimal, bounded HTTP read/search profile and `CREATE_THINGS`/connection creation disabled where the selected config permits. The README's prerequisites are broad; preflight whether the chosen HTTP-only profile truly runs without Kafka/MMock rather than silently assuming. Avoid load-test defaults aimed at performance benchmarking; set low arrival rate and duration.

## Integration Approach and Limitations

1. Pin `3.9.8`, inventory actual Compose services, environment, health checks, image tags, ports, networks, and restart policy read-only.
2. Build base graph nodes from the five documented microservices plus MongoDB, nginx, UI, and Swagger UI when present. Use Compose dependencies/network membership with explicit evidence labels.
3. Represent Pekko membership as a cluster relationship, not invented per-request edges. Add runtime edges only when traces or metrics supply credible evidence; flag correlations as inferred.
4. Read health through Docker metadata or loopback-only probes; collect metrics from the mapped per-service Prometheus endpoints; measure user-facing success with a bounded API canary/load tool.
5. Keep Ditto discovery read-only. Never call DevOps endpoints for topology discovery unless credentials are separately authorized, scoped, and available only to the operator; do not place privileged credentials in the AI process.

Limitations: default Compose is single-instance and has no high-availability guarantee; health checks only indicate service health at their probe; default metrics ports are internal; default trace export is off; test benchmark dependencies add setup and mutation risk; static Compose describes configured relationships, not every runtime call; chaos-testing peers in the Pekko cluster may cause broad effects. The first fault should be one short gateway or Things-Search restart, not MongoDB failure or a cluster-wide network partition.

## Licensing and Separation

The upstream `LICENSE` is Eclipse Public License 2.0 and its repository includes notices. This repository's original files use MIT, selected for simple reuse of standalone custom work; MIT asks recipients to retain notices and disclaims warranty, but does not include Apache-2.0's express patent grant. It does not change Ditto's license. Keep Ditto as an ignored external checkout or, only if there is a clear reproducibility need, a pinned Git submodule that remains separately licensed. Do not vendor upstream source, copy files without license review, or claim endorsement. Confirm Bosch hackathon/employer contribution and public-release terms before publishing.
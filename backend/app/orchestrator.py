from __future__ import annotations

from typing import Any

from .agents.discovery import DittoDiscoveryAgent
from .agents.mapping import ArchitectureMapperAgent
from .agents.planning import ExperimentPlanningAgent
from .agents.telemetry import TelemetryObservabilityAgent
from .settings import Settings
from .store import LocalRepository


class AgentOrchestrator:
    """Coordinates specialists; each agent returns evidence-bearing records."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.discovery_agent = DittoDiscoveryAgent(settings.compose_file, settings.kubernetes_manifests)
        self.mapping_agent = ArchitectureMapperAgent()
        self.telemetry_agent = TelemetryObservabilityAgent(settings.prometheus_url)
        self.repository = LocalRepository(settings.database_path)
        self.planning_agent = ExperimentPlanningAgent(settings.policy_path, self.repository)

    def discover_architecture(self) -> dict[str, Any]:
        report = self.discovery_agent.discover()
        return self.mapping_agent.map(report)

    def collect_telemetry(self) -> dict[str, Any]:
        return self.telemetry_agent.collect()

    def capture_baseline(self) -> dict[str, Any]:
        graph = self.discover_architecture()
        if graph["status"] != "available":
            raise ValueError("No discovered deployment is available for a baseline.")
        telemetry = self.collect_telemetry()
        return self.repository.save_baseline(graph["graph_version"], telemetry)

    def plan_experiments(self, baseline_id: str, max_candidates: int) -> dict[str, Any]:
        graph = self.discover_architecture()
        telemetry = self.collect_telemetry()
        baseline = self.repository.get_baseline(baseline_id)
        if baseline is None:
            raise LookupError("Baseline was not found.")
        return self.planning_agent.plan(graph, telemetry, baseline, max_candidates)

    def agent_status(self) -> list[dict[str, str]]:
        discovery = "ready" if self.settings.compose_file.is_file() or any(path.is_file() for path in self.settings.kubernetes_manifests) else "waiting_for_manifest"
        return [
            {"id": "ditto_discovery", "name": self.discovery_agent.name, "status": discovery},
            {"id": "architecture_mapping", "name": self.mapping_agent.name, "status": "ready"},
            {"id": "telemetry_observability", "name": self.telemetry_agent.name, "status": "ready_to_poll"},
            {"id": "experiment_planning", "name": self.planning_agent.name, "status": "blocked_until_baseline"},
        ]
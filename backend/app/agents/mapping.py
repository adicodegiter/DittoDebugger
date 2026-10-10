from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .discovery import DITTO_ROLES, DiscoveryReport


DITTO_CLUSTER_MEMBERS = set(DITTO_ROLES)


@dataclass(frozen=True)
class ArchitectureMapperAgent:
    name: str = "Architecture and Dependency Mapping Agent"

    def map(self, report: DiscoveryReport) -> dict[str, Any]:
        nodes = [component.to_dict() for component in report.components]
        relationships = [relationship.to_dict() for relationship in report.relationships]
        ditto_components = [
            node for node in nodes
            if node["id"] in DITTO_CLUSTER_MEMBERS or node.get("labels", {}).get("ditto_role") in DITTO_ROLES.values()
        ]
        ditto_members = sorted(node["id"] for node in ditto_components)
        discovered_roles = {
            node.get("labels", {}).get("ditto_role", DITTO_ROLES.get(node["id"]))
            for node in ditto_components
        }
        component_ids = {node["id"] for node in nodes}
        clusters = []
        if ditto_members:
            clusters.append({
                "id": "ditto-pekko-cluster",
                "members": ditto_members,
                "source": "ditto_docs:architecture-overview",
                "confidence": 1.0,
                "complete": discovered_roles == set(DITTO_ROLES.values()),
                "relationship": "documented_cluster_membership_not_request_flow",
            })

        dependent_counts = {component_id: 0 for component_id in component_ids}
        for relationship in relationships:
            if relationship["relation"] in {"compose_depends_on", "configured_database_host", "kubernetes_service_selector"}:
                dependent_counts[relationship["target"]] = dependent_counts.get(relationship["target"], 0) + 1
        maximum_dependents = max(dependent_counts.values(), default=0)
        criticality = {
            component_id: {
                "configured_dependents": count,
                "relative_score": count / maximum_dependents if maximum_dependents else 0.0,
                "evidence_type": "static",
            }
            for component_id, count in sorted(dependent_counts.items())
        }
        canonical_graph = {
            "nodes": nodes,
            "edges": relationships,
            "clusters": clusters,
            "network_zones": [zone.to_dict() for zone in report.network_zones],
            "criticality": criticality,
        }
        graph_version = hashlib.sha256(json.dumps(canonical_graph, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:16]
        return {
            "status": report.status,
            "graph_version": graph_version,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **canonical_graph,
            "source_files": list(report.source_files),
            "warnings": list(report.warnings),
        }
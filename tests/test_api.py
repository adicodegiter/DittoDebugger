from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import create_app
from app.settings import Settings


class LocalApiTests(unittest.TestCase):
    def test_health_and_dashboard_are_local_workbench_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(
                compose_file=root / "missing-compose.yml",
                kubernetes_manifests=(),
                prometheus_url="http://127.0.0.1:9090",
                database_path=root / "workbench.sqlite3",
                policy_path=ROOT / "configs" / "experiment-policy.yaml",
            )
            client = TestClient(create_app(settings))
            health = client.get("/api/v1/health").json()
            architecture = client.get("/api/v1/architecture").json()
            dashboard = client.get("/")
        self.assertFalse(health["execution_enabled"])
        self.assertEqual(architecture["status"], "unavailable")
        self.assertEqual(architecture["nodes"], [])
        self.assertEqual(dashboard.status_code, 200)
        self.assertIn("System overview", dashboard.text)

    def test_execute_endpoint_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(root / "missing.yml", (), "http://127.0.0.1:9090", root / "db.sqlite3", ROOT / "configs" / "experiment-policy.yaml")
            response = TestClient(create_app(settings)).post("/api/v1/experiments/test/execute")
        self.assertEqual(response.status_code, 503)
        self.assertIn("disabled", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
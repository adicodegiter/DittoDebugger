"""Shared settings for all project scripts.

Values come from environment variables, falling back to the repo-root .env file
(gitignored), then to the local-only defaults of the Ditto docker deployment.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
METRICS_DIR = DATA_DIR / "metrics"

NAMESPACE = "bosch.fleet"
POLICY_ID = f"{NAMESPACE}:policy"


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader: KEY=VALUE lines; never overrides existing env vars."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(REPO_ROOT / ".env")

DITTO_URL = (os.environ.get("DITTO_URL") or os.environ.get("DITTO_BASE_URL")
             or "http://127.0.0.1:8080").rstrip("/")
DITTO_USER = os.environ.get("DITTO_USER", "ditto")
DITTO_PASS = os.environ.get("DITTO_PASS", "ditto")
AUTH = (DITTO_USER, DITTO_PASS)
API = f"{DITTO_URL}/api/2"


def policy_body(user: str = DITTO_USER) -> dict:
    """Policy granting the (nginx pre-authenticated) user full access to fleet twins."""
    return {
        "entries": {
            "owner": {
                "subjects": {f"nginx:{user}": {"type": "basic auth user via nginx"}},
                "resources": {
                    "policy:/": {"grant": ["READ", "WRITE"], "revoke": []},
                    "thing:/": {"grant": ["READ", "WRITE"], "revoke": []},
                    "message:/": {"grant": ["READ", "WRITE"], "revoke": []},
                },
            }
        }
    }

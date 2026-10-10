# Deployment and Local Development

## Stage-1 Environment

The only runnable application at this stage is upstream Ditto. This custom repository intentionally has no root `docker-compose.yml`: the workbench API, Prometheus wiring, and dashboard do not exist yet, so a compose file now would imply a complete stack when it is not. The first integration milestone will add a project-owned Compose override for observability and a pinned custom API image only after their ports and health checks are verified.

Requirements for upstream's single-instance Docker Compose sample: Docker daemon and Compose v2, at least 2 CPU cores and 4 GB RAM available to Docker, network access to fetch the pinned source/images, and enough free disk for images and synthetic data. Use the PowerShell commands in the root README. Ditto's sample can open HTTP/API and database ports on the host; inspect `docker compose config` and bind any additional ports only to `127.0.0.1`.

## Environment and Secrets

`.env.example` contains endpoint defaults only. Copy it to `.env` only when an implemented service needs local overrides; `.env` is ignored. Store credentials in a local secret manager or process environment, never in files committed to Git. Do not copy the upstream's `nginx.htpasswd`, development DevOps password, tokens, or private certificates into this repository. Keep the Ditto DevOps API disabled or inaccessible to the planner/LLM; if an integration test needs it, use a dedicated local credential with minimal scope.

`configs/telemetry.yaml` shows the intended per-service metric targets (`19095`-`19099`) but they are not ports provided by Ditto. During P0, add a separate, uncommitted/local-only Compose override with those ports bound to `127.0.0.1`, or use another verified private scrape network. Then run Prometheus on a private Compose network and confirm every target returns the expected exposition format. Do not expose metrics or Prometheus to the LAN.

## Development Checks

Python 3.12+ is required for the planned API. The current scaffold has only schema/YAML test dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

When implemented, the local developer workflow will start Ditto separately, start Prometheus and the workbench from the project-owned Compose file, wait for health, run contract/unit tests, and use a low-rate synthetic test namespace. `docker compose down` must stop only the named local project. The workbench must not default to host/LAN binding.

## Release/Publication

GitHub Actions validates contracts and scans for secrets. Before public release, confirm Bosch hackathon/employer permission and authorship, pin all images/actions/dependencies, run a dependency CVE check and license inventory, verify secret scanning/push protection, review the generated Docker/network configuration, and test cleanup from an interrupted experiment. Local `git init` is complete; no remote has been added and no public repository has been created or pushed.
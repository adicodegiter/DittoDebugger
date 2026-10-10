from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .orchestrator import AgentOrchestrator
from .settings import REPOSITORY_ROOT, Settings


class PlanRequest(BaseModel):
    baseline_id: str = Field(min_length=1, max_length=100)
    max_candidates: int = Field(default=3, ge=1, le=10)


def create_app(settings: Settings | None = None, orchestrator: AgentOrchestrator | None = None) -> FastAPI:
    application = FastAPI(
        title="Ditto AI Chaos Engineering Workbench",
        version="1.0.0",
        description="Local-only, evidence-backed discovery and experiment planning. Fault execution is disabled in this build.",
    )
    application.state.orchestrator = orchestrator or AgentOrchestrator(settings or Settings.from_environment())

    @application.get("/api/v1/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "execution_enabled": False,
            "agents": application.state.orchestrator.agent_status(),
            "notes": ["Health reports workbench process state only; it does not imply Ditto or Prometheus is reachable."],
        }

    @application.get("/api/v1/agents")
    def agents() -> dict[str, Any]:
        return {"agents": application.state.orchestrator.agent_status()}

    @application.post("/api/v1/discovery/refresh")
    def refresh_discovery() -> dict[str, Any]:
        try:
            return application.state.orchestrator.discover_architecture()
        except (OSError, ValueError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @application.get("/api/v1/architecture")
    def architecture() -> dict[str, Any]:
        try:
            return application.state.orchestrator.discover_architecture()
        except (OSError, ValueError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @application.get("/api/v1/telemetry")
    def telemetry() -> dict[str, Any]:
        return application.state.orchestrator.collect_telemetry()

    @application.post("/api/v1/baselines")
    def capture_baseline() -> dict[str, Any]:
        try:
            return application.state.orchestrator.capture_baseline()
        except ValueError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @application.post("/api/v1/experiments/plan")
    def plan_experiments(request: PlanRequest) -> dict[str, Any]:
        try:
            return application.state.orchestrator.plan_experiments(request.baseline_id, request.max_candidates)
        except LookupError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @application.post("/api/v1/experiments/{experiment_id}/execute")
    def execute_experiment(experiment_id: str) -> None:
        raise HTTPException(
            status_code=503,
            detail="Fault execution is disabled. Docker is unavailable or the local runner has not passed its safety preflight.",
        )

    @application.get("/")
    def dashboard() -> FileResponse:
        return FileResponse(REPOSITORY_ROOT / "frontend" / "index.html")

    application.mount("/assets", StaticFiles(directory=REPOSITORY_ROOT / "frontend"), name="assets")
    return application


app = create_app()
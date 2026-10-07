import secrets
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import Field

from zip_ds.models import ValidatedModel
from zip_ds.pipeline import ScanSource, run_scan
from zip_ds.queries.providers import ProviderManager
from zip_ds.reporting import PlagiarismReport


class ScanRequest(ValidatedModel):
    document_id: str = Field(min_length=1)
    suspicious_text: str = Field(min_length=1)
    sources: list[ScanSource] = Field(default_factory=list)


class ReportStore:
    """Process-local report store; reports are never persisted to disk."""

    def __init__(self) -> None:
        self._reports: dict[UUID, PlagiarismReport] = {}

    def put(self, report: PlagiarismReport) -> PlagiarismReport:
        self._reports[report.report_id] = report
        return report

    def get(self, report_id: UUID) -> PlagiarismReport | None:
        return self._reports.get(report_id)


def create_app(
    api_key: str | None = None, provider_manager: ProviderManager | None = None
) -> FastAPI:
    """Create the ZIP-DS REST application with an isolated in-memory report store."""
    if api_key is not None and not api_key:
        raise ValueError("api_key must be non-empty when configured")
    app = FastAPI(title="ZIP-DS", version="0.1.0")
    store = ReportStore()

    def authorize(x_api_key: str | None = Header(default=None)) -> None:
        if api_key is not None and (
            x_api_key is None or not secrets.compare_digest(x_api_key, api_key)
        ):
            raise HTTPException(status_code=401, detail="invalid API key")

    @app.post("/v1/scan", response_model=PlagiarismReport)
    def scan(request: ScanRequest, _authorized: None = Depends(authorize)) -> PlagiarismReport:
        report = run_scan(request.document_id, request.suspicious_text, request.sources)
        if provider_manager is not None:
            report = report.model_copy(update={"provider_statuses": provider_manager.statuses()})
        return store.put(report)

    @app.get("/v1/reports/{report_id}", response_model=PlagiarismReport)
    def report(report_id: UUID, _authorized: None = Depends(authorize)) -> PlagiarismReport:
        result = store.get(report_id)
        if result is None:
            raise HTTPException(status_code=404, detail="report not found")
        return result

    return app


__all__ = ["ReportStore", "ScanRequest", "create_app"]

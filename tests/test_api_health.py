from fastapi.testclient import TestClient

from zip_ds.api import create_app
from zip_ds.queries.providers import ProviderClient, ProviderManager


async def provider_call(_query):
    return []


def test_health_endpoint_reports_service_and_provider_status():
    manager = ProviderManager([ProviderClient(name="primary", call=provider_call)])
    client = TestClient(create_app(provider_manager=manager))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "provider_statuses": [{"name": "primary", "available": True, "failed_until": 0.0}],
    }

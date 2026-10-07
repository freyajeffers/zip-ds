from fastapi.testclient import TestClient

from zip_ds.api import create_app
from zip_ds.queries.providers import ProviderClient, ProviderManager


async def provider_call(_query):
    return []


def test_scan_response_includes_provider_statuses():
    manager = ProviderManager([ProviderClient(name="primary", call=provider_call)])
    client = TestClient(create_app(provider_manager=manager))

    response = client.post(
        "/v1/scan",
        json={"document_id": "doc", "suspicious_text": "text", "sources": []},
    )

    assert response.status_code == 200
    assert response.json()["provider_statuses"] == [
        {"name": "primary", "available": True, "failed_until": 0.0}
    ]

from fastapi.testclient import TestClient

from zip_ds.api import create_app


def test_configured_api_key_protects_scan_and_report_routes():
    client = TestClient(create_app(api_key="runtime-secret"))
    body = {"document_id": "doc", "suspicious_text": "text", "sources": []}

    assert client.post("/v1/scan", json=body).status_code == 401
    response = client.post("/v1/scan", json=body, headers={"x-api-key": "runtime-secret"})
    assert response.status_code == 200
    report_id = response.json()["report_id"]
    assert client.get(f"/v1/reports/{report_id}").status_code == 401
    assert (
        client.get(f"/v1/reports/{report_id}", headers={"x-api-key": "runtime-secret"}).status_code
        == 200
    )

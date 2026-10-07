from fastapi.testclient import TestClient

from zip_ds.api import create_app


def test_scan_endpoint_returns_report_and_report_lookup():
    client = TestClient(create_app())
    response = client.post(
        "/v1/scan",
        json={
            "document_id": "doc-api",
            "suspicious_text": "The cat quickly crossed the quiet garden before sunrise.",
            "sources": [
                {
                    "url": "https://example.com/source",
                    "text": "Before sunrise, the cat crossed the quiet garden quickly.",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_id"] == "doc-api"
    report = client.get(f"/v1/reports/{payload['report_id']}")
    assert report.status_code == 200
    assert report.json()["report_id"] == payload["report_id"]


def test_scan_endpoint_rejects_unknown_fields():
    client = TestClient(create_app())
    response = client.post(
        "/v1/scan",
        json={"document_id": "doc", "suspicious_text": "text", "unknown": True},
    )
    assert response.status_code == 422

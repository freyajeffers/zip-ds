from zip_ds.pipeline import ScanSource, run_scan


def test_run_scan_integrates_alignment_and_reporting():
    text = "The cat quickly crossed the quiet garden before sunrise."
    report = run_scan(
        document_id="doc-1",
        suspicious_text=text,
        sources=[
            ScanSource(
                url="https://example.com/source",
                text="Before sunrise, the cat crossed the quiet garden quickly.",
            )
        ],
    )

    assert report.document_id == "doc-1"
    assert report.score.evidence_count == 1
    assert report.score.coverage_score == 1.0
    assert report.evidence[0].alignment_type == "semantic"


def test_run_scan_ignores_sources_below_semantic_threshold():
    report = run_scan(
        document_id="doc-1",
        suspicious_text="Short text only.",
        sources=[ScanSource(url="https://example.com/source", text="Short text only.")],
    )

    assert report.score.evidence_count == 0
    assert report.evidence == []

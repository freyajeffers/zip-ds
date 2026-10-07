from zip_ds.reporting.report import PlagiarismReport, build_report
from zip_ds.reporting.scoring import AlignmentEvidence, calculate_score


def evidence(words: int, confidence: float = 1.0) -> AlignmentEvidence:
    return AlignmentEvidence(
        suspicious_chunk_id="chunk-1",
        source_url="https://example.com/source",
        alignment_type="verbatim",
        matched_word_count=words,
        confidence_score=confidence,
    )


def test_score_suppresses_evidence_shorter_than_seven_words():
    result = calculate_score([evidence(6), evidence(10, 0.8)], total_suspicious_words=20)

    assert result.evidence_count == 1
    assert result.matched_word_count == 10
    assert result.coverage_score == 0.5
    assert result.confidence_score == 0.8


def test_report_contains_typed_score_and_evidence():
    report = build_report(
        document_id="doc-1",
        total_suspicious_words=20,
        evidence=[evidence(10, 0.8)],
    )

    assert isinstance(report, PlagiarismReport)
    assert report.document_id == "doc-1"
    assert report.score.coverage_score == 0.5
    assert len(report.evidence) == 1


def test_score_rejects_invalid_word_total():
    try:
        calculate_score([], total_suspicious_words=0)
    except ValueError as error:
        assert "total_suspicious_words" in str(error)
    else:
        raise AssertionError("expected total word validation")

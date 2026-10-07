from zip_ds import __all__ as root_exports
from zip_ds.parsers import __all__ as parser_exports
from zip_ds.queries import __all__ as query_exports
from zip_ds.stylometry import __all__ as stylometry_exports


def test_package_exports_are_explicit_and_importable():
    assert set(root_exports) >= {"DocumentChunk", "StyleScores", "SearchCandidate", "SourceType"}
    assert set(parser_exports) >= {
        "NormalizedText",
        "SecurityError",
        "normalize_text",
        "read_txt",
        "read_pdf",
        "read_docx",
    }
    assert set(query_exports) >= {
        "QueryBudget",
        "SerpCache",
        "generate_queries",
        "split_chunk_for_queries",
    }
    assert set(stylometry_exports) >= {"analyze"}

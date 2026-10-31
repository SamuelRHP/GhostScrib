"""Unit tests for ghostscrib.integrity citation checking and caching."""

import json
from unittest.mock import MagicMock, patch
from ghostscrib.integrity.cache import CitationCache
from ghostscrib.integrity.matcher import (
    calculate_title_similarity,
    extract_doi,
    extract_search_query_from_reference,
)
from ghostscrib.integrity.verifier import CitationVerifier


def test_doi_extraction():
    ref = "1. Vaswani, A., et al. Attention is all you need. doi: 10.1145/3292500.3330701, 2017."
    assert extract_doi(ref) == "10.1145/3292500.3330701"

    ref2 = "No doi here in this reference string."
    assert extract_doi(ref2) is None


def test_query_extraction_and_similarity():
    ref = "[1] J. Smith. Deep Learning for Distributed Systems. IEEE Trans. 2023."
    query = extract_search_query_from_reference(ref)
    assert "[1]" not in query
    assert "Deep Learning" in query

    sim = calculate_title_similarity("Deep Learning for Distributed Systems", "Deep Learning for Distributed Systems")
    assert sim >= 0.95

    sim_diff = calculate_title_similarity("Deep Learning for Distributed Systems", "Quantum Mechanics Fundamentals")
    assert sim_diff < 0.35


def test_verifier_mocked_verified_doi(tmp_path):
    cache = CitationCache(cache_file=tmp_path / "cache.json")
    verifier = CitationVerifier(cache=cache)

    mock_resp_data = {
        "status": "ok",
        "message": {"title": ["Attention Is All You Need"]},
    }

    ref = "Vaswani et al. Attention is all you need. 10.1145/3292500.3330701"
    with patch("urllib.request.urlopen") as mock_url:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(mock_resp_data).encode("utf-8")
        mock_url.return_value.__enter__.return_value = mock_resp

        res = verifier.verify_single_reference(ref, online=True)
        assert res.status == "verified"
        assert res.matched_doi == "10.1145/3292500.3330701"
        assert res.similarity >= 0.85

        # Test cache hit on second run: urlopen should not be called again
        mock_url.reset_mock()
        res_cached = verifier.verify_single_reference(ref, online=True)
        assert res_cached.status == "verified"
        assert mock_url.call_count == 0


def test_verifier_offline_mode(tmp_path):
    cache = CitationCache(cache_file=tmp_path / "cache.json")
    verifier = CitationVerifier(cache=cache)
    res = verifier.verify_single_reference("A. Turing 1950", online=False)
    assert res.status == "not_checked"


def test_verify_references_batch(tmp_path):
    cache = CitationCache(cache_file=tmp_path / "cache.json")
    verifier = CitationVerifier(cache=cache)

    refs = [
        "Ref 1 with no match",
        "Ref 2 with no match",
    ]
    body = "In text citation [1] and [5] cited here."

    with patch.object(verifier, "verify_single_reference") as mock_single:
        from ghostscrib.schema import ReferenceDetail
        mock_single.side_effect = [
            ReferenceDetail(raw=refs[0], status="verified", similarity=0.9),
            ReferenceDetail(raw=refs[1], status="unverified", similarity=0.2),
        ]
        result = verifier.verify_references(refs, body_text=body, online=True)
        assert result.total == 2
        assert result.verified == 1
        assert result.unverified == 1
        assert result.out_of_range_intext_citations == [5]


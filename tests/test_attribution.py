"""Unit tests for ghostscrib.attribution module."""

import numpy as np
import pytest

from ghostscrib.attribution.classifier import attribute_document, compute_cosine_similarity
from ghostscrib.attribution.features import build_transition_feature_vector, get_rank_bucket
from ghostscrib.attribution.fingerprints import load_fingerprints, save_fingerprint


def test_get_rank_bucket():
    assert get_rank_bucket(0) == 0
    assert get_rank_bucket(5) == 0
    assert get_rank_bucket(10) == 1
    assert get_rank_bucket(99) == 1
    assert get_rank_bucket(100) == 2
    assert get_rank_bucket(999) == 2
    assert get_rank_bucket(1000) == 3
    assert get_rank_bucket(50000) == 3


def test_build_transition_feature_vector():
    bucket_seq = [0, 1, 0, 2, 3, 0, 1, 1, 2, 0]
    entropy_seq = [2.5, 3.1, 1.8, 4.0, 5.2, 2.1, 2.9, 3.0, 3.8, 2.4]

    vec = build_transition_feature_vector(bucket_seq, entropy_seq)
    assert len(vec) == 22
    assert vec.dtype == np.float32

    # Check bucket distribution sum == 1.0
    assert pytest.approx(vec[:4].sum(), 0.001) == 1.0


def test_cosine_similarity():
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v3 = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    assert pytest.approx(compute_cosine_similarity(v1, v2), 0.001) == 1.0
    assert pytest.approx(compute_cosine_similarity(v1, v3), 0.001) == 0.0


def test_attribution_unavailable_on_short_text(tmp_path):
    # Create 2 dummy fingerprints
    save_fingerprint("GPT-4o", np.ones(22, dtype=np.float32), fingerprints_dir=tmp_path)
    save_fingerprint("Claude-3.5", np.ones(22, dtype=np.float32), fingerprints_dir=tmp_path)

    short_text = "This is a short text with very few words."
    res = attribute_document(short_text, fingerprints_dir=tmp_path)
    assert res.status == "unavailable"
    assert "under the 10,000 tokens" in res.reason


def test_attribution_unavailable_insufficient_fingerprints(tmp_path):
    # Only 1 fingerprint
    save_fingerprint("GPT-4o", np.ones(22, dtype=np.float32), fingerprints_dir=tmp_path)

    long_text = "word " * 6000
    res = attribute_document(long_text, fingerprints_dir=tmp_path)
    assert res.status == "unavailable"
    assert "Fewer than 2 candidate fingerprints" in res.reason


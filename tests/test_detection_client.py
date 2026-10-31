"""Unit tests for LukkinenClient with mocked HTTP responses."""

import json
from unittest.mock import MagicMock, patch
import pytest

from ghostscrib.detection.client import DetectorError, DetectorUnavailableError, LukkinenClient


def test_is_healthy_success():
    client = LukkinenClient("http://127.0.0.1:8790")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        assert client.is_healthy() is True


def test_is_healthy_failure():
    client = LukkinenClient("http://127.0.0.1:8790")
    with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")):
        assert client.is_healthy() is False


def test_detect_success():
    client = LukkinenClient("http://127.0.0.1:8790")
    mock_data = {
        "verdict": "likely AI-generated",
        "share_words": {"ai": 0.8, "uncertain": 0.1, "human": 0.1},
        "n_paragraphs": 4,
        "n_skipped": 0,
        "paragraphs": [
            {
                "text": "Sample paragraph text with sufficient length for evaluation.",
                "words": 50,
                "score": 1.25,
                "label": "ai",
                "signals": {"model1": 1.2},
                "sentences": [{"text": "Sample paragraph text.", "score": 1.25}],
            }
        ],
        "structure_traits": [{"trait": "avg_sent_len", "value": 24.5, "human_mean": 21.0, "z": 1.5}],
        "sentence_threshold": 1.0,
        "sentence_threshold_5": 0.0,
        "thresholds": {"ai": 1.0, "uncertain": 0.0},
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(mock_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = client.detect("Sample text")
        assert result["verdict"] == "likely AI-generated"
        assert len(result["paragraphs"]) == 1
        assert result["paragraphs"][0]["label"] == "ai"
        assert len(result["structure_traits"]) == 1


def test_detect_unavailable():
    client = LukkinenClient("http://127.0.0.1:8790")
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        with pytest.raises(DetectorUnavailableError):
            client.detect("Sample text")


def test_detect_http_error():
    client = LukkinenClient("http://127.0.0.1:8790")
    import urllib.error
    from io import BytesIO
    err = urllib.error.HTTPError(
        url="http://127.0.0.1:8790/api/detect",
        code=500,
        msg="Internal Server Error",
        hdrs={},
        fp=BytesIO(b"Server error"),
    )
    with patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(DetectorError):
            client.detect("Sample text")


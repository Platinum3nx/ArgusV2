"""Hosted-mode integration failure tests for ProxyClient.

Exercises retry logic, non-retryable status codes, malformed payloads,
timeouts, and connection errors against the ProxyClient from llm_provider.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import requests

from src.core.llm_provider import MAX_RETRIES, ProxyClient


def _make_client() -> ProxyClient:
    return ProxyClient(
        model="claude-sonnet-4-6",
        proxy_url="http://test",
        proxy_token="tok",
    )


def _mock_response(status_code: int, json_data: dict | None = None) -> MagicMock:
    """Build a fake requests.Response with the given status and JSON body."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.headers = {}
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("No JSON")

    def _raise_for_status():
        if 400 <= status_code < 600:
            exc = requests.HTTPError(response=resp)
            raise exc

    resp.raise_for_status = _raise_for_status
    return resp


class TestHostedFailures(unittest.TestCase):
    """Verify ProxyClient retry/error behaviour under mocked HTTP failures."""

    # ------------------------------------------------------------------
    # 1. 401 Unauthorized -- NOT retryable, must raise immediately
    # ------------------------------------------------------------------
    @patch("src.core.llm_provider.requests.post")
    def test_401_unauthorized(self, mock_post: MagicMock) -> None:
        mock_post.return_value = _mock_response(401)
        client = _make_client()

        with self.assertRaises(requests.HTTPError):
            client.generate("hello")

        # 401 is not in RETRYABLE_STATUS, so only one call should be made
        self.assertEqual(mock_post.call_count, 1)

    # ------------------------------------------------------------------
    # 2. 429 Rate Limit -- retryable, exhausts all retries
    # ------------------------------------------------------------------
    @patch("src.core.llm_provider.random.random", return_value=0.5)
    @patch("src.core.llm_provider.time.sleep")
    @patch("src.core.llm_provider.requests.post")
    def test_429_rate_limit_exhausts_retries(
        self,
        mock_post: MagicMock,
        mock_sleep: MagicMock,
        mock_random: MagicMock,
    ) -> None:
        mock_post.return_value = _mock_response(429)
        client = _make_client()

        with self.assertRaises(requests.HTTPError):
            client.generate("hello")

        self.assertEqual(mock_post.call_count, MAX_RETRIES)
        self.assertEqual(mock_sleep.call_count, MAX_RETRIES - 1)

    # ------------------------------------------------------------------
    # 3. 502 retry then success on third attempt
    # ------------------------------------------------------------------
    @patch("src.core.llm_provider.random.random", return_value=0.5)
    @patch("src.core.llm_provider.time.sleep")
    @patch("src.core.llm_provider.requests.post")
    def test_502_retry_then_success(
        self,
        mock_post: MagicMock,
        mock_sleep: MagicMock,
        mock_random: MagicMock,
    ) -> None:
        fail_resp = _mock_response(502)
        ok_resp = _mock_response(200, {"text": "success"})
        mock_post.side_effect = [fail_resp, fail_resp, ok_resp]
        client = _make_client()

        result = client.generate("hello")
        self.assertEqual(result, "success")
        self.assertEqual(mock_post.call_count, 3)
        # sleep called twice (after first two failures)
        self.assertEqual(mock_sleep.call_count, 2)

    # ------------------------------------------------------------------
    # 4. Malformed payload retried (missing 'text' key), then success
    # ------------------------------------------------------------------
    @patch("src.core.llm_provider.random.random", return_value=0.5)
    @patch("src.core.llm_provider.time.sleep")
    @patch("src.core.llm_provider.requests.post")
    def test_malformed_payload_retried(
        self,
        mock_post: MagicMock,
        mock_sleep: MagicMock,
        mock_random: MagicMock,
    ) -> None:
        bad_resp = _mock_response(200, {"wrong": "shape"})
        ok_resp = _mock_response(200, {"text": "ok"})
        mock_post.side_effect = [bad_resp, ok_resp]
        client = _make_client()

        result = client.generate("hello")
        self.assertEqual(result, "ok")
        self.assertEqual(mock_post.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

    # ------------------------------------------------------------------
    # 5. Timeout then success
    # ------------------------------------------------------------------
    @patch("src.core.llm_provider.random.random", return_value=0.5)
    @patch("src.core.llm_provider.time.sleep")
    @patch("src.core.llm_provider.requests.post")
    def test_timeout_then_success(
        self,
        mock_post: MagicMock,
        mock_sleep: MagicMock,
        mock_random: MagicMock,
    ) -> None:
        ok_resp = _mock_response(200, {"text": "recovered"})
        mock_post.side_effect = [requests.Timeout("timed out"), ok_resp]
        client = _make_client()

        result = client.generate("hello")
        self.assertEqual(result, "recovered")
        self.assertEqual(mock_post.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

    # ------------------------------------------------------------------
    # 6. ConnectionError exhausts all retries
    # ------------------------------------------------------------------
    @patch("src.core.llm_provider.random.random", return_value=0.5)
    @patch("src.core.llm_provider.time.sleep")
    @patch("src.core.llm_provider.requests.post")
    def test_connection_error_exhausts_retries(
        self,
        mock_post: MagicMock,
        mock_sleep: MagicMock,
        mock_random: MagicMock,
    ) -> None:
        mock_post.side_effect = requests.ConnectionError("refused")
        client = _make_client()

        with self.assertRaises(requests.ConnectionError):
            client.generate("hello")

        self.assertEqual(mock_post.call_count, MAX_RETRIES)
        self.assertEqual(mock_sleep.call_count, MAX_RETRIES - 1)


if __name__ == "__main__":
    unittest.main()

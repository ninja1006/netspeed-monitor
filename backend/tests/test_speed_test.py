"""Speed test helpers (mocked HTTP)."""

from unittest.mock import MagicMock, patch

from backend.poller.speed_test import SpeedResult, run_speed_test


def test_run_speed_test_success() -> None:
    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [b"x" * 100_000]
    mock_response.raise_for_status = MagicMock()

    mock_stream = MagicMock()
    mock_stream.__enter__.return_value = mock_response
    mock_stream.__exit__.return_value = None

    mock_client = MagicMock()
    mock_client.stream.return_value = mock_stream
    mock_client.head.return_value = MagicMock(status_code=200)

    with (
        patch("backend.poller.speed_test.get_adapter_ipv4", return_value="192.168.1.10"),
        patch("backend.poller.speed_test._make_client") as make_client,
    ):
        make_client.return_value.__enter__.return_value = mock_client
        result = run_speed_test("Ethernet")

    assert isinstance(result, SpeedResult)
    assert result.download_mbps is not None
    assert result.download_mbps > 0
    assert result.latency_ms is not None

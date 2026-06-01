"""Unit tests for VPN/virtual adapter name filtering."""

import sys

import pytest

from backend.poller.adapter_filter import (
    is_virtual_adapter_name,
    list_physical_adapters,
    select_physical_adapter,
)


@pytest.mark.parametrize(
    "name,expected_virtual",
    [
        ("Ethernet", False),
        ("Wi-Fi", False),
        ("OpenVPN TAP-Windows6", True),
        ("TUNnel WireGuard", True),
        ("vEthernet (Default Switch)", True),
        ("NordLynx", True),
        ("Local Area Connection", False),
    ],
)
def test_is_virtual_adapter_name(name: str, expected_virtual: bool) -> None:
    assert is_virtual_adapter_name(name) is expected_virtual


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only WMI selection")
def test_select_physical_adapter_on_windows() -> None:
    adapter = select_physical_adapter()
    assert adapter is not None
    assert not is_virtual_adapter_name(adapter)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only WMI selection")
def test_list_physical_adapters_not_empty() -> None:
    adapters = list_physical_adapters()
    assert len(adapters) >= 1
    assert all(not is_virtual_adapter_name(name) for name in adapters)

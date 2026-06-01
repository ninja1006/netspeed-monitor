"""VPN-aware physical network adapter selection (Windows)."""

from __future__ import annotations

import logging
import socket
import sys
from dataclasses import dataclass

import psutil

logger = logging.getLogger(__name__)

# Substrings matched case-insensitively against adapter names / descriptions.
VIRTUAL_KEYWORDS: tuple[str, ...] = (
    "tap",
    "tun",
    "wintun",
    "wireguard",
    "openvpn",
    "hyper-v",
    "vethernet",
    "virtual",
    "vpn",
    "ppp",
    "loopback",
    "nordlynx",
    "tailscale",
    "zerotier",
    "hamachi",
    "softether",
    "cisco anyconnect",
    "juniper",
    "globalprotect",
)

# WMI NetConnectionStatus: 2 = Connected
_NET_CONNECTED = 2


@dataclass(frozen=True)
class AdapterInfo:
    name: str
    interface_index: int | None
    description: str
    is_virtual: bool


def is_virtual_adapter_name(name: str, description: str = "") -> bool:
    """Return True if name or description looks like a VPN/virtual adapter."""
    text = f"{name} {description}".lower()
    return any(keyword in text for keyword in VIRTUAL_KEYWORDS)


def _normalize_psutil_name(name: str) -> str:
    return name.strip()


def _wmi_adapters() -> list[AdapterInfo]:
    if sys.platform != "win32":
        return []
    try:
        import wmi  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("WMI module not available")
        return []

    results: list[AdapterInfo] = []
    try:
        conn = wmi.WMI()
        for nic in conn.Win32_NetworkAdapter():
            name = (nic.NetConnectionID or nic.Name or "").strip()
            if not name:
                continue
            description = (nic.Name or nic.Description or "").strip()
            physical = getattr(nic, "PhysicalAdapter", None)
            status = int(getattr(nic, "NetConnectionStatus", 0) or 0)
            virtual = is_virtual_adapter_name(name, description)
            if physical is False:
                virtual = True
            if status != _NET_CONNECTED:
                continue
            if virtual:
                continue
            idx = getattr(nic, "InterfaceIndex", None)
            results.append(
                AdapterInfo(
                    name=name,
                    interface_index=int(idx) if idx is not None else None,
                    description=description,
                    is_virtual=False,
                )
            )
    except Exception:
        logger.exception("WMI adapter enumeration failed")
    return results


def _default_route_interface_index() -> int | None:
    if sys.platform != "win32":
        return None
    try:
        import wmi  # type: ignore[import-untyped]
    except ImportError:
        return None

    try:
        conn = wmi.WMI()
        routes = conn.Win32_IP4RouteTable(Destination="0.0.0.0", Mask="0.0.0.0")
        best_metric: int | None = None
        best_index: int | None = None
        for route in routes:
            metric = int(getattr(route, "Metric1", 9999) or 9999)
            idx = getattr(route, "InterfaceIndex", None)
            if idx is None:
                continue
            if best_metric is None or metric < best_metric:
                best_metric = metric
                best_index = int(idx)
        return best_index
    except Exception:
        logger.exception("WMI default route lookup failed")
        return None


def _index_to_name(adapters: list[AdapterInfo]) -> dict[int, str]:
    return {
        a.interface_index: a.name
        for a in adapters
        if a.interface_index is not None
    }


def _psutil_physical_candidates() -> list[str]:
    """Fallback names from psutil excluding virtual patterns."""
    names: list[str] = []
    for name, stats in psutil.net_if_stats().items():
        if not stats.isup:
            continue
        norm = _normalize_psutil_name(name)
        if is_virtual_adapter_name(norm):
            continue
        names.append(norm)
    return names


def _traffic_bytes(name: str) -> int:
    counters = psutil.net_io_counters(pernic=True).get(name)
    if counters is None:
        return 0
    return int(counters.bytes_sent + counters.bytes_recv)


def list_physical_adapters() -> list[str]:
    """All non-virtual connected adapter names (WMI first, psutil fallback)."""
    wmi_list = _wmi_adapters()
    if wmi_list:
        return [a.name for a in wmi_list]
    return _psutil_physical_candidates()


def get_adapter_ipv4(adapter_name: str) -> str | None:
    """IPv4 address for binding HTTP tests to a specific interface."""
    for name, addrs in psutil.net_if_addrs().items():
        if _normalize_psutil_name(name) != _normalize_psutil_name(adapter_name):
            continue
        for addr in addrs:
            if addr.family != socket.AF_INET:
                continue
            ip = addr.address
            if ip and not ip.startswith("169.254.") and not ip.startswith("127."):
                return ip
    return None


def select_physical_adapter() -> str | None:
    """
    Choose the physical adapter for speed tests.

    1. WMI connected, non-virtual adapters
    2. Prefer adapter tied to default route if it is physical
    3. Else highest traffic among physical candidates
    4. psutil-only fallback if WMI empty
    """
    adapters = _wmi_adapters()
    if not adapters:
        fallback = _psutil_physical_candidates()
        if not fallback:
            logger.warning("No physical adapters found (psutil fallback)")
            return None
        chosen = max(fallback, key=_traffic_bytes)
        logger.info("Adapter selected via psutil fallback: %s", chosen)
        return chosen

    by_index = _index_to_name(adapters)
    default_idx = _default_route_interface_index()
    if default_idx is not None and default_idx in by_index:
        chosen = by_index[default_idx]
        logger.info("Adapter selected via default route: %s (ifIndex=%s)", chosen, default_idx)
        return chosen

    # VPN often owns default route — pick busiest physical NIC
    names = [a.name for a in adapters]
    chosen = max(names, key=_traffic_bytes)
    logger.info("Adapter selected via traffic heuristic: %s", chosen)
    return chosen

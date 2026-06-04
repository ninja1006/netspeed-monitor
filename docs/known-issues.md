# Known Issues & Workarounds

| ID | Issue | Workaround | Fixed in |
|----|-------|------------|----------|
| — | — | — | — |

---

## VPN validation (Issue #8)

Record results after testing with VPN on/off.

| Field | Value |
|-------|-------|
| **Test date** | 2026-06-05 |
| **Machine** | Windows 10/11 (DESKTOP-APMNGOH) |
| **Physical adapter (no VPN)** | Ethernet (ifIndex=11) |
| **Adapter with VPN connected** | N/A — no VPN client used in QA pass |
| **Poller log shows physical NIC?** | Yes |
| **Download range (physical path)** | ~1.9–2.4 Mbps (HTTP download, SPEEDMON_DEV=1) |
| **Notes** | Poller consistently selects `Ethernet` via default route. VPN-on retest skipped — no VPN connected during Issue #8 QA. Re-run with VPN when available (see docs/integration-test.md §3). |

**Expected (v1):** `adapter_filter` picks default-route physical adapter; VPN virtual adapters excluded by name/WMI.

**Observed on this project (dev machine):**

- Without VPN: `Adapter selected via default route: Ethernet (ifIndex=11)`
- Samples ~1.9–2.4 Mbps download, ~800–950 ms latency (HTTP test, 10s dev interval)
- VPN-on test: not performed on this machine during Issue #8

---

## Integration test bugs

Log new GitHub issues here with links:

| Bug | Issue URL | Status |
|-----|-----------|--------|
| — | none filed | Issue #8 QA passed |

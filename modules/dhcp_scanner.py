"""
dhcp_scanner.py
----------------
Lightweight ping-sweep across a subnet to find live hosts — useful
for spotting IP conflicts or confirming which addresses in a DHCP
range are actually in use. Uses threads so a /24 scans in seconds.
No raw sockets/admin privileges required (unlike ARP scanning),
so it runs the same way on a locked-down work laptop.
"""

import ipaddress
import platform
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def _ping_once(ip: str, timeout: float) -> bool:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip]
    else:
        cmd = ["ping", "-c", "1", "-W", str(max(1, int(timeout))), ip]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout + 2)
        return proc.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _resolve_hostname(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return "unknown"


def scan_subnet(cidr: str, timeout: float = 0.5, max_workers: int = 50) -> list:
    network = ipaddress.ip_network(cidr, strict=False)
    hosts = list(network.hosts())

    live_hosts = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_ping_once, str(ip), timeout): ip for ip in hosts}
        for future in as_completed(futures):
            ip = futures[future]
            if future.result():
                live_hosts.append(str(ip))

    results = [{"ip": ip, "hostname": _resolve_hostname(ip)} for ip in sorted(
        live_hosts, key=lambda x: ipaddress.ip_address(x)
    )]
    return results


def print_scan_result(results: list) -> None:
    print(f"\n--- Subnet Scan: {len(results)} live host(s) found ---")
    if not results:
        print("  No live hosts responded (subnet may block ICMP).")
        return
    for entry in results:
        print(f"  {entry['ip']:<16} {entry['hostname']}")

"""
network_diagnostics.py
-----------------------
TCP/IP and DNS troubleshooting helpers. Wraps the OS ping/traceroute
utilities (cross-platform) and does DNS resolution via the socket
module so it works with zero extra dependencies.
"""

import platform
import re
import socket
import subprocess
import time


def ping_host(host: str, count: int = 4) -> dict:
    """Ping a host and return latency + packet loss stats."""
    system = platform.system().lower()
    count_flag = "-n" if system == "windows" else "-c"

    try:
        proc = subprocess.run(
            ["ping", count_flag, str(count), host],
            capture_output=True,
            text=True,
            timeout=count * 3 + 5,
        )
        output = proc.stdout
        reachable = proc.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"host": host, "reachable": False, "error": str(exc)}

    loss_match = re.search(r"(\d+)% (packet )?loss", output)
    packet_loss = int(loss_match.group(1)) if loss_match else None

    avg_latency = None
    # Linux/macOS format: "min/avg/max/mdev = 0.02/0.03/0.05/0.01 ms"
    linux_match = re.search(r"= [\d.]+/([\d.]+)/", output)
    # Windows format: "Average = 23ms"
    win_match = re.search(r"Average = (\d+)ms", output)
    if linux_match:
        avg_latency = float(linux_match.group(1))
    elif win_match:
        avg_latency = float(win_match.group(1))

    return {
        "host": host,
        "reachable": reachable,
        "packet_loss_pct": packet_loss,
        "avg_latency_ms": avg_latency,
        "raw_output": output,
    }


def resolve_dns(host: str) -> dict:
    """Resolve a hostname to its IP address(es) and measure lookup time."""
    start = time.time()
    try:
        ip_list = list({info[4][0] for info in socket.getaddrinfo(host, None)})
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return {"host": host, "resolved": True, "ips": ip_list, "lookup_ms": elapsed_ms}
    except socket.gaierror as exc:
        return {"host": host, "resolved": False, "error": str(exc)}


def traceroute(host: str, max_hops: int = 30) -> dict:
    """Run the OS traceroute/tracert utility and parse hop count."""
    system = platform.system().lower()
    cmd = ["tracert", "-h", str(max_hops), host] if system == "windows" \
        else ["traceroute", "-m", str(max_hops), host]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        hops = lines[1:] if len(lines) > 1 else []
        return {"host": host, "hops": hops, "raw_output": proc.stdout}
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"host": host, "hops": [], "error": str(exc)}


def print_ping_result(result: dict) -> None:
    print(f"\n--- Ping: {result['host']} ---")
    if result.get("error"):
        print(f"  Error: {result['error']}")
        return
    status = "UP" if result["reachable"] else "DOWN"
    print(f"  Status:       {status}")
    print(f"  Packet loss:  {result.get('packet_loss_pct', 'n/a')}%")
    print(f"  Avg latency:  {result.get('avg_latency_ms', 'n/a')} ms")


def print_dns_result(result: dict) -> None:
    print(f"\n--- DNS: {result['host']} ---")
    if not result.get("resolved"):
        print(f"  Resolution failed: {result.get('error')}")
        return
    print(f"  Resolved IPs: {', '.join(result['ips'])}")
    print(f"  Lookup time:  {result['lookup_ms']} ms")


def print_traceroute_result(result: dict) -> None:
    print(f"\n--- Traceroute: {result['host']} ---")
    if result.get("error"):
        print(f"  Error: {result['error']}")
        return
    print(f"  Hops: {len(result['hops'])}")
    for hop in result["hops"][:10]:
        print(f"    {hop.strip()}")

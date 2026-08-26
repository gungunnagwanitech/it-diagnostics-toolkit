"""
system_health.py
------------------
Local endpoint health check: CPU, memory, disk usage, and a quick
flag for anything that would warrant an L1 ticket (low disk space,
high CPU/mem load). Requires psutil.
"""

import platform
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None

DISK_WARN_THRESHOLD_PCT = 85
CPU_WARN_THRESHOLD_PCT = 90
MEM_WARN_THRESHOLD_PCT = 90


def get_system_health() -> dict:
    if psutil is None:
        return {"error": "psutil is not installed. Run: pip install psutil"}

    cpu_pct = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    warnings = []
    if cpu_pct >= CPU_WARN_THRESHOLD_PCT:
        warnings.append(f"High CPU usage: {cpu_pct}%")
    if mem.percent >= MEM_WARN_THRESHOLD_PCT:
        warnings.append(f"High memory usage: {mem.percent}%")
    if disk.percent >= DISK_WARN_THRESHOLD_PCT:
        warnings.append(f"Low disk space: {disk.percent}% used")

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "os": f"{platform.system()} {platform.release()}",
        "cpu_pct": cpu_pct,
        "mem_pct": mem.percent,
        "mem_total_gb": round(mem.total / (1024 ** 3), 2),
        "mem_used_gb": round(mem.used / (1024 ** 3), 2),
        "disk_pct": disk.percent,
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        "warnings": warnings,
    }


def print_health_report(result: dict) -> None:
    print("\n--- System Health ---")
    if result.get("error"):
        print(f"  {result['error']}")
        return
    print(f"  OS:      {result['os']}")
    print(f"  CPU:     {result['cpu_pct']}%")
    print(f"  Memory:  {result['mem_pct']}%  ({result['mem_used_gb']} / {result['mem_total_gb']} GB)")
    print(f"  Disk:    {result['disk_pct']}%  ({result['disk_free_gb']} GB free of {result['disk_total_gb']} GB)")
    if result["warnings"]:
        print("  Warnings:")
        for w in result["warnings"]:
            print(f"    - {w}")
    else:
        print("  No issues detected.")

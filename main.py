#!/usr/bin/env python3
"""
IT Diagnostics Toolkit
-----------------------
A single-command CLI that automates common L1 IT support checks:
network diagnostics, subnet validation, system health, a local
network device scan, and (optional) M365 user reporting.

Every check is logged to sample_output/ticket_log.csv so runs
leave an audit trail, similar to a helpdesk ticket history.

Usage:
    python main.py ping google.com
    python main.py dns google.com
    python main.py subnet 192.168.1.0/24
    python main.py health
    python main.py scan 192.168.1.0/24
    python main.py m365-report          # requires Graph API credentials
    python main.py full-check google.com 192.168.1.0/24
"""

import argparse
import sys

from modules import network_diagnostics as netdiag
from modules import subnet_calculator as subnetcalc
from modules import system_health as syshealth
from modules import dhcp_scanner as scanner
from modules import m365_report as m365
from modules.ticket_logger import log_result


def cmd_ping(args):
    result = netdiag.ping_host(args.host)
    log_result("ping", args.host, result)
    netdiag.print_ping_result(result)


def cmd_dns(args):
    result = netdiag.resolve_dns(args.host)
    log_result("dns", args.host, result)
    netdiag.print_dns_result(result)


def cmd_traceroute(args):
    result = netdiag.traceroute(args.host)
    log_result("traceroute", args.host, {"hops": len(result.get("hops", []))})
    netdiag.print_traceroute_result(result)


def cmd_subnet(args):
    result = subnetcalc.analyze(args.cidr)
    log_result("subnet", args.cidr, result)
    subnetcalc.print_subnet_result(result)


def cmd_health(args):
    result = syshealth.get_system_health()
    log_result("system-health", "localhost", result)
    syshealth.print_health_report(result)


def cmd_scan(args):
    result = scanner.scan_subnet(args.cidr, timeout=args.timeout)
    log_result("subnet-scan", args.cidr, {"live_hosts": len(result)})
    scanner.print_scan_result(result)


def cmd_m365(args):
    result = m365.generate_user_report()
    log_result("m365-report", "graph-api", {"users": len(result)})
    m365.print_user_report(result)


def cmd_full_check(args):
    print("=" * 60)
    print(" FULL DIAGNOSTIC CHECK")
    print("=" * 60)
    cmd_ping(argparse.Namespace(host=args.host))
    cmd_dns(argparse.Namespace(host=args.host))
    cmd_subnet(argparse.Namespace(cidr=args.cidr))
    cmd_health(argparse.Namespace())
    print("\nFull check complete. See sample_output/ticket_log.csv for the log.")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="it-toolkit",
        description="Automated L1 IT diagnostics CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_ping = sub.add_parser("ping", help="Ping a host and report latency/loss")
    p_ping.add_argument("host")
    p_ping.set_defaults(func=cmd_ping)

    p_dns = sub.add_parser("dns", help="Resolve DNS for a host")
    p_dns.add_argument("host")
    p_dns.set_defaults(func=cmd_dns)

    p_trace = sub.add_parser("traceroute", help="Trace the route to a host")
    p_trace.add_argument("host")
    p_trace.set_defaults(func=cmd_traceroute)

    p_subnet = sub.add_parser("subnet", help="Analyze a CIDR block (VLAN/subnet planning)")
    p_subnet.add_argument("cidr", help="e.g. 192.168.1.0/24")
    p_subnet.set_defaults(func=cmd_subnet)

    p_health = sub.add_parser("health", help="Report local system health (CPU, RAM, disk)")
    p_health.set_defaults(func=cmd_health)

    p_scan = sub.add_parser("scan", help="Ping-sweep a subnet for live hosts")
    p_scan.add_argument("cidr", help="e.g. 192.168.1.0/24")
    p_scan.add_argument("--timeout", type=float, default=0.5)
    p_scan.set_defaults(func=cmd_scan)

    p_m365 = sub.add_parser("m365-report", help="Generate a read-only M365 user/license report")
    p_m365.set_defaults(func=cmd_m365)

    p_full = sub.add_parser("full-check", help="Run ping + dns + subnet + health in one shot")
    p_full.add_argument("host")
    p_full.add_argument("cidr")
    p_full.set_defaults(func=cmd_full_check)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)


if __name__ == "__main__":
    main()

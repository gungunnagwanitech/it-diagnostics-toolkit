"""
subnet_calculator.py
---------------------
Validates and analyzes CIDR blocks for subnetting/VLAN planning:
network address, broadcast address, usable host range, host count,
and subnet mask — the kind of math an L1 tech does when assigning
VLANs or troubleshooting IP addressing issues.
"""

import ipaddress


def analyze(cidr: str) -> dict:
    try:
        network = ipaddress.ip_network(cidr, strict=False)
    except ValueError as exc:
        return {"cidr": cidr, "valid": False, "error": str(exc)}

    hosts = list(network.hosts())
    return {
        "cidr": cidr,
        "valid": True,
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "netmask": str(network.netmask),
        "prefix_length": network.prefixlen,
        "total_addresses": network.num_addresses,
        "usable_hosts": len(hosts),
        "first_usable": str(hosts[0]) if hosts else None,
        "last_usable": str(hosts[-1]) if hosts else None,
        "is_private": network.is_private,
    }


def suggest_vlan_split(cidr: str, num_vlans: int) -> list:
    """Split a given CIDR into `num_vlans` equal-sized subnets, if possible."""
    network = ipaddress.ip_network(cidr, strict=False)
    import math
    bits_needed = math.ceil(math.log2(num_vlans))
    new_prefix = network.prefixlen + bits_needed
    if new_prefix > 30:
        return []
    return [str(subnet) for subnet in network.subnets(new_prefix=new_prefix)][:num_vlans]


def print_subnet_result(result: dict) -> None:
    print(f"\n--- Subnet Analysis: {result['cidr']} ---")
    if not result.get("valid"):
        print(f"  Invalid CIDR: {result.get('error')}")
        return
    print(f"  Network address:    {result['network_address']}")
    print(f"  Broadcast address:  {result['broadcast_address']}")
    print(f"  Subnet mask:        {result['netmask']} (/{result['prefix_length']})")
    print(f"  Total addresses:    {result['total_addresses']}")
    print(f"  Usable hosts:       {result['usable_hosts']}")
    print(f"  Usable range:       {result['first_usable']} - {result['last_usable']}")
    print(f"  Private range:      {result['is_private']}")

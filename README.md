# IT Diagnostics Toolkit

A single-command CLI that automates the diagnostic checks an L1 IT support
technician runs every day — network troubleshooting, subnet/VLAN validation,
endpoint health checks, live-host discovery, and M365 user reporting — with
every run logged to an auditable CSV "ticket log."

Built to mirror real helpdesk workflows: instead of running 5–6 separate
tools by hand, one command produces a clean report and a paper trail.

## Features

| Module | What it does | Maps to |
|---|---|---|
| `network_diagnostics.py` | Ping, DNS resolution, traceroute | TCP/IP & DNS troubleshooting |
| `subnet_calculator.py` | Validates CIDR blocks, computes usable host ranges, suggests VLAN splits | Subnetting / VLAN planning |
| `system_health.py` | CPU, memory, disk usage with warning thresholds | Desktop / hardware diagnostics |
| `dhcp_scanner.py` | Threaded ping-sweep to find live hosts on a subnet | DHCP / IP conflict troubleshooting |
| `m365_report.py` | Read-only Microsoft Graph API user & license report | M365 / Workspace administration |
| `ticket_logger.py` | Logs every check to `sample_output/ticket_log.csv` | Documentation / audit trail |

## Quick Start

```bash
git clone https://github.com/<your-username>/it-diagnostics-toolkit.git
cd it-diagnostics-toolkit
pip install -r requirements.txt

python main.py ping google.com
python main.py dns google.com
python main.py subnet 192.168.1.0/24
python main.py health
python main.py scan 192.168.1.0/24
python main.py m365-report
python main.py full-check google.com 192.168.1.0/24
```

## Example Output

```
--- Subnet Analysis: 192.168.1.0/24 ---
  Network address:    192.168.1.0
  Broadcast address:  192.168.1.255
  Subnet mask:        255.255.255.0 (/24)
  Total addresses:    256
  Usable hosts:       254
  Usable range:       192.168.1.1 - 192.168.1.254
  Private range:      True

--- System Health ---
  OS:      Linux 6.18.44
  CPU:     0.0%
  Memory:  6.7%  (0.26 / 3.9 GB)
  Disk:    46.1%  (9.98 GB free of 251.97 GB)
  No issues detected.
```

Every run also appends a row to `sample_output/ticket_log.csv`:

```
timestamp,check_type,target,summary
2026-08-26T15:54:13,subnet,192.168.1.0/24,cidr=192.168.1.0/24; valid=True; ...
2026-08-26T15:54:14,system-health,localhost,cpu_pct=0.0; mem_pct=6.7; ...
```

## M365 Reporting (optional, live credentials)

`m365-report` works out of the box with sample data. To pull live data from
your own Microsoft 365 tenant, register an app in Azure AD with
`User.Read.All` permission and set:

```bash
export MS_TENANT_ID=<your-tenant-id>
export MS_CLIENT_ID=<your-client-id>
export MS_CLIENT_SECRET=<your-client-secret>
```

## Why I Built This

Most L1 tickets — "can't connect to Wi-Fi," "my laptop is slow," "what's
this device's IP range" — start with the same few diagnostic steps. This
toolkit collapses those steps into one command and keeps a record of what
was checked, similar to a lightweight self-service helpdesk tool.

## Tech Stack

- Python 3.10+ (stdlib: `ipaddress`, `socket`, `subprocess`, `csv`)
- [`psutil`](https://pypi.org/project/psutil/) for system health
- [`requests`](https://pypi.org/project/requests/) for the Microsoft Graph API
- `argparse` for the CLI, `ThreadPoolExecutor` for concurrent subnet scanning

## Possible Extensions

- Aruba Central API integration for AP status/signal strength
- Google Workspace Admin SDK support alongside M365
- Web dashboard (Flask) instead of CLI-only output
- Scheduled runs via cron / Task Scheduler with email alerts on warnings

## License

MIT — see [LICENSE](LICENSE).

"""
m365_report.py
----------------
Read-only Microsoft 365 user/license report via the Microsoft Graph API.
Demonstrates the kind of workplace-tools administration an IT intern
does day to day: listing users, checking license assignment, and
flagging accounts that haven't signed in recently.

Requires environment variables:
    MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET
(app registration needs User.Read.All, delegated or application permission)

If credentials are not configured, this module falls back to a
clearly-labeled sample dataset so the tool still runs end-to-end
for demo purposes.
"""

import os

try:
    import requests
except ImportError:
    requests = None

GRAPH_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
GRAPH_USERS_URL = "https://graph.microsoft.com/v1.0/users?$select=displayName,userPrincipalName,accountEnabled,assignedLicenses"

SAMPLE_DATA = [
    {"displayName": "Asha Rao", "userPrincipalName": "asha.rao@example.com",
     "accountEnabled": True, "licensed": True},
    {"displayName": "Vikram Shah", "userPrincipalName": "vikram.shah@example.com",
     "accountEnabled": True, "licensed": False},
    {"displayName": "Priya Nair", "userPrincipalName": "priya.nair@example.com",
     "accountEnabled": False, "licensed": True},
]


def _get_access_token() -> str:
    tenant = os.environ["MS_TENANT_ID"]
    client_id = os.environ["MS_CLIENT_ID"]
    client_secret = os.environ["MS_CLIENT_SECRET"]

    resp = requests.post(
        GRAPH_TOKEN_URL.format(tenant=tenant),
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def generate_user_report() -> list:
    required_env = ("MS_TENANT_ID", "MS_CLIENT_ID", "MS_CLIENT_SECRET")
    if requests is None or not all(os.environ.get(v) for v in required_env):
        # No live credentials configured — return sample data so the
        # CLI still works end-to-end for a demo / portfolio run.
        return [{**u, "source": "SAMPLE DATA"} for u in SAMPLE_DATA]

    token = _get_access_token()
    resp = requests.get(
        GRAPH_USERS_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    users = resp.json().get("value", [])

    return [
        {
            "displayName": u.get("displayName"),
            "userPrincipalName": u.get("userPrincipalName"),
            "accountEnabled": u.get("accountEnabled"),
            "licensed": bool(u.get("assignedLicenses")),
            "source": "LIVE",
        }
        for u in users
    ]


def print_user_report(users: list) -> None:
    source = users[0]["source"] if users else "n/a"
    print(f"\n--- M365 User Report (source: {source}) ---")
    print(f"  {'Name':<20}{'UPN':<30}{'Enabled':<10}{'Licensed'}")
    for u in users:
        print(f"  {u['displayName']:<20}{u['userPrincipalName']:<30}"
              f"{str(u['accountEnabled']):<10}{u['licensed']}")
    disabled = sum(1 for u in users if not u["accountEnabled"])
    unlicensed = sum(1 for u in users if not u["licensed"])
    print(f"\n  Total users: {len(users)} | Disabled: {disabled} | Unlicensed: {unlicensed}")

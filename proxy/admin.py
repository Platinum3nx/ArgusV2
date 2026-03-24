"""Argus proxy token management CLI helper.

Generates env var content for ARGUS_PROXY_TOKENS_JSON — does NOT modify live state.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys


def _load_current() -> dict:
    raw = os.environ.get("ARGUS_PROXY_TOKENS_JSON", "").strip()
    if raw:
        return json.loads(raw)
    single = os.environ.get("ARGUS_PROXY_TOKEN", "").strip()
    if single:
        return {single: {"name": "default", "daily_limit": 500}}
    return {}


def cmd_issue(args: argparse.Namespace) -> None:
    current = _load_current()
    token = secrets.token_urlsafe(32)
    current[token] = {"name": args.name, "daily_limit": args.daily_limit}
    print(json.dumps(current, indent=2))
    print(f"\n# New token for '{args.name}': {token}", file=sys.stderr)


def cmd_revoke(args: argparse.Namespace) -> None:
    current = _load_current()
    if args.token not in current:
        print(f"Token not found in current config", file=sys.stderr)
        sys.exit(1)
    del current[args.token]
    print(json.dumps(current, indent=2))


def cmd_list(args: argparse.Namespace) -> None:
    current = _load_current()
    if not current:
        print("No tokens configured.")
        return
    for token, cfg in current.items():
        masked = token[:6] + "..." + token[-4:] if len(token) > 10 else "***"
        print(f"  {masked}  name={cfg.get('name', '?')}  daily_limit={cfg.get('daily_limit', '?')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Argus proxy token management")
    sub = parser.add_subparsers(dest="command")

    issue_p = sub.add_parser("issue", help="Issue a new token")
    issue_p.add_argument("--name", required=True, help="Token owner name")
    issue_p.add_argument("--daily-limit", type=int, default=500, help="Daily request limit")

    revoke_p = sub.add_parser("revoke", help="Revoke a token")
    revoke_p.add_argument("--token", required=True, help="Token to revoke")

    sub.add_parser("list", help="List configured tokens")

    args = parser.parse_args()
    if args.command == "issue":
        cmd_issue(args)
    elif args.command == "revoke":
        cmd_revoke(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

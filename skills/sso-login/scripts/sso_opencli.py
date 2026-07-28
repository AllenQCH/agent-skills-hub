#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time


PLATFORMS = {
    "cn": {
        "sso_url": "https://account.heytea.com/sso/login",
        "account_host": "account.heytea.com",
        "org_name": "喜茶",
    },
    "uswest": {
        "sso_url": "https://account.heytea-co.com/sso/login",
        "account_host": "account.heytea-co.com",
        "org_name": "Heytea",
    },
    "sg": {
        "sso_url": "https://account.heytea-co.com/sso/login",
        "account_host": "account.heytea-co.com",
        "org_name": "Heytea",
    },
    "test": {
        "sso_url": "https://test-go-1-cas.heyteago.com/sso/login",
        "account_host": "test-go-1-cas.heyteago.com",
        "org_name": "喜茶",
    },
    "test-intl": {
        "sso_url": "https://account-intl-go-1.test.heytea-co.com/sso/login",
        "account_host": "account-intl-go-1.test.heytea-co.com",
        "org_name": "喜茶",
    },
    "dev": {
        "sso_url": "https://cas-go-1.dev.heytea.com/sso/login",
        "account_host": "cas-go-1.dev.heytea.com",
        "org_name": "喜茶",
    },
}

REUSE_WRAPPER = "/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh"


def run_command(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        capture_output=True,
    )


def ensure_opencli_available() -> None:
    try:
        run_command(["opencli", "--help"])
    except FileNotFoundError as exc:
        raise RuntimeError("opencli is not installed or not on PATH.") from exc


def doctor_ok(verbose: bool = False) -> tuple[bool, str]:
    result = run_command(["opencli", "doctor", "-v"], check=False)
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    ok = result.returncode == 0
    if verbose:
        print(output)
    return ok, output


def open_page(session: str, url: str) -> None:
    run_command(["bash", REUSE_WRAPPER, "--session", session, "open", url])


def get_current_url(session: str) -> str:
    result = run_command(["opencli", "browser", session, "get", "url"])
    return result.stdout.strip()


def get_current_title(session: str) -> str:
    result = run_command(["opencli", "browser", session, "get", "title"])
    return result.stdout.strip()


def wait_seconds(session: str, seconds: int) -> None:
    run_command(
        ["opencli", "browser", session, "wait", "time", str(seconds), "--timeout", str(seconds * 1000 + 1000)]
    )


def session_is_valid(url: str, title: str, account_host: str) -> bool:
    normalized_url = url.lower()
    normalized_title = title.lower()
    if account_host in normalized_url and "/sso/login" in normalized_url:
        return False
    if "login" in normalized_title and account_host in normalized_url:
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or refresh HeyTea SSO with opencli Browser Bridge.",
    )
    parser.add_argument("--platform", "-p", default="cn", choices=sorted(PLATFORMS))
    parser.add_argument("--session", default=None, help="opencli browser session name")
    parser.add_argument("--status", action="store_true", help="Only check readiness and session status.")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="How long to wait for manual login to complete.",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_opencli_available()

    platform_cfg = PLATFORMS[args.platform]
    session = args.session or f"heytea-sso-{args.platform}"

    print(f"PLATFORM={args.platform}")
    print(f"SSO_URL={platform_cfg['sso_url']}")
    print(f"SESSION={session}")

    doctor_success, doctor_output = doctor_ok(verbose=args.verbose)
    if not doctor_success:
        print("STATUS=OPENCLI_NOT_READY")
        print("DETAIL=Browser Bridge extension is not connected. Run `opencli doctor -v` after opening Chrome and connecting the extension.")
        if not args.verbose and doctor_output:
            print("DOCTOR_OUTPUT_START")
            print(doctor_output)
            print("DOCTOR_OUTPUT_END")
        return 2

    open_page(session, platform_cfg["sso_url"])
    current_url = get_current_url(session)
    current_title = get_current_title(session)

    print(f"CURRENT_URL={current_url}")
    print(f"CURRENT_TITLE={current_title}")

    if session_is_valid(current_url, current_title, platform_cfg["account_host"]):
        print("STATUS=VALID")
        return 0

    if args.status:
        print("STATUS=LOGIN_REQUIRED")
        return 1

    print(f"ACTION=Please complete manual login for {platform_cfg['org_name']} in Chrome, then keep this session open.")

    deadline = time.time() + args.timeout_seconds
    while time.time() < deadline:
        wait_seconds(session, 3)
        current_url = get_current_url(session)
        current_title = get_current_title(session)
        print(f"POLL_URL={current_url}")
        print(f"POLL_TITLE={current_title}")
        if session_is_valid(current_url, current_title, platform_cfg["account_host"]):
            print("STATUS=VALID")
            return 0

    print("STATUS=TIMEOUT")
    print("DETAIL=Manual login was not completed before timeout.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

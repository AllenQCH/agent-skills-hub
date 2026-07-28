#!/usr/bin/env python3
"""Discover and clone private GitLab repositories while preserving namespace paths."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


SSH_RE = re.compile(r"^git@([^:]+):(.+?)(?:\.git)?$")
HTTPS_RE = re.compile(r"^https?://([^/]+)/(.+?)(?:\.git)?$")


def parse_repo_url(url: str) -> tuple[str, str, str]:
    url = url.strip()
    match = SSH_RE.match(url)
    if match:
        host, namespace = match.groups()
        return host, namespace, f"git@{host}:{namespace}.git"
    match = HTTPS_RE.match(url)
    if match:
        host, namespace = match.groups()
        return host, namespace, f"git@{host}:{namespace}.git"
    raise ValueError(f"unsupported repo URL: {url}")


def include_namespace(namespace: str, prefixes: list[str]) -> bool:
    if not prefixes:
        return True
    return any(namespace == prefix.rstrip("/") or namespace.startswith(prefix.rstrip("/") + "/") for prefix in prefixes)


def read_repo_file(path: Path) -> list[str]:
    repos: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            repos.append(line)
    return repos


def scan_local_remotes(paths: Iterable[Path]) -> list[str]:
    repos: list[str] = []
    for root in paths:
        if not root.exists():
            continue
        for dirpath, dirnames, _ in os.walk(root):
            if ".git" not in dirnames:
                continue
            result = subprocess.run(
                ["git", "-C", dirpath, "remote", "get-url", "origin"],
                text=True,
                capture_output=True,
            )
            if result.returncode == 0:
                repos.append(result.stdout.strip())
            dirnames[:] = []
    return repos


def gitlab_api_projects(gitlab_url: str, group: str, token_env: str, include_subgroups: bool) -> list[str]:
    token = os.environ.get(token_env)
    if not token:
        raise RuntimeError(f"missing token env: {token_env}")

    base = gitlab_url.rstrip("/")
    group_id = urllib.parse.quote(group, safe="")
    repos: list[str] = []
    page = 1

    while True:
        query = urllib.parse.urlencode(
            {
                "include_subgroups": "true" if include_subgroups else "false",
                "simple": "true",
                "per_page": "100",
                "page": str(page),
            }
        )
        url = f"{base}/api/v4/groups/{group_id}/projects?{query}"
        req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": token})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
        if not data:
            break
        for project in data:
            ssh_url = project.get("ssh_url_to_repo")
            if ssh_url:
                repos.append(ssh_url)
        page += 1

    return repos


def heytea_bk_projects(project_code: str, bug_killer_root: Path) -> list[str]:
    scripts = bug_killer_root / "skills" / "heytea-git" / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        from clone_repo import BKDevOpsClient  # type: ignore
    except Exception as exc:  # pragma: no cover - environment-specific adapter
        raise RuntimeError(f"cannot load HeyTea BK adapter from {scripts}: {exc}") from exc

    client = BKDevOpsClient(verbose=False)
    repos = client.list_repos(project_code)
    return [r["ssh_url"] for r in repos if r.get("ssh_url")]


def clone_one(ssh_url: str, namespace: str, dest: Path, depth: int, dry_run: bool) -> str:
    target = dest / namespace
    rel = target.relative_to(dest)
    if (target / ".git").is_dir():
        return f"skip {rel}"
    if dry_run:
        return f"would clone {rel} <- {ssh_url}"

    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone"]
    if depth > 0:
        cmd.extend(["--depth", str(depth)])
    cmd.extend([ssh_url, str(target)])
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=20")
    result = subprocess.run(cmd, text=True, capture_output=True, env=env)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()[-1]
        return f"failed {rel}: {detail}"
    return f"cloned {rel}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True, type=Path, help="Destination root directory")
    parser.add_argument("--repo", action="append", default=[], help="Repository URL; repeatable")
    parser.add_argument("--repo-file", type=Path, help="File containing repository URLs")
    parser.add_argument("--scan-remotes", action="append", type=Path, default=[], help="Scan local repos for origin URLs")
    parser.add_argument("--gitlab-url", help="GitLab base URL for API discovery")
    parser.add_argument("--group", help="GitLab group path for API discovery")
    parser.add_argument("--token-env", default="GITLAB_TOKEN", help="Environment variable containing GitLab token")
    parser.add_argument("--no-include-subgroups", action="store_true", help="Do not include GitLab subgroups")
    parser.add_argument("--heytea-bk-project-code", help="HeyTea BlueKing DevOps project code")
    parser.add_argument(
        "--heytea-bk-root",
        type=Path,
        default=Path("/Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer"),
        help="Path to local bug-killer package for HeyTea BK discovery",
    )
    parser.add_argument("--include-prefix", action="append", default=[], help="Namespace prefix to include; repeatable")
    parser.add_argument("--depth", type=int, default=1, help="Clone depth; use 0 for full history")
    parser.add_argument("--dry-run", action="store_true", help="Print planned clones without writing")
    args = parser.parse_args()

    raw_urls: list[str] = list(args.repo)
    if args.repo_file:
        raw_urls.extend(read_repo_file(args.repo_file))
    if args.scan_remotes:
        raw_urls.extend(scan_local_remotes(args.scan_remotes))
    if args.gitlab_url and args.group:
        raw_urls.extend(gitlab_api_projects(args.gitlab_url, args.group, args.token_env, not args.no_include_subgroups))
    if args.heytea_bk_project_code:
        raw_urls.extend(heytea_bk_projects(args.heytea_bk_project_code, args.heytea_bk_root))

    repos: dict[str, str] = {}
    errors = 0
    for raw_url in raw_urls:
        try:
            _, namespace, ssh_url = parse_repo_url(raw_url)
        except ValueError as exc:
            print(f"warn: {exc}", file=sys.stderr)
            errors += 1
            continue
        if include_namespace(namespace, args.include_prefix):
            repos[namespace] = ssh_url

    print(f"selected={len(repos)}")
    failed = 0
    skipped = 0
    cloned = 0
    for namespace, ssh_url in sorted(repos.items()):
        status = clone_one(ssh_url, namespace, args.dest.expanduser(), args.depth, args.dry_run)
        print(status)
        if status.startswith("failed"):
            failed += 1
        elif status.startswith("skip"):
            skipped += 1
        elif status.startswith("cloned"):
            cloned += 1

    print(f"summary cloned={cloned} skipped={skipped} failed={failed} parse_errors={errors} total={len(repos)}")
    return 1 if failed or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import argparse
import json
import re
import shlex
import subprocess
import sys

SESSION = "dbauto-query"
URL = "https://dbauto.heyteago.com/sqlquery/"
REUSE_WRAPPER = "/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh"

INSTANCE_ALIASES = {
    "hsp-ids": "供应链中台prod-hsp-ids--生产MySQL灾备",
    "hsp-pof": "供应链中台prod-hsp-pof--生产MySQL灾备",
    "hsp-pof-scm": "供应链中台prod-hsp-pof-scm--生产MySQL灾备",
    "cn-test": "国内--测试环境--MySQL5.7",
    "cn-test-mysql57": "国内--测试环境--MySQL5.7",
    "cn-test-mysql80": "国内--测试环境--MySQL8.0",
}

READ_ONLY_RE = re.compile(r"^\s*(select|show|desc|describe|explain|with)\b", re.IGNORECASE | re.DOTALL)
FORBIDDEN_RE = re.compile(
    r"\b(update|insert|delete|drop|alter|truncate|replace|merge|grant|revoke|call|set)\b",
    re.IGNORECASE,
)


def run_opencli(args: list[str], timeout: int = 30) -> str:
    cmd = ["opencli", "browser", SESSION, *args]
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout


def js_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def ensure_page() -> None:
    title = run_opencli(["get", "title"]).strip()
    url = run_opencli(["get", "url"]).strip()
    if "dbauto.heyteago.com/sqlquery" not in url or "SQL审核查询平台" not in title:
        result = subprocess.run(
            ["bash", REUSE_WRAPPER, "--session", SESSION, "open", URL],
            text=True,
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            raise SystemExit(result.returncode)


def list_instances(pattern: str) -> None:
    ensure_page()
    js = f"""(() => {{
      const opts = Array.from(document.querySelectorAll("#instance_name option"))
        .map((o, i) => ({{i, value: o.value, text: o.textContent.trim(), group: o.parentElement?.label || ""}}))
        .filter(x => x.value || x.text);
      return opts.filter(x => new RegExp({js_literal(pattern)}, "i").test(x.text) || new RegExp({js_literal(pattern)}, "i").test(x.value));
    }})()"""
    print(run_opencli(["eval", js]))


def list_resources(instance: str, resource_type: str, db: str | None = None) -> None:
    ensure_page()
    instance_name = INSTANCE_ALIASES.get(instance, instance)
    data_fields = f"""instance_name: {js_literal(instance_name)}, resource_type: {js_literal(resource_type)}"""
    if db:
        data_fields += f""", db_name: {js_literal(db)}"""
    js = f"""(() => new Promise(resolve => {{
      $.ajax({{
        type: "get",
        url: "/instance/instance_resource/",
        dataType: "json",
        data: {{{data_fields}}},
        success: data => resolve(data),
        error: (xhr, ts, err) => resolve({{status: -1, msg: err || ts, http_status: xhr.status, text: (xhr.responseText || "").slice(0, 1000)}})
      }});
    }}))()"""
    print(run_opencli(["eval", js], timeout=60))


def assert_read_only(sql: str) -> None:
    normalized = sql.strip()
    if not READ_ONLY_RE.search(normalized):
        raise SystemExit("Refusing non-read-only SQL. Generate a work-order SQL instead of executing it.")
    if FORBIDDEN_RE.search(normalized):
        raise SystemExit("Refusing non-read-only SQL. Generate a work-order SQL instead of executing it.")


def query(instance: str, db: str, sql: str, limit: str) -> None:
    ensure_page()
    assert_read_only(sql)
    instance_name = INSTANCE_ALIASES.get(instance, instance)
    js = f"""(() => new Promise(resolve => {{
      const csrf = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
      $.ajax({{
        type: "post",
        url: "/query/",
        dataType: "json",
        headers: {{"X-CSRFToken": csrf}},
        data: {{
          instance_name: {js_literal(instance_name)},
          db_name: {js_literal(db)},
          schema_name: "",
          tb_name: "",
          sql_content: {js_literal(sql)},
          limit_num: {js_literal(limit)}
        }},
        success: data => resolve(data),
        error: (xhr, ts, err) => resolve({{status: -1, msg: err || ts, http_status: xhr.status, text: (xhr.responseText || "").slice(0, 1000)}})
      }});
    }}))()"""
    print(run_opencli(["eval", js], timeout=120))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-common-instances", action="store_true")
    parser.add_argument(
        "--list-cn-test-instances",
        action="store_true",
        help="List domestic test MySQL 5.7/8.0 instances",
    )
    parser.add_argument("--list-dbs", action="store_true", help="List databases for --instance")
    parser.add_argument("--list-tables", action="store_true", help="List tables for --instance and --db")
    parser.add_argument("--instance", default="hsp-ids", help="Instance alias or full dbauto instance name")
    parser.add_argument("--db", default="center_hsp_invoice")
    parser.add_argument("--sql")
    parser.add_argument("--limit", default="100")
    args = parser.parse_args()

    if args.list_common_instances:
        list_instances(
            "prod-hsp-ids--生产MySQL灾备|prod-hsp-pof--生产MySQL灾备|prod-hsp-pof-scm--生产MySQL灾备"
        )
        return

    if args.list_cn_test_instances:
        list_instances(r"^国内--测试环境--MySQL(?:5\.7|8\.0)$")
        return

    if args.list_dbs:
        list_resources(args.instance, "database")
        return

    if args.list_tables:
        list_resources(args.instance, "table", args.db)
        return

    if not args.sql:
        quoted = " ".join(shlex.quote(x) for x in INSTANCE_ALIASES)
        raise SystemExit(
            "--sql is required unless an instance-listing option is used. "
            f"Known aliases: {quoted}"
        )

    query(args.instance, args.db, args.sql, args.limit)


if __name__ == "__main__":
    main()

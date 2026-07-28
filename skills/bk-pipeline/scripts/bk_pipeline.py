#!/usr/bin/env python3
"""Deterministic HeyTea BlueKing (蓝盾/devops-bk) pipeline CLI over opencli Browser Bridge.

复用浏览器里已登录的 `bk-console` session，在页面上下文里跑同源鉴权 fetch 直接调
BK process REST API，替代 LLM operator 的逐步 UI 导航，速度更快、无需重复登录。

设计对齐 dbauto-sql-query 脚本：opencli browser <session> eval <js> 返回 JSON。

安全约束（沿用 tool_bk_pipeline_operator 规则）：
- 只读命令（inspect/status/startup-info/params）随时可跑。
- 写命令（trigger/retry/stop）默认 dry-run 只打印 payload，加 --confirm 才真正发送。
- 从不批量触发全部 service，必须指定明确的 pipeline/build。
- 不打印 cookie / CSRF / session。

AI-GENERATED (Cursor)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.parse import urlencode

SESSION = "bk-console"
ORIGIN = "https://devops-bk.heyteago.com"
CONSOLE_ENTRY = f"{ORIGIN}/console/platform/entry"
REUSE_WRAPPER = "/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh"


def run_opencli(args: list[str], timeout: int = 60) -> str:
    """执行 opencli browser 子命令并返回 stdout；失败时透传 stderr 并退出。"""
    cmd = ["opencli", "browser", SESSION, *args]
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout


def doctor_ready() -> bool:
    """检查 opencli Browser Bridge 是否连通。"""
    result = subprocess.run(
        ["opencli", "doctor", "-v"], text=True, capture_output=True, check=False
    )
    return result.returncode == 0


def ensure_page() -> None:
    """确保 bk-console 落在 devops-bk 且已登录，否则打开控制台入口或报错。"""
    if not doctor_ready():
        print(json.dumps({
            "ok": False,
            "status": "OPENCLI_NOT_READY",
            "detail": "Browser Bridge 未连通。打开 Chrome 并连接扩展后重试 `opencli doctor -v`。",
        }, ensure_ascii=False))
        raise SystemExit(2)

    url = run_opencli(["get", "url"]).strip()
    if "devops-bk.heyteago.com" not in url:
        subprocess.run(
            ["bash", REUSE_WRAPPER, "--session", SESSION, "open", CONSOLE_ENTRY],
            text=True, capture_output=True, timeout=60, check=False,
        )
        url = run_opencli(["get", "url"]).strip()

    if "/sso/login" in url.lower() or "login" in url.lower() and "console" not in url.lower():
        print(json.dumps({
            "ok": False,
            "status": "LOGIN_REQUIRED",
            "detail": "bk-console 未登录，请在 Chrome 手动登录 devops-bk 后重跑。",
        }, ensure_ascii=False))
        raise SystemExit(1)


def js_literal(value) -> str:
    """把 Python 值序列化成可安全嵌入 JS 的字面量。"""
    return json.dumps(value, ensure_ascii=False)


SENSITIVE_MARKERS = ("password", "passwd", "secret", "token", "cookie", "credential", "_pat", "pat_")


def _is_sensitive_name(value: object) -> bool:
    name = str(value or "").lower()
    return any(marker in name for marker in SENSITIVE_MARKERS)


def _redact_sensitive(value):
    """Redact both sensitive property names and key/value parameter records."""
    if isinstance(value, list):
        return [_redact_sensitive(item) for item in value]
    if not isinstance(value, dict):
        return value

    result = {}
    parameter_name = value.get("key") or value.get("id") or value.get("name")
    for key, item in value.items():
        if _is_sensitive_name(key) or (key == "value" and _is_sensitive_name(parameter_name)):
            result[key] = "[REDACTED]"
        else:
            result[key] = _redact_sensitive(item)
    return result


def _parse_opencli_output(output: str) -> dict:
    try:
        value, _ = json.JSONDecoder().raw_decode(output.lstrip())
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenCLI returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError("OpenCLI returned unexpected response type")
    return value


def api_call(method: str, path: str, project_code: str, body: dict | None = None,
             timeout: int = 120) -> str:
    """在页面上下文里对 BK 同源接口发起鉴权 fetch，返回 {http_status, ok, body}。"""
    method_u = method.upper()
    body_js = "undefined" if body is None else js_literal(json.dumps(body, ensure_ascii=False))
    js = f"""(() => new Promise(async (resolve) => {{
      try {{
        const headers = {{"Accept": "application/json"}};
        const projectCode = {js_literal(project_code)};
        if (projectCode) headers["X-DEVOPS-PROJECT-ID"] = projectCode;
        const method = {js_literal(method_u)};
        const opts = {{ method, credentials: "include", headers }};
        if ({body_js} !== undefined && method !== "GET") {{
          headers["Content-Type"] = "application/json";
          opts.body = {body_js};
        }}
        const resp = await fetch({js_literal(path)}, opts);
        const text = await resp.text();
        let parsed;
        try {{ parsed = JSON.parse(text); }} catch (e) {{ parsed = text.slice(0, 2000); }}
        resolve({{ http_status: resp.status, ok: resp.ok, body: parsed }});
      }} catch (err) {{
        resolve({{ http_status: -1, ok: false, error: String(err) }});
      }}
    }}))()"""
    return run_opencli(["eval", js], timeout=timeout)


# --- 只读命令 -------------------------------------------------------------

def cmd_inspect(a: argparse.Namespace) -> None:
    """读取流水线基础信息，可选附带某次构建详情。"""
    ensure_page()
    print(api_call("GET",
                   f"/ms/process/api/user/pipelineInfos/{a.project}/{a.pipeline}/detail",
                   a.project))
    if a.build:
        print(api_call("GET",
                       f"/ms/process/api/user/builds/{a.project}/{a.pipeline}/{a.build}/detail",
                       a.project))


def cmd_status(a: argparse.Namespace) -> None:
    """读取某次构建的状态详情与 executeCount。"""
    ensure_page()
    print(api_call("GET",
                   f"/ms/process/api/user/builds/{a.project}/{a.pipeline}/{a.build}/detail",
                   a.project))
    print(api_call("GET",
                   f"/ms/process/api/user/pipelines/cw/pipeline/{a.pipeline}/build/{a.build}/executeCount",
                   a.project))


def cmd_startup_info(a: argparse.Namespace) -> None:
    """读取手动启动所需的参数字段（用于发现 trigger 入参）。"""
    ensure_page()
    print(api_call("GET",
                   f"/ms/process/api/user/builds/{a.project}/{a.pipeline}/manualStartupInfo",
                   a.project))


def cmd_params(a: argparse.Namespace) -> None:
    """读取历史构建的实际参数（用于复用同一需求的 payload）。"""
    ensure_page()
    result = _parse_opencli_output(api_call(
        "GET",
        f"/ms/process/api/user/builds/{a.project}/{a.pipeline}/{a.build}/parameters",
        a.project,
    ))
    print(json.dumps(_redact_sensitive(result), ensure_ascii=False, indent=2))


# --- 写命令（默认 dry-run） ----------------------------------------------

def _load_values(a: argparse.Namespace) -> dict:
    """Load and normalize trigger values to BK's top-level string map."""
    if a.values_file:
        with open(a.values_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif a.values_json:
        data = json.loads(a.values_json)
    else:
        raise SystemExit("trigger 需要 --values-file 或 --values-json。")
    if not isinstance(data, dict):
        raise SystemExit("trigger 请求体必须是 JSON 对象。")
    if isinstance(data.get("values"), list):
        data = {
            item["key"]: str(item.get("value", ""))
            for item in data["values"]
            if isinstance(item, dict) and item.get("key")
        }
    if not data:
        raise SystemExit("trigger 请求体不能为空。")
    if not all(isinstance(value, str) for value in data.values()):
        raise SystemExit("trigger 参数值必须是字符串。")
    return data


def _confirm_gate(a: argparse.Namespace, action: str, path: str, body: dict | None) -> bool:
    """dry-run 时打印将发送的内容并返回 False；--confirm 时返回 True。"""
    if not a.confirm:
        print(json.dumps({
            "ok": True,
            "mode": "dry-run",
            "action": action,
            "would_POST": f"{ORIGIN}{path}",
            "body": body,
            "hint": "确认无误后加 --confirm 真正发送。",
        }, ensure_ascii=False, indent=2))
        return False
    return True


def cmd_trigger(a: argparse.Namespace) -> None:
    """手动触发一条流水线（默认 dry-run）。"""
    body = _load_values(a)
    path = f"/ms/process/api/user/builds/{a.project}/{a.pipeline}"
    if not _confirm_gate(a, "trigger", path, body):
        return
    ensure_page()
    print(api_call("POST", path, a.project, body=body))


def cmd_retry(a: argparse.Namespace) -> None:
    """重试一次已存在的构建（默认 dry-run）。"""
    query = urlencode({
        "taskId": a.task or "",
        "skip": "false",
        "failedContainer": "false",
    })
    path = f"/ms/process/api/user/builds/{a.project}/{a.pipeline}/{a.build}/retry?{query}"
    if not _confirm_gate(a, "retry", path, None):
        return
    ensure_page()
    print(api_call("POST", path, a.project))


def cmd_stop(a: argparse.Namespace) -> None:
    """停止一次运行中的构建（默认 dry-run）。"""
    path = f"/ms/process/api/user/builds/{a.project}/{a.pipeline}/{a.build}/stop"
    if not _confirm_gate(a, "stop", path, None):
        return
    ensure_page()
    print(api_call("POST", path, a.project))


def build_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器。"""
    p = argparse.ArgumentParser(
        prog="bk_pipeline.py",
        description="BlueKing 流水线 opencli 指令：只读随时跑，写命令默认 dry-run。",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp: argparse.ArgumentParser, need_build: bool = False) -> None:
        sp.add_argument("--project", required=True, help="projectCode")
        sp.add_argument("--pipeline", required=True, help="pipelineId")
        if need_build:
            sp.add_argument("--build", required=True, help="buildId")

    sp = sub.add_parser("inspect", help="流水线信息(+可选构建详情)")
    add_common(sp)
    sp.add_argument("--build", help="buildId（可选）")
    sp.set_defaults(func=cmd_inspect)

    sp = sub.add_parser("status", help="构建状态 + executeCount")
    add_common(sp, need_build=True)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("startup-info", help="手动启动参数字段")
    add_common(sp)
    sp.set_defaults(func=cmd_startup_info)

    sp = sub.add_parser("params", help="历史构建实际参数")
    add_common(sp, need_build=True)
    sp.set_defaults(func=cmd_params)

    sp = sub.add_parser("trigger", help="手动触发(默认 dry-run)")
    add_common(sp)
    sp.add_argument("--values-file", help="JSON 文件，参数为顶层字符串键值")
    sp.add_argument("--values-json", help="内联 JSON，例如 {\"BK_CI_BUILD_MSG\":\"手动触发\"}")
    sp.add_argument("--confirm", action="store_true", help="真正发送 POST")
    sp.set_defaults(func=cmd_trigger)

    sp = sub.add_parser("retry", help="重试构建(默认 dry-run)")
    add_common(sp, need_build=True)
    sp.add_argument("--task", help="失败任务 taskId；不传则重试整个构建")
    sp.add_argument("--confirm", action="store_true", help="真正发送 POST")
    sp.set_defaults(func=cmd_retry)

    sp = sub.add_parser("stop", help="停止构建(默认 dry-run)")
    add_common(sp, need_build=True)
    sp.add_argument("--confirm", action="store_true", help="真正发送 POST")
    sp.set_defaults(func=cmd_stop)

    return p


def main() -> None:
    """入口。"""
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create a DingTalk online spreadsheet test-delivery document via dws."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


PIPELINE_BASE_URL = "https://devops-bk.heyteago.com/console/pipeline"
SHEET_TEMPLATE_ORDER = [
    "服务清单",
    "提测配置清单-TEST",
    "提测配置清单-PROD",
    "数据库脚本",
    "定时任务 XXL-JOB",
    "发布流程",
]
SHEET_NAMES = SHEET_TEMPLATE_ORDER
BATCH_ESTIMATED_REMOTE_CALLS = 6
LEGACY_ESTIMATED_REMOTE_CALLS = 22

DEFAULT_TARGETS_BY_REGION = {
    "cn": {
        "workspaceId": "26116527504",
        "folderId": "P7QG4Yx2Jp7N1PAgi41lknj2V9dEq3XD",
        "folderName": "国内迭代",
    },
    "intl": {
        "workspaceId": "",
        "folderId": "",
        "folderName": "海外迭代",
    },
}


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def text(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(part for item in value if (part := text(item)))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False) if value else ""
    return str(value)


def yes_no(value: Any) -> str:
    if value is True:
        return "是"
    if value is False:
        return "否"
    return text(value)


def parse_json_output(stdout: str, command: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"dws did not return JSON for command: {' '.join(command)}\n{stdout}"
        ) from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"dws returned non-object JSON: {data}")
    if data.get("success") is False or data.get("error"):
        raise RuntimeError(json.dumps(data, ensure_ascii=False, indent=2))
    return data


def run_dws(args: list[str]) -> dict[str, Any]:
    command = ["dws", *args, "--format", "json", "--yes"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return parse_json_output(result.stdout, command)


def run_dws_mcp(product: str, tool: str, payload: dict[str, Any]) -> dict[str, Any]:
    command = [
        "dws",
        "mcp",
        product,
        tool,
        "--json",
        json.dumps(payload, ensure_ascii=False),
        "--format",
        "json",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    data = parse_json_output(result.stdout, command)
    response = data.get("response")
    if isinstance(response, dict):
        content = response.get("content")
        if isinstance(content, dict):
            return content
    return data


def recursive_values(obj: Any):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key, value
            yield from recursive_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from recursive_values(item)


def extract_node_id(response: dict[str, Any]) -> str:
    preferred_keys = {"nodeId", "node_id", "dentryUuid", "dentry_uuid", "uuid"}
    for key, value in recursive_values(response):
        if key in preferred_keys and isinstance(value, str) and value.strip():
            return value.strip()
    for _, value in recursive_values(response):
        if isinstance(value, str):
            match = re.search(r"/nodes/([A-Za-z0-9]+)", value)
            if match:
                return match.group(1)
    raise RuntimeError(
        "Could not find nodeId in dws sheet create response:\n"
        + json.dumps(response, ensure_ascii=False, indent=2)
    )


def column_name(index: int) -> str:
    name = ""
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def range_for(values: list[list[str]]) -> str:
    rows = max(1, len(values))
    cols = max(1, max((len(row) for row in values), default=1))
    return f"A1:{column_name(cols)}{rows}"


def parse_range_dimensions(range_address: str) -> tuple[int, int]:
    start, end = range_address.split(":")
    start_col = re.match(r"([A-Z]+)(\d+)", start)
    end_col = re.match(r"([A-Z]+)(\d+)", end)
    if not start_col or not end_col:
        raise ValueError(f"Invalid range address: {range_address}")
    start_name, start_row = start_col.group(1), int(start_col.group(2))
    end_name, end_row = end_col.group(1), int(end_col.group(2))

    def col_index(name: str) -> int:
        value = 0
        for ch in name:
            value = value * 26 + (ord(ch) - 64)
        return value

    rows = end_row - start_row + 1
    cols = col_index(end_name) - col_index(start_name) + 1
    return rows, cols


def normalize_rows(rows: list[list[Any]]) -> list[list[str]]:
    width = max((len(row) for row in rows), default=1)
    return [[text(cell) for cell in row] + [""] * (width - len(row)) for row in rows]


def build_font_weights(rows: int, cols: int) -> list[list[str]]:
    return [["bold"] * cols for _ in range(rows)]


def pipeline_url(project_id: str, pipeline_id: str) -> str:
    if not project_id or not pipeline_id:
        return ""
    return f"{PIPELINE_BASE_URL}/{project_id}/{pipeline_id}"


def pipeline_detail_url(project_id: str, pipeline_id: str, build_id: str | None) -> str:
    base_url = pipeline_url(project_id, pipeline_id)
    if not base_url or not build_id:
        return base_url
    return f"{base_url}/detail/{build_id}"


def merge_context(evidence: dict[str, Any], bk_config: dict[str, Any]) -> dict[str, Any]:
    context = dict(evidence)
    demand = bk_config.get("demand") or {}
    requirement = dict(context.get("requirement") or {})
    requirement.setdefault("number", demand.get("number"))
    requirement.setdefault("title", demand.get("title"))
    requirement.setdefault("url", demand.get("url"))
    context["requirement"] = requirement
    if "developer" not in context and bk_config.get("developer"):
        context["developer"] = bk_config["developer"]
    if "tester" not in context and bk_config.get("tester"):
        context["tester"] = bk_config["tester"]
    if bk_config.get("pipelines"):
        context["pipelines"] = bk_config["pipelines"]
    return context


def normalize_region(value: Any) -> str:
    region = text(value).strip().lower()
    if region in {"cn", "domestic", "china", "国内"}:
        return "cn"
    if region in {"intl", "international", "overseas", "海外", "国外"}:
        return "intl"
    return region


def resolve_target_location(args: argparse.Namespace, context: dict[str, Any]) -> dict[str, str]:
    """Resolve AliDocs target folder from explicit args or demand region."""
    explicit_workspace = text(args.workspace_id).strip()
    explicit_folder = text(args.folder_id).strip()
    if explicit_workspace or explicit_folder:
        return {
            "workspaceId": explicit_workspace,
            "folderId": explicit_folder,
            "source": "explicit_args",
            "folderName": "",
        }

    region = normalize_region(context.get("region"))
    target = DEFAULT_TARGETS_BY_REGION.get(region)
    if not target:
        return {"workspaceId": "", "folderId": "", "source": "unresolved", "folderName": ""}

    workspace_id = text(target.get("workspaceId")).strip()
    folder_id = text(target.get("folderId")).strip()
    if not workspace_id or not folder_id:
        folder_name = text(target.get("folderName")) or region
        raise ValueError(
            f"Missing default AliDocs target for region={region} ({folder_name}). "
            "Pass --workspace-id and --folder-id explicitly, or configure DEFAULT_TARGETS_BY_REGION."
        )
    return {
        "workspaceId": workspace_id,
        "folderId": folder_id,
        "source": f"region:{region}",
        "folderName": text(target.get("folderName")),
    }


def local_git_user_name(repo_path: Path) -> str:
    if not repo_path.exists():
        return ""
    for command in (
        ["git", "-C", str(repo_path), "config", "--local", "user.name"],
        ["git", "-C", str(repo_path), "config", "user.name"],
    ):
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return ""


def context_services(context: dict[str, Any]) -> list[dict[str, Any]]:
    evidence_services = list(context.get("services") or [])
    evidence_by_name = {
        text(service.get("name") or service.get("service_name")): service
        for service in evidence_services
        if text(service.get("name") or service.get("service_name"))
    }
    pipeline_services = []
    for pipeline in context.get("pipelines") or []:
        for service in pipeline.get("services") or []:
            service_name = text(service.get("service_name") or service.get("name"))
            merged_service = dict(evidence_by_name.get(service_name) or {})
            pipeline_fields = {
                "name": service_name,
                "branch": service.get("branch"),
                "owner": service.get("owner"),
                "level": service.get("level"),
                "pipeline_name": service.get("pipeline_name"),
            }
            merged_service.update({
                key: value for key, value in pipeline_fields.items()
                if value not in (None, "")
            })
            pipeline_services.append(merged_service)

    # The delivery service list mirrors services that have a demand pipeline.
    # Maven dependency artifacts may still appear in development evidence, but
    # they are published before consumers and are not independently deployed.
    services = pipeline_services or evidence_services
    return [service for service in services if is_delivery_service(service)]


def is_delivery_service(service: dict[str, Any]) -> bool:
    repository_type = text(
        service.get("repository_type")
        or service.get("repositoryType")
        or service.get("type")
    ).strip().lower()
    remote_action = text(
        service.get("remote_action") or service.get("remoteAction")
    ).strip().lower()
    return repository_type != "maven_dependency" and remote_action != "artifact_publish"


def default_owner_name(context: dict[str, Any]) -> str:
    developer = context.get("developer") or {}
    explicit_owner = text(developer.get("name")) or text(developer.get("id"))
    if explicit_owner:
        return explicit_owner

    cwd = Path.cwd()
    for service in context_services(context):
        service_name = text(service.get("name") or service.get("service_name"))
        if not service_name:
            continue
        owner = local_git_user_name(cwd / service_name)
        if owner:
            return owner

    return local_git_user_name(cwd)


def first_pipeline_for_service(context: dict[str, Any], service_name: str | None) -> dict[str, Any]:
    has_service_bindings = False
    for pipeline in context.get("pipelines") or []:
        pipeline_services = pipeline.get("services") or []
        has_service_bindings = has_service_bindings or bool(pipeline_services)
        for service in pipeline_services:
            if service.get("service_name") == service_name:
                return pipeline
    if has_service_bindings:
        return {}
    pipelines = context.get("pipelines") or []
    return pipelines[0] if pipelines else {}


def build_service_rows(context: dict[str, Any]) -> list[list[Any]]:
    requirement = context.get("requirement") or {}
    default_owner = default_owner_name(context)
    demand_name = " ".join(
        part for part in [text(requirement.get("number")), text(requirement.get("title"))]
        if part
    )
    rows = [[
        "流水线名称",
        "服务AppID",
        "服务名",
        "名称",
        "负责人",
        "分支",
        "服务等级",
        "是否新服务",
        "服务规格",
        "首次部署流水线",
        "需求流水线",
    ]]
    services = context_services(context)
    for service in services:
        service_name = service.get("name") or service.get("service_name")
        pipeline = first_pipeline_for_service(context, service_name)
        rows.append([
            pipeline.get("pipelineName") or demand_name,
            service.get("app_id") or service.get("appId") or "",
            service_name,
            service.get("display_name") or service.get("name_cn") or "",
            service.get("owner") or default_owner,
            service.get("branch"),
            service.get("level") or "",
            yes_no(service.get("is_new_service")),
            service.get("spec") or "",
            service.get("first_deploy_pipeline") or "",
            pipeline_detail_url(
                text(pipeline.get("projectId")),
                text(pipeline.get("pipelineId")),
                pipeline.get("buildId"),
            ) if pipeline else "",
        ])
    return rows


def build_config_rows(context: dict[str, Any], env_key: str) -> list[list[Any]]:
    rows = [["服务", "配置", "负责人", "备注"]]
    default_owner = default_owner_name(context)
    configs = context.get(env_key) or context.get("config_changes") or []
    for item in configs:
        if isinstance(item, dict):
            rows.append([
                item.get("service"),
                item.get("config") or item.get("content"),
                item.get("owner") or default_owner,
                item.get("remark") or item.get("note"),
            ])
        else:
            rows.append(["", item, default_owner, ""])
    return rows


def build_db_rows(context: dict[str, Any]) -> list[list[Any]]:
    rows = [["数据库类型", "数据库名称", "DDL语句", "负责人", "涉及服务名称", "状态"]]
    default_owner = default_owner_name(context)
    for item in context.get("db_scripts") or []:
        if isinstance(item, dict):
            rows.append([
                item.get("type") or item.get("database_type"),
                item.get("database") or item.get("database_name"),
                item.get("ddl") or item.get("sql"),
                item.get("owner") or default_owner,
                item.get("service") or item.get("service_name"),
                item.get("status") or "",
            ])
        else:
            rows.append(["", "", item, default_owner, "", ""])
    return rows


def build_job_rows(context: dict[str, Any]) -> list[list[Any]]:
    rows = [
        ["AppName", "名称", "注册方式"],
        *([["", "", ""]] * 9),
        [
            "执行器",
            "任务描述",
            "负责人",
            "报警邮件",
            "调度类型",
            "Cron",
            "运行模式",
            "JobHandler",
            "任务参数",
            "路由策略",
            "子任务id",
            "调度过期策略",
            "阻塞处理策略",
            "任务超时时间",
            "失败重试次数",
            "状态",
        ],
    ]
    default_owner = default_owner_name(context)
    for item in context.get("jobs") or []:
        if isinstance(item, dict):
            rows.append([
                item.get("executor"),
                item.get("description") or item.get("task_description"),
                item.get("owner") or default_owner,
                item.get("alarm_email"),
                item.get("schedule_type"),
                item.get("cron"),
                item.get("run_mode"),
                item.get("job_handler"),
                item.get("params"),
                item.get("route_strategy"),
                item.get("child_job_id"),
                item.get("misfire_strategy"),
                item.get("block_strategy"),
                item.get("timeout"),
                item.get("retry_count"),
                item.get("status") or "",
            ])
    return rows


def build_release_flow_rows(context: dict[str, Any]) -> list[list[Any]]:
    rows = [["步骤", "动作", "完成情况", "预计时间", "备注"]]
    for item in context.get("release_flow") or []:
        if isinstance(item, dict):
            rows.append([
                item.get("step"),
                item.get("action"),
                item.get("status"),
                item.get("eta") or item.get("expected_time"),
                item.get("remark") or item.get("note"),
            ])
        else:
            rows.append(["", item, "", "", ""])
    return rows


def build_workbook(context: dict[str, Any]) -> dict[str, list[list[str]]]:
    return {
        "服务清单": normalize_rows(build_service_rows(context)),
        "提测配置清单-TEST": normalize_rows(build_config_rows(context, "test_configs")),
        "提测配置清单-PROD": normalize_rows(build_config_rows(context, "prod_configs")),
        "数据库脚本": normalize_rows(build_db_rows(context)),
        "定时任务 XXL-JOB": normalize_rows(build_job_rows(context)),
        "发布流程": normalize_rows(build_release_flow_rows(context)),
    }


def build_header_style_plan() -> dict[str, list[str]]:
    return {
        "服务清单": ["A1:K1"],
        "提测配置清单-TEST": ["A1:D1"],
        "提测配置清单-PROD": ["A1:D1"],
        "数据库脚本": ["A1:F1"],
        "定时任务 XXL-JOB": ["A1:C1", "A11:P11"],
        "发布流程": ["A1:E1"],
    }


def build_table_put_sheets(
    workbook: dict[str, list[list[str]]],
) -> list[dict[str, Any]]:
    """Build a schema-safe table_put payload that only bootstraps sheet tabs."""
    names = list(workbook)
    if len(names) > 1:
        # DingTalk inserts newly created sheets before existing non-default tabs.
        names = [names[0], *reversed(names[1:])]

    sheets = []
    for name in names:
        rows = normalize_rows(workbook[name])
        width = max((len(row) for row in rows), default=1)
        sheets.append({
            "name": name,
            "columns": [f"column_{index}" for index in range(1, width + 1)],
            # dws v1.0.10 validates table_put cells as objects even though the
            # Tool IR describes primitive values. Keep data empty and write the
            # real cells through batch_update below.
            "data": [],
            "header": False,
            "mode": "overwrite",
            "startCell": "A1",
            "allowOverwrite": True,
        })
    return sheets


def build_sheet_write_operations(
    workbook: dict[str, list[list[str]]],
    style_plan: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Build one value-and-style operation per sheet for atomic batch writing."""
    operations = []
    for sheet_name, rows in workbook.items():
        normalized = normalize_rows(rows)
        cells = [
            [{"type": "text", "text": value} for value in row]
            for row in normalized
        ]

        for range_address in style_plan.get(sheet_name, []):
            start, end = range_address.split(":")
            start_match = re.fullmatch(r"([A-Z]+)(\d+)", start)
            end_match = re.fullmatch(r"([A-Z]+)(\d+)", end)
            if not start_match or not end_match:
                raise ValueError(f"Invalid range address: {range_address}")

            def col_index(name: str) -> int:
                value = 0
                for ch in name:
                    value = value * 26 + (ord(ch) - 64)
                return value

            start_col = col_index(start_match.group(1))
            end_col = col_index(end_match.group(1))
            start_row = int(start_match.group(2))
            end_row = int(end_match.group(2))
            for row_index in range(start_row - 1, end_row):
                for col_index_value in range(start_col - 1, end_col):
                    cells[row_index][col_index_value]["cellStyles"] = {
                        "fontWeight": "bold"
                    }

        operations.append({
            "toolName": "set_cell_range",
            "input": {
                "sheetId": sheet_name,
                "rangeAddress": range_for(normalized),
                "cells": cells,
            },
        })
    return operations


def default_doc_name(context: dict[str, Any]) -> str:
    requirement = context.get("requirement") or {}
    number = text(requirement.get("number"))
    title = text(requirement.get("title"))
    if not number or not title:
        raise ValueError(
            "AliDocs document naming requires both the BK requirement number and Chinese title"
        )
    return f"{number}-{title}"


def resolve_doc_name(context: dict[str, Any], requested_name: str | None) -> str:
    expected_name = default_doc_name(context)
    if requested_name and text(requested_name) != expected_name:
        raise ValueError(
            f"AliDocs document name must match the BK requirement: {expected_name}"
        )
    return expected_name


def sheet_identifier(sheet: dict[str, Any]) -> str:
    return text(sheet.get("sheetId") or sheet.get("id") or sheet.get("name"))


def sheet_title(sheet: dict[str, Any]) -> str:
    return text(sheet.get("name") or sheet.get("title"))


def plan_sheet_creation(
    existing_sheets: list[dict[str, Any]],
    template_order: list[str],
) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    if not template_order:
        return plan

    remaining = list(template_order)
    if existing_sheets:
        default_sheet = existing_sheets[0]
        plan.append({
            "name": remaining.pop(0),
            "actualName": sheet_title(default_sheet),
            "sheetId": sheet_identifier(default_sheet),
            "action": "reuse_default",
            "canRename": True,
        })

    for name in reversed(remaining):
        plan.append({
            "name": name,
            "actualName": name,
            "sheetId": "",
            "action": "create",
            "canRename": True,
        })
    return plan


def rename_default_sheet_if_needed(node_id: str, sheet_item: dict[str, Any]) -> dict[str, Any] | None:
    if sheet_item.get("action") != "reuse_default":
        return None
    sheet_id = text(sheet_item.get("sheetId"))
    target_name = text(sheet_item.get("name"))
    actual_name = text(sheet_item.get("actualName"))
    if not sheet_id or not target_name or actual_name == target_name:
        return None
    return run_dws_mcp("sheet", "update_sheet", {
        "nodeId": node_id,
        "sheetId": sheet_id,
        "title": target_name,
        "index": 0,
    })


def apply_bold_styles(node_id: str, sheet_id: str, ranges: list[str]) -> list[dict[str, Any]]:
    results = []
    for range_address in ranges:
        rows, cols = parse_range_dimensions(range_address)
        results.append(run_dws_mcp("sheet", "update_range", {
            "nodeId": node_id,
            "sheetId": sheet_id,
            "rangeAddress": range_address,
            "fontWeights": build_font_weights(rows, cols),
        }))
    return results


def create_document(args: argparse.Namespace, workbook: dict[str, list[list[str]]], context: dict[str, Any]) -> dict[str, Any]:
    doc_name = resolve_doc_name(context, args.name)
    style_plan = build_header_style_plan()
    target_location = resolve_target_location(args, context)
    write_strategy = getattr(args, "write_strategy", "batch")
    if args.dry_run:
        return {
            "dry_run": True,
            "writeStrategy": write_strategy,
            "estimatedRemoteCalls": (
                BATCH_ESTIMATED_REMOTE_CALLS
                if write_strategy == "batch"
                else LEGACY_ESTIMATED_REMOTE_CALLS
            ),
            "legacyEstimatedRemoteCalls": LEGACY_ESTIMATED_REMOTE_CALLS,
            "documentName": doc_name,
            "workspaceId": target_location["workspaceId"],
            "folderId": target_location["folderId"],
            "targetSource": target_location["source"],
            "targetFolderName": target_location["folderName"],
            "sheets": list(workbook.keys()),
            "rowCounts": {name: len(rows) for name, rows in workbook.items()},
            "headerStylePlan": style_plan,
            "missingDataPolicy": "empty cells",
        }

    create_args = ["sheet", "create", "--name", doc_name]
    if target_location["workspaceId"]:
        create_args.extend(["--workspace", target_location["workspaceId"]])
    if target_location["folderId"]:
        create_args.extend(["--folder", target_location["folderId"]])
    create_response = run_dws(create_args)
    node_id = extract_node_id(create_response)

    initial_list_response = run_dws(["sheet", "list", "--node", node_id])
    sheet_plan = plan_sheet_creation(
        initial_list_response.get("sheets", []),
        list(workbook.keys()),
    )
    remote_call_count = 2

    if write_strategy == "batch":
        default_sheet = sheet_plan[0] if sheet_plan else None
        if default_sheet:
            rename_response = rename_default_sheet_if_needed(node_id, default_sheet)
            if rename_response:
                remote_call_count += 1

        table_response = run_dws_mcp("sheet", "table_put", {
            "nodeId": node_id,
            "sheets": build_table_put_sheets(workbook),
        })
        remote_call_count += 1

        write_operations = build_sheet_write_operations(workbook, style_plan)
        write_response = run_dws_mcp("sheet", "batch_update", {
            "nodeId": node_id,
            "operations": write_operations,
            "continueOnError": False,
        })
        remote_call_count += 1

        list_response = run_dws(["sheet", "list", "--node", node_id])
        remote_call_count += 1
        final_sheet_names = [sheet_title(sheet) for sheet in list_response.get("sheets", [])]
        order_matches = final_sheet_names == list(workbook.keys())
        online_url = f"https://alidocs.dingtalk.com/i/nodes/{node_id}"
        return {
            "success": order_matches,
            "documentName": doc_name,
            "nodeId": node_id,
            "url": online_url,
            "workspaceId": target_location["workspaceId"],
            "folderId": target_location["folderId"],
            "targetSource": target_location["source"],
            "targetFolderName": target_location["folderName"],
            "writeStrategy": "batch",
            "remoteCallCount": remote_call_count,
            "sheetBootstrap": table_response.get("success", True),
            "writeBatch": write_response.get("success", True),
            "writeOperationCount": len(write_operations),
            "sheetTemplateOrder": list(workbook.keys()),
            "actualSheetOrder": final_sheet_names,
            "headerStylePlan": style_plan,
            "sheetList": list_response.get("sheets", []),
            "warnings": [] if order_matches else ["Created sheet order does not match the template order."],
        }

    created_sheets = []
    for sheet_item in sheet_plan:
        sheet_name = sheet_item["name"]
        rows = workbook[sheet_name]
        if sheet_item["action"] == "create":
            sheet_response = run_dws(["sheet", "new", "--node", node_id, "--name", sheet_name])
            remote_call_count += 1
            sheet_id = sheet_response.get("sheetId") or sheet_response.get("id") or sheet_name
            sheet_item["sheetId"] = text(sheet_id)
        else:
            sheet_id = sheet_item["sheetId"]
            rename_response = rename_default_sheet_if_needed(node_id, sheet_item)
            if rename_response:
                remote_call_count += 1
                sheet_item["actualName"] = text(rename_response.get("name")) or sheet_name
        update_response = run_dws([
            "sheet",
            "range",
            "update",
            "--node",
            node_id,
            "--sheet-id",
            str(sheet_id),
            "--range",
            range_for(rows),
            "--values",
            json.dumps(rows, ensure_ascii=False),
        ])
        remote_call_count += 1
        style_responses = apply_bold_styles(node_id, str(sheet_id), style_plan.get(sheet_name, []))
        remote_call_count += len(style_responses)
        created_sheets.append({
            "name": sheet_name,
            "actualName": sheet_item.get("actualName") or sheet_name,
            "sheetId": sheet_id,
            "action": sheet_item["action"],
            "rows": len(rows),
            "update": update_response.get("success", True),
            "styles": len(style_responses),
            "styleRanges": style_plan.get(sheet_name, []),
        })

    list_response = run_dws(["sheet", "list", "--node", node_id])
    remote_call_count += 1
    final_sheet_names = [sheet_title(sheet) for sheet in list_response.get("sheets", [])]
    online_url = f"https://alidocs.dingtalk.com/i/nodes/{node_id}"
    return {
        "success": True,
        "documentName": doc_name,
        "nodeId": node_id,
        "url": online_url,
        "workspaceId": target_location["workspaceId"],
        "folderId": target_location["folderId"],
        "targetSource": target_location["source"],
        "targetFolderName": target_location["folderName"],
        "writeStrategy": "legacy",
        "remoteCallCount": remote_call_count,
        "createdSheets": created_sheets,
        "sheetTemplateOrder": list(workbook.keys()),
        "actualSheetOrder": final_sheet_names,
        "headerStylePlan": style_plan,
        "sheetNameLimitations": [],
        "sheetList": list_response.get("sheets", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-id", help="DingTalk workspaceId / knowledge base ID")
    parser.add_argument("--folder-id", help="Optional target folder node ID")
    parser.add_argument(
        "--name",
        help="Optional assertion; must equal <BK requirement number>-<BK requirement Chinese title>",
    )
    parser.add_argument("--evidence", help="Evidence JSON path")
    parser.add_argument("--bk-config", help="BK docs/bk/{demand}.json path")
    parser.add_argument("--output-json", help="Write result JSON to this path")
    parser.add_argument(
        "--write-strategy",
        choices=["batch", "legacy"],
        default="batch",
        help="Use the fast multi-sheet batch path or the legacy per-sheet path",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing AliDocs")
    args = parser.parse_args()

    if not args.evidence and not args.bk_config:
        parser.error("at least one of --evidence or --bk-config is required")

    evidence = load_json(args.evidence)
    bk_config = load_json(args.bk_config)
    context = merge_context(evidence, bk_config)
    workbook = build_workbook(context)
    result = create_document(args, workbook, context)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.output_json:
        Path(args.output_json).write_text(output + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

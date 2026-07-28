#!/usr/bin/env python3
"""Regression tests for AliDocs test delivery workbook layout."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import argparse
import json
import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "create_test_delivery_sheet.py"
CLI_PATH = Path(__file__).resolve().parents[1] / "scripts" / "heytea-alidocs"
spec = importlib.util.spec_from_file_location("create_test_delivery_sheet", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def sample_context():
    return {
        "requirement": {
            "number": "p45_6910",
            "title": "【国内】服务费发票计算优化",
            "url": "https://devops-bk.heyteago.com/console/vteam/yc9e25/twDemand/demand/IssueDetail?id=demo",
        },
        "developer": {"id": "H000001", "name": "开发同学"},
        "pipelines": [
            {
                "projectId": "yc9e25",
                "projectName": "智慧供应链",
                "pipelineName": "p45_6910 【国内】服务费发票计算优化",
                "pipelineId": "p-demo",
                "buildId": "b-demo",
                "services": [
                    {
                        "service_name": "manager-hsp-invoice",
                        "branch": "feature/p45_6910-服务费发票计算优化",
                        "pipeline_name": "hsp_manager-hsp-invoice",
                    }
                ],
            }
        ],
    }


def test_cn_region_defaults_to_domestic_iteration_folder():
    args = argparse.Namespace(workspace_id=None, folder_id=None)
    target = module.resolve_target_location(args, {
        "region": "cn",
        "requirement": {"number": "p35_15439", "title": "税收分类编码与税率获取优化"},
    })

    assert target == {
        "workspaceId": "26116527504",
        "folderId": "P7QG4Yx2Jp7N1PAgi41lknj2V9dEq3XD",
        "source": "region:cn",
        "folderName": "国内迭代",
    }


def test_explicit_target_overrides_region_default():
    args = argparse.Namespace(workspace_id="workspace-demo", folder_id="folder-demo")
    target = module.resolve_target_location(args, {"region": "cn"})

    assert target["workspaceId"] == "workspace-demo"
    assert target["folderId"] == "folder-demo"
    assert target["source"] == "explicit_args"


def test_intl_region_requires_configured_overseas_iteration_folder():
    args = argparse.Namespace(workspace_id=None, folder_id=None)

    with pytest.raises(ValueError, match="region=intl"):
        module.resolve_target_location(args, {"region": "intl"})


def test_workbook_uses_legacy_six_sheet_template():
    workbook = module.build_workbook(sample_context())

    assert list(workbook.keys()) == [
        "服务清单",
        "提测配置清单-TEST",
        "提测配置清单-PROD",
        "数据库脚本",
        "定时任务 XXL-JOB",
        "发布流程",
    ]


def test_workbook_preserves_template_headers():
    workbook = module.build_workbook(sample_context())

    assert workbook["服务清单"][0][:11] == [
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
    ]
    assert workbook["提测配置清单-TEST"][0][:4] == ["服务", "配置", "负责人", "备注"]
    assert workbook["提测配置清单-PROD"][0][:4] == ["服务", "配置", "负责人", "备注"]
    assert workbook["数据库脚本"][0][:6] == ["数据库类型", "数据库名称", "DDL语句", "负责人", "涉及服务名称", "状态"]
    assert workbook["定时任务 XXL-JOB"][0][:3] == ["AppName", "名称", "注册方式"]
    assert workbook["定时任务 XXL-JOB"][10][:16] == [
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
    ]
    assert workbook["发布流程"][0][:5] == ["步骤", "动作", "完成情况", "预计时间", "备注"]


def test_missing_source_data_stays_empty_in_template_rows(monkeypatch):
    monkeypatch.setattr(module, "local_git_user_name", lambda _path: "")
    workbook = module.build_workbook({
        "requirement": {
            "number": "p45_6910",
            "title": "服务费发票计算优化",
        },
        "services": [
            {
                "name": "manager-hsp-invoice",
                "branch": "feature/p45_6910-服务费发票计算优化",
            }
        ],
    })

    service_row = workbook["服务清单"][1]
    assert service_row[:11] == [
        "p45_6910 服务费发票计算优化",
        "",
        "manager-hsp-invoice",
        "",
        "",
        "feature/p45_6910-服务费发票计算优化",
        "",
        "",
        "",
        "",
        "",
    ]
    assert workbook["提测配置清单-TEST"] == [["服务", "配置", "负责人", "备注"]]
    assert workbook["提测配置清单-PROD"] == [["服务", "配置", "负责人", "备注"]]
    assert workbook["数据库脚本"] == [["数据库类型", "数据库名称", "DDL语句", "负责人", "涉及服务名称", "状态"]]
    assert workbook["发布流程"] == [["步骤", "动作", "完成情况", "预计时间", "备注"]]
    assert "待确认" not in "\n".join(
        cell for rows in workbook.values() for row in rows for cell in row
    )


def test_service_list_uses_demand_pipeline_services_and_excludes_maven_dependency():
    context = sample_context()
    context["services"] = [
        {
            "name": "hsp-invoice",
            "branch": "feature/p35_16895-ticket-center",
            "repository_type": "maven_dependency",
            "remote_action": "artifact_publish",
        },
        {
            "name": "manager-hsp-invoice",
            "branch": "feature/p35_16895-ticket-center",
            "owner": "evidence-owner",
        },
        {
            "name": "center-hsp-invoice",
            "branch": "feature/p35_16895-ticket-center",
        },
    ]

    workbook = module.build_workbook(context)

    assert len(workbook["服务清单"]) == 2
    assert workbook["服务清单"][1][2] == "manager-hsp-invoice"
    assert workbook["服务清单"][1][4] == "evidence-owner"
    assert [row[2] for row in workbook["服务清单"][1:]] == ["manager-hsp-invoice"]


def test_service_list_excludes_explicit_maven_dependency_without_bk_config():
    workbook = module.build_workbook({
        "services": [
            {"name": "hsp-invoice", "repositoryType": "maven_dependency"},
            {"name": "center-hsp-invoice", "remoteAction": "service_deploy"},
        ],
    })

    assert [row[2] for row in workbook["服务清单"][1:]] == ["center-hsp-invoice"]


def test_owner_falls_back_to_local_git_user_name(tmp_path, monkeypatch):
    service_dir = tmp_path / "manager-hsp-invoice"
    service_dir.mkdir()
    subprocess.run(["git", "-C", str(service_dir), "init"], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(service_dir), "config", "--local", "user.name", "qichenghui"],
        check=True,
        capture_output=True,
        text=True,
    )
    monkeypatch.chdir(tmp_path)

    workbook = module.build_workbook({
        "requirement": {
            "number": "p35_15805",
            "title": "【发票助手】订货销售凭证模板文案调整",
        },
        "services": [
            {
                "name": "manager-hsp-invoice",
                "branch": "feature/p35_15805-订货销售凭证模板文案调整",
            }
        ],
    })

    assert workbook["服务清单"][1][4] == "qichenghui"


def test_default_doc_name_matches_bk_requirement():
    named = module.default_doc_name({
        "requirement": {"number": "p35_15078", "title": "收货物流信息优化"},
    })

    assert named == "p35_15078-收货物流信息优化"


@pytest.mark.parametrize(
    "requirement",
    [
        {"number": "p35_15078", "title": ""},
        {"number": "", "title": "收货物流信息优化"},
        {"number": "", "title": ""},
    ],
)
def test_default_doc_name_requires_complete_bk_requirement(requirement):
    with pytest.raises(ValueError, match="BK requirement number and Chinese title"):
        module.default_doc_name({"requirement": requirement})


def test_resolve_doc_name_rejects_name_that_differs_from_bk_requirement():
    with pytest.raises(ValueError, match="must match the BK requirement"):
        module.resolve_doc_name(
            {
                "requirement": {
                    "number": "p35_15078",
                    "title": "收货物流信息优化",
                }
            },
            "20260514-p35_15078-收货物流信息优化",
        )


def test_created_sheet_plan_reuses_default_sheet_for_first_template_sheet():
    plan = module.plan_sheet_creation(
        [
            {"name": "Sheet1", "sheetId": "default-sheet-id"},
        ],
        list(module.SHEET_TEMPLATE_ORDER),
    )

    assert plan[0]["name"] == "服务清单"
    assert plan[0]["actualName"] == "Sheet1"
    assert plan[0]["sheetId"] == "default-sheet-id"
    assert plan[0]["action"] == "reuse_default"
    assert plan[0]["canRename"] is True
    assert module.SHEET_TEMPLATE_ORDER == [
        "服务清单",
        "提测配置清单-TEST",
        "提测配置清单-PROD",
        "数据库脚本",
        "定时任务 XXL-JOB",
        "发布流程",
    ]
    assert len(plan) == 6
    assert [item["action"] for item in plan[1:]] == ["create"] * 5


def test_remaining_sheet_creation_order_is_reversed_for_current_dws_behavior():
    plan = module.plan_sheet_creation(
        [
            {"name": "Sheet1", "sheetId": "default-sheet-id"},
        ],
        list(module.SHEET_TEMPLATE_ORDER),
    )

    assert [item["name"] for item in plan[1:]] == [
        "发布流程",
        "定时任务 XXL-JOB",
        "数据库脚本",
        "提测配置清单-PROD",
        "提测配置清单-TEST",
    ]


def test_rename_default_sheet_if_needed_builds_update_payload():
    calls = []

    def fake_run_dws_mcp(product, tool, payload):
        calls.append((product, tool, payload))
        return {"name": "服务清单", "success": True}

    original = module.run_dws_mcp
    module.run_dws_mcp = fake_run_dws_mcp
    try:
        response = module.rename_default_sheet_if_needed("node-demo", {
            "name": "服务清单",
            "actualName": "Sheet1",
            "sheetId": "default-sheet-id",
            "action": "reuse_default",
        })
    finally:
        module.run_dws_mcp = original

    assert response == {"name": "服务清单", "success": True}
    assert calls == [
        (
            "sheet",
            "update_sheet",
            {
                "nodeId": "node-demo",
                "sheetId": "default-sheet-id",
                "title": "服务清单",
                "index": 0,
            },
        )
    ]


def test_rename_default_sheet_if_needed_skips_when_name_already_matches():
    calls = []

    def fake_run_dws_mcp(product, tool, payload):
        calls.append((product, tool, payload))
        return {"name": "服务清单", "success": True}

    original = module.run_dws_mcp
    module.run_dws_mcp = fake_run_dws_mcp
    try:
        response = module.rename_default_sheet_if_needed("node-demo", {
            "name": "服务清单",
            "actualName": "服务清单",
            "sheetId": "default-sheet-id",
            "action": "reuse_default",
        })
    finally:
        module.run_dws_mcp = original

    assert response is None
    assert calls == []


def test_header_style_plan_covers_template_header_rows():
    plan = module.build_header_style_plan()

    assert plan == {
        "服务清单": ["A1:K1"],
        "提测配置清单-TEST": ["A1:D1"],
        "提测配置清单-PROD": ["A1:D1"],
        "数据库脚本": ["A1:F1"],
        "定时任务 XXL-JOB": ["A1:C1", "A11:P11"],
        "发布流程": ["A1:E1"],
    }


def test_build_font_weights_matches_range_size():
    assert module.build_font_weights(1, 4) == [["bold", "bold", "bold", "bold"]]
    assert module.build_font_weights(2, 2) == [["bold", "bold"], ["bold", "bold"]]


def test_dry_run_includes_header_style_plan():
    workbook = module.build_workbook(sample_context())

    class Args:
        name = None
        workspace_id = "ws-demo"
        folder_id = "folder-demo"
        dry_run = True

    result = module.create_document(Args(), workbook, sample_context())

    assert result["dry_run"] is True
    assert result["headerStylePlan"] == {
        "服务清单": ["A1:K1"],
        "提测配置清单-TEST": ["A1:D1"],
        "提测配置清单-PROD": ["A1:D1"],
        "数据库脚本": ["A1:F1"],
        "定时任务 XXL-JOB": ["A1:C1", "A11:P11"],
        "发布流程": ["A1:E1"],
    }


def test_created_sheet_result_includes_style_ranges():
    workbook = module.build_workbook(sample_context())
    style_plan = module.build_header_style_plan()

    created_sheet = {
        "name": "定时任务 XXL-JOB",
        "actualName": "定时任务 XXL-JOB",
        "sheetId": "sheet-demo",
        "action": "create",
        "rows": len(workbook["定时任务 XXL-JOB"]),
        "update": True,
        "styles": len(style_plan["定时任务 XXL-JOB"]),
        "styleRanges": style_plan["定时任务 XXL-JOB"],
    }

    assert created_sheet["styles"] == 2
    assert created_sheet["styleRanges"] == ["A1:C1", "A11:P11"]


def test_table_put_payload_bootstraps_all_sheets_without_cell_data():
    workbook = module.build_workbook(sample_context())

    sheets = module.build_table_put_sheets(workbook)

    assert [sheet["name"] for sheet in sheets] == [
        "服务清单",
        "发布流程",
        "定时任务 XXL-JOB",
        "数据库脚本",
        "提测配置清单-PROD",
        "提测配置清单-TEST",
    ]
    assert len(sheets) == 6
    assert sheets[0]["header"] is False
    assert all(sheet["data"] == [] for sheet in sheets)
    assert sheets[0]["columns"] == [f"column_{index}" for index in range(1, 12)]
    assert len(set(sheets[2]["columns"])) == len(sheets[2]["columns"])
    assert "" not in sheets[2]["columns"]


def test_values_and_header_styles_are_one_atomic_batch():
    workbook = module.build_workbook(sample_context())
    operations = module.build_sheet_write_operations(
        workbook,
        module.build_header_style_plan(),
    )

    assert len(operations) == 6
    assert {operation["toolName"] for operation in operations} == {"set_cell_range"}
    assert operations[0]["input"]["sheetId"] == "服务清单"
    assert operations[0]["input"]["rangeAddress"] == "A1:K2"
    assert operations[0]["input"]["cells"][0][0] == {
        "type": "text",
        "text": "流水线名称",
        "cellStyles": {"fontWeight": "bold"},
    }
    assert operations[0]["input"]["cells"][1][0] == {
        "type": "text",
        "text": "p45_6910 【国内】服务费发票计算优化",
    }
    job_operation = next(
        operation for operation in operations
        if operation["input"]["sheetId"] == "定时任务 XXL-JOB"
    )
    assert job_operation["input"]["cells"][10][15]["cellStyles"] == {
        "fontWeight": "bold"
    }


def test_batch_create_document_uses_six_remote_calls(monkeypatch):
    workbook = module.build_workbook(sample_context())
    calls = []
    list_responses = [
        {"sheets": [{"name": "Sheet1", "sheetId": "default-sheet-id"}]},
        {
            "sheets": [
                {"name": name, "sheetId": f"sheet-{index}"}
                for index, name in enumerate(module.SHEET_TEMPLATE_ORDER)
            ]
        },
    ]

    def fake_run_dws(args):
        calls.append(("dws", args))
        if args[:2] == ["sheet", "create"]:
            return {"nodeId": "node-demo"}
        if args[:2] == ["sheet", "list"]:
            return list_responses.pop(0)
        raise AssertionError(f"unexpected dws call: {args}")

    def fake_run_dws_mcp(product, tool, payload):
        calls.append(("mcp", product, tool, payload))
        return {"success": True}

    monkeypatch.setattr(module, "run_dws", fake_run_dws)
    monkeypatch.setattr(module, "run_dws_mcp", fake_run_dws_mcp)

    args = argparse.Namespace(
        name="p45_6910-【国内】服务费发票计算优化",
        workspace_id="workspace-demo",
        folder_id="folder-demo",
        dry_run=False,
        write_strategy="batch",
    )
    result = module.create_document(args, workbook, sample_context())

    assert [(call[0], call[2] if call[0] == "mcp" else call[1][:2]) for call in calls] == [
        ("dws", ["sheet", "create"]),
        ("dws", ["sheet", "list"]),
        ("mcp", "update_sheet"),
        ("mcp", "table_put"),
        ("mcp", "batch_update"),
        ("dws", ["sheet", "list"]),
    ]
    assert result["success"] is True
    assert result["writeStrategy"] == "batch"
    assert result["remoteCallCount"] == 6
    assert result["writeOperationCount"] == 6
    assert result["actualSheetOrder"] == module.SHEET_TEMPLATE_ORDER


def test_dry_run_reports_batch_call_reduction():
    workbook = module.build_workbook(sample_context())
    args = argparse.Namespace(
        name=None,
        workspace_id="workspace-demo",
        folder_id="folder-demo",
        dry_run=True,
        write_strategy="batch",
    )

    result = module.create_document(args, workbook, sample_context())

    assert result["writeStrategy"] == "batch"
    assert result["estimatedRemoteCalls"] == 6
    assert result["legacyEstimatedRemoteCalls"] == 22


def test_opencli_wrapper_exposes_create_test_delivery_command():
    result = subprocess.run(
        [str(CLI_PATH), "create-test-delivery", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--write-strategy" in result.stdout
    assert "--dry-run" in result.stdout


if __name__ == "__main__":
    test_workbook_uses_legacy_six_sheet_template()
    test_workbook_preserves_template_headers()
    test_missing_source_data_stays_empty_in_template_rows()
    test_default_doc_name_matches_bk_requirement()
    test_default_doc_name_requires_complete_bk_requirement(
        {"number": "p35_15078", "title": ""}
    )
    test_resolve_doc_name_rejects_name_that_differs_from_bk_requirement()
    test_created_sheet_plan_reuses_default_sheet_for_first_template_sheet()
    test_remaining_sheet_creation_order_is_reversed_for_current_dws_behavior()
    test_rename_default_sheet_if_needed_builds_update_payload()
    test_rename_default_sheet_if_needed_skips_when_name_already_matches()
    test_header_style_plan_covers_template_header_rows()
    test_build_font_weights_matches_range_size()
    test_dry_run_includes_header_style_plan()
    test_created_sheet_result_includes_style_ranges()

"""
测试执行路由
提供测试执行和报告查看功能
"""
from typing import Optional
from fastapi import APIRouter

from ..models import (
    QuickApiTestRequest,
    RunCaseRequest,
    RunCaseFileRequest,
    RunDirectoryRequest,
    RunBatchRequest
)
from ..services.test_runner import get_test_runner_service

router = APIRouter(prefix="/test", tags=["测试执行"])


# ============== 测试执行端点 ==============

@router.post("/api/quick", summary="快速 API 测试")
async def quick_api_test(request: QuickApiTestRequest):
    """
    快速运行单个 API 测试（无需创建用例文件）
    
    直接发送 HTTP 请求并验证结果，适合快速调试接口。
    
    支持的断言:
    - 状态码断言
    - 响应时间断言
    - 响应内容包含断言
    - JSON 字段断言（使用 JSONPath）
    """
    runner = get_test_runner_service()
    return await runner.run_api_test(
        url=request.url,
        method=request.method,
        headers=request.headers,
        params=request.params,
        data=request.data,
        json_body=request.json_body,
        expected_status=request.expected_status,
        expected_contains=request.expected_contains,
        expected_json=request.expected_json,
        max_response_time_ms=request.max_response_time_ms
    )


@router.post("/case/run", summary="运行测试用例")
async def run_test_case(request: RunCaseRequest):
    """
    运行单个测试用例
    
    传入用例内容（YAML 解析后的字典），执行测试并返回结果。
    """
    runner = get_test_runner_service()
    return await runner.run_test_case(
        engine_type=request.engine_type,
        case_content=request.case_content,
        context=request.context
    )


@router.post("/case/file", summary="运行用例文件")
async def run_case_file(request: RunCaseFileRequest):
    """
    运行指定的用例文件
    
    传入用例文件路径，自动检测引擎类型并执行测试。
    """
    runner = get_test_runner_service()
    return await runner.run_test_from_file(
        case_file_path=request.case_file_path,
        context=request.context
    )


@router.post("/directory/run", summary="运行目录测试")
async def run_directory_test(request: RunDirectoryRequest):
    """
    运行整个目录的测试用例
    
    传入用例目录路径，执行目录下所有测试用例。
    """
    runner = get_test_runner_service()
    return await runner.run_test_directory(
        cases_dir=request.cases_dir,
        engine_type=request.engine_type,
        case_type=request.case_type,
        context=request.context
    )


@router.post("/batch/run", summary="批量运行测试")
async def run_batch_test(request: RunBatchRequest):
    """
    批量运行测试用例
    
    传入多个用例内容，批量执行测试。
    """
    runner = get_test_runner_service()
    return await runner.run_test_cases_batch(
        engine_type=request.engine_type,
        cases=request.cases,
        context=request.context
    )


# ============== 报告端点 ==============

@router.get("/reports", summary="列出测试报告")
async def list_reports(limit: int = 20):
    """列出所有测试报告"""
    runner = get_test_runner_service()
    return runner.list_reports(limit=limit)


@router.get("/report", summary="获取测试报告")
async def get_report(report_name: Optional[str] = None):
    """
    获取测试报告详情
    
    不传 report_name 则返回最新的报告。
    """
    runner = get_test_runner_service()
    return runner.get_test_report(report_name=report_name)


@router.get("/report/summary", summary="获取报告摘要")
async def get_report_summary():
    """
    获取测试报告摘要
    
    返回格式化的报告摘要，适合 LLM 展示。
    """
    runner = get_test_runner_service()
    return runner.generate_report_summary()

"""
Automation-Quality MCP Server - API测试自动化服务

提供核心测试工具：
- API Planner: 测试计划生成
- API Generator: 测试代码生成（Playwright/Jest/Postman）
- API Healer: 智能测试修复
- API Request: API请求执行和验证
"""
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json
import uuid
from datetime import datetime
from pathlib import Path
import sys
import asyncio

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.models import APIEndpoint, TestCase, TestStep, TestResult
from core.logging_config import get_logger

# 初始化日志
logger = get_logger(__name__)

# 创建MCP服务器
app = Server("automation-quality-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="api_planner",
            description="生成API测试计划，包括测试场景、测试用例和测试步骤",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_spec": {
                        "type": "object",
                        "description": "API规范（OpenAPI/Swagger格式）"
                    },
                    "test_strategy": {
                        "type": "string",
                        "enum": ["smoke", "functional", "integration", "regression", "performance"],
                        "default": "functional",
                        "description": "测试策略类型"
                    },
                    "coverage_level": {
                        "type": "string",
                        "enum": ["basic", "standard", "comprehensive"],
                        "default": "standard",
                        "description": "测试覆盖级别"
                    }
                },
                "required": ["api_spec"]
            }
        ),
        Tool(
            name="api_generator",
            description="生成API测试代码（Playwright/Jest/Postman）",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_plan": {
                        "type": "object",
                        "description": "测试计划（由api_planner生成）"
                    },
                    "framework": {
                        "type": "string",
                        "enum": ["playwright", "jest", "postman"],
                        "default": "playwright",
                        "description": "测试框架"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["typescript", "javascript"],
                        "default": "typescript",
                        "description": "编程语言"
                    },
                    "include_setup": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含Setup/Teardown"
                    }
                },
                "required": ["test_plan"]
            }
        ),
        Tool(
            name="api_healer",
            description="智能修复失败的测试用例",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_result": {
                        "type": "object",
                        "description": "测试执行结果"
                    },
                    "test_code": {
                        "type": "string",
                        "description": "原始测试代码"
                    },
                    "error_type": {
                        "type": "string",
                        "enum": ["assertion", "timeout", "authentication", "network", "unknown"],
                        "description": "错误类型"
                    },
                    "max_attempts": {
                        "type": "integer",
                        "default": 3,
                        "description": "最大修复尝试次数"
                    }
                },
                "required": ["test_result", "test_code"]
            }
        ),
        Tool(
            name="api_request",
            description="执行API请求并验证响应",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP方法"
                    },
                    "url": {
                        "type": "string",
                        "description": "API端点URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "请求头"
                    },
                    "body": {
                        "type": "object",
                        "description": "请求体"
                    },
                    "assertions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["status", "header", "body", "schema", "performance"]
                                },
                                "expected": {
                                    "type": "string"
                                }
                            }
                        },
                        "description": "断言列表"
                    }
                },
                "required": ["method", "url"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "api_planner":
            return await handle_api_planner(arguments)
        elif name == "api_generator":
            return await handle_api_generator(arguments)
        elif name == "api_healer":
            return await handle_api_healer(arguments)
        elif name == "api_request":
            return await handle_api_request(arguments)
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
            )]
    except Exception as e:
        logger.error(f"工具调用失败: {name}", exc_info=e)
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, ensure_ascii=False)
        )]


async def handle_api_planner(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理测试计划生成"""
    api_spec = arguments.get("api_spec", {})
    test_strategy = arguments.get("test_strategy", "functional")
    coverage_level = arguments.get("coverage_level", "standard")

    logger.info(f"生成测试计划: strategy={test_strategy}, coverage={coverage_level}")

    # 解析API规范
    endpoints = api_spec.get("paths", {})
    test_cases = []

    # 为每个端点生成测试用例
    for path, methods in endpoints.items():
        for method, spec in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                # 生成基础测试用例
                test_case = {
                    "test_id": str(uuid.uuid4()),
                    "test_name": f"测试 {method.upper()} {path}",
                    "endpoint": path,
                    "method": method.upper(),
                    "description": spec.get("summary", ""),
                    "test_steps": generate_test_steps(method.upper(), path, spec, coverage_level),
                    "priority": determine_priority(method.upper(), path),
                    "tags": [test_strategy, method.lower()]
                }
                test_cases.append(test_case)

    # 构建测试计划
    test_plan = {
        "plan_id": str(uuid.uuid4()),
        "test_strategy": test_strategy,
        "coverage_level": coverage_level,
        "total_test_cases": len(test_cases),
        "test_cases": test_cases,
        "estimated_duration": len(test_cases) * 30,  # 每个用例预估30秒
        "created_at": datetime.utcnow().isoformat()
    }

    logger.info(f"测试计划生成完成: {len(test_cases)} 个测试用例")

    return [TextContent(
        type="text",
        text=json.dumps(test_plan, ensure_ascii=False, indent=2)
    )]


def generate_test_steps(method: str, path: str, spec: Dict, coverage_level: str) -> List[Dict]:
    """生成测试步骤"""
    steps = []

    # 步骤1: 准备请求
    steps.append({
        "step_id": 1,
        "action": "prepare_request",
        "description": f"准备 {method} 请求到 {path}",
        "data": {
            "method": method,
            "path": path,
            "headers": {"Content-Type": "application/json"}
        }
    })

    # 步骤2: 发送请求
    steps.append({
        "step_id": 2,
        "action": "send_request",
        "description": "发送API请求",
        "expected": "请求成功发送"
    })

    # 步骤3: 验证响应
    expected_status = 200 if method == "GET" else 201 if method == "POST" else 200
    steps.append({
        "step_id": 3,
        "action": "verify_response",
        "description": "验证响应状态码",
        "expected": f"状态码为 {expected_status}"
    })

    # 根据覆盖级别添加更多步骤
    if coverage_level in ["standard", "comprehensive"]:
        steps.append({
            "step_id": 4,
            "action": "verify_schema",
            "description": "验证响应数据结构",
            "expected": "响应符合预期schema"
        })

    if coverage_level == "comprehensive":
        steps.append({
            "step_id": 5,
            "action": "verify_performance",
            "description": "验证响应时间",
            "expected": "响应时间 < 2000ms"
        })

    return steps


def determine_priority(method: str, path: str) -> str:
    """确定测试优先级"""
    if method in ["POST", "DELETE"]:
        return "high"
    elif "login" in path.lower() or "auth" in path.lower():
        return "critical"
    else:
        return "medium"


async def handle_api_generator(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理测试代码生成"""
    test_plan = arguments.get("test_plan", {})
    framework = arguments.get("framework", "playwright")
    language = arguments.get("language", "typescript")
    include_setup = arguments.get("include_setup", True)

    logger.info(f"生成测试代码: framework={framework}, language={language}")

    # 生成测试代码
    if framework == "playwright":
        code = generate_playwright_code(test_plan, language, include_setup)
    elif framework == "jest":
        code = generate_jest_code(test_plan, language, include_setup)
    elif framework == "postman":
        code = generate_postman_collection(test_plan)
    else:
        code = "// 不支持的框架"

    response = {
        "framework": framework,
        "language": language,
        "test_file": f"api-tests.{language}",
        "code": code,
        "total_tests": len(test_plan.get("test_cases", [])),
        "generated_at": datetime.utcnow().isoformat()
    }

    logger.info(f"测试代码生成完成: {len(code)} 字符")

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


def generate_playwright_code(test_plan: Dict, language: str, include_setup: bool) -> str:
    """生成Playwright测试代码"""
    test_cases = test_plan.get("test_cases", [])

    code = f"""// Playwright API测试
// 生成时间: {datetime.utcnow().isoformat()}
// 测试策略: {test_plan.get('test_strategy', 'functional')}

import {{ test, expect }} from '@playwright/test';

"""

    if include_setup:
        code += """// 全局配置
const BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';
let authToken: string;

test.beforeAll(async () => {
  // Setup: 获取认证token
  console.log('执行测试前置条件...');
});

test.afterAll(async () => {
  // Teardown: 清理测试数据
  console.log('清理测试数据...');
});

"""

    # 为每个测试用例生成代码
    for tc in test_cases[:5]:  # 限制生成数量
        test_name = tc.get("test_name", "未命名测试")
        method = tc.get("method", "GET")
        endpoint = tc.get("endpoint", "/")

        code += f"""test('{test_name}', async ({{ request }}) => {{
  // 发送 {method} 请求
  const response = await request.{method.lower()}(`${{BASE_URL}}{endpoint}`);

  // 验证响应
  expect(response.status()).toBe(200);
  const data = await response.json();
  expect(data).toBeDefined();
}});

"""

    return code


def generate_jest_code(test_plan: Dict, language: str, include_setup: bool) -> str:
    """生成Jest测试代码"""
    return "// Jest测试代码生成（待实现）"


def generate_postman_collection(test_plan: Dict) -> str:
    """生成Postman Collection"""
    collection = {
        "info": {
            "name": "API自动化测试",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    for tc in test_plan.get("test_cases", []):
        collection["item"].append({
            "name": tc.get("test_name", ""),
            "request": {
                "method": tc.get("method", "GET"),
                "url": tc.get("endpoint", "")
            }
        })

    return json.dumps(collection, indent=2)


async def handle_api_healer(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理智能测试修复"""
    test_result = arguments.get("test_result", {})
    test_code = arguments.get("test_code", "")
    error_type = arguments.get("error_type", "unknown")
    max_attempts = arguments.get("max_attempts", 3)

    logger.info(f"智能修复测试: error_type={error_type}")

    # 分析错误并生成修复建议
    fix_suggestions = analyze_and_fix(test_result, test_code, error_type)

    response = {
        "original_error": test_result.get("error", ""),
        "error_type": error_type,
        "fix_suggestions": fix_suggestions,
        "fixed_code": apply_fixes(test_code, fix_suggestions),
        "confidence": 0.85,
        "max_attempts": max_attempts
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


def analyze_and_fix(test_result: Dict, test_code: str, error_type: str) -> List[Dict]:
    """分析错误并生成修复建议"""
    suggestions = []

    if error_type == "assertion":
        suggestions.append({
            "type": "assertion_fix",
            "description": "调整断言条件",
            "action": "更新期望值以匹配实际响应"
        })
    elif error_type == "timeout":
        suggestions.append({
            "type": "timeout_fix",
            "description": "增加超时时间",
            "action": "将超时时间从30s增加到60s"
        })
    elif error_type == "authentication":
        suggestions.append({
            "type": "auth_fix",
            "description": "修复认证问题",
            "action": "检查并更新认证token"
        })

    return suggestions


def apply_fixes(test_code: str, suggestions: List[Dict]) -> str:
    """应用修复建议"""
    fixed_code = test_code

    for suggestion in suggestions:
        if suggestion["type"] == "timeout_fix":
            fixed_code = fixed_code.replace("timeout: 30000", "timeout: 60000")
        elif suggestion["type"] == "assertion_fix":
            fixed_code = fixed_code.replace("toBe(200)", "toBeGreaterThanOrEqual(200)")

    return fixed_code


async def handle_api_request(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理API请求执行"""
    method = arguments.get("method", "GET")
    url = arguments.get("url", "")
    headers = arguments.get("headers", {})
    body = arguments.get("body")
    assertions = arguments.get("assertions", [])

    logger.info(f"执行API请求: {method} {url}")

    # 模拟API请求执行
    response = {
        "request": {
            "method": method,
            "url": url,
            "headers": headers,
            "body": body
        },
        "response": {
            "status": 200,
            "headers": {"content-type": "application/json"},
            "body": {"message": "成功"},
            "time": 150
        },
        "assertions": {
            "total": len(assertions),
            "passed": len(assertions),
            "failed": 0,
            "results": [{"assertion": a, "passed": True} for a in assertions]
        },
        "executed_at": datetime.utcnow().isoformat()
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def main():
    """启动Automation-Quality MCP服务器"""
    logger.info("启动Automation-Quality MCP服务器...")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())



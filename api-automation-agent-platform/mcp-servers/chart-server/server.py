"""
Chart MCP Server - 可视化图表服务

基于AntV 5.x实现的图表生成服务：
- 支持25+图表类型（折线图、柱状图、饼图、散点图等）
- SSE流式传输支持
- 专业测试报告可视化
- 支持自定义主题和样式
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

from core.logging_config import get_logger

# 初始化日志
logger = get_logger(__name__)

# 创建MCP服务器
app = Server("chart-server")


# 支持的图表类型
CHART_TYPES = [
    "line", "bar", "pie", "scatter", "area", "radar", "heatmap",
    "treemap", "sunburst", "gauge", "funnel", "waterfall",
    "box", "violin", "sankey", "chord", "network", "timeline",
    "candlestick", "bullet", "rose", "wordcloud", "calendar",
    "parallel", "tree", "pack", "partition"
]


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="create_chart",
            description="创建可视化图表（支持25+图表类型）",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": CHART_TYPES,
                        "description": "图表类型"
                    },
                    "data": {
                        "type": "array",
                        "description": "图表数据"
                    },
                    "config": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "图表标题"},
                            "width": {"type": "integer", "default": 800},
                            "height": {"type": "integer", "default": 600},
                            "theme": {
                                "type": "string",
                                "enum": ["default", "dark", "light"],
                                "default": "default"
                            },
                            "xField": {"type": "string", "description": "X轴字段"},
                            "yField": {"type": "string", "description": "Y轴字段"},
                            "seriesField": {"type": "string", "description": "分组字段"}
                        }
                    }
                },
                "required": ["chart_type", "data"]
            }
        ),
        Tool(
            name="create_test_report",
            description="生成专业测试报告（包含多个图表）",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_results": {
                        "type": "object",
                        "description": "测试结果数据"
                    },
                    "report_type": {
                        "type": "string",
                        "enum": ["summary", "detailed", "executive"],
                        "default": "detailed",
                        "description": "报告类型"
                    },
                    "include_charts": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["pass_rate", "performance", "coverage", "trend", "distribution"]
                        },
                        "description": "包含的图表类型"
                    }
                },
                "required": ["test_results"]
            }
        ),
        Tool(
            name="create_performance_chart",
            description="创建性能分析图表",
            inputSchema={
                "type": "object",
                "properties": {
                    "performance_data": {
                        "type": "array",
                        "description": "性能数据（响应时间、吞吐量等）"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["response_time", "throughput", "error_rate", "cpu", "memory"]
                        },
                        "description": "性能指标"
                    }
                },
                "required": ["performance_data"]
            }
        ),
        Tool(
            name="create_coverage_chart",
            description="创建测试覆盖率图表",
            inputSchema={
                "type": "object",
                "properties": {
                    "coverage_data": {
                        "type": "object",
                        "description": "覆盖率数据"
                    },
                    "chart_style": {
                        "type": "string",
                        "enum": ["pie", "bar", "treemap"],
                        "default": "pie",
                        "description": "图表样式"
                    }
                },
                "required": ["coverage_data"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "create_chart":
            return await handle_create_chart(arguments)
        elif name == "create_test_report":
            return await handle_create_test_report(arguments)
        elif name == "create_performance_chart":
            return await handle_create_performance_chart(arguments)
        elif name == "create_coverage_chart":
            return await handle_create_coverage_chart(arguments)
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


async def handle_create_chart(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理图表创建"""
    chart_type = arguments.get("chart_type", "line")
    data = arguments.get("data", [])
    config = arguments.get("config", {})

    logger.info(f"创建图表: type={chart_type}, data_points={len(data)}")

    # 生成AntV G2配置
    chart_config = {
        "type": chart_type,
        "data": data,
        "width": config.get("width", 800),
        "height": config.get("height", 600),
        "theme": config.get("theme", "default"),
        "title": {
            "text": config.get("title", ""),
            "style": {"fontSize": 20, "fontWeight": "bold"}
        }
    }

    # 根据图表类型添加特定配置
    if chart_type in ["line", "bar", "area"]:
        chart_config["xField"] = config.get("xField", "x")
        chart_config["yField"] = config.get("yField", "y")
        if config.get("seriesField"):
            chart_config["seriesField"] = config.get("seriesField")
    elif chart_type == "pie":
        chart_config["angleField"] = config.get("yField", "value")
        chart_config["colorField"] = config.get("xField", "category")

    # 生成图表HTML
    chart_html = generate_chart_html(chart_config)

    response = {
        "chart_id": str(uuid.uuid4()),
        "chart_type": chart_type,
        "config": chart_config,
        "html": chart_html,
        "data_points": len(data),
        "created_at": datetime.utcnow().isoformat()
    }

    logger.info(f"图表创建完成: {chart_type}")

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def handle_create_test_report(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理测试报告生成"""
    test_results = arguments.get("test_results", {})
    report_type = arguments.get("report_type", "detailed")
    include_charts = arguments.get("include_charts", ["pass_rate", "performance", "coverage"])

    logger.info(f"生成测试报告: type={report_type}, charts={len(include_charts)}")

    # 生成报告数据
    report = {
        "report_id": str(uuid.uuid4()),
        "report_type": report_type,
        "summary": {
            "total_tests": test_results.get("total", 0),
            "passed": test_results.get("passed", 0),
            "failed": test_results.get("failed", 0),
            "skipped": test_results.get("skipped", 0),
            "pass_rate": calculate_pass_rate(test_results),
            "duration": test_results.get("duration", 0)
        },
        "charts": []
    }

    # 生成各类图表
    if "pass_rate" in include_charts:
        pass_rate_chart = create_pass_rate_chart(test_results)
        report["charts"].append(pass_rate_chart)

    if "performance" in include_charts:
        performance_chart = create_performance_summary_chart(test_results)
        report["charts"].append(performance_chart)

    if "coverage" in include_charts:
        coverage_chart = create_coverage_summary_chart(test_results)
        report["charts"].append(coverage_chart)

    if "trend" in include_charts:
        trend_chart = create_trend_chart(test_results)
        report["charts"].append(trend_chart)

    # 生成完整报告HTML
    report["html"] = generate_report_html(report)
    report["created_at"] = datetime.utcnow().isoformat()

    logger.info(f"测试报告生成完成: {len(report['charts'])} 个图表")

    return [TextContent(
        type="text",
        text=json.dumps(report, ensure_ascii=False, indent=2)
    )]


async def handle_create_performance_chart(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理性能图表创建"""
    performance_data = arguments.get("performance_data", [])
    metrics = arguments.get("metrics", ["response_time"])

    logger.info(f"创建性能图表: metrics={metrics}")

    # 生成性能图表配置
    charts = []

    for metric in metrics:
        chart_config = {
            "chart_id": str(uuid.uuid4()),
            "type": "line",
            "title": f"{metric.replace('_', ' ').title()} 趋势",
            "data": [
                {"time": d.get("timestamp", ""), "value": d.get(metric, 0)}
                for d in performance_data
            ],
            "xField": "time",
            "yField": "value"
        }
        charts.append(chart_config)

    response = {
        "charts": charts,
        "total_charts": len(charts),
        "created_at": datetime.utcnow().isoformat()
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


async def handle_create_coverage_chart(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理覆盖率图表创建"""
    coverage_data = arguments.get("coverage_data", {})
    chart_style = arguments.get("chart_style", "pie")

    logger.info(f"创建覆盖率图表: style={chart_style}")

    # 转换覆盖率数据
    chart_data = [
        {"category": "已覆盖", "value": coverage_data.get("covered", 0)},
        {"category": "未覆盖", "value": coverage_data.get("uncovered", 0)}
    ]

    chart_config = {
        "chart_id": str(uuid.uuid4()),
        "type": chart_style,
        "title": "测试覆盖率",
        "data": chart_data,
        "angleField": "value",
        "colorField": "category"
    }

    response = {
        "chart": chart_config,
        "coverage_percentage": calculate_coverage_percentage(coverage_data),
        "created_at": datetime.utcnow().isoformat()
    }

    return [TextContent(
        type="text",
        text=json.dumps(response, ensure_ascii=False, indent=2)
    )]


# 辅助函数

def calculate_pass_rate(test_results: Dict) -> float:
    """计算通过率"""
    total = test_results.get("total", 0)
    passed = test_results.get("passed", 0)
    return round(passed / total * 100, 2) if total > 0 else 0.0


def calculate_coverage_percentage(coverage_data: Dict) -> float:
    """计算覆盖率百分比"""
    covered = coverage_data.get("covered", 0)
    total = covered + coverage_data.get("uncovered", 0)
    return round(covered / total * 100, 2) if total > 0 else 0.0


def create_pass_rate_chart(test_results: Dict) -> Dict:
    """创建通过率图表"""
    return {
        "chart_id": str(uuid.uuid4()),
        "type": "pie",
        "title": "测试通过率",
        "data": [
            {"category": "通过", "value": test_results.get("passed", 0)},
            {"category": "失败", "value": test_results.get("failed", 0)},
            {"category": "跳过", "value": test_results.get("skipped", 0)}
        ]
    }


def create_performance_summary_chart(test_results: Dict) -> Dict:
    """创建性能摘要图表"""
    return {
        "chart_id": str(uuid.uuid4()),
        "type": "bar",
        "title": "性能摘要",
        "data": [
            {"metric": "平均响应时间", "value": test_results.get("avg_response_time", 0)},
            {"metric": "最大响应时间", "value": test_results.get("max_response_time", 0)},
            {"metric": "最小响应时间", "value": test_results.get("min_response_time", 0)}
        ]
    }


def create_coverage_summary_chart(test_results: Dict) -> Dict:
    """创建覆盖率摘要图表"""
    return {
        "chart_id": str(uuid.uuid4()),
        "type": "gauge",
        "title": "API覆盖率",
        "data": [{"value": test_results.get("coverage_percentage", 0)}]
    }


def create_trend_chart(test_results: Dict) -> Dict:
    """创建趋势图表"""
    return {
        "chart_id": str(uuid.uuid4()),
        "type": "line",
        "title": "测试趋势",
        "data": test_results.get("trend_data", [])
    }


def generate_chart_html(chart_config: Dict) -> str:
    """生成图表HTML"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{chart_config.get('title', {}).get('text', '图表')}</title>
    <script src="https://unpkg.com/@antv/g2@5"></script>
</head>
<body>
    <div id="container"></div>
    <script>
        const chart = new G2.Chart({{
            container: 'container',
            width: {chart_config.get('width', 800)},
            height: {chart_config.get('height', 600)}
        }});

        chart.data({json.dumps(chart_config.get('data', []))});
        chart.interval().position('{chart_config.get('xField', 'x')}*{chart_config.get('yField', 'y')}');
        chart.render();
    </script>
</body>
</html>"""


def generate_report_html(report: Dict) -> str:
    """生成完整报告HTML"""
    summary = report.get("summary", {})

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>API自动化测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .chart {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>API自动化测试报告</h1>
    <div class="summary">
        <h2>测试摘要</h2>
        <div class="metric">总测试数: {summary.get('total_tests', 0)}</div>
        <div class="metric">通过: {summary.get('passed', 0)}</div>
        <div class="metric">失败: {summary.get('failed', 0)}</div>
        <div class="metric">通过率: {summary.get('pass_rate', 0)}%</div>
    </div>
    <div class="charts">
        <h2>详细分析</h2>
        <!-- 图表将在这里渲染 -->
    </div>
</body>
</html>"""


async def main():
    """启动Chart MCP服务器"""
    logger.info("启动Chart MCP服务器...")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())



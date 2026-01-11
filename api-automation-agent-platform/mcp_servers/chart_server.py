"""
Chart MCP Server - 基于AntV的专业数据可视化引擎

支持25+种图表类型：
- 基础图表：饼图、柱状图、折线图、散点图
- 高级图表：瀑布图、桑基图、关系图、热力图
- 地理图表：地图、日历图

技术特点：
- SSE流式传输
- 响应式设计
- 主题定制
- 交互式图例
"""
import asyncio
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from pathlib import Path
from datetime import datetime
import uuid

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types


# 创建Chart MCP服务器
chart_server = Server("antv-data-visualization")


# 图表类型定义
CHART_TYPES = {
    # 基础图表
    "pie": "饼图",
    "bar": "柱状图", 
    "line": "折线图",
    "scatter": "散点图",
    "area": "面积图",
    "column": "柱状图",
    
    # 高级图表
    "waterfall": "瀑布图",
    "sankey": "桑基图",
    "graph": "关系图",
    "heatmap": "热力图",
    "treemap": "树图",
    "sunburst": "旭日图",
    "radar": "雷达图",
    "gauge": "仪表盘",
    "funnel": "漏斗图",
    
    # 地理图表
    "map": "地图",
    "calendar": "日历图",
    "timeline": "时间轴",
    
    # 特殊图表
    "boxplot": "箱线图",
    "violin": "小提琴图",
    "histogram": "直方图",
    "scatter-matrix": "散点矩阵",
    "parallel": "平行坐标图"
}


@chart_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """列出可用的工具"""
    return [
        types.Tool(
            name="chart_generate_basic",
            description="生成基础图表（饼图、柱状图、折线图、散点图）",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "description": "图表类型",
                        "enum": ["pie", "bar", "line", "scatter", "area", "column"]
                    },
                    "data": {
                        "type": "array",
                        "description": "图表数据"
                    },
                    "title": {
                        "type": "string",
                        "description": "图表标题"
                    },
                    "theme": {
                        "type": "string",
                        "description": "主题样式",
                        "default": "default"
                    }
                },
                "required": ["chart_type", "data"]
            }
        ),
        types.Tool(
            name="chart_generate_advanced",
            description="生成高级图表（瀑布图、桑基图、关系图、热力图等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "description": "图表类型",
                        "enum": ["waterfall", "sankey", "graph", "heatmap", "treemap", "sunburst", "radar", "gauge", "funnel"]
                    },
                    "data": {
                        "type": "array",
                        "description": "图表数据"
                    },
                    "title": {
                        "type": "string",
                        "description": "图表标题"
                    },
                    "config": {
                        "type": "object",
                        "description": "高级配置"
                    }
                },
                "required": ["chart_type", "data"]
            }
        ),
        types.Tool(
            name="chart_generate_geographic",
            description="生成地理图表（地图、日历图等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "description": "图表类型",
                        "enum": ["map", "calendar", "timeline"]
                    },
                    "data": {
                        "type": "array",
                        "description": "图表数据"
                    },
                    "title": {
                        "type": "string",
                        "description": "图表标题"
                    },
                    "geo_config": {
                        "type": "object",
                        "description": "地理配置"
                    }
                },
                "required": ["chart_type", "data"]
            }
        ),
        types.Tool(
            name="chart_stream_generate",
            description="SSE流式生成图表",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "description": "图表类型"
                    },
                    "data": {
                        "type": "array",
                        "description": "图表数据"
                    },
                    "config": {
                        "type": "object",
                        "description": "图表配置"
                    }
                },
                "required": ["chart_type", "data"]
            }
        ),
        types.Tool(
            name="chart_test_results",
            description="生成API测试结果专用图表",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_results": {
                        "type": "array",
                        "description": "测试结果数据"
                    },
                    "chart_style": {
                        "type": "string",
                        "description": "图表样式",
                        "enum": ["summary", "detailed", "timeline"],
                        "default": "summary"
                    }
                },
                "required": ["test_results"]
            }
        )
    ]


@chart_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """处理工具调用"""
    try:
        if name == "chart_generate_basic":
            return await _handle_chart_generate_basic(arguments)
        elif name == "chart_generate_advanced":
            return await _handle_chart_generate_advanced(arguments)
        elif name == "chart_generate_geographic":
            return await _handle_chart_generate_geographic(arguments)
        elif name == "chart_stream_generate":
            return await _handle_chart_stream_generate(arguments)
        elif name == "chart_test_results":
            return await _handle_chart_test_results(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error calling tool {name}: {str(e)}"
            )
        ]


async def _handle_chart_generate_basic(arguments: dict) -> list[types.TextContent]:
    """处理基础图表生成"""
    chart_type = arguments.get("chart_type")
    data = arguments.get("data", [])
    title = arguments.get("title", "")
    theme = arguments.get("theme", "default")
    
    # 生成AntV配置
    antv_config = _generate_antv_config(chart_type, data, title, theme)
    
    # 生成图表HTML
    chart_html = _generate_chart_html(antv_config, chart_type)
    
    formatted_result = {
        "status": "success",
        "chart_type": chart_type,
        "chart_name": CHART_TYPES.get(chart_type, chart_type),
        "title": title,
        "theme": theme,
        "data_points": len(data),
        "antv_config": antv_config,
        "chart_html": chart_html,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def _handle_chart_generate_advanced(arguments: dict) -> list[types.TextContent]:
    """处理高级图表生成"""
    chart_type = arguments.get("chart_type")
    data = arguments.get("data", [])
    title = arguments.get("title", "")
    config = arguments.get("config", {})
    
    # 生成高级AntV配置
    antv_config = _generate_advanced_antv_config(chart_type, data, title, config)
    
    # 生成图表HTML
    chart_html = _generate_chart_html(antv_config, chart_type)
    
    formatted_result = {
        "status": "success",
        "chart_type": chart_type,
        "chart_name": CHART_TYPES.get(chart_type, chart_type),
        "title": title,
        "data_points": len(data),
        "antv_config": antv_config,
        "chart_html": chart_html,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def _handle_chart_generate_geographic(arguments: dict) -> list[types.TextContent]:
    """处理地理图表生成"""
    chart_type = arguments.get("chart_type")
    data = arguments.get("data", [])
    title = arguments.get("title", "")
    geo_config = arguments.get("geo_config", {})
    
    # 生成地理AntV配置
    antv_config = _generate_geographic_antv_config(chart_type, data, title, geo_config)
    
    # 生成图表HTML
    chart_html = _generate_chart_html(antv_config, chart_type)
    
    formatted_result = {
        "status": "success",
        "chart_type": chart_type,
        "chart_name": CHART_TYPES.get(chart_type, chart_type),
        "title": title,
        "data_points": len(data),
        "antv_config": antv_config,
        "chart_html": chart_html,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def _handle_chart_stream_generate(arguments: dict) -> list[types.TextContent]:
    """处理流式图表生成"""
    chart_type = arguments.get("chart_type")
    data = arguments.get("data", [])
    config = arguments.get("config", {})
    
    # 生成流式配置
    stream_config = {
        "chart_type": chart_type,
        "data": data,
        "config": config,
        "streaming": True,
        "animation": {
            "appear": {
                "animation": "wave-in",
                "duration": 1000
            }
        }
    }
    
    # 模拟SSE流式传输
    stream_chunks = []
    for i, chunk in enumerate(_generate_stream_chunks(stream_config)):
        stream_chunks.append({
            "chunk_id": i,
            "type": "chart_data",
            "content": chunk,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    formatted_result = {
        "status": "success",
        "chart_type": chart_type,
        "streaming": True,
        "chunks_count": len(stream_chunks),
        "stream_config": stream_config,
        "stream_chunks": stream_chunks,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


async def _handle_chart_test_results(arguments: dict) -> list[types.TextContent]:
    """处理测试结果图表生成"""
    test_results = arguments.get("test_results", [])
    chart_style = arguments.get("chart_style", "summary")
    
    # 生成测试结果专用图表
    test_charts = _generate_test_result_charts(test_results, chart_style)
    
    formatted_result = {
        "status": "success",
        "chart_style": chart_style,
        "test_results_count": len(test_results),
        "charts": test_charts,
        "summary": {
            "total_tests": len(test_results),
            "passed_tests": len([r for r in test_results if r.get('status') == 'passed']),
            "failed_tests": len([r for r in test_results if r.get('status') == 'failed']),
            "success_rate": len([r for r in test_results if r.get('status') == 'passed']) / max(len(test_results), 1) * 100
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(formatted_result, indent=2, ensure_ascii=False)
        )
    ]


def _generate_antv_config(chart_type: str, data: List[Dict], title: str, theme: str) -> Dict[str, Any]:
    """生成AntV基础配置"""
    base_config = {
        "type": chart_type,
        "data": data,
        "theme": theme,
        "animation": {
            "appear": {
                "animation": "wave-in",
                "duration": 1000
            }
        }
    }
    
    # 根据图表类型添加特定配置
    if chart_type == "pie":
        base_config.update({
            "angleField": "value",
            "colorField": "category",
            "radius": 0.8,
            "innerRadius": 0.6,
            "label": {
                "type": "outer",
                "content": "{name} {percentage}"
            }
        })
    elif chart_type == "bar":
        base_config.update({
            "xField": "category",
            "yField": "value",
            "seriesField": "category",
            "legend": True
        })
    elif chart_type == "line":
        base_config.update({
            "xField": "category",
            "yField": "value",
            "smooth": True,
            "legend": True
        })
    elif chart_type == "scatter":
        base_config.update({
            "xField": "x",
            "yField": "y",
            "sizeField": "value",
            "colorField": "category"
        })
    
    if title:
        base_config["title"] = {
            "text": title,
            "subtext": f"Generated at {datetime.utcnow().isoformat()}"
        }
    
    return base_config


def _generate_advanced_antv_config(chart_type: str, data: List[Dict], title: str, config: Dict) -> Dict[str, Any]:
    """生成AntV高级配置"""
    advanced_config = {
        "type": chart_type,
        "data": data,
        "animation": {
            "appear": {
                "animation": "wave-in",
                "duration": 1500
            }
        }
    }
    
    # 根据图表类型添加高级配置
    if chart_type == "waterfall":
        advanced_config.update({
            "xField": "category",
            "yField": "value",
            "meta": {
                "type": {"alias": "类型"}
            }
        })
    elif chart_type == "sankey":
        advanced_config.update({
            "sourceField": "source",
            "targetField": "target",
            "weightField": "value"
        })
    elif chart_type == "graph":
        advanced_config.update({
            "layout": "force",
            "nodeSize": 20,
            "nodeStateStyles": {
                "hover": {
                    "stroke": "#ff4d4f",
                    "lineWidth": 2
                }
            }
        })
    elif chart_type == "heatmap":
        advanced_config.update({
            "xField": "x",
            "yField": "y",
            "colorField": "value",
            "color": ["#blues", "#greens", "#reds"]
        })
    
    if title:
        advanced_config["title"] = {
            "text": title,
            "subtext": f"Advanced {CHART_TYPES.get(chart_type, chart_type)}"
        }
    
    return advanced_config


def _generate_geographic_antv_config(chart_type: str, data: List[Dict], title: str, geo_config: Dict) -> Dict[str, Any]:
    """生成地理AntV配置"""
    geographic_config = {
        "type": chart_type,
        "data": data,
        "animation": {
            "appear": {
                "animation": "wave-in",
                "duration": 2000
            }
        }
    }
    
    if chart_type == "map":
        geographic_config.update({
            "geo": {
                "viewId": "geo",
                "registerMap": {
                    "type": "FeatureCollection",
                    "features": []
                }
            },
            "layer": {
                "name": "base",
                "type": "fill",
                "source": "geo"
            }
        })
    elif chart_type == "calendar":
        geographic_config.update({
            "xField": "month",
            "yField": "day",
            "colorField": "value"
        })
    
    if title:
        geographic_config["title"] = {
            "text": title,
            "subtext": f"Geographic {CHART_TYPES.get(chart_type, chart_type)}"
        }
    
    return geographic_config


def _generate_chart_html(antv_config: Dict[str, Any], chart_type: str) -> str:
    """生成图表HTML"""
    config_json = json.dumps(antv_config, ensure_ascii=False)
    
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AntV Chart - {chart_type}</title>
    <script src="https://gw.alipayobjects.com/os/lib/antv/5.0.7/dist/antv-g.min.js"></script>
    <style>
        #chart-container {{
            width: 100%;
            height: 400px;
        }}
    </style>
</head>
<body>
    <div id="chart-container"></div>
    <script>
        const data = {config_json};
        const chart = new G2.Chart({{
            container: 'chart-container',
            width: 800,
            height: 400,
        }});
        
        chart.data(data.data);
        chart.render();
    </script>
</body>
</html>
"""
    return html_template


async def _generate_stream_chunks(stream_config: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """生成流式数据块"""
    chart_type = stream_config.get("chart_type")
    data = stream_config.get("data", [])
    
    # 模拟流式传输
    for i, chunk in enumerate(data):
        chunk_data = {
            "chunk_id": i,
            "type": "data_point",
            "content": chunk,
            "chart_type": chart_type
        }
        yield json.dumps(chunk_data, ensure_ascii=False)
        
        # 模拟延迟
        await asyncio.sleep(0.1)


def _generate_test_result_charts(test_results: List[Dict], chart_style: str) -> List[Dict[str, Any]]:
    """生成测试结果专用图表"""
    charts = []
    
    if chart_style in ["summary", "detailed"]:
        # 成功率饼图
        passed = len([r for r in test_results if r.get('status') == 'passed'])
        failed = len([r for r in test_results if r.get('status') == 'failed'])
        
        pie_chart = {
            "chart_type": "pie",
            "title": "Test Results Summary",
            "data": [
                {"category": "Passed", "value": passed},
                {"category": "Failed", "value": failed}
            ],
            "config": {
                "radius": 0.8,
                "innerRadius": 0.6
            }
        }
        charts.append(pie_chart)
    
    if chart_style in ["detailed", "timeline"]:
        # 执行时间线图
        timeline_chart = {
            "chart_type": "line",
            "title": "Test Execution Timeline",
            "data": [
                {"category": f"Test {i+1}", "value": r.get('duration', 0)}
                for i, r in enumerate(test_results)
            ],
            "config": {
                "smooth": True,
                "legend": True
            }
        }
        charts.append(timeline_chart)
    
    return charts


async def main():
    """启动Chart MCP服务器"""
    # 使用stdio传输
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await chart_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="antv-data-visualization",
                server_version="1.0.0",
                capabilities=chart_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def create_chart_server():
    """创建Chart MCP服务器实例"""
    return chart_server


if __name__ == "__main__":
    asyncio.run(main())

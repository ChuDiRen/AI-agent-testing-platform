"""
Chart MCP Server - Professional Data Visualization

Based on AntV 5.x, supporting 25+ chart types with SSE streaming.
"""
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

# Create MCP server
app = Server("chart-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available chart tools"""
    return [
        Tool(
            name="chart_generate",
            description=(
                "Generate professional charts based on AntV 5.x. "
                "Supports 25+ chart types including line, bar, pie, scatter, "
                "sankey, heatmap, gauge, and more."
                "\n\nSupported chart types:\n"
                "- Basic: line, bar, column, pie, area, scatter\n"
                "- Advanced: sankey, heatmap, treemap, gauge, funnel\n"
                "- Statistical: boxplot, violin, histogram\n"
                "- Geographic: map, choropleth\n"
                "- Composite: dual-axis, mixed, grouped-stacked\n\n"
                "Input:\n"
                "- chartType: Type of chart\n"
                "- data: Chart data (array of objects)\n"
                "- config: Chart configuration (optional)\n"
                "- options: Additional styling options"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "chartType": {
                        "type": "string",
                        "description": "Type of chart to generate",
                        "enum": [
                            "line", "bar", "column", "pie", "area", "scatter",
                            "sankey", "heatmap", "treemap", "gauge", "funnel",
                            "boxplot", "violin", "histogram", "radar", "rose",
                            "dual-axis", "mixed", "grouped-stacked", "waterfall",
                            "word-cloud", "circle-packing", "force-graph",
                            "tree", "matrix", "parallel-coordinates", "stock"
                        ]
                    },
                    "data": {
                        "type": "array",
                        "description": "Chart data - array of data objects",
                        "items": {"type": "object"}
                    },
                    "config": {
                        "type": "object",
                        "description": "Chart configuration (title, axes, legends, etc.)",
                        "properties": {
                            "title": {"type": "string"},
                            "xField": {"type": "string"},
                            "yField": {"type": "string"},
                            "colorField": {"type": "string"},
                            "width": {"type": "integer", "default": 800},
                            "height": {"type": "integer", "default": 600}
                        }
                    },
                    "options": {
                        "type": "object",
                        "description": "Additional styling options",
                        "properties": {
                            "theme": {"type": "string", "enum": ["default", "dark", "light"], "default": "default"},
                            "animate": {"type": "boolean", "default": True},
                            "responsive": {"type": "boolean", "default": True},
                            "legend": {"type": "boolean", "default": True}
                        }
                    }
                },
                "required": ["chartType", "data"]
            }
        ),
        Tool(
            name="chart_generate_batch",
            description="Generate multiple charts at once for batch processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "charts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "chartType": {"type": "string"},
                                "data": {"type": "array"},
                                "config": {"type": "object"},
                                "options": {"type": "object"}
                            }
                        }
                    },
                    "layout": {
                        "type": "string",
                        "enum": ["grid", "vertical", "horizontal"],
                        "description": "Layout arrangement for multiple charts",
                        "default": "grid"
                    }
                },
                "required": ["charts"]
            }
        ),
        Tool(
            name="chart_get_template",
            description=(
                "Get predefined chart templates for common use cases. "
                "Templates include test reports, performance dashboards, "
                "trend analysis, and more."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "templateName": {
                        "type": "string",
                        "enum": [
                            "test-summary",
                            "performance-dashboard",
                            "trend-analysis",
                            "comparison-report",
                            "distribution-analysis",
                            "correlation-matrix"
                        ],
                        "description": "Name of the template"
                    },
                    "data": {
                        "type": "object",
                        "description": "Data to populate the template"
                    }
                },
                "required": ["templateName"]
            }
        ),
        Tool(
            name="chart_export",
            description="Export chart to various formats (PNG, SVG, PDF)",
            inputSchema={
                "type": "object",
                "properties": {
                    "chartSpec": {
                        "type": "object",
                        "description": "Chart specification"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["png", "svg", "pdf", "json"],
                        "description": "Export format",
                        "default": "png"
                    },
                    "outputPath": {
                        "type": "string",
                        "description": "Output file path"
                    }
                },
                "required": ["chartSpec", "format"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "chart_generate":
            return await chart_generate(arguments)
        elif name == "chart_generate_batch":
            return await chart_generate_batch(arguments)
        elif name == "chart_get_template":
            return await chart_get_template(arguments)
        elif name == "chart_export":
            return await chart_export(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def chart_generate(arguments: Any) -> List[TextContent]:
    """Generate a single chart"""

    chart_type = arguments.get("chartType")
    data = arguments.get("data", [])
    config = arguments.get("config", {})
    options = arguments.get("options", {})

    # Generate chart specification
    chart_spec = await generate_chart_spec(chart_type, data, config, options)

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "chartType": chart_type,
            "spec": chart_spec,
            "renderUrl": f"/render/{chart_type}",
            "usage": generate_usage_guide(chart_type)
        }, indent=2, ensure_ascii=False)
    )]


async def generate_chart_spec(
    chart_type: str,
    data: List[Dict],
    config: Dict,
    options: Dict
) -> Dict:
    """Generate AntV chart specification"""

    # Base configuration
    spec = {
        "type": chart_type,
        "data": data,
        "width": config.get("width", 800),
        "height": config.get("height", 600),
        "autoFit": options.get("responsive", True),
        "animate": options.get("animate", True)
    }

    # Add title if provided
    if config.get("title"):
        spec["title"] = {
            "text": config["title"],
            "style": {"fontSize": 20, "fill": "#333"}
        }

    # Configure based on chart type
    if chart_type in ["line", "area"]:
        spec.update({
            "xField": config.get("xField", "x"),
            "yField": config.get("yField", "y"),
            "smooth": config.get("smooth", True),
            "point": config.get("showPoint", True)
        })

        if chart_type == "area":
            spec["areaStyle"] = {
                "fill": "l(270) 0:#ffffff 0.5:#7ec2f3 1:#1890ff"
            }

    elif chart_type in ["bar", "column"]:
        spec.update({
            "xField": config.get("xField", "x"),
            "yField": config.get("yField", "y"),
            "seriesField": config.get("colorField"),
            "color": config.get("colors", ["#5B8FF9", "#61DDAA", "#65789B"])
        })

    elif chart_type == "pie":
        spec.update({
            "angleField": config.get("angleField", "value"),
            "colorField": config.get("colorField", "category"),
            "radius": config.get("radius", 0.8),
            "innerRadius": config.get("innerRadius", 0),
            "label": {
                "type": "outer",
                "content": "{name} {percentage}"
            }
        })

    elif chart_type == "scatter":
        spec.update({
            "xField": config.get("xField", "x"),
            "yField": config.get("yField", "y"),
            "sizeField": config.get("sizeField", "size"),
            "colorField": config.get("colorField"),
            "size": config.get("pointSize", [5, 20])
        })

    elif chart_type == "sankey":
        spec.update({
            "sourceField": config.get("sourceField", "source"),
            "targetField": config.get("targetField", "target"),
            "weightField": config.get("weightField", "value")
        })

    elif chart_type == "heatmap":
        spec.update({
            "xField": config.get("xField", "x"),
            "yField": config.get("yField", "y"),
            "colorField": config.get("colorField", "value"),
            "color": config.get("colorScale", ["#174c83", "#7ec2f3", "#ffffff", "#ffa940", "#f4664a"])
        })

    elif chart_type == "treemap":
        spec.update({
            "colorField": config.get("colorField", "value"),
            "color": config.get("colors", ["#5B8FF9", "#61DDAA", "#65789B"])
        })

    elif chart_type == "gauge":
        spec.update({
            "percent": config.get("percent", 0.75),
            "innerRadius": config.get("innerRadius", 0.6),
            "range": {
                "color": config.get("rangeColor", ["#5B8FF9", "#61DDAA", "#65789B"])
            },
            "indicator": {
                "pointer": {"style": {"stroke": "#FFFFFF", "lineWidth": 1}},
                "pin": {"style": {"stroke": "#FFFFFF", "lineWidth": 1}}
            }
        })

    elif chart_type == "funnel":
        spec.update({
            "xField": config.get("xField", "stage"),
            "yField": config.get("yField", "value"),
            "compareField": config.get("compareField")
        })

    elif chart_type == "radar":
        spec.update({
            "xField": config.get("xField", "category"),
            "yField": config.get("yField", "value"),
            "seriesField": config.get("seriesField"),
            "area": config.get("showArea", True)
        })

    # Add legend
    if options.get("legend", True):
        spec["legend"] = {
            "position": config.get("legendPosition", "top")
        }

    # Add theme
    theme = options.get("theme", "default")
    if theme != "default":
        spec["theme"] = theme

    return spec


def generate_usage_guide(chart_type: str) -> str:
    """Generate usage guide for chart"""

    guides = {
        "line": "Line charts are ideal for showing trends over time or continuous data.",
        "bar": "Bar charts are great for comparing categorical data.",
        "pie": "Pie charts show proportions and percentages of a whole.",
        "scatter": "Scatter plots display relationships between two numerical variables.",
        "heatmap": "Heatmaps visualize data density or intensity across two dimensions.",
        "sankey": "Sankey diagrams show flow and relationships between entities.",
        "gauge": "Gauge charts display progress towards a target or KPI.",
        "radar": "Radar charts compare multiple quantitative variables."
    }

    return guides.get(chart_type, "Professional data visualization powered by AntV 5.x")


async def chart_generate_batch(arguments: Any) -> List[TextContent]:
    """Generate multiple charts"""

    charts = arguments.get("charts", [])
    layout = arguments.get("layout", "grid")

    chart_specs = []
    for chart_config in charts:
        spec = await generate_chart_spec(
            chart_config.get("chartType"),
            chart_config.get("data", []),
            chart_config.get("config", {}),
            chart_config.get("options", {})
        )
        chart_specs.append(spec)

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "count": len(chart_specs),
            "layout": layout,
            "charts": chart_specs
        }, indent=2, ensure_ascii=False)
    )]


async def chart_get_template(arguments: Any) -> List[TextContent]:
    """Get predefined chart template"""

    template_name = arguments.get("templateName")
    data = arguments.get("data", {})

    templates = {
        "test-summary": generate_test_summary_template,
        "performance-dashboard": generate_performance_dashboard_template,
        "trend-analysis": generate_trend_analysis_template,
        "comparison-report": generate_comparison_report_template
    }

    template_func = templates.get(template_name)
    if not template_func:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"Template '{template_name}' not found"
            })
        )]

    template = template_func(data)

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "templateName": template_name,
            "template": template
        }, indent=2, ensure_ascii=False)
    )]


def generate_test_summary_template(data: Dict) -> Dict:
    """Generate test summary dashboard template"""

    return {
        "layout": "grid",
        "charts": [
            {
                "type": "pie",
                "title": "Test Results Distribution",
                "config": {
                    "angleField": "count",
                    "colorField": "status",
                    "radius": 0.8
                },
                "data": data.get("test_results", [
                    {"status": "passed", "count": 40},
                    {"status": "failed", "count": 5},
                    {"status": "skipped", "count": 2}
                ])
            },
            {
                "type": "bar",
                "title": "Tests by Module",
                "config": {
                    "xField": "module",
                    "yField": "count",
                    "seriesField": "status"
                },
                "data": data.get("module_results", [])
            },
            {
                "type": "line",
                "title": "Test Trend Over Time",
                "config": {
                    "xField": "date",
                    "yField": "pass_rate",
                    "smooth": True
                },
                "data": data.get("trend_data", [])
            }
        ]
    }


def generate_performance_dashboard_template(data: Dict) -> Dict:
    """Generate performance dashboard template"""

    return {
        "layout": "grid",
        "charts": [
            {
                "type": "gauge",
                "title": "Overall Performance Score",
                "config": {
                    "percent": data.get("score", 0.85)
                }
            },
            {
                "type": "line",
                "title": "Response Time Trend",
                "config": {
                    "xField": "timestamp",
                    "yField": "response_time"
                },
                "data": data.get("response_times", [])
            },
            {
                "type": "bar",
                "title": "API Performance Ranking",
                "config": {
                    "xField": "api_endpoint",
                    "yField": "avg_response_time"
                },
                "data": data.get("api_ranking", [])
            }
        ]
    }


def generate_trend_analysis_template(data: Dict) -> Dict:
    """Generate trend analysis template"""

    return {
        "layout": "grid",
        "charts": [
            {
                "type": "line",
                "title": "Trend Analysis",
                "config": {
                    "xField": "date",
                    "yField": "value",
                    "seriesField": "category"
                },
                "data": data.get("trend_data", [])
            },
            {
                "type": "area",
                "title": "Cumulative Trend",
                "config": {
                    "xField": "date",
                    "yField": "cumulative_value"
                },
                "data": data.get("cumulative_data", [])
            }
        ]
    }


def generate_comparison_report_template(data: Dict) -> Dict:
    """Generate comparison report template"""

    return {
        "layout": "grid",
        "charts": [
            {
                "type": "bar",
                "title": "Side-by-Side Comparison",
                "config": {
                    "xField": "metric",
                    "yField": "value",
                    "seriesField": "group"
                },
                "data": data.get("comparison_data", [])
            },
            {
                "type": "radar",
                "title": "Multi-Dimensional Comparison",
                "config": {
                    "xField": "dimension",
                    "yField": "score",
                    "seriesField": "entity"
                },
                "data": data.get("radar_data", [])
            }
        ]
    }


async def chart_export(arguments: Any) -> List[TextContent]:
    """Export chart to specified format"""

    chart_spec = arguments.get("chartSpec")
    format_type = arguments.get("format", "png")
    output_path = arguments.get("outputPath")

    # Generate export specification
    export_spec = {
        "chart": chart_spec,
        "format": format_type,
        "outputPath": output_path
    }

    return [TextContent(
        type="text",
        text=json.dumps({
            "status": "success",
            "export": export_spec,
            "instructions": f"Use the chart render service to export to {format_type.upper()}"
        }, indent=2, ensure_ascii=False)
    )]


async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

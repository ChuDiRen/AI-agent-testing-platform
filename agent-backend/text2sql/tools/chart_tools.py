"""
图表生成工具

集成mcp-server-chart生成数据可视化图表
"""

from typing import Any, Dict, List, Optional
from langchain_core.tools import tool
from enum import Enum


class ChartType(str, Enum):
    """图表类型"""
    BAR = "bar_chart"
    LINE = "line_chart"
    PIE = "pie_chart"
    COLUMN = "column_chart"
    SCATTER = "scatter_chart"
    AREA = "area_chart"


def infer_chart_type(data: List[Dict[str, Any]], columns: List[str]) -> ChartType:
    """根据数据推断合适的图表类型
    
    Args:
        data: 查询结果数据
        columns: 列名列表
        
    Returns:
        推荐的图表类型
    """
    if not data or len(columns) < 2:
        return ChartType.BAR
    
    # 分析数据特征
    first_row = data[0]
    row_count = len(data)
    
    # 检查是否有时间类型列
    time_keywords = ['date', 'time', 'year', 'month', 'day', 'created', 'updated']
    has_time = any(
        any(kw in col.lower() for kw in time_keywords) 
        for col in columns
    )
    
    # 检查数值列
    numeric_cols = []
    for col in columns:
        val = first_row.get(col)
        if isinstance(val, (int, float)):
            numeric_cols.append(col)
    
    # 如果类别数少于等于7，且有数值列，适合饼图
    if row_count <= 7 and len(numeric_cols) >= 1:
        return ChartType.PIE
    
    # 如果有时间列，适合折线图
    if has_time:
        return ChartType.LINE
    
    # 如果数据量大，适合柱状图
    if row_count > 10:
        return ChartType.BAR
    
    # 如果有两个数值列，可以用散点图
    if len(numeric_cols) >= 2:
        return ChartType.SCATTER
    
    return ChartType.BAR


def prepare_chart_data(
    data: List[Dict[str, Any]], 
    x_column: str, 
    y_column: str
) -> Dict[str, Any]:
    """准备图表数据
    
    Args:
        data: 原始数据
        x_column: X轴列
        y_column: Y轴列
        
    Returns:
        格式化的图表数据
    """
    labels = []
    values = []
    
    for row in data:
        labels.append(str(row.get(x_column, "")))
        val = row.get(y_column, 0)
        if isinstance(val, (int, float)):
            values.append(val)
        else:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                values.append(0)
    
    return {
        "labels": labels,
        "values": values,
        "x_column": x_column,
        "y_column": y_column
    }


@tool
def recommend_chart_type(
    data: List[Dict[str, Any]], 
    columns: List[str]
) -> Dict[str, Any]:
    """根据数据推荐图表类型
    
    Args:
        data: 查询结果数据
        columns: 列名列表
        
    Returns:
        推荐的图表类型和理由
    """
    chart_type = infer_chart_type(data, columns)
    
    reasons = {
        ChartType.BAR: "数据适合分类比较，推荐使用柱状图",
        ChartType.LINE: "数据包含时间序列，推荐使用折线图",
        ChartType.PIE: "数据类别较少，适合展示占比，推荐使用饼图",
        ChartType.SCATTER: "数据包含多个数值变量，推荐使用散点图查看相关性",
        ChartType.COLUMN: "数据适合横向比较，推荐使用条形图",
        ChartType.AREA: "数据适合展示累积趋势，推荐使用面积图"
    }
    
    return {
        "recommended_type": chart_type.value,
        "reason": reasons.get(chart_type, "默认推荐"),
        "data_rows": len(data),
        "columns": columns
    }


@tool
def generate_bar_chart(
    data: List[Dict[str, Any]],
    x_column: str,
    y_column: str,
    title: str = "Bar Chart"
) -> Dict[str, Any]:
    """生成柱状图配置
    
    Args:
        data: 数据列表
        x_column: X轴列名
        y_column: Y轴列名
        title: 图表标题
        
    Returns:
        图表配置
    """
    chart_data = prepare_chart_data(data, x_column, y_column)
    
    return {
        "chart_type": "bar",
        "title": title,
        "data": {
            "labels": chart_data["labels"],
            "datasets": [{
                "label": y_column,
                "data": chart_data["values"]
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "legend": {"position": "top"},
                "title": {"display": True, "text": title}
            }
        }
    }


@tool
def generate_line_chart(
    data: List[Dict[str, Any]],
    x_column: str,
    y_column: str,
    title: str = "Line Chart"
) -> Dict[str, Any]:
    """生成折线图配置
    
    Args:
        data: 数据列表
        x_column: X轴列名
        y_column: Y轴列名
        title: 图表标题
        
    Returns:
        图表配置
    """
    chart_data = prepare_chart_data(data, x_column, y_column)
    
    return {
        "chart_type": "line",
        "title": title,
        "data": {
            "labels": chart_data["labels"],
            "datasets": [{
                "label": y_column,
                "data": chart_data["values"],
                "fill": False,
                "borderColor": "rgb(75, 192, 192)",
                "tension": 0.1
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "legend": {"position": "top"},
                "title": {"display": True, "text": title}
            }
        }
    }


@tool
def generate_pie_chart(
    data: List[Dict[str, Any]],
    label_column: str,
    value_column: str,
    title: str = "Pie Chart"
) -> Dict[str, Any]:
    """生成饼图配置
    
    Args:
        data: 数据列表
        label_column: 标签列名
        value_column: 数值列名
        title: 图表标题
        
    Returns:
        图表配置
    """
    chart_data = prepare_chart_data(data, label_column, value_column)
    
    # 默认颜色
    colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)'
    ]
    
    return {
        "chart_type": "pie",
        "title": title,
        "data": {
            "labels": chart_data["labels"],
            "datasets": [{
                "data": chart_data["values"],
                "backgroundColor": colors[:len(chart_data["values"])]
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "legend": {"position": "right"},
                "title": {"display": True, "text": title}
            }
        }
    }


@tool
def generate_chart(
    data: List[Dict[str, Any]],
    columns: List[str],
    chart_type: Optional[str] = None,
    title: str = "Chart"
) -> Dict[str, Any]:
    """智能生成图表
    
    自动选择合适的图表类型和配置
    
    Args:
        data: 查询结果数据
        columns: 列名列表
        chart_type: 指定的图表类型（可选）
        title: 图表标题
        
    Returns:
        图表配置
    """
    if not data or len(columns) < 2:
        return {
            "success": False,
            "error": "数据不足以生成图表（至少需要2列数据）"
        }
    
    # 确定图表类型
    if chart_type:
        try:
            ctype = ChartType(chart_type)
        except ValueError:
            ctype = infer_chart_type(data, columns)
    else:
        ctype = infer_chart_type(data, columns)
    
    # 选择X和Y轴
    x_column = columns[0]
    y_column = columns[1] if len(columns) > 1 else columns[0]
    
    # 找到数值列作为Y轴
    for col in columns[1:]:
        val = data[0].get(col)
        if isinstance(val, (int, float)):
            y_column = col
            break
    
    # 生成对应类型的图表
    if ctype == ChartType.BAR:
        return generate_bar_chart.invoke({
            "data": data, "x_column": x_column, 
            "y_column": y_column, "title": title
        })
    elif ctype == ChartType.LINE:
        return generate_line_chart.invoke({
            "data": data, "x_column": x_column,
            "y_column": y_column, "title": title
        })
    elif ctype == ChartType.PIE:
        return generate_pie_chart.invoke({
            "data": data, "label_column": x_column,
            "value_column": y_column, "title": title
        })
    else:
        # 默认柱状图
        return generate_bar_chart.invoke({
            "data": data, "x_column": x_column,
            "y_column": y_column, "title": title
        })


# 工具列表
CHART_TOOLS = [
    recommend_chart_type,
    generate_bar_chart,
    generate_line_chart,
    generate_pie_chart,
    generate_chart
]

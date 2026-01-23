"""
AntV Chart Integration - Professional Data Visualization

This module provides comprehensive AntV 5.x integration with 25+ chart types,
SSE streaming support, and advanced customization options.
"""
from typing import Any, Dict, List, Optional, Union
import json
import uuid
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio


class ChartType(Enum):
    """Supported chart types"""
    # Basic charts
    LINE = "line"
    BAR = "bar"
    COLUMN = "column"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    
    # Advanced charts
    SANKEY = "sankey"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    BOXPLOT = "boxplot"
    VIOLIN = "violin"
    HISTOGRAM = "histogram"
    RADAR = "radar"
    ROSE = "rose"
    
    # Composite charts
    DUAL_AXIS = "dual-axis"
    MIXED = "mixed"
    GROUPED_STACKED = "grouped-stacked"
    WATERFALL = "waterfall"
    
    # Specialized charts
    WORD_CLOUD = "word-cloud"
    CIRCLE_PACKING = "circle-packing"
    FORCE_GRAPH = "force-graph"
    TREE = "tree"
    MATRIX = "matrix"
    PARALLEL_COORDINATES = "parallel-coordinates"
    STOCK = "stock"
    
    # Geographic charts
    MAP = "map"
    CHOROPLETH = "choropleth"
    CALENDAR = "calendar"


@dataclass
class ChartData:
    """Chart data structure"""
    values: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChartConfig:
    """Chart configuration"""
    title: Optional[str] = None
    width: int = 800
    height: int = 600
    theme: str = "default"
    responsive: bool = True
    animate: bool = True
    colors: List[str] = None
    legend: Optional[Dict[str, Any]] = None
    tooltip: Optional[Dict[str, Any]] = None


@dataclass
class ChartSpec:
    """Complete chart specification"""
    chart_id: str
    chart_type: ChartType
    data: ChartData
    config: ChartConfig
    antv_spec: Dict[str, Any]
    render_url: str
    created_at: str


class AntVChartEngine:
    """
    AntV 5.x Chart Engine
    
    Provides comprehensive chart generation with:
    - 25+ chart types
    - SSE streaming support
    - Advanced customization
    - Theme support
    - Export capabilities
    """

    def __init__(self, base_url: str = "http://localhost:3000"):
        """Initialize AntV chart engine"""
        self.base_url = base_url
        self.chart_cache: Dict[str, ChartSpec] = {}
        
        # Default color palettes
        self.color_palettes = {
            "default": ["#5B8FF9", "#61DDAA", "#65789B", "#F6BD16", "#E86452"],
            "pastel": ["#91CC75", "#5470C6", "#91CC75", "#EE6666", "#73C0DE"],
            "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"],
            "business": ["#1890FF", "#52C41A", "#FAAD14", "#F5222D", "#722ED1"],
            "scientific": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        }
        
        # Chart type configurations
        self.chart_configs = self._initialize_chart_configs()

    def _initialize_chart_configs(self) -> Dict[ChartType, Dict[str, Any]]:
        """Initialize default configurations for each chart type"""
        return {
            ChartType.LINE: {
                "required_fields": ["xField", "yField"],
                "optional_fields": ["seriesField", "smooth", "point"],
                "default_config": {
                    "smooth": True,
                    "point": {"size": 3, "shape": "circle"},
                    "interaction": {"tooltip": {"shared": True}}
                }
            },
            ChartType.BAR: {
                "required_fields": ["xField", "yField"],
                "optional_fields": ["seriesField", "colorField"],
                "default_config": {
                    "barWidthRatio": 0.8,
                    "interaction": {"tooltip": {"shared": True}}
                }
            },
            ChartType.PIE: {
                "required_fields": ["angleField", "colorField"],
                "optional_fields": ["radius", "innerRadius"],
                "default_config": {
                    "radius": 0.8,
                    "innerRadius": 0,
                    "label": {"type": "outer", "content": "{name} {percentage}"}
                }
            },
            ChartType.SCATTER: {
                "required_fields": ["xField", "yField"],
                "optional_fields": ["sizeField", "colorField"],
                "default_config": {
                    "size": [5, 20],
                    "shape": "circle",
                    "interaction": {"tooltip": {"shared": True}}
                }
            },
            ChartType.SANKEY: {
                "required_fields": ["sourceField", "targetField", "weightField"],
                "optional_fields": [],
                "default_config": {
                    "nodeWidth": 0.02,
                    "nodePadding": 0.01,
                    "nodeAlign": "justify"
                }
            },
            ChartType.HEATMAP: {
                "required_fields": ["xField", "yField", "colorField"],
                "optional_fields": [],
                "default_config": {
                    "color": ["#174c83", "#7ec2f3", "#ffffff", "#ffa940", "#f4664a"],
                    "meta": {}
                }
            },
            ChartType.GAUGE: {
                "required_fields": ["percent"],
                "optional_fields": ["range"],
                "default_config": {
                    "range": {"color": ["#30BF78", "#FAAD14", "#F4664A"]},
                    "indicator": {"pointer": { "style": { "stroke": "#D0D0D0" }}},
                    "statistic": {"content": { "style": { "fontSize": "36px" }}}
                }
            }
        }

    async def create_chart(
        self,
        chart_type: Union[str, ChartType],
        data: Union[List[Dict[str, Any]], ChartData],
        config: Optional[Union[Dict[str, Any], ChartConfig]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ChartSpec:
        """
        Create a chart specification
        
        Args:
            chart_type: Type of chart to create
            data: Chart data
            config: Chart configuration
            options: Additional options
        
        Returns:
            Complete chart specification
        """
        # Convert chart type
        if isinstance(chart_type, str):
            chart_type = ChartType(chart_type)
        
        # Prepare data
        if isinstance(data, list):
            chart_data = ChartData(values=data)
        else:
            chart_data = data
        
        # Prepare config
        if isinstance(config, dict):
            chart_config = ChartConfig(**config)
        elif config is None:
            chart_config = ChartConfig()
        else:
            chart_config = config
        
        # Generate AntV specification
        antv_spec = await self._generate_antv_spec(chart_type, chart_data, chart_config, options or {})
        
        # Create chart specification
        chart_spec = ChartSpec(
            chart_id=str(uuid.uuid4()),
            chart_type=chart_type,
            data=chart_data,
            config=chart_config,
            antv_spec=antv_spec,
            render_url=f"{self.base_url}/render/{chart_spec.chart_id}",
            created_at=datetime.utcnow().isoformat()
        )
        
        # Cache the specification
        self.chart_cache[chart_spec.chart_id] = chart_spec
        
        return chart_spec

    async def _generate_antv_spec(
        self,
        chart_type: ChartType,
        data: ChartData,
        config: ChartConfig,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AntV chart specification"""
        
        # Base specification
        spec = {
            "type": chart_type.value,
            "data": data.values,
            "width": config.width,
            "height": config.height,
            "autoFit": config.responsive,
            "animate": config.animate,
            "theme": config.theme
        }
        
        # Add title
        if config.title:
            spec["title"] = {
                "text": config.title,
                "style": {"fontSize": 20, "fill": "#333"}
            }
        
        # Get chart type configuration
        type_config = self.chart_configs.get(chart_type, {})
        default_config = type_config.get("default_config", {})
        
        # Merge configurations
        merged_config = {**default_config, **options}
        
        # Apply chart type specific configuration
        if chart_type == ChartType.LINE:
            spec.update({
                "xField": merged_config.get("xField", "x"),
                "yField": merged_config.get("yField", "y"),
                "smooth": merged_config.get("smooth", True),
                "point": merged_config.get("point", {"size": 3}),
                "seriesField": merged_config.get("seriesField")
            })
            
        elif chart_type == ChartType.BAR:
            spec.update({
                "xField": merged_config.get("xField", "x"),
                "yField": merged_config.get("yField", "y"),
                "seriesField": merged_config.get("seriesField"),
                "color": config.colors or self.color_palettes.get(config.theme, self.color_palettes["default"])
            })
            
        elif chart_type == ChartType.PIE:
            spec.update({
                "angleField": merged_config.get("angleField", "value"),
                "colorField": merged_config.get("colorField", "category"),
                "radius": merged_config.get("radius", 0.8),
                "innerRadius": merged_config.get("innerRadius", 0),
                "label": merged_config.get("label", {
                    "type": "outer",
                    "content": "{name} {percentage}"
                }),
                "color": config.colors or self.color_palettes.get(config.theme, self.color_palettes["default"])
            })
            
        elif chart_type == ChartType.SCATTER:
            spec.update({
                "xField": merged_config.get("xField", "x"),
                "yField": merged_config.get("yField", "y"),
                "sizeField": merged_config.get("sizeField", "size"),
                "colorField": merged_config.get("colorField"),
                "size": merged_config.get("size", [5, 20]),
                "color": config.colors or self.color_palettes.get(config.theme, self.color_palettes["default"])
            })
            
        elif chart_type == ChartType.SANKEY:
            spec.update({
                "sourceField": merged_config.get("sourceField", "source"),
                "targetField": merged_config.get("targetField", "target"),
                "weightField": merged_config.get("weightField", "value"),
                "nodeWidth": merged_config.get("nodeWidth", 0.02),
                "nodePadding": merged_config.get("nodePadding", 0.01)
            })
            
        elif chart_type == ChartType.HEATMAP:
            spec.update({
                "xField": merged_config.get("xField", "x"),
                "yField": merged_config.get("yField", "y"),
                "colorField": merged_config.get("colorField", "value"),
                "color": merged_config.get("color", ["#174c83", "#7ec2f3", "#ffffff", "#ffa940", "#f4664a"])
            })
            
        elif chart_type == ChartType.GAUGE:
            spec.update({
                "percent": merged_config.get("percent", 0.7),
                "range": merged_config.get("range", {
                    "color": ["#30BF78", "#FAAD14", "#F4664A"]
                }),
                "indicator": merged_config.get("indicator", {
                    "pointer": {"style": {"stroke": "#D0D0D0"}}
                }),
                "statistic": merged_config.get("statistic", {
                    "content": {"style": {"fontSize": "36px"}}
                })
            })
            
        elif chart_type == ChartType.RADAR:
            spec.update({
                "xField": merged_config.get("xField", "item"),
                "yField": merged_config.get("yField", "value"),
                "seriesField": merged_config.get("seriesField", "category"),
                "area": merged_config.get("area", True),
                "color": config.colors or self.color_palettes.get(config.theme, self.color_palettes["default"])
            })
            
        elif chart_type == ChartType.FUNNEL:
            spec.update({
                "xField": merged_config.get("xField", "stage"),
                "yField": merged_config.get("yField", "value"),
                "compareField": merged_config.get("compareField"),
                "color": config.colors or self.color_palettes.get(config.theme, self.color_palettes["default"])
            })
            
        # Add legend configuration
        if config.legend:
            spec["legend"] = config.legend
        elif chart_type in [ChartType.PIE, ChartType.BAR, ChartType.LINE]:
            spec["legend"] = {"position": "bottom"}
        
        # Add tooltip configuration
        if config.tooltip:
            spec["tooltip"] = config.tooltip
        else:
            spec["tooltip"] = {"shared": True}
        
        # Add interaction configuration
        spec["interaction"] = merged_config.get("interaction", {"tooltip": {"shared": True}})
        
        return spec

    async def create_batch_charts(
        self,
        chart_requests: List[Dict[str, Any]]
    ) -> List[ChartSpec]:
        """Create multiple charts in batch"""
        charts = []
        
        for request in chart_requests:
            chart = await self.create_chart(
                chart_type=request.get("chartType"),
                data=request.get("data", []),
                config=request.get("config"),
                options=request.get("options")
            )
            charts.append(chart)
        
        return charts

    async def get_chart_template(self, template_name: str) -> Dict[str, Any]:
        """Get predefined chart template"""
        templates = {
            "test_results_pie": {
                "chartType": "pie",
                "config": {
                    "title": "Test Results Distribution",
                    "width": 600,
                    "height": 400
                },
                "data_example": [
                    {"category": "Passed", "value": 85},
                    {"category": "Failed", "value": 10},
                    {"category": "Skipped", "value": 5}
                ]
            },
            "performance_line": {
                "chartType": "line",
                "config": {
                    "title": "Performance Trends",
                    "width": 800,
                    "height": 400
                },
                "options": {
                    "xField": "time",
                    "yField": "responseTime",
                    "smooth": True
                },
                "data_example": [
                    {"time": "00:00", "responseTime": 120},
                    {"time": "00:05", "responseTime": 150},
                    {"time": "00:10", "responseTime": 100}
                ]
            },
            "api_coverage_bar": {
                "chartType": "bar",
                "config": {
                    "title": "API Coverage",
                    "width": 800,
                    "height": 400
                },
                "options": {
                    "xField": "endpoint",
                    "yField": "coverage"
                },
                "data_example": [
                    {"endpoint": "/login", "coverage": 95},
                    {"endpoint": "/users", "coverage": 80},
                    {"endpoint": "/orders", "coverage": 70}
                ]
            }
        }
        
        return templates.get(template_name, {"error": "Template not found"})

    async def export_chart(
        self,
        chart_id: str,
        format: str = "png",
        quality: int = 90
    ) -> Dict[str, Any]:
        """Export chart to specified format"""
        if chart_id not in self.chart_cache:
            return {"error": "Chart not found"}
        
        chart_spec = self.chart_cache[chart_id]
        
        export_info = {
            "chart_id": chart_id,
            "format": format,
            "quality": quality,
            "export_url": f"{self.base_url}/export/{chart_id}.{format}",
            "download_url": f"{self.base_url}/download/{chart_id}.{format}",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return export_info

    async def stream_chart_updates(
        self,
        chart_id: str,
        data_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Stream real-time chart updates via SSE"""
        if chart_id not in self.chart_cache:
            return {"error": "Chart not found"}
        
        # In a real implementation, this would use SSE
        stream_info = {
            "chart_id": chart_id,
            "stream_url": f"{self.base_url}/stream/{chart_id}",
            "updates": data_updates,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return stream_info

    def get_chart_by_id(self, chart_id: str) -> Optional[ChartSpec]:
        """Get chart specification by ID"""
        return self.chart_cache.get(chart_id)

    def list_charts(self) -> List[ChartSpec]:
        """List all cached charts"""
        return list(self.chart_cache.values())

    def delete_chart(self, chart_id: str) -> bool:
        """Delete chart from cache"""
        if chart_id in self.chart_cache:
            del self.chart_cache[chart_id]
            return True
        return False

    def get_supported_chart_types(self) -> List[Dict[str, Any]]:
        """Get list of supported chart types with descriptions"""
        return [
            {
                "type": chart_type.value,
                "name": chart_type.name.replace("_", " ").title(),
                "category": self._get_chart_category(chart_type),
                "description": self._get_chart_description(chart_type)
            }
            for chart_type in ChartType
        ]

    def _get_chart_category(self, chart_type: ChartType) -> str:
        """Get chart category"""
        basic = {ChartType.LINE, ChartType.BAR, ChartType.COLUMN, ChartType.PIE, ChartType.AREA, ChartType.SCATTER}
        advanced = {ChartType.SANKEY, ChartType.HEATMAP, ChartType.TREEMAP, ChartType.GAUGE, ChartType.FUNNEL}
        statistical = {ChartType.BOXPLOT, ChartType.VIOLIN, ChartType.HISTOGRAM, ChartType.RADAR, ChartType.ROSE}
        geographic = {ChartType.MAP, ChartType.CHOROPLETH, ChartType.CALENDAR}
        
        if chart_type in basic:
            return "Basic"
        elif chart_type in advanced:
            return "Advanced"
        elif chart_type in statistical:
            return "Statistical"
        elif chart_type in geographic:
            return "Geographic"
        else:
            return "Specialized"

    def _get_chart_description(self, chart_type: ChartType) -> str:
        """Get chart description"""
        descriptions = {
            ChartType.LINE: "Display trends over continuous data",
            ChartType.BAR: "Compare values across categories",
            ChartType.PIE: "Show proportions of a whole",
            ChartType.SCATTER: "Display relationship between two variables",
            ChartType.SANKEY: "Visualize flow and relationships",
            ChartType.HEATMAP: "Show data intensity across two dimensions",
            ChartType.GAUGE: "Display progress or KPI metrics",
            ChartType.RADAR: "Compare multiple variables across categories"
        }
        return descriptions.get(chart_type, "Advanced data visualization chart")


# Global instance for MCP server integration
antv_engine: Optional[AntVChartEngine] = None


def get_antv_engine(**kwargs) -> AntVChartEngine:
    """Get or create global AntV engine instance"""
    global antv_engine
    if antv_engine is None:
        antv_engine = AntVChartEngine(**kwargs)
    return antv_engine

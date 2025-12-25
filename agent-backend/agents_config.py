"""
智能体元数据配置

定义所有可用智能体的元数据信息，供前端展示和选择
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AgentMetadata:
    """智能体元数据"""
    id: str                          # 智能体ID (对应 langgraph.json 中的 key)
    name: str                        # 显示名称
    description: str                 # 描述
    icon: str                        # 图标 (emoji 或图标名称)
    category: str                    # 分类
    tags: List[str]                  # 标签
    version: str = "1.0.0"           # 版本
    author: str = "AI Testing Team"  # 作者
    is_streaming: bool = False       # 是否支持流式输出
    requires_config: bool = False    # 是否需要额外配置
    config_schema: Optional[dict] = None  # 配置 schema


# 所有可用的智能体配置
AGENTS_METADATA: List[AgentMetadata] = [
    # ============== Text-to-SQL 系列 ==============
    AgentMetadata(
        id="text2sql_agent",
        name="Text2SQL 智能体",
        description="自然语言转SQL查询，支持多轮对话、Schema分析、SQL生成与执行、图表生成",
        icon="🗄️",
        category="数据分析",
        tags=["SQL", "数据库", "自然语言"],
        is_streaming=False,
    ),
    AgentMetadata(
        id="text2sql_stream",
        name="Text2SQL (流式)",
        description="自然语言转SQL查询，支持流式输出，实时展示生成过程",
        icon="🗄️",
        category="数据分析",
        tags=["SQL", "数据库", "流式"],
        is_streaming=True,
    ),
    
    # ============== Text-to-TestCase 系列 ==============
    AgentMetadata(
        id="text2testcase_agent",
        name="测试用例生成智能体",
        description="根据需求文档自动生成测试用例，支持需求分析、测试点设计、用例编写、评审优化",
        icon="🧪",
        category="测试工具",
        tags=["测试用例", "自动化", "需求分析"],
        is_streaming=False,
    ),
    AgentMetadata(
        id="text2testcase_stream",
        name="测试用例生成 (流式)",
        description="测试用例生成智能体，支持流式输出，实时展示生成进度",
        icon="🧪",
        category="测试工具",
        tags=["测试用例", "流式", "实时"],
        is_streaming=True,
    ),
    
    # ============== SQL Agent 系列 ==============
    AgentMetadata(
        id="sql_agent",
        name="SQL Agent (基础版)",
        description="基础SQL查询智能体，支持简单的自然语言转SQL",
        icon="📊",
        category="数据分析",
        tags=["SQL", "基础"],
    ),
    AgentMetadata(
        id="sql_agent_hitl",
        name="SQL Agent (人机协作)",
        description="支持人工介入的SQL智能体，可在关键节点暂停等待确认",
        icon="🤝",
        category="数据分析",
        tags=["SQL", "HITL", "人机协作"],
    ),
    AgentMetadata(
        id="sql_agent_graph",
        name="SQL Agent (图模式)",
        description="基于图工作流的SQL智能体，支持复杂查询场景",
        icon="🔀",
        category="数据分析",
        tags=["SQL", "图工作流"],
    ),
    
    # ============== API Agent ==============
    AgentMetadata(
        id="api_agent",
        name="API 测试智能体",
        description="自动化API测试智能体，支持接口调用、参数验证、响应断言",
        icon="🔌",
        category="测试工具",
        tags=["API", "接口测试", "自动化"],
    ),
]


# 智能体分类
AGENT_CATEGORIES = {
    "数据分析": {
        "name": "数据分析",
        "description": "数据查询、SQL生成、数据可视化相关智能体",
        "icon": "📊",
    },
    "测试工具": {
        "name": "测试工具",
        "description": "测试用例生成、API测试、自动化测试相关智能体",
        "icon": "🧪",
    },
}


def get_agent_by_id(agent_id: str) -> Optional[AgentMetadata]:
    """根据ID获取智能体元数据"""
    for agent in AGENTS_METADATA:
        if agent.id == agent_id:
            return agent
    return None


def get_agents_by_category(category: str) -> List[AgentMetadata]:
    """根据分类获取智能体列表"""
    return [agent for agent in AGENTS_METADATA if agent.category == category]


def get_all_agents() -> List[dict]:
    """获取所有智能体信息 (字典格式，便于 JSON 序列化)"""
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "icon": agent.icon,
            "category": agent.category,
            "tags": agent.tags,
            "version": agent.version,
            "is_streaming": agent.is_streaming,
        }
        for agent in AGENTS_METADATA
    ]


def get_categories() -> List[dict]:
    """获取所有分类信息"""
    return [
        {
            "id": key,
            "name": value["name"],
            "description": value["description"],
            "icon": value["icon"],
        }
        for key, value in AGENT_CATEGORIES.items()
    ]

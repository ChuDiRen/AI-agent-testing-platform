"""
Text2API State Definition

API请求生成任务的状态定义
"""
from typing import TypedDict, List, Optional, Dict, Any


class Text2APIState(TypedDict, total=False):
    """
    Text2API状态定义
    
    继承BaseState的通用字段，添加API特有字段
    """
    # 通用字段
    messages: List[Dict[str, Any]]
    completed: bool
    error: Optional[str]
    
    # API特有字段
    description: str                   # 用户描述
    api_spec: Optional[str]            # API规范/文档
    base_url: Optional[str]            # 基础URL
    auth_type: str                     # 认证类型 (none/bearer/basic/apikey)
    request: Optional[Dict[str, Any]]  # 生成的请求对象
    curl: Optional[str]                # cURL命令
    explanation: Optional[str]         # 请求说明


def create_initial_state(
    description: str = "",
    api_spec: str = "",
    base_url: str = "",
    auth_type: str = "none"
) -> Text2APIState:
    """创建初始状态"""
    return Text2APIState(
        messages=[],
        completed=False,
        error=None,
        description=description,
        api_spec=api_spec,
        base_url=base_url,
        auth_type=auth_type,
        request=None,
        curl=None,
        explanation=None,
    )

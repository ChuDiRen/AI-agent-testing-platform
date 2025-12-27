from typing import Optional, List, Any, Dict

from pydantic import BaseModel, Field


# ==================== 测试计划查询相关 ====================
class ApiCollectionInfoQuery(BaseModel):
    """测试集合查询请求"""
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    project_id: Optional[int] = Field(default=None, description="项目ID")
    plan_name: Optional[str] = Field(default=None, description="计划名称")

# ==================== 测试计划创建/更新相关 ====================
class ApiCollectionInfoCreate(BaseModel):
    """测试集合创建请求"""
    project_id: Optional[int] = Field(default=None, description="项目ID")
    plan_name: str = Field(description="计划名称")
    plan_desc: Optional[str] = Field(default=None, description="计划描述")
    collection_env: Optional[List[Dict[str, Any]]] = Field(default=None, description="全局环境变量（JSON数组）")
    plugin_code: Optional[str] = Field(default='api_engine', description="执行引擎插件代码")

class ApiCollectionInfoUpdate(BaseModel):
    """测试集合更新请求"""
    id: int = Field(description="计划ID")
    project_id: Optional[int] = Field(default=None, description="项目ID")
    plan_name: Optional[str] = Field(default=None, description="计划名称")
    plan_desc: Optional[str] = Field(default=None, description="计划描述")
    collection_env: Optional[List[Dict[str, Any]]] = Field(default=None, description="全局环境变量（JSON数组）")
    plugin_code: Optional[str] = Field(default=None, description="执行引擎插件代码")

# ==================== 计划用例关联相关 ====================
class ApiCollectionDetailCreate(BaseModel):
    """集合详情创建请求"""
    collection_info_id: int = Field(description="测试集合ID")
    case_info_id: int = Field(description="用例ID")
    run_order: int = Field(default=0, description="执行顺序")
    ddt_data: Optional[List[Dict[str, Any]]] = Field(default=None, description="数据驱动数据（数组）")

class ApiCollectionDetailUpdate(BaseModel):
    """集合详情更新请求"""
    id: int = Field(description="关联ID")
    run_order: Optional[int] = Field(default=None, description="执行顺序")
    ddt_data: Optional[List[Dict[str, Any]]] = Field(default=None, description="数据驱动数据（数组）")

class ApiCollectionDetailResponse(BaseModel):
    """集合详情响应"""
    id: int
    plan_id: int
    case_info_id: int
    run_order: int
    ddt_data: Optional[str]
    create_time: Optional[str]
    # 扩展字段（关联查询）
    case_name: Optional[str] = None
    case_desc: Optional[str] = None

# ==================== 测试计划详情相关 ====================
class ApiCollectionInfoWithCases(BaseModel):
    """测试集合详情响应（含关联用例）"""
    id: int
    project_id: Optional[int]
    plan_name: str
    plan_desc: Optional[str]
    create_time: Optional[str]
    update_time: Optional[str]
    cases: List[ApiCollectionDetailResponse] = Field(default=[], description="关联的用例列表")

# ==================== 批量添加用例 ====================
class BatchAddCasesRequest(BaseModel):
    """批量添加用例到计划"""
    plan_id: int = Field(description="测试计划ID")
    case_ids: List[int] = Field(description="用例ID列表")

# ==================== 数据驱动更新相关 ====================
class UpdateDdtDataRequest(BaseModel):
    """更新用例的数据驱动数据"""
    plan_case_id: int = Field(description="计划用例关联ID")
    ddt_data: List[Dict[str, Any]] = Field(description="数据驱动数据（数组）")

# ==================== 测试计划执行相关 ====================
class ApiCollectionInfoExecuteRequest(BaseModel):
    """测试集合执行请求"""
    plan_id: int = Field(description="测试计划ID")
    test_name: Optional[str] = Field(default=None, description="测试名称")

class ApiCollectionInfoExecuteResponse(BaseModel):
    """测试集合执行响应"""
    execution_uuid: str = Field(description="批量执行UUID")
    status: str = Field(description="执行状态")
    message: str = Field(description="执行消息")
    total_cases: int = Field(description="总用例数")


# ==================== 机器人关联相关 ====================
class PlanRobotCreate(BaseModel):
    """测试计划关联机器人请求"""
    plan_id: int = Field(description="测试计划ID")
    robot_id: int = Field(description="机器人ID")
    is_enabled: bool = Field(default=True, description="是否启用通知")
    notify_on_success: bool = Field(default=True, description="成功时是否通知")
    notify_on_failure: bool = Field(default=True, description="失败时是否通知")


class PlanRobotUpdate(BaseModel):
    """更新测试计划机器人关联"""
    id: int = Field(description="关联ID")
    is_enabled: Optional[bool] = Field(default=None, description="是否启用通知")
    notify_on_success: Optional[bool] = Field(default=None, description="成功时是否通知")
    notify_on_failure: Optional[bool] = Field(default=None, description="失败时是否通知")


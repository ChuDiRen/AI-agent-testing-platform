from typing import Optional, List, Any, Dict

from pydantic import BaseModel, Field


# ==================== 用例查询相关 ====================
class ApiInfoCaseQuery(BaseModel):
    """API用例查询请求"""
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    project_id: Optional[int] = Field(default=None, description="项目ID")
    case_name: Optional[str] = Field(default=None, description="用例名称")

# ==================== 步骤相关 ====================
class ApiInfoCaseStepCreate(BaseModel):
    """API用例步骤创建请求"""
    run_order: int = Field(description="运行序号")
    step_desc: Optional[str] = Field(default=None, description="步骤描述")
    operation_type_id: Optional[int] = Field(default=None, description="操作类型ID")
    keyword_id: Optional[int] = Field(default=None, description="关键字ID")
    step_data: Optional[Dict[str, Any]] = Field(default=None, description="步骤数据（字典格式）")

class ApiInfoCaseStepUpdate(BaseModel):
    """API用例步骤更新请求"""
    id: int = Field(description="步骤ID")
    run_order: Optional[int] = Field(default=None, description="运行序号")
    step_desc: Optional[str] = Field(default=None, description="步骤描述")
    operation_type_id: Optional[int] = Field(default=None, description="操作类型ID")
    keyword_id: Optional[int] = Field(default=None, description="关键字ID")
    step_data: Optional[Dict[str, Any]] = Field(default=None, description="步骤数据（字典格式）")

class ApiInfoCaseStepResponse(BaseModel):
    """API用例步骤响应"""
    id: int
    case_info_id: int
    run_order: int
    step_desc: Optional[str]
    operation_type_id: Optional[int]
    keyword_id: Optional[int]
    step_data: Optional[str]  # JSON字符串
    create_time: Optional[str]

# ==================== 用例创建/更新相关 ====================
class ApiInfoCaseCreate(BaseModel):
    """API用例创建请求"""
    project_id: Optional[int] = Field(default=None, description="项目ID")
    case_name: str = Field(description="用例名称")
    case_desc: Optional[str] = Field(default=None, description="用例描述")
    context_config: Optional[Dict[str, Any]] = Field(default=None, description="全局配置")
    ddts: Optional[List[Dict[str, Any]]] = Field(default=None, description="数据驱动列表")
    steps: Optional[List[ApiInfoCaseStepCreate]] = Field(default=None, description="用例步骤列表")

class ApiInfoCaseUpdate(BaseModel):
    """API用例更新请求"""
    id: int = Field(description="用例ID")
    project_id: Optional[int] = Field(default=None, description="项目ID")
    case_name: Optional[str] = Field(default=None, description="用例名称")
    case_desc: Optional[str] = Field(default=None, description="用例描述")
    context_config: Optional[Dict[str, Any]] = Field(default=None, description="全局配置")
    ddts: Optional[List[Dict[str, Any]]] = Field(default=None, description="数据驱动列表")
    steps: Optional[List[ApiInfoCaseStepCreate]] = Field(default=None, description="用例步骤列表")

# ==================== 用例响应相关 ====================
class ApiInfoCaseResponse(BaseModel):
    """API用例响应（基本信息）"""
    id: int
    project_id: Optional[int]
    case_name: str
    case_desc: Optional[str]
    create_time: Optional[str]
    modify_time: Optional[str]

class ApiInfoCaseWithSteps(BaseModel):
    """API用例详情响应（含步骤）"""
    id: int
    project_id: Optional[int]
    case_name: str
    case_desc: Optional[str]
    create_time: Optional[str]
    modify_time: Optional[str]
    steps: List[ApiInfoCaseStepResponse] = Field(default=[], description="用例步骤列表")

# ==================== YAML生成相关 ====================
class YamlGenerateRequest(BaseModel):
    """YAML生成请求"""
    case_id: int = Field(description="用例ID")
    context_vars: Optional[Dict[str, Any]] = Field(default=None, description="上下文变量")

class YamlGenerateResponse(BaseModel):
    """YAML生成响应"""
    yaml_content: str = Field(description="生成的YAML内容")
    file_path: Optional[str] = Field(default=None, description="文件路径")

# ==================== 用例执行相关 ====================
class ApiInfoCaseExecuteRequest(BaseModel):
    """API用例执行请求
    
    支持两种模式：
    - 单用例执行：提供 case_id
    - 批量执行计划：提供 plan_id（执行计划中所有用例）
    """
    case_id: Optional[int] = Field(default=None, description="用例ID（单用例执行时必填）")
    plan_id: Optional[int] = Field(default=None, description="测试计划ID（批量执行时必填）")
    test_name: Optional[str] = Field(default=None, description="测试名称")
    context_vars: Optional[Dict[str, Any]] = Field(default=None, description="上下文变量")
    executor_code: Optional[str] = Field(default=None, description="执行器插件代码(例如 web_engine)，为空时可使用后端默认配置")

class ApiInfoCaseExecuteResponse(BaseModel):
    """API用例执行响应"""
    test_id: int = Field(description="测试历史ID")
    status: str = Field(description="执行状态")
    message: str = Field(description="执行消息")


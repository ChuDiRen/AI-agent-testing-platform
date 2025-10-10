# Copyright (c) 2025 左岚. All rights reserved.
"""
浏览器自动化测试数据模式
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


class BrowserTestStepCreate(BaseModel):
    """浏览器测试步骤创建模式"""
    step_name: str = Field(..., description="步骤名称")
    step_type: str = Field(..., description="步骤类型")
    action_config: Dict[str, Any] = Field(..., description="动作配置")
    wait_config: Optional[Dict[str, Any]] = Field(None, description="等待配置")
    validation_config: Optional[Dict[str, Any]] = Field(None, description="验证配置")
    screenshot_config: Optional[Dict[str, Any]] = Field(None, description="截图配置")
    condition_config: Optional[Dict[str, Any]] = Field(None, description="条件配置")
    is_enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="步骤描述")

    class Config:
        schema_extra = {
            "example": {
                "step_name": "登录操作",
                "step_type": "input",
                "action_config": {
                    "locator": {"type": "css", "value": "#username"},
                    "text": "testuser",
                    "clear_first": True
                },
                "validation_config": {
                    "type": "element_exists",
                    "locator": {"type": "css", "value": "#submit"},
                    "enabled": True
                }
            }
        }


class BrowserTestCaseCreate(BaseModel):
    """浏览器测试用例创建模式"""
    suite_id: int = Field(..., description="所属套件ID")
    name: str = Field(..., min_length=1, max_length=200, description="用例名称")
    description: Optional[str] = Field(None, description="用例描述")
    test_steps: List[BrowserTestStepCreate] = Field(..., description="测试步骤")
    test_data: Optional[Dict[str, Any]] = Field(None, description="测试数据")
    assertions: Optional[Dict[str, Any]] = Field(None, description="验证断言")
    priority: str = Field("P2", description="优先级: P0/P1/P2/P3")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="超时时间(秒)")
    retry_count: Optional[int] = Field(None, ge=0, le=10, description="重试次数")
    tags: Optional[str] = Field(None, description="标签")
    sort_order: int = Field(0, description="排序序号")

    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['P0', 'P1', 'P2', 'P3']:
            raise ValueError('优先级必须是 P0, P1, P2, P3 之一')
        return v

    class Config:
        schema_extra = {
            "example": {
                "suite_id": 1,
                "name": "用户登录测试",
                "description": "测试用户登录功能",
                "test_steps": [
                    {
                        "step_name": "打开登录页面",
                        "step_type": "navigate",
                        "action_config": {
                            "url": "https://example.com/login"
                        },
                        "validation_config": {
                            "type": "title_contains",
                            "expected_value": "登录页面"
                        }
                    },
                    {
                        "step_name": "输入用户名",
                        "step_type": "input",
                        "action_config": {
                            "locator": {"type": "css", "value": "#username"},
                            "text": "testuser"
                        }
                    },
                    {
                        "step_name": "输入密码",
                        "step_type": "input",
                        "action_config": {
                            "locator": {"type": "css", "value": "#password"},
                            "text": "password123"
                        }
                    },
                    {
                        "step_name": "点击登录按钮",
                        "step_type": "click",
                        "action_config": {
                            "locator": {"type": "css", "value": "#login-button"}
                        }
                    },
                    {
                        "step_name": "验证登录成功",
                        "step_type": "wait",
                        "action_config": {
                            "wait_type": "element_visible",
                            "locator": {"type": "css", "value": ".welcome-message"},
                            "timeout": 10
                        }
                    }
                ],
                "priority": "P1",
                "timeout": 30,
                "retry_count": 2
            }
        }


class BrowserTestSuiteCreate(BaseModel):
    """浏览器测试套件创建模式"""
    name: str = Field(..., min_length=1, max_length=200, description="套件名称")
    description: Optional[str] = Field(None, description="套件描述")
    browser_type: str = Field("chrome", description="浏览器类型")
    browser_version: Optional[str] = Field(None, description="浏览器版本")
    headless: bool = Field(True, description="是否无头模式")
    window_size: str = Field("1920x1080", description="窗口大小")
    timeout: int = Field(30, ge=1, le=300, description="超时时间(秒)")
    retry_count: int = Field(0, ge=0, le=10, description="重试次数")
    parallel_execution: bool = Field(False, description="是否并行执行")
    max_parallel: int = Field(3, ge=1, le=10, description="最大并行数")
    environment: Optional[Dict[str, Any]] = Field(None, description="环境配置")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="浏览器能力配置")
    tags: Optional[str] = Field(None, description="标签")

    @validator('browser_type')
    def validate_browser_type(cls, v):
        if v not in ['chrome', 'firefox', 'edge', 'safari']:
            raise ValueError('浏览器类型必须是 chrome, firefox, edge, safari 之一')
        return v

    @validator('window_size')
    def validate_window_size(cls, v):
        try:
            width, height = v.split('x')
            if int(width) <= 0 or int(height) <= 0:
                raise ValueError('窗口尺寸必须大于0')
        except Exception:
            raise ValueError('窗口尺寸格式错误，应为 widthxheight')
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "用户登录测试套件",
                "description": "包含用户登录相关的所有测试用例",
                "browser_type": "chrome",
                "headless": True,
                "window_size": "1920x1080",
                "timeout": 30,
                "retry_count": 2,
                "parallel_execution": False,
                "tags": "login,authentication"
            }
        }


class BrowserTestExecutionRequest(BaseModel):
    """浏览器测试执行请求模式"""
    context: Optional[Dict[str, Any]] = Field(None, description="执行上下文")
    environment_id: Optional[int] = Field(None, description="环境ID")

    class Config:
        schema_extra = {
            "example": {
                "context": {
                    "username": "testuser",
                    "password": "password123"
                },
                "environment_id": 1
            }
        }


class BrowserTestStepAction(BaseModel):
    """浏览器测试步骤动作配置"""
    type: str = Field(..., description="动作类型")
    locator: Optional[Dict[str, str]] = Field(None, description="元素定位器")
    url: Optional[str] = Field(None, description="URL地址")
    text: Optional[str] = Field(None, description="输入文本")
    clear_first: Optional[bool] = Field(True, description="是否先清空")
    filename: Optional[str] = Field(None, description="文件名")
    script: Optional[str] = Field(None, description="JavaScript脚本")
    args: Optional[List[Any]] = Field(None, description="脚本参数")
    wait_type: Optional[str] = Field(None, description="等待类型")
    time: Optional[int] = Field(1, description="等待时间(秒)")
    duration: Optional[int] = Field(None, description="持续时间(秒)")
    frame_locator: Optional[Union[str, int, Dict[str, str]]] = Field(None, description="框架定位器")
    window_handle: Optional[str] = Field(None, description="窗口句柄")
    window_index: Optional[int] = Field(None, description="窗口索引")
    enabled: Optional[bool] = Field(None, description="是否启用")

    class Config:
        schema_extra = {
            "example": {
                "type": "click",
                "locator": {"type": "css", "value": ".submit-button"},
                "timeout": 10
            }
        }


class BrowserTestStepValidation(BaseModel):
    """浏览器测试步骤验证配置"""
    type: str = Field(..., description="验证类型")
    locator: Optional[Dict[str, str]] = Field(None, description="元素定位器")
    expected_value: Optional[str] = Field(None, description="期望值")
    attribute: Optional[str] = Field(None, description="属性名")
    operator: Optional[str] = Field("equals", description="操作符")
    enabled: bool = Field(True, description="是否启用")

    class Config:
        schema_extra = {
            "example": {
                "type": "element_exists",
                "locator": {"type": "css", "value": ".success-message"},
                "enabled": True
            }
        }


class BrowserTestStepScreenshot(BaseModel):
    """浏览器测试步骤截图配置"""
    enabled: bool = Field(False, description="是否启用截图")
    filename: Optional[str] = Field(None, description="文件名")
    on_success: bool = Field(True, description="成功时截图")
    on_failure: bool = Field(True, description="失败时截图")
    on_error: bool = Field(True, description="错误时截图")

    class Config:
        schema_extra = {
            "example": {
                "enabled": True,
                "filename": "step_screenshot.png",
                "on_success": True,
                "on_failure": True,
                "on_error": True
            }
        }


class BrowserTestStepResponse(BaseModel):
    """浏览器测试步骤响应"""
    step_number: int = Field(..., description="步骤序号")
    step_name: str = Field(..., description="步骤名称")
    step_type: str = Field(..., description="步骤类型")
    status: str = Field(..., description="执行状态")
    start_time: float = Field(..., description="开始时间戳")
    duration: float = Field(..., description="执行时长(秒)")
    error_message: Optional[str] = Field(None, description="错误信息")
    screenshot: Optional[str] = Field(None, description="截图文件路径")


class BrowserTestExecutionResult(BaseModel):
    """浏览器测试执行结果"""
    total_steps: int = Field(..., description="总步骤数")
    completed_steps: int = Field(..., description="完成步骤数")
    step_results: List[BrowserTestStepResponse] = Field(..., description="步骤结果列表")
    total_duration: float = Field(..., description="总执行时长(秒)")
    screenshots: List[str] = Field(default_factory=list, description="截图列表")
    logs: List[str] = Field(default_factory=list, description="执行日志")


class BrowserTestExecutionResponse(BaseModel):
    """浏览器测试执行响应"""
    execution_id: int = Field(..., description="执行ID")
    case_id: int = Field(..., description="用例ID")
    suite_id: int = Field(..., description="套件ID")
    status: str = Field(..., description="执行状态")
    result: Optional[BrowserTestExecutionResult] = Field(None, description="执行结果")
    logs: Optional[str] = Field(None, description="执行日志")
    error_message: Optional[str] = Field(None, description="错误信息")
    screenshots: Optional[List[str]] = Field(None, description="截图列表")
    duration: Optional[int] = Field(None, description="执行时长(毫秒)")
    steps_total: Optional[int] = Field(None, description="总步骤数")
    steps_passed: Optional[int] = Field(None, description="通过步骤数")
    steps_failed: Optional[int] = Field(None, description="失败步骤数")
    step_results: Optional[List[Dict]] = Field(None, description="步骤执行结果")
    browser_info: Optional[Dict[str, Any]] = Field(None, description="浏览器信息")
    environment_info: Optional[Dict[str, Any]] = Field(None, description="环境信息")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    executed_at: Optional[datetime] = Field(None, description="执行时间")
    finished_at: Optional[datetime] = Field(None, description="完成时间")


class BrowserTestSuiteResponse(BaseModel):
    """浏览器测试套件响应"""
    suite_id: int = Field(..., description="套件ID")
    name: str = Field(..., description="套件名称")
    description: Optional[str] = Field(None, description="套件描述")
    browser_type: str = Field(..., description="浏览器类型")
    browser_version: Optional[str] = Field(None, description="浏览器版本")
    headless: bool = Field(..., description="是否无头模式")
    window_size: str = Field(..., description="窗口大小")
    timeout: int = Field(..., description="超时时间(秒)")
    retry_count: int = Field(..., description="重试次数")
    parallel_execution: bool = Field(..., description="是否并行执行")
    max_parallel: int = Field(..., description="最大并行数")
    environment: Optional[Dict[str, Any]] = Field(None, description="环境配置")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="浏览器能力配置")
    status: str = Field(..., description="状态")
    tags: Optional[str] = Field(None, description="标签")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    statistics: Optional[Dict[str, Any]] = Field(None, description="统计信息")


class BrowserTestCaseResponse(BaseModel):
    """浏览器测试用例响应"""
    case_id: int = Field(..., description="用例ID")
    suite_id: int = Field(..., description="套件ID")
    name: str = Field(..., description="用例名称")
    description: Optional[str] = Field(None, description="用例描述")
    test_steps: List[Dict[str, Any]] = Field(..., description="测试步骤")
    test_data: Optional[Dict[str, Any]] = Field(None, description="测试数据")
    assertions: Optional[Dict[str, Any]] = Field(None, description="验证断言")
    priority: str = Field(..., description="优先级")
    status: str = Field(..., description="状态")
    tags: Optional[str] = Field(None, description="标签")
    test_steps_count: int = Field(..., description="测试步骤数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    execution_history: Optional[List[Dict]] = Field(None, description="执行历史")


class BrowserTestEnvironmentCreate(BaseModel):
    """浏览器测试环境创建模式"""
    name: str = Field(..., min_length=1, max_length=100, description="环境名称")
    description: Optional[str] = Field(None, description="环境描述")
    base_url: Optional[str] = Field(None, description="基础URL")
    proxy_config: Optional[Dict[str, Any]] = Field(None, description="代理配置")
    network_conditions: Optional[Dict[str, Any]] = Field(None, description="网络条件配置")
    browser_config: Optional[Dict[str, Any]] = Field(None, description="浏览器配置")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="特殊能力配置")
    test_data_config: Optional[Dict[str, Any]] = Field(None, description="测试数据配置")
    variables: Optional[Dict[str, Any]] = Field(None, description="环境变量")
    is_default: bool = Field(False, description="是否默认环境")

    class Config:
        schema_extra = {
            "example": {
                "name": "测试环境",
                "description": "用于功能测试的默认环境",
                "base_url": "https://test.example.com",
                "variables": {
                    "username": "testuser",
                    "password": "password123"
                }
            }
        }


class BrowserTestEnvironmentResponse(BaseModel):
    """浏览器测试环境响应"""
    env_id: int = Field(..., description="环境ID")
    name: str = Field(..., description="环境名称")
    description: Optional[str] = Field(None, description="环境描述")
    base_url: Optional[str] = Field(None, description="基础URL")
    proxy_config: Optional[Dict[str, Any]] = Field(None, description="代理配置")
    network_conditions: Optional[Dict[str, Any]] = Field(None, description="网络条件配置")
    browser_config: Optional[Dict[str, Any]] = Field(None, description="浏览器配置")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="特殊能力配置")
    test_data_config: Optional[Dict[str, Any]] = Field(None, description="测试数据配置")
    variables: Optional[Dict[str, Any]] = Field(None, description="环境变量")
    is_default: bool = Field(..., description="是否默认环境")
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class BrowserTestStepTemplate(BaseModel):
    """浏览器测试步骤模板"""
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    step_type: str = Field(..., description="步骤类型")
    action_template: Dict[str, Any] = Field(..., description="动作模板")
    validation_template: Optional[Dict[str, Any]] = Field(None, description="验证模板")
    category: str = Field("common", description="步骤分类")
    tags: List[str] = Field(default_factory=list, description="标签")

    class Config:
        schema_extra = {
            "example": {
                "name": "点击按钮",
                "description": "点击指定按钮",
                "step_type": "click",
                "action_template": {
                    "locator": {"type": "css", "value": "button"},
                    "timeout": 10
                },
                "validation_template": {
                    "type": "element_exists",
                    "locator": {"type": "css", "value": ".success-message"},
                    "enabled": True
                },
                "category": "common",
                "tags": ["click", "interaction"]
            }
        }
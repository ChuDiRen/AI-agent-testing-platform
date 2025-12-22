"""
用例生成相关的数据模型
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# ============== API 测试模型 ==============

class ApiAssert(BaseModel):
    """API 断言配置"""
    type: str = Field(..., description="断言类型: status_code/contains/equals/jsonpath/response_time/json_length")
    expected: Any = Field(default=None, description="期望值")
    value: Optional[str] = Field(default=None, description="比较值（用于 equals 类型）")
    jsonpath: Optional[str] = Field(default=None, description="JSONPath 表达式（用于 jsonpath 类型）")
    operator: Optional[str] = Field(default="==", description="比较运算符: ==/!=/>/</>=/<=/contains")
    max_ms: Optional[int] = Field(default=None, description="最大响应时间（毫秒）")


class ApiExtract(BaseModel):
    """API 数据提取配置"""
    name: str = Field(..., description="变量名")
    jsonpath: str = Field(..., description="JSONPath 表达式")
    index: int = Field(default=0, description="提取索引")


class GenerateApiCaseRequest(BaseModel):
    """生成 API 测试用例请求"""
    name: str = Field(..., description="用例名称")
    description: str = Field(..., description="用例描述")
    url: str = Field(..., description="请求 URL")
    method: str = Field(default="GET", description="HTTP 方法: GET/POST/PUT/DELETE/PATCH")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(default=None, description="URL 参数")
    data: Optional[Dict[str, Any]] = Field(default=None, description="表单数据")
    json_body: Optional[Dict[str, Any]] = Field(default=None, description="JSON 请求体")
    extracts: Optional[List[ApiExtract]] = Field(default=None, description="数据提取配置")
    asserts: Optional[List[ApiAssert]] = Field(default=None, description="断言配置")
    save_path: Optional[str] = Field(default=None, description="保存路径")
    format: str = Field(default="pytest", description="输出格式: yaml/pytest，默认 pytest")
    feature: str = Field(default="API测试", description="Allure feature 标签（pytest 格式用）")
    story: str = Field(default="接口测试", description="Allure story 标签（pytest 格式用）")


# ============== Web 测试模型 ==============

class WebAction(BaseModel):
    """Web 操作配置"""
    type: str = Field(..., description="操作类型: click/input/clear/select/hover/wait/scroll/screenshot/assert_text/assert_title/assert_url/assert_element")
    locator: Optional[str] = Field(default=None, description="元素定位器")
    locator_type: Optional[str] = Field(default="css", description="定位器类型: css/xpath/id/role")
    text: Optional[str] = Field(default=None, description="输入文本")
    expected: Optional[str] = Field(default=None, description="期望值（断言用）")
    value: Optional[str] = Field(default=None, description="选择值（select 用）")
    filename: Optional[str] = Field(default=None, description="截图文件名")
    seconds: Optional[int] = Field(default=None, description="等待秒数")
    direction: Optional[str] = Field(default=None, description="滚动方向: up/down")
    distance: Optional[int] = Field(default=None, description="滚动距离")
    match: Optional[str] = Field(default="contains", description="URL 匹配方式: contains/equals/startswith")
    visible: Optional[bool] = Field(default=True, description="元素是否可见")


class GenerateWebCaseRequest(BaseModel):
    """生成 Web 测试用例请求"""
    name: str = Field(..., description="用例名称")
    description: str = Field(..., description="用例描述")
    url: str = Field(..., description="目标 URL")
    browser: str = Field(default="chromium", description="浏览器: chromium/firefox/webkit")
    headless: bool = Field(default=True, description="无头模式")
    actions: Optional[List[WebAction]] = Field(default=None, description="操作列表")
    save_path: Optional[str] = Field(default=None, description="保存路径")
    format: str = Field(default="pytest", description="输出格式: yaml/pytest，默认 pytest")
    feature: str = Field(default="Web测试", description="Allure feature 标签（pytest 格式用）")
    story: str = Field(default="UI自动化", description="Allure story 标签（pytest 格式用）")


# ============== Mobile 测试模型 ==============

class MobileAction(BaseModel):
    """Mobile 操作配置"""
    type: str = Field(..., description="操作类型: click/input/clear/long_press/swipe/tap/wait/screenshot/back/home/assert_text/assert_element/assert_toast")
    locator: Optional[str] = Field(default=None, description="元素定位器")
    locator_type: Optional[str] = Field(default="id", description="定位器类型: id/xpath/accessibility_id/class_name")
    text: Optional[str] = Field(default=None, description="输入文本")
    expected: Optional[str] = Field(default=None, description="期望值")
    filename: Optional[str] = Field(default=None, description="截图文件名")
    seconds: Optional[int] = Field(default=None, description="等待秒数")
    duration: Optional[int] = Field(default=None, description="长按时长（秒）")
    direction: Optional[str] = Field(default=None, description="滑动方向: up/down/left/right")
    distance: Optional[int] = Field(default=None, description="滑动距离")
    x: Optional[int] = Field(default=None, description="点击 X 坐标")
    y: Optional[int] = Field(default=None, description="点击 Y 坐标")


class GenerateMobileCaseRequest(BaseModel):
    """生成 Mobile 测试用例请求"""
    name: str = Field(..., description="用例名称")
    description: str = Field(..., description="用例描述")
    platform: str = Field(default="android", description="平台: android/ios")
    app_package: Optional[str] = Field(default=None, description="Android 包名")
    app_activity: Optional[str] = Field(default=None, description="Android Activity")
    bundle_id: Optional[str] = Field(default=None, description="iOS Bundle ID")
    actions: Optional[List[MobileAction]] = Field(default=None, description="操作列表")
    save_path: Optional[str] = Field(default=None, description="保存路径")
    format: str = Field(default="pytest", description="输出格式: yaml/pytest，默认 pytest")
    feature: str = Field(default="Mobile测试", description="Allure feature 标签（pytest 格式用）")
    story: str = Field(default="APP自动化", description="Allure story 标签（pytest 格式用）")


# ============== Perf 测试模型 ==============

class PerfScenario(BaseModel):
    """性能测试场景配置"""
    method: str = Field(default="get", description="HTTP 方法: get/post/put/delete")
    url: str = Field(..., description="请求路径（相对于 host）")
    name: str = Field(..., description="请求名称（报告分组）")
    params: Optional[Dict[str, Any]] = Field(default=None, description="URL 参数")
    json_body: Optional[Dict[str, Any]] = Field(default=None, description="JSON 请求体", alias="json")
    data: Optional[Dict[str, Any]] = Field(default=None, description="表单数据")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")
    check_status: Optional[Dict[str, int]] = Field(default=None, description="状态码检查: {expected: 200}")
    check_response_time: Optional[Dict[str, int]] = Field(default=None, description="响应时间检查: {max_ms: 500}")
    check_contains: Optional[Dict[str, str]] = Field(default=None, description="响应内容检查: {text: 'success'}")
    validate_json: Optional[Dict[str, Any]] = Field(default=None, description="JSON 验证: {path: '$.code', expected: 0}")
    
    class Config:
        populate_by_name = True


class GeneratePerfCaseRequest(BaseModel):
    """生成性能测试用例请求"""
    name: str = Field(..., description="用例名称")
    description: str = Field(..., description="用例描述")
    host: str = Field(..., description="目标主机 URL，如 http://api.example.com")
    scenarios: List[PerfScenario] = Field(..., description="测试场景列表")
    users: int = Field(default=10, description="并发用户数")
    spawn_rate: float = Field(default=1, description="用户生成速率（每秒）")
    run_time: str = Field(default="60s", description="运行时长，如 60s/5m/1h")
    think_time: Optional[Dict[str, Any]] = Field(default=None, description="思考时间: {seconds: 1} 或 {min: 1, max: 3}")
    save_path: Optional[str] = Field(default=None, description="保存路径")
    format: str = Field(default="pytest", description="输出格式: yaml/pytest（生成 Locust 脚本），默认 pytest")


# ============== 通用模型 ==============

class GenerateFromYamlRequest(BaseModel):
    """从 YAML 创建用例请求"""
    yaml_content: str = Field(..., description="YAML 格式的用例内容")
    engine_type: str = Field(default="api", description="引擎类型: api/web/mobile/perf")
    save_path: Optional[str] = Field(default=None, description="保存路径")

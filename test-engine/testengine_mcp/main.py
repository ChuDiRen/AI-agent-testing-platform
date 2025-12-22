"""
Test Engine MCP Server
核心功能：生成 4 种测试用例 + 执行测试 + 精美报告

使用方法:
    cd test-engine
    python -m uvicorn testengine_mcp.main:app --reload --port 8100
    
MCP 端点:
    http://localhost:8100/mcp
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 导入 FastAPI-MCP
try:
    from fastapi_mcp import FastApiMCP
    HAS_FASTAPI_MCP = True
except ImportError:
    HAS_FASTAPI_MCP = False
    print("警告: fastapi-mcp 未安装，MCP 功能将不可用")
    print("请运行: pip install fastapi-mcp")

# 导入路由
from .routers import test_router, case_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("=" * 60)
    print("[*] Test Engine MCP Server 启动中...")
    print("=" * 60)
    yield
    print("Test Engine MCP Server 已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="Test Engine MCP",
    description="""
# 🧪 Test Engine MCP Server

统一的自动化测试引擎 MCP 服务，为 LLM 提供测试能力。

## 🎯 核心功能

### 1. 生成测试用例 (`/cases/generate`)

| 类型 | 端点 | 说明 |
|------|------|------|
| API | `/cases/generate/api` | HTTP 接口测试用例 |
| Web | `/cases/generate/web` | 浏览器自动化测试用例 |
| Mobile | `/cases/generate/mobile` | Android/iOS 测试用例 |
| Perf | `/cases/generate/perf` | 性能压测用例 |

### 2. 执行测试 (`/test`)

| 端点 | 说明 |
|------|------|
| `/test/api/quick` | 快速 API 测试（无需创建用例） |
| `/test/case/run` | 运行单个用例 |
| `/test/case/file` | 运行用例文件 |
| `/test/directory/run` | 运行整个目录 |
| `/test/batch/run` | 批量运行用例 |

### 3. 测试报告 (`/test/report`)

| 端点 | 说明 |
|------|------|
| `/test/reports` | 列出所有报告 |
| `/test/report` | 获取报告详情 |
| `/test/report/summary` | 获取报告摘要 |

## 📊 断言类型

### API 断言
- `status_code`: 状态码断言
- `contains`: 响应包含文本
- `equals`: 精确匹配
- `jsonpath`: JSON 路径断言
- `response_time`: 响应时间断言
- `json_length`: JSON 数组长度断言

### Web 断言
- `assert_text`: 页面文本断言
- `assert_title`: 页面标题断言
- `assert_url`: URL 断言
- `assert_element`: 元素存在断言
- `assert_element_text`: 元素文本断言

### Mobile 断言
- `assert_text`: 文本存在断言
- `assert_element`: 元素存在断言
- `assert_toast`: Toast 消息断言

### Perf 断言
- `check_status`: 状态码检查
- `check_response_time`: 响应时间检查
- `check_contains`: 响应内容检查
- `validate_json`: JSON 验证

## 🔧 测试引擎

| 引擎 | 技术栈 | 说明 |
|------|--------|------|
| API | httpx | 异步 HTTP 接口测试 |
| Web | Playwright | 浏览器自动化测试 |
| Mobile | Appium | Android/iOS 自动化测试 |
| Perf | Locust | 性能压力测试 |
""",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(case_router.router)
app.include_router(test_router.router)


# 根路由
@app.get("/", tags=["系统"])
async def root():
    """服务根路由"""
    return {
        "name": "Test Engine MCP Server",
        "version": "3.0.0",
        "description": "统一的自动化测试引擎 MCP 服务",
        "docs": "/docs",
        "mcp_endpoint": "/mcp" if HAS_FASTAPI_MCP else "未启用",
        "core_features": {
            "case_generation": {
                "description": "生成 4 种测试用例",
                "types": ["API", "Web", "Mobile", "Perf"],
                "endpoints": [
                    "POST /cases/generate/api",
                    "POST /cases/generate/web",
                    "POST /cases/generate/mobile",
                    "POST /cases/generate/perf"
                ]
            },
            "test_execution": {
                "description": "执行测试用例",
                "endpoints": [
                    "POST /test/api/quick - 快速API测试",
                    "POST /test/case/run - 运行用例",
                    "POST /test/directory/run - 运行目录"
                ]
            },
            "test_report": {
                "description": "精美测试报告",
                "endpoints": [
                    "GET /test/reports - 报告列表",
                    "GET /test/report - 报告详情",
                    "GET /test/report/summary - 报告摘要"
                ]
            }
        }
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "mcp_enabled": HAS_FASTAPI_MCP
    }


# 创建并挂载 MCP 服务器
if HAS_FASTAPI_MCP:
    mcp = FastApiMCP(
        app,
        name="test-engine-mcp",
        description="自动化测试引擎 MCP 服务：生成 API/Web/Mobile/Perf 测试用例，执行测试，生成精美报告"
    )
    
    # 挂载 MCP 服务器到 /mcp 路径
    mcp.mount()
    
    print("[OK] MCP 服务已启用，端点: /mcp")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "testengine_mcp.main:app",
        host="0.0.0.0",
        port=8100,
        reload=True
    )

# API 文档生成技能

## 触发条件
- 关键词：API 文档、接口文档、Swagger、OpenAPI、文档生成
- 场景：当用户需要生成或维护 API 文档时

## 核心规范

### 规范1：OpenAPI 规范结构

```yaml
openapi: 3.0.3
info:
  title: AI 测试平台 API
  description: AI 智能体测试平台接口文档
  version: 1.0.0
  contact:
    name: API Support
    email: support@example.com

servers:
  - url: http://localhost:8000/api/v1
    description: 开发环境
  - url: https://api.example.com/v1
    description: 生产环境

tags:
  - name: users
    description: 用户管理
  - name: tests
    description: 测试管理
```

### 规范2：接口定义规范

```yaml
paths:
  /users:
    get:
      tags:
        - users
      summary: 获取用户列表
      description: 分页获取系统中的用户列表
      operationId: listUsers
      parameters:
        - name: page
          in: query
          description: 页码
          required: false
          schema:
            type: integer
            default: 1
            minimum: 1
        - name: page_size
          in: query
          description: 每页数量
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
```

### 规范3：FastAPI 自动文档

```python
from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field

app = FastAPI(
    title="AI 测试平台 API",
    description="AI 智能体测试平台接口文档",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
    openapi_url="/openapi.json"
)

class UserCreate(BaseModel):
    """用户创建请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secret123"
            }
        }

@app.post(
    "/users",
    response_model=UserResponse,
    summary="创建用户",
    description="创建新用户账号，需要管理员权限",
    tags=["users"],
    responses={
        201: {"description": "创建成功"},
        400: {"description": "参数错误"},
        409: {"description": "用户已存在"}
    }
)
async def create_user(user: UserCreate):
    """
    创建新用户：
    
    - **username**: 用户名，3-50个字符
    - **email**: 有效的邮箱地址
    - **password**: 密码，至少6个字符
    """
    pass
```

### 规范4：响应模型定义

```python
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')

class ResponseBase(GenericModel, Generic[T]):
    """统一响应格式"""
    code: int = Field(0, description="状态码，0表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

class PaginatedResponse(GenericModel, Generic[T]):
    """分页响应格式"""
    code: int = 0
    message: str = "success"
    data: List[T] = []
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")

# 使用示例
class UserResponse(ResponseBase[User]):
    pass

class UserListResponse(PaginatedResponse[User]):
    pass
```

### 规范5：错误响应定义

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# 定义错误响应
class ErrorResponse(BaseModel):
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    details: Optional[dict] = Field(None, description="详细信息")

# 在 OpenAPI 中注册
responses = {
    400: {
        "description": "请求参数错误",
        "content": {
            "application/json": {
                "schema": ErrorResponse.schema(),
                "example": {
                    "code": 40001,
                    "message": "参数校验失败",
                    "details": {"field": "email", "error": "格式不正确"}
                }
            }
        }
    },
    401: {
        "description": "未授权",
        "content": {
            "application/json": {
                "example": {"code": 40101, "message": "Token 已过期"}
            }
        }
    },
    404: {
        "description": "资源不存在",
        "content": {
            "application/json": {
                "example": {"code": 40401, "message": "用户不存在"}
            }
        }
    }
}
```

### 规范6：文档注释规范

```python
@router.get("/tests/{test_id}/results")
async def get_test_results(
    test_id: int = Path(..., description="测试ID", ge=1),
    status: Optional[str] = Query(None, description="结果状态", enum=["pass", "fail", "skip"]),
    limit: int = Query(100, description="返回数量限制", ge=1, le=1000)
) -> TestResultsResponse:
    """
    获取测试执行结果
    
    ## 功能说明
    获取指定测试的执行结果列表，支持按状态筛选。
    
    ## 权限要求
    - 需要登录
    - 需要测试查看权限
    
    ## 返回说明
    - 返回按执行时间倒序排列的结果列表
    - 包含每个测试用例的执行状态、耗时、错误信息等
    
    ## 示例
    ```
    GET /api/v1/tests/123/results?status=fail&limit=50
    ```
    """
    pass
```

### 规范7：文档导出

```python
import json
import yaml

# 导出 OpenAPI JSON
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    return app.openapi()

# 导出 OpenAPI YAML
@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    openapi_schema = app.openapi()
    return Response(
        content=yaml.dump(openapi_schema, allow_unicode=True),
        media_type="application/x-yaml"
    )

# 命令行导出
# python -c "import json; from main import app; print(json.dumps(app.openapi(), indent=2))" > openapi.json
```

## 禁止事项
- ❌ 接口没有描述说明
- ❌ 参数缺少类型和约束
- ❌ 没有定义错误响应
- ❌ 示例数据不完整
- ❌ 文档与实际接口不一致

## 检查清单
- [ ] 所有接口是否有 summary 和 description
- [ ] 参数是否有完整的类型定义
- [ ] 是否定义了所有可能的响应状态
- [ ] 是否提供了请求/响应示例
- [ ] 文档是否与代码同步更新

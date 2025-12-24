# Claude Code 项目规范

## 项目概述

AI Agent Testing Platform - 接口自动化测试平台，支持 API 测试、AI 辅助测试用例生成。

## 技术栈

### 后端 (platform-fastapi-server)
- **语言**: Python 3.10+
- **框架**: FastAPI
- **数据库**: MySQL (PyMySQL + aiomysql)
- **ORM**: SQLModel
- **消息队列**: RabbitMQ / 内存队列
- **测试**: pytest + httpx

### 前端 (platform-vue-web)
- **框架**: Vue 3 + JavaScript (主体) + React (AI 对话组件)
- **UI 组件**: Element Plus
- **状态管理**: Vuex
- **构建工具**: Vite
- **样式**: TailwindCSS + WindiCSS

## 项目结构

```
AI-agent-testing-platform/
├── platform-fastapi-server/   # 后端服务 (端口 5000)
│   ├── apitest/               # API 测试模块
│   │   ├── api/               # Controller 层
│   │   ├── service/           # Service 层
│   │   ├── model/             # Model 层 (SQLModel)
│   │   └── schemas/           # Pydantic Schema
│   ├── sysmanage/             # 系统管理模块
│   ├── aiassistant/           # AI 助手模块
│   ├── msgmanage/             # 消息管理模块
│   ├── generator/             # 代码生成器
│   ├── core/                  # 核心组件
│   └── config/                # 配置文件
│
├── platform-vue-web/          # 前端应用 (端口 3000)
│   └── src/
│       ├── views/             # 页面组件
│       │   ├── apitest/       # API 测试模块
│       │   ├── system/        # 系统管理
│       │   └── aiassistant/   # AI 助手
│       ├── components/        # 公共组件
│       ├── composables/       # 组合式函数
│       ├── store/             # Vuex 状态管理
│       ├── router/            # 路由配置
│       └── agent-react/       # React AI 对话组件
│
├── test-engine/               # 测试引擎
├── api-engine/                # API 引擎
├── web-engine/                # Web 引擎
├── mobile-engine/             # 移动端引擎
└── perf-engine/               # 性能引擎
```

## 后端开发规范

### 三层架构
```
Controller (api/) → Service (service/) → Model (model/)
```

### Controller 规范
```python
# 文件命名: {Module}Controller.py
# 路由前缀: /{ModuleName}
module_route = APIRouter(prefix=f"/{module_name}", tags=["模块描述"])

# 标准接口命名
@module_route.post("/queryByPage")    # 分页查询
@module_route.get("/queryById")       # 按ID查询
@module_route.post("/insert")         # 新增
@module_route.put("/update")          # 更新
@module_route.delete("/delete")       # 删除
```

### Service 规范
```python
# 文件命名: {module}_service.py
class XxxService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page, page_size, **filters):
        pass
    
    def get_by_id(self, id):
        pass
    
    def create(self, **kwargs):
        pass
    
    def update(self, id, update_data):
        pass
    
    def delete(self, id):
        pass
```

### 响应格式
```python
from core.resp_model import respModel

# 成功响应
return respModel.ok_resp(obj=data)
return respModel.ok_resp_list(lst=datas, total=total)
return respModel.ok_resp_text(msg="操作成功")

# 错误响应
return respModel.error_resp("错误信息")
```

## 前端开发规范

### 文件结构
```
views/{module}/
├── {Module}List.vue          # 列表页
├── {Module}Form.vue          # 表单弹窗
├── {module}.js               # API 接口定义
└── components/               # 模块私有组件
```

### API 接口定义
```javascript
// {module}.js
import axios from '@/axios'

export function queryByPage(data) {
  return axios.post(`/api/{Module}/queryByPage`, data)
}

export function queryById(id) {
  return axios.get(`/api/{Module}/queryById`, { params: { id } })
}

export function insert(data) {
  return axios.post(`/api/{Module}/insert`, data)
}

export function update(data) {
  return axios.put(`/api/{Module}/update`, data)
}

export function deleteById(id) {
  return axios.delete(`/api/{Module}/delete`, { params: { id } })
}
```

### 组件规范
- 使用 `<script setup>` 语法
- 使用 Element Plus 组件
- 使用 Composables 封装可复用逻辑

## 快捷命令

| 命令 | 说明 |
|------|------|
| /dev | 智能开发流程（需求→设计→开发→测试） |
| /crud | 一键生成 CRUD 代码 |
| /check | 全栈代码规范检查 |
| /api-doc | 生成 API 文档 |
| /test | 生成测试用例 |

## 可用技能（24个）

### 后端开发
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| crud-development | CRUD、增删改查、业务模块 | 四层架构 CRUD 开发规范 |
| api-development | API、接口、FastAPI、路由 | RESTful API 设计规范 |
| database-ops | 数据库、SQL、建表、字典 | 数据库操作、建表、字典 |
| backend-annotations | 注解、装饰器、Depends | 注解使用规范 |
| error-handler | 异常、错误、Exception | 异常处理规范 |

### 前端开发
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| ui-pc | PC端、Element Plus、表格、表单 | Element Plus 封装组件使用 |
| store-pc | Vuex、Pinia、状态管理 | Pinia 状态管理 |

### 移动端
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| ui-mobile | 移动端、H5、小程序、Vant | WD UI 组件库 |
| ui-design-mobile | 移动端设计、rem、vw | 移动端设计规范 |
| store-mobile | 移动端状态、uni-app store | 移动端状态管理 |
| uniapp-platform | uni-app、条件编译、跨平台 | 跨平台条件编译 |

### 业务集成
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| payment-integration | 支付、微信支付、支付宝 | 支付功能集成 |
| wechat-integration | 微信、公众号、JSSDK | 微信生态集成 |
| file-oss-management | 文件上传、OSS、对象存储 | 文件上传与 OSS |
| ai-langchain4j | AI、大模型、LLM、LangChain | AI 大模型集成 |

### 质量保障
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| bug-detective | Bug、排查、调试 | Bug 排查 |
| performance-doctor | 性能、优化、缓存 | 性能优化 |
| security-guard | 安全、XSS、SQL注入 | 安全防护 |
| code-patterns | 设计模式、代码规范 | 代码规范 |

### 工程管理
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| architecture-design | 架构、分层、模块化 | 架构设计 |
| project-navigator | 项目结构、目录、文件在哪 | 项目结构导航 |
| git-workflow | Git、分支、提交、PR | Git 工作流 |
| tech-decision | 技术选型、对比、推荐 | 技术选型 |
| brainstorm | 头脑风暴、想法、方案 | 头脑风暴 |

## 注意事项

1. **代码复用**: 开发前先检查 `apitest/service/` 是否有可复用的 Service
2. **权限控制**: 接口需要添加 `dependencies=[Depends(check_permission("xxx:xxx:xxx"))]`
3. **日志记录**: 使用 `from core.logger import get_logger` 记录日志
4. **错误处理**: 所有接口需要 try-except 包裹，使用 `respModel` 返回
5. **数据库会话**: 使用 `session: Session = Depends(get_session)` 注入

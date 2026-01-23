# Claude Code 项目规范

## 项目概述

AI Agent Testing Platform - 接口自动化测试平台，支持 API 测试、AI 辅助测试用例生成。

---

## 🧩 五大套件速查

### 套件关系图
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            🧩 Plugins（打包分发层）                          │
│         把 Commands + Skills + SubAgents + MCP 打包成可分享的工具箱           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────────────┐
│ 📋 Commands       │   │ 📚 Skills         │   │ 🤖 SubAgents              │
│ 手动触发的工作流   │   │ 自动应用的知识    │   │ 独立上下文的专业助手       │
│ /dev /crud /check │   │ 关键词自动激活    │   │ /agent <name> 调用        │
└───────────────────┘   └───────────────────┘   └───────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          🔌 MCP（外部连接层）                                │
│                   连接 GitHub、数据库、文件系统等外部资源                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 快速决策表
| 我想... | 用... | 示例 |
|---------|-------|------|
| 手动触发某个流程 | Commands | `/check --scope backend` |
| 自动应用某类知识 | Skills | 写Python时自动检查规范 |
| 访问外部数据 | MCP | 读GitHub Issues、查数据库 |
| 深度专业分析 | SubAgents | `/agent security-auditor` |
| 打包分享给团队 | Plugins | 安装 code-review 插件 |

---

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

### 四层架构
```
Controller (api/) → Service (service/) → Model (model/) → Schema (schemas/)
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

### Schema 规范
```python
# 文件命名: {ModuleName}Schema.py
# 用于定义 Pydantic 模型和请求/响应 Schema
class UserCreate(BaseModel):
    username: str
    password: str
```

### Service 规范
```python
# 文件命名: {module}Service.py
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

## 快捷命令 (Commands)

### 开发命令
| 命令 | 说明 | 示例 |
|------|------|------|
| /dev | 智能开发流程（需求→设计→开发→测试） | `/dev 用户登录功能` |
| /crud | 一键生成 CRUD 代码 | `/crud user --fields "name:string:用户名"` |
| /api-doc | 生成 API 文档 | `/api-doc --module user` |
| /test | 生成测试用例 | `/test user_service.py --type unit` |

### 质量命令
| 命令 | 说明 | 示例 |
|------|------|------|
| /check | 全栈代码规范检查 | `/check --scope backend --fix` |
| /review | 智能代码审查 | `/review --mode full --agent` |
| /perf | 性能分析与优化 | `/perf --scope database` |
| /security | 安全漏洞扫描 | `/security --scope all` |
| /debug | 问题排查辅助 | `/debug 接口返回500错误` |

### SubAgent 命令
| 命令 | 说明 | 示例 |
|------|------|------|
| /agent | 调用专业 SubAgent | `/agent security-auditor 审查认证模块` |

### 重构命令
| 命令 | 说明 | 示例 |
|------|------|------|
| /backend-refactor | 后端代码重构 | `/backend-refactor --module apitest` |
| /frontend-refactor | 前端代码重构 | `/frontend-refactor --module user` |

### 运维命令
| 命令 | 说明 | 示例 |
|------|------|------|
| /db | 数据库设计与操作 | `/db design user --fields "..."` |
| /deploy | 部署配置生成 | `/deploy docker` |

## SubAgents (13个)

独立上下文的专业助手，适合深度分析任务。

### agents/ 目录 (7个)
| Agent | 说明 | 适用场景 |
|-------|------|----------|
| database-architect | 数据库架构师 | 表设计、SQL 优化 |
| test-engineer | 测试工程师 | 测试用例设计 |
| api-documenter | API 文档专家 | 接口文档生成 |
| prompt-engineer | 提示词工程师 | Prompt 优化 |
| ai-engineer | AI 工程师 | AI 功能开发 |
| python-pro | Python 专家 | Python 高级开发 |
| project-manager | 项目管理 | 项目规划协调 |

### plugins/ 目录 (6个)
| Agent | 所属插件 | 适用场景 |
|-------|----------|----------|
| code-reviewer | code-quality | 代码质量审查 |
| security-auditor | security | 安全漏洞扫描 |
| debugger | debugger | Bug 排查定位 |
| frontend-developer | fullstack | UI 组件开发 |
| backend-architect | fullstack | API 设计、架构 |

**使用方式**: `/agent <agent名称> <任务描述>`

## MCP 外部连接 (10个)

| MCP Server | 说明 | 用途 |
|------------|------|------|
| mysql | MySQL 数据库 | 执行 SQL、查看表结构 |
| postgresql | PostgreSQL 数据库 | 数据库操作 |
| github | GitHub | 读取 Issues、PR |
| filesystem | 文件系统 | 读写项目文件 |
| memory | 知识图谱 | 存储分析结果 |
| fetch | 网络请求 | 调用外部 API |
| sequential-thinking | 顺序思考 | 复杂问题推理 |
| brave-search | 网络搜索 | 搜索技术文档 |
| puppeteer | 浏览器自动化 | 网页截图、测试 |
| sqlite | SQLite | 本地数据存储 |

**配置文件**: `.claude/mcp.json`

## 可用技能（27个）

> 注：部分 Skill 已整合到 `plugins/` 目录，详见 `plugins/README.md`

### 后端开发 (5个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| api-development | API、接口、FastAPI、路由 | RESTful API 设计规范 |
| api-documentation | API文档、Swagger、OpenAPI | API 文档生成 |
| database-design | 数据库、SQL、建表、字典 | 数据库设计与操作 |
| backend-annotations | 注解、装饰器、Depends | 注解使用规范 |
| error-handler | 异常、错误、Exception | 异常处理规范 |

### 前端开发 (2个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| store-management | Vuex、Pinia、状态管理 | 状态管理规范 |
| prototype-design | 原型、UI设计、界面设计 | 原型设计规范 |

### 移动端 (3个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| ui-mobile | 移动端、H5、小程序、Vant | 移动端 UI 组件 |
| store-mobile | 移动端状态、uni-app store | 移动端状态管理 |
| uniapp-platform | uni-app、条件编译、跨平台 | 跨平台条件编译 |

### 业务集成 (4个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| payment-integration | 支付、微信支付、支付宝 | 支付功能集成 |
| wechat-integration | 微信、公众号、JSSDK | 微信生态集成 |
| file-oss-management | 文件上传、OSS、对象存储 | 文件上传与 OSS |
| ai-langchain4j | AI、大模型、LLM、LangChain | AI 大模型集成 |

### AI 开发 (2个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| ai-agent | Agent、智能体、AI Agent | AI Agent 开发 |
| ai-prompt | Prompt、提示词、提示工程 | 提示词工程 |

### 质量保障 (1个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| code-patterns | 设计模式、代码规范 | 代码规范 |

> 注：bug-detective、performance、security-guard、code-review 已整合到 `plugins/`

### 测试 (3个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| api-testing | 接口测试、API测试、pytest | API 自动化测试 |
| unit-testing | 单元测试、unittest、mock | 单元测试规范 |
| webapp-testing | Web测试、E2E、Playwright | 端到端测试 |

### 工程管理 (6个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| architecture-design | 架构、分层、模块化 | 架构设计 |
| project-navigator | 项目结构、目录、文件在哪 | 项目结构导航 |
| git-workflow | Git、分支、提交、PR | Git 工作流 |
| tech-decision | 技术选型、对比、推荐 | 技术选型 |
| brainstorm | 头脑风暴、想法、方案 | 头脑风暴 |
| task-splitting | 任务拆分、需求拆分 | 任务分解 |

### DevOps (3个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| ci-cd | CI/CD、持续集成、GitHub Actions | 持续集成部署 |
| docker-deploy | Docker、容器、部署 | 容器化部署 |
| logging-monitor | 日志、监控、告警 | 日志监控 |

### 工具 (1个)
| 技能 | 触发关键词 | 说明 |
|------|-----------|------|
| skill-creator | 创建技能、新技能 | 技能开发工具 |

### 插件内 Skills (6个)
| 技能 | 所属插件 | 说明 |
|------|----------|------|
| crud-development | fullstack | CRUD 开发规范 |
| ui-pc | fullstack | Element Plus 组件 |
| code-review | code-quality | 代码评审 |
| bug-detective | debugger | Bug 排查 |
| performance | debugger | 性能优化 |
| security-guard | security | 安全防护 |

## 搜索工具使用指南

### 代码搜索工具

#### 使用规则
1. 搜索代码时，**优先使用** `grep_search` 工具
2. 该工具提供强大的文本搜索功能
3. 适用于：查找相关代码、理解代码结构、搜索特定功能实现

#### 调用示例
```
使用 grep_search 搜索 [你的查询]
```

## 注意事项

1. **代码复用**: 开发前先检查 `apitest/service/` 是否有可复用的 Service
2. **权限控制**: 接口需要添加 `dependencies=[Depends(check_permission("xxx:xxx:xxx"))]`
3. **日志记录**: 使用 `from core.logger import get_logger` 记录日志
4. **错误处理**: 所有接口需要 try-except 包裹，使用 `respModel` 返回
5. **数据库会话**: 使用 `session: Session = Depends(get_session)` 注入

# 项目结构导航技能

## 触发条件
- 关键词：项目结构、目录、文件在哪、代码在哪、架构
- 场景：当用户需要了解项目结构或查找代码位置时

## 核心规范

### 规范1：项目整体结构

```
AI-agent-testing-platform/
├── platform-fastapi-server/    # 后端服务 (FastAPI)
├── platform-vue-web/           # 前端应用 (Vue 3)
├── test-engine/                # 测试引擎
├── api-engine/                 # API 引擎
├── web-engine/                 # Web 引擎
├── mobile-engine/              # 移动端引擎
├── perf-engine/                # 性能引擎
├── .claude/                    # Claude 配置
└── openspec/                   # 规范文档
```

### 规范2：后端项目结构 (platform-fastapi-server)

```
platform-fastapi-server/
├── app.py                      # 应用入口，路由注册
├── run.py                      # 启动脚本
├── requirements.txt            # Python 依赖
├── config/                     # 配置文件
│   ├── dev_settings.py         # 开发环境配置
│   ├── prod_settings.py        # 生产环境配置
│   └── test_settings.py        # 测试环境配置
├── core/                       # 核心模块
│   ├── database.py             # 数据库连接
│   ├── dependencies.py         # 依赖注入（权限校验等）
│   ├── exceptions.py           # 异常类定义
│   ├── resp_model.py           # 统一响应模型
│   ├── logger.py               # 日志配置
│   ├── minio_client.py         # MinIO 客户端
│   ├── MinioUtils.py           # MinIO 工具类
│   ├── FileService.py          # 文件服务
│   ├── AiStreamService.py      # AI 流式服务
│   ├── WebSocketManager.py     # WebSocket 管理
│   └── ...
├── {module}/                   # 业务模块（如 apitest, login, sysmanage）
│   ├── __init__.py
│   ├── api/                    # Controller 层
│   │   └── {Module}Controller.py
│   ├── model/                  # Model 层
│   │   └── {Module}Model.py
│   ├── schemas/                # 请求/响应模式
│   │   └── {module}_schema.py
│   └── service/                # Service 层
│       └── {module}_service.py
├── agent_langgraph/            # LangGraph AI 代理
├── scripts/                    # 脚本工具
└── tests/                      # 测试用例
```

### 规范3：前端项目结构 (platform-vue-web)

```
platform-vue-web/
├── index.html                  # 入口 HTML
├── vite.config.js              # Vite 配置
├── package.json                # 依赖配置
├── tailwind.config.js          # Tailwind 配置
├── src/
│   ├── main.js                 # 应用入口
│   ├── App.vue                 # 根组件
│   ├── axios.js                # Axios 封装
│   ├── router/                 # 路由配置
│   │   └── index.js
│   ├── store/                  # Vuex 状态管理
│   │   └── index.js
│   ├── views/                  # 页面组件
│   │   ├── apitest/            # API 测试模块
│   │   ├── login/              # 登录模块
│   │   ├── system/             # 系统管理模块
│   │   └── ...
│   ├── components/             # 公共组件
│   │   ├── BaseForm/
│   │   ├── BaseTable/
│   │   └── ...
│   ├── composables/            # 组合式函数
│   ├── directives/             # 自定义指令
│   ├── styles/                 # 样式文件
│   └── utils/                  # 工具函数
```

### 规范4：模块文件对应关系

| 功能 | 后端文件 | 前端文件 |
|------|---------|---------|
| API 接口管理 | `apitest/api/ApiInfoController.py` | `views/apitest/apiinfo/` |
| 测试用例 | `apitest/api/ApiInfoCaseController.py` | `views/apitest/apiinfocase/` |
| 测试任务 | `apitest/api/TestTaskController.py` | `views/apitest/task/` |
| 用户管理 | `sysmanage/api/UserController.py` | `views/system/user/` |
| 角色管理 | `sysmanage/api/RoleController.py` | `views/system/role/` |
| 菜单管理 | `sysmanage/api/MenuController.py` | `views/system/menu/` |

### 规范5：快速定位指南

| 要找什么 | 去哪里找 |
|---------|---------|
| 数据库配置 | `config/dev_settings.py` |
| 统一响应格式 | `core/resp_model.py` |
| 权限校验 | `core/dependencies.py` |
| 异常处理 | `core/exceptions.py` |
| 路由注册 | `app.py` |
| 前端路由 | `src/router/index.js` |
| 全局状态 | `src/store/index.js` |
| API 封装 | `src/views/{module}/{module}.js` |
| 公共样式 | `src/styles/` |

### 规范6：新增模块检查清单

**后端：**
- [ ] `{module}/__init__.py` - 模块初始化
- [ ] `{module}/api/{Module}Controller.py` - 控制器
- [ ] `{module}/model/{Module}Model.py` - 数据模型
- [ ] `{module}/schemas/{module}_schema.py` - 请求模式
- [ ] `{module}/service/{module}_service.py` - 业务服务
- [ ] `app.py` - 注册路由

**前端：**
- [ ] `views/{module}/{Module}List.vue` - 列表页
- [ ] `views/{module}/{Module}Form.vue` - 表单弹窗
- [ ] `views/{module}/{module}.js` - API 定义
- [ ] `router/index.js` - 注册路由

## 常见问题

**Q: 新增一个业务模块需要创建哪些文件？**
A: 后端 4 个文件（Controller、Model、Schema、Service），前端 3 个文件（List、Form、API），加上路由注册。

**Q: 公共组件放在哪里？**
A: `src/components/` 目录下，按功能分子目录。

**Q: 如何添加新的 API 路由？**
A: 在 `app.py` 中使用 `app.include_router()` 注册。

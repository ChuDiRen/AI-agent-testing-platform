# AI Agent Testing Platform - FastAPI Backend

基于 FastAPI + SQLModel 的 AI 智能体测试平台后端服务

## 技术栈

- **Web框架**: FastAPI 0.104.1
- **ORM**: SQLModel 0.0.14
- **数据库**: MySQL / SQLite (可配置切换)
- **认证**: python-jose (JWT)
- **对象存储**: MinIO
- **配置管理**: Pydantic Settings

## 项目结构

```
platform-fastapi-server/
├── app.py                 # FastAPI应用入口
├── run.py                 # 启动脚本
├── requirements.txt       # 项目依赖
├── config/               # 配置文件
│   ├── dev_settings.py   # 开发环境配置
│   ├── test_settings.py  # 测试环境配置
│   └── prod_settings.py  # 生产环境配置
├── core/                 # 核心模块
│   ├── database.py       # 数据库连接和会话管理
│   ├── dependencies.py   # 依赖注入函数
│   ├── JwtUtil.py        # JWT工具类
│   ├── MinioUtils.py     # MinIO对象存储工具
│   ├── resp_model.py     # 统一响应模型
│   ├── AiStreamService.py      # AI流式调用服务
│   ├── ConversationService.py  # 对话上下文管理
│   ├── StreamTestCaseParser.py # 流式测试用例解析器
│   ├── PromptService.py        # 提示词渲染服务
│   ├── FileService.py          # 文件处理服务
│   └── init_ai_data.py         # AI数据初始化
├── login/                # 登录模块
│   └── api/
│       └── LoginController.py
├── sysmanage/            # 系统管理模块
│   ├── model/
│   │   ├── user.py       # 用户模型
│   │   ├── role.py       # 角色模型
│   │   ├── menu.py       # 菜单模型
│   │   └── dept.py       # 部门模型
│   └── api/
│       ├── UserController.py
│       ├── RoleController.py
│       ├── MenuController.py
│       └── DeptController.py
├── apitest/              # API测试模块
│   ├── model/            # 数据模型
│   │   ├── ApiProjectModel.py
│   │   ├── ApiDbBaseModel.py
│   │   ├── ApiKeyWordModel.py
│   │   ├── ApiMetaModel.py
│   │   ├── ApiInfoModel.py
│   │   └── ApiOperationTypeModel.py
│   └── api/              # 接口控制器
│       ├── ApiProjectContoller.py
│       ├── ApiDbBaseController.py
│       ├── ApiKeyWordController.py
│       ├── ApiMetaController.py
│       ├── ApiInfoController.py
│       └── ApiOperationTypeController.py
└── aiassistant/          # AI测试助手模块 ⭐新增
    ├── model/            # 数据模型
    │   ├── AiModel.py            # AI模型配置
    │   ├── PromptTemplate.py     # 提示词模板
    │   ├── AiConversation.py     # AI对话会话
    │   ├── AiMessage.py          # AI对话消息
    │   ├── AiGenerateHistory.py  # 生成历史记录
    │   └── TestCaseModel.py      # AI生成的测试用例
    ├── api/              # 接口控制器
    │   ├── AiModelController.py          # AI模型管理
    │   ├── PromptTemplateController.py   # 提示词模板管理
    │   ├── TestCaseController.py         # 测试用例管理
    │   └── AiConversationController.py   # AI对话接口（SSE流式）
    └── schemas/          # Schema定义
        ├── ai_model_schema.py
        ├── prompt_template_schema.py
        ├── test_case_schema.py
        ├── ai_conversation_schema.py
        └── ai_message_schema.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 数据库配置（支持MySQL和SQLite切换）

编辑 `config/dev_settings.py` 配置文件：

**使用SQLite（默认，开箱即用）**：
```python
DB_TYPE = "sqlite"  # 使用SQLite
SQLITE_DATABASE = "./data/ai_agent.db"  # SQLite数据库文件路径
```

**使用MySQL**：
```python
DB_TYPE = "mysql"  # 使用MySQL
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "platfrom_back"
```

### 其他配置

```python
# JWT密钥配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# MinIO配置
# 注意：9000是API端口（SDK连接），9001是控制台端口（浏览器访问）
MINIO_CLIENT_URL = "http://192.168.163.128:9000"
MINIO_ENDPOINT = "192.168.163.128:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "12345678"
MINIO_SECURE = False

# 关键字文件目录
KEY_WORDS_DIR = "./keywords"
```

### 环境切换

- **开发环境**: 使用 `config/dev_settings.py` (默认SQLite)
- **测试环境**: 使用 `config/test_settings.py` (默认SQLite)
- **生产环境**: 使用 `config/prod_settings.py` (默认MySQL)

## 启动应用

### 开发模式（热重载）

```bash
python run.py
```

或

```bash
python app.py
```

### 生产模式

```bash
uvicorn app:application --host 0.0.0.0 --port 8000 --workers 4
```

## API文档

启动应用后访问：

- **交互式文档 (Swagger UI)**: http://localhost:8000/docs
- **备选文档 (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 主要功能模块

### 1. 用户认证

- `POST /login` - 用户登录

### 2. AI测试助手模块 ⭐新增

完整的AI驱动测试用例生成系统，支持ChatGPT风格的对话式交互。

#### 2.1 AI模型管理

- `GET /AiModel/queryByPage` - 分页查询AI模型
- `GET /AiModel/queryById/{id}` - 根据ID查询AI模型
- `POST /AiModel/insert` - 新增AI模型
- `PUT /AiModel/update` - 更新AI模型
- `DELETE /AiModel/delete/{id}` - 删除AI模型
- `PUT /AiModel/toggle/{id}` - 启用/禁用AI模型
- `POST /AiModel/test/{id}` - 测试AI模型连接

**AI模型配置字段**：
- `model_name`: 模型名称（如：DeepSeek-Chat）
- `model_code`: 模型代码（如：deepseek-chat）
- `provider`: 提供商（如：DeepSeek、阿里云）
- `api_url`: API接口地址
- `api_key`: API密钥
- `is_enabled`: 是否启用
- `description`: 模型描述

#### 2.2 提示词模板管理

- `GET /PromptTemplate/queryByPage` - 分页查询提示词模板
- `GET /PromptTemplate/queryById/{id}` - 根据ID查询模板
- `POST /PromptTemplate/insert` - 新增提示词模板
- `PUT /PromptTemplate/update` - 更新提示词模板
- `DELETE /PromptTemplate/delete/{id}` - 删除提示词模板
- `PUT /PromptTemplate/toggle/{id}` - 激活/停用模板
- `GET /PromptTemplate/by-test-type` - 按测试类型查询模板

**提示词模板字段**：
- `name`: 模板名称
- `template_type`: 模板类型（system/user/assistant）
- `test_type`: 测试类型（API/Web/App/通用）
- `content`: 模板内容（支持变量替换）
- `variables`: 模板变量（JSON格式）
- `is_active`: 是否激活

#### 2.3 测试用例管理

- `GET /TestCase/queryByPage` - 分页查询测试用例
- `GET /TestCase/queryById/{id}` - 根据ID查询测试用例
- `POST /TestCase/insert` - 新增测试用例
- `PUT /TestCase/update` - 更新测试用例
- `DELETE /TestCase/delete/{id}` - 删除测试用例
- `POST /TestCase/batch-insert` - 批量保存测试用例
- `GET /TestCase/export-yaml/{id}` - 导出单个用例为YAML
- `POST /TestCase/export-batch-yaml` - 批量导出用例为YAML

**测试用例字段**：
- `case_name`: 用例名称
- `test_type`: 测试类型（API/Web/App）
- `priority`: 优先级（P0/P1/P2/P3）
- `test_steps_json`: 测试步骤（JSON格式）
- `test_steps_yaml`: 测试步骤（YAML格式）
- `expected_result`: 预期结果
- `tags`: 标签
- `project_id`: 所属项目
- `conversation_id`: 来源对话会话

#### 2.4 AI对话接口（核心功能）

- `POST /AiConversation/create` - 创建新对话会话
- `GET /AiConversation/list` - 获取用户的对话列表
- `GET /AiConversation/detail/{id}` - 获取对话详情（包含消息历史）
- `POST /AiConversation/stream` - **流式对话接口（SSE）** ⭐核心
- `DELETE /AiConversation/delete/{id}` - 删除对话会话

**流式对话特性**：
- ✅ Server-Sent Events (SSE) 实时流式输出
- ✅ 支持多轮对话，自动管理上下文
- ✅ 实时解析AI输出中的JSON测试用例
- ✅ 支持文件上传（TXT/Word/PDF需求文档）
- ✅ 可配置AI模型和提示词模板
- ✅ 自动保存对话历史和生成的测试用例

**流式输出事件类型**：
- `message`: 普通文本消息
- `testcase`: 完整测试用例JSON
- `error`: 错误信息
- `done`: 生成完成

### 3. RBAC权限管理系统 🆕

#### 3.1 用户管理

- `POST /user/queryByPage` - 分页查询用户（支持按用户名、部门、状态过滤）
- `GET /user/queryById` - 根据ID查询用户
- `POST /user/insert` - 新增用户
- `PUT /user/update` - 更新用户
- `DELETE /user/delete` - 删除用户
- `POST /user/assignRoles` - 为用户分配角色 🆕
- `GET /user/roles/{user_id}` - 获取用户的角色 🆕
- `PUT /user/updateStatus` - 更新用户状态（锁定/启用）🆕

**用户字段说明**：
- `id`: 用户ID（主键）
- `username`: 用户名（唯一索引）
- `password`: 密码（加密存储）
- `dept_id`: 部门ID
- `email`: 邮箱
- `mobile`: 联系电话
- `status`: 状态（0锁定 1有效）
- `ssex`: 性别（0男 1女 2保密）
- `avatar`: 头像URL
- `description`: 描述
- `create_time`: 创建时间
- `modify_time`: 修改时间
- `last_login_time`: 最近访问时间

#### 3.2 角色管理 🆕

- `POST /role/queryByPage` - 分页查询角色
- `GET /role/queryById` - 根据ID查询角色
- `POST /role/insert` - 新增角色
- `PUT /role/update` - 更新角色
- `DELETE /role/delete` - 删除角色
- `POST /role/assignMenus` - 为角色分配菜单权限
- `GET /role/menus/{role_id}` - 获取角色的菜单权限

#### 3.3 菜单/权限管理 🆕

- `GET /menu/tree` - 获取菜单树
- `GET /menu/queryById` - 根据ID查询菜单
- `POST /menu/insert` - 新增菜单
- `PUT /menu/update` - 更新菜单
- `DELETE /menu/delete` - 删除菜单
- `GET /menu/user/{user_id}` - 获取用户的菜单权限（用于前端动态路由）

#### 3.4 部门管理 🆕

- `GET /dept/tree` - 获取部门树
- `GET /dept/queryById` - 根据ID查询部门
- `POST /dept/insert` - 新增部门
- `PUT /dept/update` - 更新部门
- `DELETE /dept/delete` - 删除部门

### 3. 初始数据 🆕

首次启动时，系统会自动初始化以下RBAC数据：

**默认账号**：
- 用户名：`admin`
- 密码：`admin123`
- 角色：超级管理员

**默认部门**：
- 总公司（顶级部门）
  - 技术部
  - 产品部
  - 运营部

**默认角色**：
- 超级管理员（拥有所有权限）
- 管理员（拥有部分管理权限）
- 普通用户（拥有基本权限）

**默认菜单**：
- 系统管理
  - 用户管理（含增删改查、分配角色按钮权限）
  - 角色管理（含增删改查、分配权限按钮权限）
  - 菜单管理（含增删改查按钮权限）
  - 部门管理（含增删改查按钮权限）
- API测试
  - 项目管理
  - 用例管理

### 4. API项目管理

- `POST /ApiProject/queryByPage` - 分页查询项目
- `GET /ApiProject/queryById` - 根据ID查询项目
- `GET /ApiProject/queryAll` - 查询所有项目
- `POST /ApiProject/insert` - 新增项目
- `PUT /ApiProject/update` - 更新项目
- `DELETE /ApiProject/delete` - 删除项目

### 5. API数据库配置管理

- `POST /ApiDbBase/queryByPage` - 分页查询数据库配置
- `GET /ApiDbBase/queryById` - 根据ID查询配置
- `POST /ApiDbBase/insert` - 新增配置（带唯一性校验）
- `PUT /ApiDbBase/update` - 更新配置
- `DELETE /ApiDbBase/delete` - 删除配置

### 6. API关键字管理

- `GET /ApiKeyWord/queryAll` - 查询所有关键字
- `POST /ApiKeyWord/queryByPage` - 分页查询关键字
- `GET /ApiKeyWord/queryById` - 根据ID查询关键字
- `POST /ApiKeyWord/insert` - 新增关键字（带唯一性校验）
- `PUT /ApiKeyWord/update` - 更新关键字（带唯一性校验）
- `DELETE /ApiKeyWord/delete` - 删除关键字
- `POST /ApiKeyWord/keywordFile` - 生成关键字文件

### 7. API元数据管理（文件管理）

- `GET /ApiMeta/queryAll` - 查询所有元数据
- `POST /ApiMeta/queryByPage` - 分页查询元数据
- `GET /ApiMeta/queryById` - 根据ID查询元数据
- `POST /ApiMeta/insert` - 上传文件并新增元数据
- `PUT /ApiMeta/update` - 更新元数据
- `DELETE /ApiMeta/delete` - 删除元数据
- `GET /ApiMeta/downloadFile` - 获取文件下载地址

### 8. 操作类型管理

- `GET /OperationType/queryAll` - 查询所有操作类型
- `POST /OperationType/queryByPage` - 分页查询操作类型
- `GET /OperationType/queryById` - 根据ID查询操作类型
- `POST /OperationType/insert` - 新增操作类型
- `PUT /OperationType/update` - 更新操作类型
- `DELETE /OperationType/delete` - 删除操作类型

### 9. AI测试助手 🆕🔥

#### 9.1 AI模型管理

- `GET /AiModel/list` - 获取AI模型列表（分页）
- `GET /AiModel/enabled` - 获取所有已启用的模型
- `GET /AiModel/{model_id}` - 获取单个AI模型详情
- `POST /AiModel/create` - 创建AI模型
- `PUT /AiModel/{model_id}` - 更新AI模型
- `DELETE /AiModel/{model_id}` - 删除AI模型
- `POST /AiModel/{model_id}/toggle` - 切换模型启用/禁用状态
- `POST /AiModel/{model_id}/test` - 测试模型API连接
- `GET /AiModel/providers/list` - 获取所有提供商列表

#### 9.2 提示词模板管理

- `GET /PromptTemplate/list` - 获取提示词模板列表（分页）
- `GET /PromptTemplate/by-type/{test_type}` - 按测试类型获取所有激活的模板
- `GET /PromptTemplate/{template_id}` - 获取单个提示词模板详情
- `POST /PromptTemplate/create` - 创建提示词模板
- `PUT /PromptTemplate/{template_id}` - 更新提示词模板
- `DELETE /PromptTemplate/{template_id}` - 删除提示词模板
- `POST /PromptTemplate/{template_id}/toggle` - 切换模板激活/停用状态

#### 9.3 测试用例管理

- `GET /TestCase/list` - 获取测试用例列表（分页）
- `GET /TestCase/{case_id}` - 获取单个测试用例详情
- `POST /TestCase/create` - 创建测试用例
- `POST /TestCase/batch-insert` - 批量插入测试用例
- `PUT /TestCase/{case_id}` - 更新测试用例
- `DELETE /TestCase/{case_id}` - 删除测试用例
- `GET /TestCase/{case_id}/export-yaml` - 导出单个测试用例为YAML格式
- `POST /TestCase/export-batch-yaml` - 批量导出测试用例为YAML格式

#### 9.4 AI对话接口（核心）

- `POST /chat` - 流式对话接口（SSE推送实时生成的内容）
- `POST /create` - 创建新对话
- `GET /list` - 获取用户对话列表
- `GET /{conversation_id}/messages` - 获取对话消息历史
- `DELETE /{conversation_id}` - 删除对话
- `PUT /{conversation_id}/title` - 更新对话标题

#### 特性说明

**🎯 完整的ChatGPT风格对话界面**：
- 实时流式输出（SSE技术）
- 消息气泡形式展示
- 测试用例卡片化显示
- 支持编辑、保存、复制操作

**🤖 多模型支持**：
- DeepSeek（推荐，高性价比）
- 通义千问（阿里云）
- ChatGPT-4/3.5（OpenAI）
- Kimi、智谱AI、文心一言、讯飞星火、Claude-3
- 支持自定义添加AI模型

**📝 可配置提示词**：
- 4种测试类型模板（API/Web/App/通用）
- 支持变量替换（`{case_count}`、`{test_type}`）
- 可自定义编辑提示词内容

**💬 多轮对话**：
- 会话自动保存
- 上下文记忆（最近10条消息）
- 支持追加需求、调整参数
- 会话管理（切换、重命名、删除）

**📂 文件上传**：
- 支持TXT/Word/PDF格式
- AI根据文档内容生成测试用例
- 自动提取文本内容

**⚡ 快捷命令**：
- `/generate N` - 生成N个测试用例
- `/format yaml` - 切换YAML格式
- `/save` - 保存当前所有用例
- `/clear` - 清空对话

**初始化数据**：
- 10个主流AI模型配置（需配置API Key）
- 4个提示词模板（开箱即用）
- AI功能菜单权限

详见: [QUICK_START_AI_TESTCASE.md](QUICK_START_AI_TESTCASE.md)

## 数据库迁移

首次启动时，应用会自动创建所有数据表。

## 环境变量

支持通过 `.env` 文件配置环境变量：

```env
# 数据库类型选择
DB_TYPE=sqlite

# SQLite配置（DB_TYPE=sqlite时使用）
SQLITE_DATABASE=./data/ai_agent.db

# MySQL配置（DB_TYPE=mysql时使用）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=platfrom_back

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# MinIO配置
# 注意：9000是API端口（SDK连接），9001是控制台端口（浏览器访问）
MINIO_ENDPOINT=192.168.163.128:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=12345678
MINIO_SECURE=False
```

## 技术特性

- ✅ 同步SQLModel，保持与原Flask代码接近
- ✅ 支持MySQL和SQLite数据库切换
- ✅ **完整RBAC权限管理系统** 🆕
  - 用户-角色-菜单权限模型
  - 部门管理（树形结构）
  - 菜单管理（支持菜单和按钮级权限）
  - 用户状态管理（启用/锁定）
  - 数据权限支持
  - **统一主键命名**（简洁高效）
    * 所有 RBAC 模型（User、Role、Menu、Dept）统一使用 `id` 作为主键
    * 简化前后端字段映射，提升开发效率
- ✅ 依赖注入（数据库会话、JWT认证、MinIO客户端）
- ✅ 统一响应格式
- ✅ 自动API文档生成
- ✅ 数据验证（Pydantic）
- ✅ 类型提示
- ✅ 文件上传下载
- ✅ JWT认证
- ✅ CORS支持
- ✅ 唯一性校验
- ✅ 自动初始化RBAC数据

## 开发规范

- 所有注释位于代码右侧，格式为 `# 注释`
- 使用类型注解
- 遵循PEP 8规范
- 保持代码简洁高效

## 版本信息

- **版本**: 2.0.0
- **框架**: FastAPI
- **ORM**: SQLModel
- **Python**: 3.8+

## 注意事项

1. **数据库选择**：
   - 开发/测试环境推荐使用SQLite（开箱即用，无需安装）
   - 生产环境推荐使用MySQL（性能更好，支持并发）
2. 使用MySQL时，确保MySQL数据库已启动并可访问
3. 确保MinIO服务已启动（如使用文件上传功能）
4. 生产环境请修改CORS配置，指定具体允许的域名
5. 生产环境请使用强密码和安全的SECRET_KEY
6. 建议使用虚拟环境进行开发

## 迁移说明

本项目已从 Flask + Flask-SQLAlchemy 迁移至 FastAPI + SQLModel：

- ✅ 保持原有功能不变
- ✅ 保持原有目录结构
- ✅ 保持原有API路径
- ✅ 保持原有响应格式
- ✅ 使用同步方式，降低迁移成本
- ✅ 所有业务逻辑保持一致


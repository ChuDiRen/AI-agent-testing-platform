# 单元测试覆盖率说明

## 测试文件列表

### 核心模块测试 (core)
- `test_core_utils.py` - 核心工具类测试
  - JwtUtils: Token创建、验证
  - TimeFormatter: 时间格式化
  - respModel: 响应模型
  - SwaggerParser: Swagger解析器
  - StreamTestCaseParser: 流式测试用例解析器
  - PromptService: 提示词服务
  - Exceptions: 异常处理

### 登录模块测试 (login)
- `test_login_controller.py` - 登录控制器测试
  - 登录成功/失败
  - 密码错误
  - 用户不存在

### 系统管理模块测试 (sysmanage)
- `test_user_controller.py` - 用户管理测试
  - 分页查询、ID查询
  - 新增、更新、删除用户
  - 角色分配、状态更新

- `test_role_controller.py` - 角色管理测试
  - 分页查询、ID查询
  - 新增、更新、删除角色
  - 菜单权限分配

- `test_menu_controller.py` - 菜单管理测试
  - 菜单树查询
  - 新增、更新、删除菜单
  - 用户菜单权限

- `test_dept_controller.py` - 部门管理测试
  - 部门树查询
  - 新增、更新、删除部门
  - 级联删除验证

### API测试模块测试 (apitest)
- `test_api_project_controller.py` - 项目管理测试
- `test_api_info_controller.py` - 接口信息测试
- `test_api_info_case_controller.py` - 测试用例测试
- `test_api_info_case_step_controller.py` - 测试步骤测试
- `test_api_collection_info_controller.py` - 接口集合测试
- `test_api_collection_detail_controller.py` - 集合详情测试
- `test_api_keyword_controller.py` - 关键字测试
- `test_api_meta_controller.py` - 元数据测试
- `test_api_operation_type_controller.py` - 操作类型测试
- `test_api_dbbase_controller.py` - 数据库配置测试
- `test_api_history_controller.py` - 历史记录测试
- `test_api_report_viewer_controller.py` - 报告查看测试
- `test_api_group_controller.py` - 接口分组测试

### 插件模块测试 (plugin)
- `test_plugin_controller.py` - 插件管理测试
  - 插件注册、查询、更新、删除
  - 插件启用/禁用
  - 健康检查
  - 执行器上传/安装

- `test_task_controller.py` - 任务调度测试
  - 执行器列表
  - 任务执行
  - 命令解析

### 消息管理模块测试 (msgmanage)
- `test_robot_config_controller.py` - 机器人配置测试
  - 分页查询、ID查询
  - 新增、更新、删除配置

- `test_robot_msg_config_controller.py` - 消息模板测试
  - 模板管理
  - 变量替换

### AI助手模块测试 (aiassistant)
- `test_ai_model_controller.py` - AI模型管理测试
  - 模型CRUD
  - 状态切换

- `test_ai_conversation_controller.py` - AI对话测试
  - 对话创建、列表、删除
  - 消息获取

- `test_prompt_template_controller.py` - 提示词模板测试
  - 模板CRUD
  - 按类型查询

- `test_test_case_controller.py` - 测试用例测试
  - 用例CRUD
  - 批量插入
  - YAML导出

### 代码生成器模块测试 (generator)
- `test_generator_controller.py` - 代码生成器测试
  - 代码预览、下载
  - 表配置管理
  - 数据库元数据服务

### 通用测试
- `test_models.py` - 数据模型测试
  - 所有SQLModel模型的创建和默认值

- `test_schemas.py` - Schema验证测试
  - 所有Pydantic Schema的验证

- `test_integration.py` - 集成测试
  - 用户角色工作流
  - API测试工作流
  - 插件执行器工作流
  - AI助手工作流
  - 机器人消息工作流

## 运行测试

```bash
# 进入测试目录
cd platform-fastapi-server

# 运行所有测试
python tests/run_tests.py

# 运行测试并生成覆盖率报告
python tests/run_tests.py --coverage

# 运行特定模块测试
python tests/run_tests.py --module core
python tests/run_tests.py --module user
python tests/run_tests.py --module plugin

# 运行特定测试文件
python tests/run_tests.py --file test_login_controller.py

# 直接使用pytest
pytest tests/ -v
pytest tests/test_core_utils.py -v
pytest tests/ -v --cov=. --cov-report=html
```

## 测试覆盖的功能模块

| 模块 | 控制器 | 测试文件 | 覆盖功能 |
|------|--------|----------|----------|
| 登录 | LoginController | test_login_controller.py | 登录验证 |
| 用户 | UserController | test_user_controller.py | CRUD、角色分配 |
| 角色 | RoleController | test_role_controller.py | CRUD、菜单分配 |
| 菜单 | MenuController | test_menu_controller.py | CRUD、树形结构 |
| 部门 | DeptController | test_dept_controller.py | CRUD、树形结构 |
| 项目 | ApiProjectController | test_api_project_controller.py | CRUD |
| 接口 | ApiInfoController | test_api_info_controller.py | CRUD |
| 用例 | ApiInfoCaseController | test_api_info_case_controller.py | CRUD |
| 步骤 | ApiInfoCaseStepController | test_api_info_case_step_controller.py | CRUD |
| 集合 | ApiCollectionInfoController | test_api_collection_info_controller.py | CRUD |
| 关键字 | ApiKeyWordController | test_api_keyword_controller.py | CRUD |
| 元数据 | ApiMetaController | test_api_meta_controller.py | CRUD |
| 操作类型 | ApiOperationTypeController | test_api_operation_type_controller.py | CRUD |
| 数据库 | ApiDbBaseController | test_api_dbbase_controller.py | CRUD |
| 历史 | ApiHistoryController | test_api_history_controller.py | CRUD |
| 插件 | PluginController | test_plugin_controller.py | 注册、管理、健康检查 |
| 任务 | TaskController | test_task_controller.py | 执行器列表、任务执行 |
| 机器人 | RobotConfigController | test_robot_config_controller.py | CRUD |
| 消息模板 | RobotMsgConfigController | test_robot_msg_config_controller.py | CRUD、变量替换 |
| AI模型 | AiModelController | test_ai_model_controller.py | CRUD、状态切换 |
| AI对话 | AiConversationController | test_ai_conversation_controller.py | 对话管理 |
| 提示词 | PromptTemplateController | test_prompt_template_controller.py | CRUD |
| 测试用例 | TestCaseController | test_test_case_controller.py | CRUD、导出 |
| 代码生成 | GeneratorController | test_generator_controller.py | 预览、下载 |
| 表配置 | GenTableController | test_generator_controller.py | CRUD |

## 测试标记

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.api` - API测试
- `@pytest.mark.database` - 数据库测试
- `@pytest.mark.slow` - 慢速测试

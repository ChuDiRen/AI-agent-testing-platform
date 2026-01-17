# 数据库初始化脚本
# 功能：使用 SQLAlchemy ORM 自动创建表结构 + 初始化默认用户数据

from datetime import datetime
import bcrypt


def _import_all_models():
    """导入所有模型类，确保 SQLAlchemy 能识别所有表"""
    # login 模块
    from login.model.UserModel import User
    # sysmanage 模块 - RBAC权限模型
    from sysmanage.model.RoleModel import Role
    from sysmanage.model.ApiModel import Api
    from sysmanage.model.MenuModel import Menu
    from sysmanage.model.DeptModel import Dept
    from sysmanage.model.DeptClosureModel import DeptClosure
    from sysmanage.model.AuditLogModel import AuditLog
    from sysmanage.model.UserRoleModel import UserRole
    from sysmanage.model.RoleMenuModel import RoleMenu
    from sysmanage.model.RoleApiModel import RoleApi
    from sysmanage.model.HistoryInfoModel import HistoryInfo
    # apitest 模块
    from apitest.model.ApiProjectModel import ApiProject
    from apitest.model.ApiInfoModel import ApiInfo
    from apitest.model.ApiMetaModel import ApiMeta
    from apitest.model.ApiDbBaseModel import ApiDbBase
    from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
    from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
    from apitest.model.ApiHistoryModel import ApiHistoryModel
    from apitest.model.ApiInfoCaseModel import ApiInfoCase
    from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
    from apitest.model.ApiKeyWordModel import ApiKeyWord
    from apitest.model.ApiOperationTypeModel import OperationType
    # msgmanage 模块
    from msgmanage.model.RobotConfigModel import RobotConfig
    from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig

    # 初始化关联关系（在所有模型导入后）
    from sysmanage.model.relationships import init_relationships
    init_relationships()

    return [User, Role, Api, Menu, Dept, DeptClosure, AuditLog,
            UserRole, RoleMenu, RoleApi, HistoryInfo,
            ApiProject, ApiInfo, ApiMeta, ApiDbBase,
            ApiCollectionInfo, ApiCollectionDetail, ApiHistoryModel,
            ApiInfoCase, ApiInfoCaseStep, ApiKeyWord, OperationType,
            RobotConfig, RobotMsgConfig]


def init_database(app, database):
    """
    初始化数据库：使用 ORM 自动创建表结构和默认数据

    Args:
        app: Flask 应用实例
        database: SQLAlchemy 数据库实例
    """
    with app.app_context():
        print("=" * 60)
        print("🔧 开始初始化数据库...")
        print("=" * 60)

        # 1. 导入所有模型
        print("✓ 正在加载所有模型...")
        models = _import_all_models()
        print(f"✓ 已加载 {len(models)} 个模型")

        # 2. 使用 ORM 自动创建所有表（如果不存在）
        print("✓ 正在创建数据库表...")
        database.create_all()
        database.session.commit()
        print("✓ 数据库表创建/同步完成")

        # 3. 初始化默认数据
        _init_default_data(database)

        print("=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)


def _init_default_data(database):
    """
    初始化默认数据

    Args:
        database: SQLAlchemy 数据库实例
    """
    # 初始化默认管理员用户
    _init_default_user(database)

    # 初始化 RBAC 权限数据
    _init_rbac_data(database)

    # 初始化操作类型
    _init_operation_types(database)

    # 初始化关键字
    _init_keywords(database)


def _init_default_user(database):
    """
    初始化默认管理员用户

    Args:
        database: SQLAlchemy 数据库实例
    """
    from login.model.UserModel import User

    try:
        # 检查是否已存在管理员用户
        admin_exists = database.session.query(User).filter_by(username='admin').first()

        if admin_exists:
            print("✓ 管理员用户已存在，跳过创建")
            return
    except Exception:
        # 表不存在时会抛出异常，继续创建用户
        pass

    # 创建默认管理员用户
    print("✓ 正在创建默认管理员用户...")

    admin_user = User()
    admin_user.username = "admin"
    admin_user.password = admin_user.set_password("admin123456")
    admin_user.create_time = datetime.now()

    database.session.add(admin_user)
    database.session.commit()

    print("✓ 默认管理员用户创建成功")
    print("  - 用户名: admin")
    print("  - 密码: admin123456")


def _init_rbac_data(database):
    """
    初始化 RBAC 权限数据（角色、菜单、API）

    Args:
        database: SQLAlchemy 数据库实例
    """
    from sysmanage.model.RoleModel import Role
    from sysmanage.model.MenuModel import Menu
    from sysmanage.model.ApiModel import Api
    from sysmanage.model.DeptModel import Dept
    from login.model.UserModel import User

    try:
        existing_count = database.session.query(Role).count()
        if existing_count > 0:
            print(f"✓ RBAC 数据已存在 ({existing_count} 条)，跳过创建")
            return
    except Exception:
        pass

    print("✓ 正在创建 RBAC 默认数据...")

    # 1. 创建角色
    admin_role = Role()
    admin_role.name = "超级管理员"
    admin_role.desc = "拥有所有权限"
    database.session.add(admin_role)

    editor_role = Role()
    editor_role.name = "普通用户"
    editor_role.desc = "普通用户角色"
    database.session.add(editor_role)
    database.session.flush()

    # 2. 创建部门
    root_dept = Dept()
    root_dept.name = "总公司"
    root_dept.desc = "总公司"
    root_dept.order = 1
    database.session.add(root_dept)
    database.session.flush()

    # 3. 创建菜单
    menus = [
        {"name": "首页", "menu_type": "catalog", "path": "/home", "icon": "home", "order": 1, "parent_id": 0, "component": "Layout"},
        {"name": "系统管理", "menu_type": "catalog", "path": "/system", "icon": "setting", "order": 2, "parent_id": 0, "component": "Layout"},
        {"name": "用户管理", "menu_type": "menu", "path": "/system/user", "icon": "user", "order": 1, "parent_id": 0, "component": "/system/user/index"},
        {"name": "角色管理", "menu_type": "menu", "path": "/system/role", "icon": "peoples", "order": 2, "parent_id": 0, "component": "/system/role/index"},
        {"name": "菜单管理", "menu_type": "menu", "path": "/system/menu", "icon": "tree-table", "order": 3, "parent_id": 0, "component": "/system/menu/index"},
        {"name": "部门管理", "menu_type": "menu", "path": "/system/dept", "icon": "tree", "order": 4, "parent_id": 0, "component": "/system/dept/index"},
        {"name": "API管理", "menu_type": "menu", "path": "/system/api", "icon": "api", "order": 5, "parent_id": 0, "component": "/system/api/index"},
        {"name": "接口测试", "menu_type": "catalog", "path": "/apitest", "icon": "test", "order": 3, "parent_id": 0, "component": "Layout"},
        {"name": "项目管理", "menu_type": "menu", "path": "/apitest/project", "icon": "project", "order": 1, "parent_id": 0, "component": "/apitest/project/index"},
        {"name": "测试集合", "menu_type": "menu", "path": "/apitest/collection", "icon": "collection", "order": 2, "parent_id": 0, "component": "/apitest/collection/index"},
        {"name": "测试用例", "menu_type": "menu", "path": "/apitest/case", "icon": "case", "order": 3, "parent_id": 0, "component": "/apitest/case/index"},
        {"name": "执行历史", "menu_type": "menu", "path": "/apitest/history", "icon": "history", "order": 4, "parent_id": 0, "component": "/apitest/history/index"},
    ]

    for menu_data in menus:
        menu = Menu()
        menu.name = menu_data["name"]
        menu.menu_type = menu_data["menu_type"]
        menu.path = menu_data["path"]
        menu.icon = menu_data["icon"]
        menu.order = menu_data["order"]
        menu.parent_id = menu_data["parent_id"]
        menu.component = menu_data["component"]
        menu.is_hidden = False
        menu.keepalive = True
        database.session.add(menu)

    # 4. 创建 API
    apis = [
        {"path": "/api/auth/login", "method": "POST", "summary": "用户登录", "tags": "auth"},
        {"path": "/api/auth/logout", "method": "POST", "summary": "用户登出", "tags": "auth"},
        {"path": "/api/auth/info", "method": "GET", "summary": "获取用户信息", "tags": "auth"},
        {"path": "/api/users", "method": "GET", "summary": "获取用户列表", "tags": "user"},
        {"path": "/api/users", "method": "POST", "summary": "创建用户", "tags": "user"},
        {"path": "/api/users/{id}", "method": "PUT", "summary": "更新用户", "tags": "user"},
        {"path": "/api/users/{id}", "method": "DELETE", "summary": "删除用户", "tags": "user"},
        {"path": "/api/roles", "method": "GET", "summary": "获取角色列表", "tags": "role"},
        {"path": "/api/roles", "method": "POST", "summary": "创建角色", "tags": "role"},
        {"path": "/api/roles/{id}", "method": "PUT", "summary": "更新角色", "tags": "role"},
        {"path": "/api/roles/{id}", "method": "DELETE", "summary": "删除角色", "tags": "role"},
        {"path": "/api/menus", "method": "GET", "summary": "获取菜单列表", "tags": "menu"},
        {"path": "/api/menus", "method": "POST", "summary": "创建菜单", "tags": "menu"},
        {"path": "/api/menus/{id}", "method": "PUT", "summary": "更新菜单", "tags": "menu"},
        {"path": "/api/menus/{id}", "method": "DELETE", "summary": "删除菜单", "tags": "menu"},
        {"path": "/api/depts", "method": "GET", "summary": "获取部门列表", "tags": "dept"},
        {"path": "/api/depts", "method": "POST", "summary": "创建部门", "tags": "dept"},
        {"path": "/api/depts/{id}", "method": "PUT", "summary": "更新部门", "tags": "dept"},
        {"path": "/api/depts/{id}", "method": "DELETE", "summary": "删除部门", "tags": "dept"},
        {"path": "/api/apis", "method": "GET", "summary": "获取API列表", "tags": "api"},
        {"path": "/api/apis", "method": "POST", "summary": "创建API", "tags": "api"},
        {"path": "/api/apis/{id}", "method": "PUT", "summary": "更新API", "tags": "api"},
        {"path": "/api/apis/{id}", "method": "DELETE", "summary": "删除API", "tags": "api"},
    ]

    for api_data in apis:
        api = Api()
        api.path = api_data["path"]
        api.method = api_data["method"]
        api.summary = api_data["summary"]
        api.tags = api_data["tags"]
        database.session.add(api)

    database.session.commit()
    print("✓ RBAC 默认数据创建成功")
    print(f"  - 角色: 超级管理员, 普通用户")
    print(f"  - 菜单: {len(menus)} 条")
    print(f"  - API: {len(apis)} 条")


def _init_operation_types(database):
    """
    初始化操作类型数据

    Args:
        database: SQLAlchemy 数据库实例
    """
    from apitest.model.ApiOperationTypeModel import OperationType

    try:
        # 检查是否已存在操作类型
        existing_count = database.session.query(OperationType).count()
        if existing_count > 0:
            print(f"✓ 操作类型已存在 ({existing_count} 条)，跳过创建")
            return
    except Exception:
        # 表不存在时会抛出异常，继续创建
        pass

    print("✓ 正在创建默认操作类型...")

    operation_types = [
        {"operation_type_name": "HTTP请求", "ex_fun_name": "http_request"},
        {"operation_type_name": "数据提取", "ex_fun_name": "data_extraction"},
        {"operation_type_name": "断言操作", "ex_fun_name": "assertion"},
        {"operation_type_name": "脚本执行", "ex_fun_name": "script_execution"},
    ]

    for op_type_data in operation_types:
        op_type = OperationType()
        op_type.operation_type_name = op_type_data["operation_type_name"]
        op_type.ex_fun_name = op_type_data["ex_fun_name"]
        op_type.create_time = datetime.now()
        database.session.add(op_type)

    database.session.commit()
    print(f"✓ 默认操作类型创建成功 ({len(operation_types)} 条)")


def _init_keywords(database):
    """
    初始化关键字数据

    Args:
        database: SQLAlchemy 数据库实例
    """
    from apitest.model.ApiKeyWordModel import ApiKeyWord
    from apitest.model.ApiOperationTypeModel import OperationType

    try:
        # 检查是否已存在关键字
        existing_count = database.session.query(ApiKeyWord).count()
        if existing_count > 0:
            print(f"✓ 关键字已存在 ({existing_count} 条)，跳过创建")
            return
    except Exception:
        # 表不存在时会抛出异常，继续创建
        pass

    print("✓ 正在创建默认关键字...")

    # 获取操作类型ID映射
    operation_types = database.session.query(OperationType).all()
    op_type_map = {op.operation_type_name: op.id for op in operation_types}

    keywords = [
        # HTTP请求
        {
            "name": "发送HTTP请求",
            "keyword_desc": "发送HTTP请求(GET/POST/PUT/DELETE等),支持headers、params、data、json、files等参数",
            "operation_type_id": op_type_map.get("HTTP请求"),
            "keyword_fun_name": "send_request",
            "keyword_value": "method,url,headers,params,data,json,files,download,timeout",
            "is_enabled": "1"
        },
        # 数据提取
        {
            "name": "提取JSON数据",
            "keyword_desc": "使用JSONPath表达式从响应中提取JSON数据",
            "operation_type_id": op_type_map.get("数据提取"),
            "keyword_fun_name": "ex_jsonData",
            "keyword_value": "EXVALUE,INDEX,VARNAME",
            "is_enabled": "1"
        },
        {
            "name": "提取正则数据",
            "keyword_desc": "使用正则表达式从响应中提取数据",
            "operation_type_id": op_type_map.get("数据提取"),
            "keyword_fun_name": "ex_reData",
            "keyword_value": "EXVALUE,INDEX,VARNAME",
            "is_enabled": "1"
        },
        {
            "name": "提取数据库数据",
            "keyword_desc": "执行SQL查询并提取数据库数据到变量",
            "operation_type_id": op_type_map.get("数据提取"),
            "keyword_fun_name": "ex_mysqlData",
            "keyword_value": "数据库,SQL,引用变量",
            "is_enabled": "1"
        },
        # 断言操作
        {
            "name": "文本比较断言",
            "keyword_desc": "比较两个值是否满足指定的比较条件(>,<,==,>=,<=,!=)",
            "operation_type_id": op_type_map.get("断言操作"),
            "keyword_fun_name": "assert_text_comparators",
            "keyword_value": "VALUE,EXPECTED,OP_STR,MESSAGE",
            "is_enabled": "1"
        },
        {
            "name": "文件MD5比较",
            "keyword_desc": "比较文件的MD5值是否一致",
            "operation_type_id": op_type_map.get("断言操作"),
            "keyword_fun_name": "assert_files_by_md5_comparators",
            "keyword_value": "value,expected",
            "is_enabled": "1"
        },
        # 脚本执行
        {
            "name": "执行Python脚本",
            "keyword_desc": "执行Python脚本文件,支持调用指定函数并传递参数",
            "operation_type_id": op_type_map.get("脚本执行"),
            "keyword_fun_name": "run_script",
            "keyword_value": "script_path,function_name,variable_name",
            "is_enabled": "1"
        },
        {
            "name": "执行Python代码",
            "keyword_desc": "执行Python代码片段,支持保存返回值到变量",
            "operation_type_id": op_type_map.get("脚本执行"),
            "keyword_fun_name": "run_code",
            "keyword_value": "code,variable_name",
            "is_enabled": "1"
        },
    ]

    for keyword_data in keywords:
        keyword = ApiKeyWord()
        keyword.name = keyword_data["name"]
        keyword.keyword_desc = keyword_data["keyword_desc"]
        keyword.operation_type_id = keyword_data["operation_type_id"]
        keyword.keyword_fun_name = keyword_data["keyword_fun_name"]
        keyword.keyword_value = keyword_data["keyword_value"]
        keyword.is_enabled = keyword_data["is_enabled"]
        keyword.create_time = datetime.now()
        database.session.add(keyword)

    database.session.commit()
    print(f"✓ 默认关键字创建成功 ({len(keywords)} 条)")


def check_database_connection(app, database):
    """
    检查数据库连接是否正常

    Args:
        app: Flask 应用实例
        database: SQLAlchemy 数据库实例

    Returns:
        bool: 连接是否成功
    """
    with app.app_context():
        try:
            database.session.execute(database.text("SELECT 1")) # 尝试执行简单查询
            print("✓ 数据库连接成功")
            return True
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            return False


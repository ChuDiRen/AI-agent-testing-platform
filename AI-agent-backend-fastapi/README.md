# FastAPI RBAC 权限管理系统

基于 RBAC（Role-Based Access Control）权限模型的 FastAPI 后端系统。

**参考设计**: [RBAC表结构设计 - BNTang](https://www.cnblogs.com/BNTang/articles/17024549.html)

---

## ✨ 功能特性

### 🔐 RBAC 权限模型
- **三层架构**: 用户 → 角色 → 菜单（权限）
- **多对多关系**: 用户-角色、角色-菜单完整实现
- **权限标识**: 规范的 `资源:操作` 格式（如 `user:view`）
- **菜单树结构**: 支持多级菜单和按钮权限

### 📋 核心功能
- ✅ **用户管理**: 注册、登录、CRUD、分页搜索、数据导出
- ✅ **角色管理**: 角色 CRUD、角色权限分配
- ✅ **菜单管理**: 菜单/按钮 CRUD、树形结构、用户菜单查询
- ✅ **部门管理**: 部门 CRUD、树形结构
- ✅ **权限关联**: 用户-角色、角色-菜单灵活配置
- ✅ **文件上传**: 头像、文件上传管理
- ✅ **JWT 认证**: 安全的 Token 认证机制
- ✅ **请求日志**: 完整的请求日志记录
- ✅ **API 限流**: 防止接口滥用

---

## 📊 数据库设计

完全按照博客 [RBAC表结构设计](https://www.cnblogs.com/BNTang/articles/17024549.html) 实现：

### 核心表结构

| 表名 | 说明 | 字段数 |
|-----|------|--------|
| t_user | 用户表 | 13 |
| t_role | 角色表 | 5 |
| t_menu | 菜单表（权限表） | 11 |
| t_user_role | 用户角色关联表 | 2 |
| t_role_menu | 角色菜单关联表 | 2 |
| t_dept | 部门表 | 6 |

### RBAC 权限流程

```
用户登录 → 查询用户角色(t_user_role) → 查询角色菜单(t_role_menu) → 获取菜单权限(t_menu.perms)
```

以用户 **BNTang** 为例：
1. 从 `t_user` 获取 user_id=1
2. 从 `t_user_role` 获取 role_id=1（管理员）
3. 从 `t_role_menu` 获取 menu_id 列表
4. 从 `t_menu` 获取权限标识（如 `user:view`, `user:add`）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_data.py
```

初始化数据（完全对应博客）：
- ✅ 用户: BNTang（密码: 1234qwer）
- ✅ 角色: 管理员
- ✅ 部门: 开发部
- ✅ 菜单: 5个（系统管理、用户管理及相关按钮）

### 3. 启动服务

```bash
python run.py
```

访问地址：
- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### 4. 测试登录

**测试账号**（来自博客数据）:
- 用户名: `BNTang`
- 密码: `1234qwer`

---

## 📚 API 接口

### 接口总览（60+ 个接口）

| 模块 | 接口数 | 说明 |
|-----|--------|------|
| 认证 | 2 | 注册、登录 |
| 用户管理 | 7 | CRUD、分页、导出 |
| 角色管理 | 5 | 完整 CRUD |
| 菜单管理 | 7 | CRUD、树结构、用户菜单 |
| 部门管理 | 5 | 完整 CRUD |
| 用户角色关联 | 3 | 分配、查询、移除 |
| 角色菜单关联 | 3 | 分配、查询、移除 |
| 文件上传 | 3 | 头像、文件上传删除 |
| 测试用例 | 6 | CRUD、执行、统计 |
| 测试报告 | 8 | CRUD、生成、导出、统计 |
| AI助手 | 9 | 聊天、会话管理、用例生成 |
| 消息通知 | 5 | CRUD、标记已读 |
| 数据管理 | 5 | 备份、恢复、清理、优化 |

### 核心接口示例

**1. 用户登录**
```bash
POST /api/v1/auth/login
{
  "username": "BNTang",
  "password": "1234qwer"
}
```

**2. 获取菜单树**
```bash
GET /api/v1/menus/tree
Authorization: Bearer {token}
```

**3. 创建测试用例**
```bash
POST /api/v1/testcases/
{
  "name": "登录功能测试",
  "test_type": "API",
  "module": "用户模块",
  "priority": "P1"
}
```

**4. 执行测试用例**
```bash
POST /api/v1/testcases/{testcase_id}/execute
{
  "environment": "test",
  "config": {"timeout": 30}
}
```

**5. 生成测试报告**
```bash
POST /api/v1/reports/generate
{
  "name": "API测试报告",
  "testcase_ids": [1, 2, 3],
  "environment": "test"
}
```

**6. AI聊天**
```bash
POST /api/v1/ai/chat
{
  "message": "帮我生成登录功能的测试用例",
  "model": "gpt-3.5-turbo"
}
```

**7. AI生成测试用例**
```bash
POST /api/v1/ai/generate-testcases
{
  "requirement": "用户登录功能",
  "test_type": "API",
  "count": 5
}
```

完整的 API 文档请查看：[API接口文档.md](API接口文档.md)

---

## 🏗️ 项目结构

```
AI-agent-frontend-fastapi/
├── app/
│   ├── api/                    # API 路由层
│   │   ├── auth.py            # 认证接口
│   │   ├── users.py           # 用户管理
│   │   ├── roles.py           # 角色管理
│   │   ├── menus.py           # 菜单管理
│   │   ├── departments.py     # 部门管理
│   │   ├── user_roles.py      # 用户角色关联
│   │   └── role_menus.py      # 角色菜单关联
│   │
│   ├── models/                 # 数据库模型（对应博客表结构）
│   │   ├── user.py            # t_user 用户表
│   │   ├── role.py            # t_role 角色表
│   │   ├── menu.py            # t_menu 菜单表
│   │   ├── department.py      # t_dept 部门表
│   │   ├── user_role.py       # t_user_role 关联表
│   │   └── role_menu.py       # t_role_menu 关联表
│   │
│   ├── schemas/                # Pydantic 数据验证
│   ├── services/               # 业务逻辑层
│   ├── repositories/           # 数据访问层
│   ├── middleware/             # 中间件
│   ├── utils/                  # 工具函数
│   ├── core/                   # 核心配置
│   └── main.py                 # 应用入口
│
├── init_data.py               # 数据初始化（博客数据）
├── run.py                     # 启动脚本
├── requirements.txt           # 依赖列表
├── API接口文档.md              # 完整 API 文档
└── README.md                  # 本文件
```

---

## 📦 技术栈

| 技术 | 版本 | 说明 |
|-----|------|------|
| FastAPI | 0.104.1 | 高性能 Web 框架 |
| SQLAlchemy | 2.0.23 | 异步 ORM |
| Pydantic | 2.5.0 | 数据验证 |
| Uvicorn | 0.24.0 | ASGI 服务器 |
| Passlib | 1.7.4 | 密码加密（BCrypt） |
| Python-Jose | 3.3.0 | JWT 认证 |
| Aiosqlite | 0.19.0 | 异步 SQLite |

---

## 🔑 初始化数据

完全按照博客数据初始化：

### 用户 (t_user)
```
user_id: 1
username: BNTang
password: 1234qwer (BCrypt加密)
email: 303158131@qq.com
mobile: 17788888888
status: 1 (有效)
ssex: 0 (男)
description: 我是帅比作者。
```

### 角色 (t_role)
```
role_id: 1
role_name: 管理员
remark: 管理员
```

### 菜单 (t_menu)
```
1. 系统管理 (菜单, type=0)
2. 用户管理 (菜单, type=0, perms=user:view)
3. 新增用户 (按钮, type=1, perms=user:add)
4. 修改用户 (按钮, type=1, perms=user:update)
5. 删除用户 (按钮, type=1, perms=user:delete)
```

### 部门 (t_dept)
```
dept_id: 1
dept_name: 开发部
parent_id: 0
```

### 关联关系
```
t_user_role: user_id=1 ↔ role_id=1 (BNTang 是管理员)
t_role_menu: role_id=1 拥有所有 5 个菜单权限
```

---

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker

```bash
# 构建镜像
docker build -t fastapi-rbac .

# 运行容器
docker run -d -p 8000:8000 fastapi-rbac
```

---

## 📖 文档说明

| 文档 | 说明 |
|-----|------|
| [README.md](README.md) | 项目主文档（本文件） |
| [API接口文档.md](API接口文档.md) | 完整的 API 接口文档（35+ 接口） |

---

## 🔗 参考资料

- **博客文章**: [RBAC表结构设计 - BNTang](https://www.cnblogs.com/BNTang/articles/17024549.html)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)

---

## 📄 许可证

MIT License

---

**项目完成**: 2025-10-02  
**表结构**: 100% 对应博客设计  
**测试数据**: 100% 对应博客数据  
**在线文档**: http://localhost:8000/docs

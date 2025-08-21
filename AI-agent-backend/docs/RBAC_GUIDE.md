# Copyright (c) 2025 左岚. All rights reserved.

# RBAC权限管理系统使用指南

## 概述

本系统实现了完整的RBAC（基于角色的访问控制）权限管理功能，严格按照经典RBAC模型设计，包含用户、角色、菜单权限、部门等核心功能。

## 数据库表结构

### 核心表

1. **t_user** - 用户表
   - USER_ID: 用户ID（主键）
   - USERNAME: 用户名（唯一）
   - PASSWORD: 加密密码
   - DEPT_ID: 部门ID（外键）
   - EMAIL: 邮箱
   - MOBILE: 手机号
   - STATUS: 状态（0锁定 1有效）
   - SSEX: 性别（0男 1女 2保密）
   - AVATAR: 头像
   - DESCRIPTION: 描述

2. **t_role** - 角色表
   - ROLE_ID: 角色ID（主键）
   - ROLE_NAME: 角色名称
   - REMARK: 角色描述

3. **t_menu** - 菜单表
   - MENU_ID: 菜单ID（主键）
   - PARENT_ID: 上级菜单ID
   - MENU_NAME: 菜单名称
   - PATH: 路由路径
   - COMPONENT: 路由组件
   - PERMS: 权限标识
   - ICON: 图标
   - TYPE: 类型（0菜单 1按钮）
   - ORDER_NUM: 排序号

4. **t_dept** - 部门表
   - DEPT_ID: 部门ID（主键）
   - PARENT_ID: 上级部门ID
   - DEPT_NAME: 部门名称
   - ORDER_NUM: 排序号

5. **t_user_role** - 用户角色关联表
   - USER_ID: 用户ID（外键）
   - ROLE_ID: 角色ID（外键）

6. **t_role_menu** - 角色菜单关联表
   - ROLE_ID: 角色ID（外键）
   - MENU_ID: 菜单ID（外键）

## API接口说明

### 用户管理 (/api/v1/users)

#### 创建用户
```http
POST /api/v1/users/
Content-Type: application/json

{
    "username": "testuser",
    "password": "123456",
    "email": "test@example.com",
    "mobile": "13800138000",
    "dept_id": 1,
    "ssex": "0",
    "description": "测试用户"
}
```

#### 用户登录
```http
POST /api/v1/users/login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123456"
}
```

#### 获取用户列表
```http
GET /api/v1/users/
```

#### 为用户分配角色
```http
POST /api/v1/users/{user_id}/roles
Content-Type: application/json

{
    "role_ids": [1, 2, 3]
}
```

### 角色管理 (/api/v1/roles)

#### 创建角色
```http
POST /api/v1/roles/
Content-Type: application/json

{
    "role_name": "管理员",
    "remark": "系统管理员角色"
}
```

#### 获取角色列表
```http
GET /api/v1/roles/?page=1&size=10
```

#### 为角色分配菜单权限
```http
POST /api/v1/roles/{role_id}/menus
Content-Type: application/json

{
    "menu_ids": [1, 2, 3, 4, 5]
}
```

### 菜单管理 (/api/v1/menus)

#### 创建菜单
```http
POST /api/v1/menus/
Content-Type: application/json

{
    "parent_id": 0,
    "menu_name": "系统管理",
    "menu_type": "0",
    "path": "/system",
    "component": "Layout",
    "icon": "el-icon-set-up",
    "order_num": 1
}
```

#### 获取菜单树
```http
GET /api/v1/menus/tree
```

#### 获取用户菜单
```http
GET /api/v1/menus/user/{user_id}
```

### 部门管理 (/api/v1/departments)

#### 创建部门
```http
POST /api/v1/departments/
Content-Type: application/json

{
    "parent_id": 0,
    "dept_name": "开发部",
    "order_num": 1
}
```

#### 获取部门树
```http
GET /api/v1/departments/tree
```

## 权限验证中间件

系统提供了完整的权限验证中间件，支持以下验证方式：

### 基础认证
```python
from app.middleware.rbac_auth import get_current_user

@router.get("/protected")
async def protected_endpoint(current_user=Depends(get_current_user)):
    return {"message": "这是受保护的接口"}
```

### 权限验证
```python
from app.middleware.rbac_auth import require_user_view

@router.get("/users")
async def get_users(current_user=Depends(require_user_view())):
    return {"users": []}
```

### 角色验证
```python
from app.middleware.rbac_auth import require_admin_role

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user=Depends(require_admin_role())):
    return {"message": "用户删除成功"}
```

## 初始数据

系统启动时会自动创建以下初始数据：

1. **默认部门**: 开发部
2. **默认角色**: 管理员
3. **默认菜单**: 系统管理 -> 用户管理（包含增删改查权限）
4. **默认用户**: admin/admin123456

## 使用示例

### 1. 完整的权限分配流程

```python
# 1. 创建部门
dept_service = DepartmentService(db)
dept = dept_service.create_department(0, "技术部", 1)

# 2. 创建角色
role_service = RoleService(db)
role = role_service.create_role("开发者", "开发人员角色")

# 3. 创建菜单权限
menu_service = MenuService(db)
system_menu = menu_service.create_menu(0, "系统管理", "0", "/system")
user_menu = menu_service.create_menu(system_menu.MENU_ID, "用户管理", "0", "/system/user", perms="user:view")

# 4. 为角色分配权限
role_service.assign_menus_to_role(role.ROLE_ID, [system_menu.MENU_ID, user_menu.MENU_ID])

# 5. 创建用户
user_service = RBACUserService(db)
user = user_service.create_user("developer", "123456", dept_id=dept.DEPT_ID)

# 6. 为用户分配角色
user_service.assign_roles_to_user(user.USER_ID, [role.ROLE_ID])
```

### 2. 权限检查

```python
# 检查用户是否有特定权限
has_permission = user_service.has_permission(user.USER_ID, "user:view")

# 获取用户所有权限
permissions = user_service.get_user_permissions(user.USER_ID)

# 获取用户可访问的菜单
user_menus = menu_service.get_user_menus(user.USER_ID)
```

## 测试

运行RBAC相关测试：

```bash
# 运行所有RBAC测试
pytest app/tests/test_rbac.py -v

# 运行API测试
pytest app/tests/test_rbac_api.py -v

# 运行特定测试
pytest app/tests/test_rbac.py::TestRoleService::test_create_role -v
```

## 注意事项

1. **密码安全**: 所有密码都使用bcrypt进行加密存储
2. **权限继承**: 菜单权限支持父子级关系，但权限不自动继承
3. **软删除**: 部分实体支持软删除，删除前会检查关联关系
4. **数据一致性**: 删除角色或菜单前会检查是否有关联数据
5. **性能优化**: 权限查询使用了适当的数据库索引和缓存策略

## 扩展功能

系统设计支持以下扩展：

1. **数据权限**: 可基于部门实现数据权限控制
2. **动态权限**: 支持运行时动态添加权限
3. **权限缓存**: 可集成Redis实现权限缓存
4. **审计日志**: 可记录权限变更和访问日志

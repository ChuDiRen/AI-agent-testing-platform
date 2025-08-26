# Copyright (c) 2025 左岚. All rights reserved.
# AI-Agent-Backend 业务语义化接口命名规范

## 命名原则

### 1. 见名知意原则
- 接口路径必须直接体现业务功能
- 使用完整的业务动词，避免缩写
- 路径层次清晰，体现业务逻辑关系

### 2. 业务语义化原则
- 以业务功能为导向，而非技术实现
- 使用中文业务术语的英文对应
- 保持业务概念的一致性

### 3. 统一性原则
- 同类操作使用统一的命名模式
- 相同业务实体使用一致的前缀
- 参数传递方式保持一致

## 命名模式

### 基础CRUD操作
```
POST /{resource}/create-{resource}     # 创建资源
POST /{resource}/get-{resource}-list   # 获取资源列表  
POST /{resource}/get-{resource}-info   # 获取资源详情
POST /{resource}/update-{resource}     # 更新资源
POST /{resource}/delete-{resource}     # 删除资源
```

### 特殊业务操作
```
POST /{resource}/get-{resource}-tree   # 获取树形结构
POST /{resource}/assign-{relation}     # 分配关系
POST /{resource}/check-{attribute}     # 检查属性
POST /{resource}/batch-{operation}     # 批量操作
```

## 各模块接口命名规范

### 用户管理模块 (/users)
```
POST /users/create-user              # 创建用户
POST /users/get-user-list           # 获取用户列表
POST /users/get-user-info           # 获取用户详情
POST /users/update-user             # 更新用户信息
POST /users/delete-user             # 删除用户
POST /users/user-login              # 用户登录
POST /users/user-logout             # 用户退出登录
POST /users/change-password         # 修改密码
POST /users/assign-user-roles       # 分配用户角色
POST /users/get-user-roles          # 获取用户角色
POST /users/check-username          # 检查用户名
```

### 角色管理模块 (/roles)
```
POST /roles/create-role             # 创建角色
POST /roles/get-role-list           # 获取角色列表
POST /roles/get-role-info           # 获取角色详情
POST /roles/update-role             # 更新角色信息
POST /roles/delete-role             # 删除角色
POST /roles/assign-role-menus       # 分配角色菜单权限
POST /roles/get-role-permissions    # 获取角色权限
POST /roles/check-role-name         # 检查角色名称
```

### 菜单管理模块 (/menus)
```
POST /menus/create-menu             # 创建菜单
POST /menus/get-menu-list           # 获取菜单列表
POST /menus/get-menu-info           # 获取菜单详情
POST /menus/update-menu             # 更新菜单信息
POST /menus/delete-menu             # 删除菜单
POST /menus/get-menu-tree           # 获取菜单树
POST /menus/get-user-menus          # 获取用户菜单
POST /menus/check-menu-name         # 检查菜单名称
```

### 部门管理模块 (/departments)
```
POST /departments/create-department     # 创建部门
POST /departments/get-department-list   # 获取部门列表
POST /departments/get-department-info   # 获取部门详情
POST /departments/update-department     # 更新部门信息
POST /departments/delete-department     # 删除部门
POST /departments/get-department-tree   # 获取部门树
POST /departments/check-department-name # 检查部门名称
```

### 权限管理模块 (/permissions)
```
POST /permissions/get-user-permissions          # 获取用户权限
POST /permissions/get-user-menus                # 获取用户菜单
POST /permissions/get-role-permissions          # 获取角色权限
POST /permissions/get-permission-menu-tree      # 获取权限管理菜单树
POST /permissions/batch-assign-user-roles       # 批量分配用户角色
POST /permissions/batch-assign-role-menus       # 批量分配角色菜单权限
POST /permissions/create-data-permission-rule   # 创建数据权限规则
POST /permissions/get-cache-statistics          # 获取权限缓存统计
POST /permissions/refresh-permission-cache      # 刷新权限缓存
POST /permissions/set-cache-config              # 设置缓存配置
```

### 仪表板模块 (/dashboard)
```
POST /dashboard/get-statistics-data     # 获取统计数据
POST /dashboard/get-system-info         # 获取系统信息
POST /dashboard/get-overview-data       # 获取概览数据
```

### 日志管理模块 (/logs)
```
POST /logs/get-log-list                 # 获取日志列表
POST /logs/get-log-info                 # 获取日志详情
POST /logs/get-log-statistics           # 获取日志统计
POST /logs/clear-logs                   # 清空日志
```

## 参数传递规范

### 请求体参数
- 所有接口统一使用POST方法
- 参数通过请求体传递，便于复杂参数处理
- 请求体使用JSON格式

### 参数命名规范
```json
{
  "user_id": 1,           // 资源ID使用下划线命名
  "page": 1,              // 分页参数
  "size": 10,             // 每页大小
  "keyword": "搜索关键词",  // 搜索关键词
  "start_time": "2025-01-01", // 时间范围
  "end_time": "2025-12-31"
}
```

## 响应格式规范

### 统一响应结构
```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "error_code": null,
  "timestamp": "2025-08-26T10:00:00.000Z"
}
```

### 业务状态码
- 200: 操作成功
- 400: 请求参数错误
- 401: 未授权
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 实施计划

### ✅ 第一阶段：核心模块重构（已完成）
1. ✅ 用户管理接口重命名
2. ✅ 角色管理接口重命名
3. ✅ 菜单管理接口重命名

### ✅ 第二阶段：扩展模块重构（已完成）
1. ✅ 部门管理接口重命名
2. ✅ 权限管理接口重命名

### ✅ 第三阶段：系统模块重构（已完成）
1. ✅ 仪表板接口重命名
2. ✅ 日志管理接口重命名

### 🔄 第四阶段：文档和测试（进行中）
1. ✅ 更新API文档
2. 🔄 更新前端调用
3. ⏳ 执行完整测试

## 注意事项

1. **向后兼容**：重构过程中保持原接口可用，逐步迁移
2. **前端同步**：接口重命名需要同步更新前端调用代码
3. **测试验证**：每个模块重构完成后立即进行功能测试
4. **文档更新**：及时更新API文档和使用说明

## 质量检查清单

- [x] 接口名称是否见名知意
- [x] 业务语义是否清晰
- [x] 命名是否符合规范
- [x] 参数传递是否一致
- [x] 响应格式是否统一
- [x] 文档是否同步更新
- [ ] 测试是否通过

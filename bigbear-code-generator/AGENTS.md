# Admin Platform - AI 开发指南

本文档为 AI 助手提供项目的详细信息和开发指南。

## 项目概述

**Admin Platform** 是一个基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台,参考了 [vue-fastapi-admin](https://github.com/mizhexiaoxiao/vue-fastapi-admin) 项目的设计思路。

### 核心特性
- ✅ RBAC 权限管理系统
- ✅ JWT 认证和授权
- ✅ 动态路由和菜单
- ✅ 用户、角色、部门管理
- ✅ 代码生成器功能
- ✅ 前后端统一部署

## 技术栈

### 后端
- **框架**: FastAPI 0.115.0+
- **ORM**: SQLModel 0.0.16+
- **数据库**: MySQL / SQLite
- **认证**: JWT (python-jose)
- **配置**: Pydantic Settings
- **模板**: Jinja2

### 前端
- **框架**: Vue 3.2+
- **UI 库**: Element Plus
- **构建工具**: Vite 4+
- **状态管理**: Pinia
- **路由**: Vue Router 4

## 项目结构

```
admin-platform/
├── app/                          # 后端应用
│   ├── api/                     # API 路由
│   │   └── v1/
│   │       └── endpoints/       # 控制器
│   ├── models/                  # 数据模型
│   ├── schemas/                 # 数据模式
│   ├── services/                # 业务逻辑
│   ├── database/                # 数据库配置
│   ├── security/                # 安全模块
│   ├── middleware/              # 中间件
│   ├── templates/               # 代码生成模板
│   └── main.py                  # 应用入口
├── web/                         # 前端应用
│   ├── src/
│   │   ├── api/                # API 接口
│   │   ├── components/         # 组件
│   │   ├── views/              # 页面
│   │   ├── router/             # 路由
│   │   ├── stores/             # 状态管理
│   │   └── utils/              # 工具类
│   ├── public/                 # 静态资源
│   └── vite.config.js          # Vite 配置
├── requirements.txt             # Python 依赖
├── pyproject.toml              # Python 项目配置
├── run.py                      # 启动脚本
├── Dockerfile                  # Docker 配置
├── docker-compose.yml          # Docker Compose
├── start.sh                    # Linux/Mac 启动脚本
├── start.bat                   # Windows 启动脚本
├── README.md                   # 项目说明
└── DEPLOY.md                   # 部署指南
```

## 核心模块说明

### 1. 认证模块 (AuthController)
- 登录认证
- JWT Token 生成和验证
- 用户信息获取

### 2. 用户管理 (UsersController)
- 用户 CRUD
- 用户角色分配
- 密码管理

### 3. 角色管理 (RolesController)
- 角色 CRUD
- 角色权限分配
- 菜单权限绑定

### 4. 菜单管理 (MenusController)
- 菜单 CRUD
- 树形结构管理
- 动态路由生成

### 5. 部门管理 (DepartmentsController)
- 部门 CRUD
- 树形结构管理
- 数据权限范围

### 6. 代码生成器 (GeneratorController)
- 表结构解析
- 代码模板渲染
- 前后端代码生成

## 数据库模型

### 核心表
- `sys_user`: 用户表
- `sys_role`: 角色表
- `sys_menu`: 菜单表
- `sys_dept`: 部门表
- `sys_user_role`: 用户角色关联表
- `sys_role_menu`: 角色菜单关联表

### 代码生成器表
- `gen_table`: 表配置
- `gen_table_column`: 字段配置
- `gen_history`: 生成历史

## API 规范

### 请求格式
```json
{
  "page": 1,
  "page_size": 10,
  "keyword": "搜索关键词"
}
```

### 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误码
- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误

## 权限控制

### 后端权限
使用依赖注入检查权限:
```python
from app.dependencies.dependencies import get_current_user, check_permission

@router.get("/api/users")
async def get_users(
    current_user: dict = Depends(get_current_user),
    has_permission: bool = Depends(check_permission("system:user:list"))
):
    pass
```

### 前端权限
使用指令控制按钮显示:
```vue
<el-button v-permission="'system:user:add'">新增</el-button>
```

## 开发规范

### 后端开发
1. 使用 SQLModel 定义数据模型
2. 使用 Pydantic Schema 验证数据
3. 业务逻辑放在 Service 层
4. 统一异常处理
5. 使用日志记录关键操作

### 前端开发
1. 组件化开发
2. 使用 Composition API
3. 统一使用 axios 封装的请求
4. 路由懒加载
5. 使用 Pinia 管理状态

## 部署说明

### 开发环境
```bash
# 后端
python run.py

# 前端
cd web && pnpm dev
```

### 生产环境
```bash
# Docker 部署
docker build -t admin-platform .
docker run -d -p 9999:80 admin-platform

# 或使用 Docker Compose
docker-compose up -d
```

## 配置说明

### 环境变量
- `APP_ENV`: 运行环境 (development/production)
- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT 密钥
- `CORS_ORIGINS`: 允许的跨域源

### 数据库配置
```env
# SQLite (默认)
DATABASE_URL=sqlite:///./admin_platform.db

# MySQL
DATABASE_URL=mysql+aiomysql://user:pass@host:3306/db
```

## 常用命令

### 后端
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py

# 运行测试
pytest
```

### 前端
```bash
# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 构建生产
pnpm build

# 预览构建
pnpm preview
```

## 扩展开发

### 添加新模块
1. 创建数据模型 (`app/models/`)
2. 创建数据模式 (`app/schemas/`)
3. 创建服务层 (`app/services/`)
4. 创建控制器 (`app/api/v1/endpoints/`)
5. 注册路由 (`app/main.py`)
6. 创建前端页面 (`web/src/views/`)
7. 添加路由配置 (`web/src/router/`)

### 添加权限
1. 在菜单管理中添加菜单
2. 配置权限标识
3. 在角色管理中分配权限
4. 后端使用 `check_permission` 检查
5. 前端使用 `v-permission` 指令

## 注意事项

1. **安全性**
   - 生产环境必须修改 SECRET_KEY
   - 使用 HTTPS 部署
   - 定期更新依赖包
   - 启用 SQL 注入防护

2. **性能优化**
   - 使用数据库索引
   - 启用查询缓存
   - 前端代码分割
   - 使用 CDN 加速

3. **数据备份**
   - 定期备份数据库
   - 保存重要配置文件
   - 版本控制代码

## 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
- [vue-fastapi-admin](https://github.com/mizhexiaoxiao/vue-fastapi-admin)

## 更新日志

### v1.0.0 (2026-01-15)
- ✅ 初始版本发布
- ✅ 完整的 RBAC 权限系统
- ✅ 代码生成器功能
- ✅ Docker 部署支持
- ✅ 前后端统一部署

## 许可证

MIT License

# Admin Platform - 现代化轻量管理平台

⭐️ 基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台

## 特性

- **最流行技术栈**: 基于 Python 3.11 和 FastAPI 高性能异步框架，结合 Vue3 和 Vite 等前沿技术进行开发
- **代码规范**: 项目内置丰富的规范插件，确保代码质量和一致性
- **动态路由**: 后端动态路由，结合 RBAC（Role-Based Access Control）权限模型，提供精细的菜单路由控制
- **JWT鉴权**: 使用 JSON Web Token（JWT）进行身份验证和授权，增强应用的安全性
- **细粒度权限控制**: 实现按钮和接口级别的权限控制
- **代码生成器**: 基于 AST 的智能代码生成器，支持前后端代码生成

## 技术栈

### 后端
- FastAPI >= 0.115.0
- SQLModel >= 0.0.16
- MySQL / SQLite
- JWT 认证
- Pydantic Settings

### 前端
- Vue 3.2+
- Naive UI
- Vite 4+
- Pinia
- Vue Router 4

## 项目结构

```
admin-platform/
├── app/                    # 后端应用目录
│   ├── api/               # API接口
│   ├── models/            # 数据模型
│   ├── schemas/           # 数据模式
│   ├── services/          # 业务逻辑
│   ├── core/              # 核心功能
│   └── utils/             # 工具类
├── web/                   # 前端应用目录
│   ├── src/              # 源代码
│   │   ├── api/          # API接口定义
│   │   ├── components/   # 组件
│   │   ├── views/        # 视图页面
│   │   ├── router/       # 路由
│   │   ├── store/        # 状态管理
│   │   └── utils/        # 工具类
│   └── public/           # 静态资源
├── requirements.txt       # Python依赖
├── pyproject.toml        # Python项目配置
├── run.py                # 后端启动脚本
└── Dockerfile            # Docker配置

```

## 快速开始

### 方法一：Docker 部署（推荐）

```bash
# 构建镜像
docker build -t admin-platform .

# 启动容器
docker run -d --restart=always --name=admin-platform -p 9999:80 admin-platform

# 访问
# http://localhost:9999
# 默认账号: admin
# 默认密码: 123456
```

### 方法二：本地开发

#### 后端启动

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate   # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动服务
```bash
python run.py
```

服务运行在 http://localhost:9999
API文档: http://localhost:9999/docs

#### 前端启动

1. 进入前端目录
```bash
cd web
```

2. 安装依赖
```bash
pnpm install
# 或
npm install
```

3. 启动开发服务器
```bash
pnpm dev
# 或
npm run dev
```

前端运行在 http://localhost:3000

## 功能模块

### 系统管理
- ✅ 用户管理
- ✅ 角色管理
- ✅ 菜单管理
- ✅ 部门管理
- ✅ 权限管理

### 代码生成
- ✅ 表配置管理
- ✅ 代码生成器
- ✅ 模板管理
- ✅ 预览和下载

### 其他功能
- ✅ 登录认证
- ✅ 个人中心
- ✅ 操作日志
- ✅ 数据统计

## 开发指南

### 环境要求
- Python 3.11+
- Node.js 18.8.0+
- MySQL 8.0+ (可选，默认使用 SQLite)

### 配置说明

后端配置文件: `app/config/settings.py`
前端配置文件: `web/.env`

### API文档

启动后端服务后访问:
- Swagger UI: http://localhost:9999/docs
- ReDoc: http://localhost:9999/redoc

## 许可证

MIT License

## 参考项目

本项目参考了 [vue-fastapi-admin](https://github.com/mizhexiaoxiao/vue-fastapi-admin) 的设计思路和部分实现。

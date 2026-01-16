---
description: 启动前后端分离项目的完整流程命令（全自动优化版）
---

# 命令：start-project

## 功能描述

完整的项目启动流程，自动串联需求收集、需求分析、原型设计、数据库设计、接口设计、架构设计、时序图设计、任务拆分（前端+后端+API测试+E2E测试）和代码脚手架初始化。

## 核心特性

- ✅ **全自动流程**：无需人工确认，架构师自动审核
- ✅ **智能模式**：新项目(--new)和迭代(--iteration)自动识别
- ✅ **三维任务**：前端+后端+测试（API+E2E）
- ✅ **质量保证**：架构师每个阶段自动审核并调整

## 使用方式

```
/start-project [项目类型] --new|--iteration [技术栈选项]
```

## 参数说明

### 项目类型（必填）
- `admin` - 企业管理后台
- `ecommerce` - 电商平台
- `mobile-h5` - 移动端H5应用
- `data-platform` - 数据分析平台
- `small-app` - 小型项目/快速原型

### 项目模式（必填，二选一）
- `--new` - 新项目初始化：执行完整9个阶段，包括脚手架初始化
- `--iteration` - 项目迭代：只执行前8个阶段，跳过脚手架初始化

### 技术栈选项（可选）
- `--backend=java` - 使用Java Spring Boot（默认）
- `--backend=python` - 使用Python FastAPI
- `--backend=nodejs` - 使用Node.js (Express/NestJS)
- `--frontend=element` - 使用Element Plus组件库（默认）
- `--frontend=vant` - 使用Vant组件库
- `--database=mysql` - 使用MySQL数据库（默认）
- `--database=postgresql` - 使用PostgreSQL数据库
- `--database=mongodb` - 使用MongoDB数据库
- `--with-redis` - 启用Redis缓存

## 自动执行流程

### 阶段一：需求收集与确认
1. 询问项目基本信息（名称、功能、规模）
2. 确认目标用户群体
3. 确认技术栈选择
4. **架构师自动评估**：评估需求的合理性和完整性
5. **输出**：需求确认信息

### 阶段二：需求分析
**执行命令**：`/analyze-requirement`

1. 业务领域分析
2. 功能模块划分
3. 用户场景梳理
4. 技术挑战识别
5. **输出**：`docs/requirement.md` 需求分析文档
6. **架构师自动审核**：自动审核并调整，直到通过

### 阶段三：原型设计
**执行命令**：`/design-prototype`

1. 页面规划与信息架构
2. UI风格设计
3. 交互流程设计
4. **输出**：`prototypes/` 目录下的HTML原型文件
5. **架构师自动审核**：自动审核并调整，直到通过

### 阶段四：数据库设计

1. 实体关系分析（ER图）
2. 表结构设计
3. 索引设计
4. **输出**：`docs/database-design.md` 数据库设计文档
5. **架构师自动审核**：自动审核并调整，直到通过

### 阶段五：接口设计
**执行命令**：`/generate-api-doc --split-modules`

1. RESTful API规范设计
2. **按功能模块拆分接口文档**
3. 请求/响应格式定义
4. **输出**：`docs/api-docs/` 目录下的模块化接口文档
   - `README.md` - API文档总览
   - `common.md` - 通用规范
   - `auth-module.md` - 认证模块
   - `user-module.md` - 用户管理模块
   - `department-module.md` - 部门管理模块
   - `role-module.md` - 角色管理模块
   - `permission-module.md` - 权限管理模块
   - `profile-module.md` - 个人中心模块
   - `log-module.md` - 日志管理模块
   - `dict-module.md` - 数据字典模块
5. **架构师自动审核**：自动审核并调整，直到通过

### 阶段六：架构设计

1. 系统架构图
2. 技术架构图
3. 部署架构图
4. **输出**：`docs/architecture.md` 架构设计文档
5. **架构师自动审核**：自动审核并调整，直到通过

### 阶段七：时序图设计
**执行命令**：`/generate-sequence-diagram`

1. 用户登录认证时序图
2. 用户管理CRUD时序图
3. 部门管理CRUD时序图
4. 角色管理CRUD时序图
5. 权限验证时序图
6. 数据库操作时序图
7. **输出**：`docs/sequence-diagrams/` 目录下的时序图文档
8. **架构师自动审核**：自动审核并调整，直到通过

### 阶段八：任务拆分
**执行命令**：`/split-tasks`

1. 按功能模块拆分任务
2. **生成三个独立任务文件**：
   - 前端任务清单：`docs/tasks-frontend.md`
   - 后端任务清单：`docs/tasks-backend.md`
   - **API测试任务清单：`docs/tasks-api-testing.md`** ⭐新增
   - **E2E测试任务清单：`docs/tasks-e2e-testing.md`** ⭐新增
3. 确定任务优先级和依赖关系
4. 估算开发时间
5. **架构师自动审核**：自动审核并调整，直到通过

### 阶段九：代码脚手架初始化
**仅新项目(--new)模式执行，迭代(--iteration)模式跳过** ⭐

1. **前端脚手架初始化**：
   - 使用Vite创建Vue3项目：`npm create vite@latest frontend -- --template vue-ts`
   - 安装组件库（Element Plus或Vant）
   - 配置开发环境（TypeScript、ESLint、Prettier）
   - 初始化路由（Vue Router）
   - 初始化状态管理（Pinia）

2. **后端脚手架初始化**：
   - **Java**：使用Spring Initializr或Maven Archetype创建Spring Boot项目
     - Spring Boot 3.x
     - Spring Security
     - Spring Data JPA/MyBatis-Plus
   - **Python**：使用FastAPI官方脚手架创建项目
     - FastAPI + uvicorn
     - SQLAlchemy/Tortoise ORM
     - JWT认证

3. **配置开发环境**：
   - 配置数据库连接
   - 配置Redis（如启用）
   - 配置跨域（CORS）
   - 配置日志系统

4. **输出**：完整的前后端项目结构
   - `frontend/` - Vue3前端项目
   - `backend/` - Java/Python后端项目

5. **架构师自动审核**：自动审核并调整，直到通过

## 执行示例

### 新项目初始化（完整流程）

```bash
/start-project admin --new --backend=java --frontend=element --database=postgresql --with-redis
```

**自动执行9个阶段**：
```
✅ 阶段1：需求收集 → 架构师自动评估
✅ 阶段2：需求分析 → /analyze-requirement → 架构师自动审核
✅ 阶段3：原型设计 → /design-prototype → 架构师自动审核
✅ 阶段4：数据库设计 → 架构师自动审核
✅ 阶段5：接口设计 → /generate-api-doc --split-modules → 架构师自动审核
✅ 阶段6：架构设计 → 架构师自动审核
✅ 阶段7：时序图设计 → /generate-sequence-diagram → 架构师自动审核
✅ 阶段8：任务拆分 → /split-tasks → 架构师自动审核
✅ 阶段9：脚手架初始化 → 架构师自动审核
```

**输出文件结构**：
```
project-name/
├── docs/
│   ├── requirement.md              # 需求分析
│   ├── database-design.md          # 数据库设计
│   ├── architecture.md             # 架构设计
│   ├── tasks-frontend.md          # 前端任务
│   ├── tasks-backend.md           # 后端任务
│   ├── tasks-api-testing.md      # API测试任务 ⭐
│   ├── tasks-e2e-testing.md      # E2E测试任务 ⭐
│   ├── api-docs/                 # API文档（模块化）
│   │   ├── README.md
│   │   ├── common.md
│   │   ├── auth-module.md
│   │   ├── user-module.md
│   │   └── ...
│   └── sequence-diagrams/         # 时序图
│       ├── README.md
│       ├── auth-sequence.md
│       └── ...
├── prototypes/                    # HTML原型
│   ├── index.html
│   └── *.html
├── frontend/                      # Vue3项目（脚手架生成）
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── backend/                       # Java/Python项目（脚手架生成）
    ├── src/
    ├── pom.xml / pyproject.toml
    └── ...
```

### 项目迭代（跳过脚手架）

```bash
/start-project admin --iteration --backend=java --frontend=element --database=postgresql
```

**自动执行8个阶段**：
```
✅ 阶段1：需求收集 → 架构师自动评估
✅ 阶段2：需求分析 → /analyze-requirement → 架构师自动审核
✅ 阶段3：原型设计 → /design-prototype → 架构师自动审核
✅ 阶段4：数据库设计 → 架构师自动审核
✅ 阶段5：接口设计 → /generate-api-doc --split-modules → 架构师自动审核
✅ 阶段6：架构设计 → 架构师自动审核
✅ 阶段7：时序图设计 → /generate-sequence-diagram → 架构师自动审核
✅ 阶段8：任务拆分 → /split-tasks → 架构师自动审核
⏭️ 阶段9：脚手架初始化 → 跳过（迭代模式）
```

**输出文件结构**：
```
project-name/
├── docs/
│   ├── requirement.md
│   ├── database-design.md
│   ├── architecture.md
│   ├── tasks-frontend.md
│   ├── tasks-backend.md
│   ├── tasks-api-testing.md      # API测试任务 ⭐
│   ├── tasks-e2e-testing.md      # E2E测试任务 ⭐
│   ├── api-docs/
│   └── sequence-diagrams/
└── prototypes/
```

## 架构师自动审核机制

### 审核流程
每个阶段完成后：
1. 架构师自动扫描输出文档
2. 按照预设标准审核
3. **审核通过**：自动进入下一阶段
4. **审核不通过**：自动调整输出，再次审核，直到通过

### 审核标准
- ✅ **完整性**：包含所有必需内容
- ✅ **正确性**：技术方案合理可行
- ✅ **一致性**：命名、格式统一规范
- ✅ **规范性**：符合编码和设计规范
- ✅ **可扩展性**：考虑未来扩展需求
- ✅ **安全性**：考虑安全措施
- ✅ **性能考虑**：考虑性能优化

### 审核要点

#### 需求文档
- [ ] 功能模块完整覆盖
- [ ] 用户场景清晰描述
- [ ] 技术挑战有针对性解决方案
- [ ] 文档结构清晰合理

#### 原型设计
- [ ] 所有页面导航一致
- [ ] UI风格统一
- [ ] 表单验证合理
- [ ] 交互流程顺畅
- [ ] 移动端适配考虑

#### 数据库设计
- [ ] ER图正确
- [ ] 表结构规范
- [ ] 外键约束完整
- [ ] 索引合理
- [ ] 初始化数据完整

#### 接口设计
- [ ] 接口命名规范
- [ ] 请求/响应格式统一
- [ ] 错误码完整
- [ ] 权限验证考虑
- [ ] 参数验证充分

#### 架构设计
- [ ] 架构图清晰
- [ ] 技术选型合理
- [ ] 模块划分清晰
- [ ] 扩展性考虑
- [ ] 性能优化考虑

#### 时序图设计
- [ ] 业务流程完整
- [ ] 接口调用时序正确
- [ ] 异常处理考虑
- [ ] 用户场景覆盖

#### 任务拆分
- [ ] 前后端任务分离
- [ ] **包含测试任务（API测试、E2E测试）** ⭐
- [ ] 任务优先级合理
- [ ] 依赖关系正确
- [ ] 工时估算合理
- [ ] 任务颗粒度合适

#### 测试任务 ⭐
- [ ] **API测试是否覆盖所有接口**
- [ ] **API测试是否覆盖正常和异常场景**
- [ ] **E2E测试是否覆盖核心业务流程**
- [ ] 测试工具和框架选择合理
- [ ] 测试环境配置完整
- [ ] 测试数据管理机制完善
- [ ] 测试覆盖率要求合理

## 模式对比

| 特性 | 新项目(--new) | 迭代(--iteration) |
|------|--------------|-------------------|
| 执行阶段 | 9个阶段 | 8个阶段 |
| 脚手架初始化 | ✅ 执行 | ⏭️ 跳过 |
| 适用场景 | 全新项目 | 功能迭代 |
| 输出文件 | 完整（含代码结构） | 仅设计文档 |
| 执行时间 | 较长 | 较短 |

## 相关命令

| 命令 | 功能 |
|------|------|
| `/analyze-requirement` | 需求分析 |
| `/design-prototype` | 原型设计 |
| `/generate-api-doc` | 生成API文档 |
| `/generate-sequence-diagram` | 生成时序图 |
| `/split-tasks` | 任务拆分 |
| `/develop-frontend` | 前端开发 |
| `/develop-backend` | 后端开发 |
| `/test-api` | API测试 |
| `/test-e2e` | E2E测试 |
| `/deploy` | 部署上线 |

## 下一步

执行 `/start-project` 后，可以：
1. **开始开发**：执行 `/develop-frontend` 或 `/develop-backend` 开始编写代码
2. **单独测试**：执行 `/test-api` 或 `/test-e2e` 进行测试
3. **按需调用**：单独调用各个命令进行特定阶段的工作

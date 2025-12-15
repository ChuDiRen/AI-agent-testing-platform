# Skills 索引

本目录包含通用的开发工作流 Skills，按类型分类组织，适用于任何技术栈。

## 目录结构

```
skills/
├── README.md                           # 本文件
├── workflows/                          # 工作流类
│   ├── project-bootstrap.md            # 项目启动工作流
│   ├── riper5-workflow.md              # RIPER-5 开发模式
│   └── task-splitting.md               # 任务拆分方法论
├── development/                        # 开发规范类
│   ├── frontend-development.md         # 前端开发规范
│   ├── backend-development.md          # 后端开发规范
│   └── code-review-checklist.md        # 代码复用检查
├── design/                             # 设计类
│   ├── prototype-design.md             # 原型设计
│   ├── api-documentation.md            # API 文档规范
│   └── database-design.md              # 数据库设计规范
└── testing/                            # 测试类
    ├── api-testing/                    # API 接口测试
    └── webapp-testing/                 # Web 应用测试
```

---

## 工作流 Skills (workflows/)

| Skill 名称 | 文件 | 描述 |
|-----------|------|------|
| 项目启动工作流 | `project-bootstrap.md` | 从零开始启动项目的标准化工作流（6阶段） |
| RIPER-5 开发模式 | `riper5-workflow.md` | 严格的五阶段开发协议 |
| 任务拆分 | `task-splitting.md` | 需求拆分为可执行任务的方法 |

---

## 开发规范 Skills (development/)

| Skill 名称 | 文件 | 描述 |
|-----------|------|------|
| 前端开发规范 | `frontend-development.md` | 通用前端开发规范和最佳实践 |
| 后端开发规范 | `backend-development.md` | 通用后端开发规范和最佳实践 |
| 代码复用检查 | `code-review-checklist.md` | 代码生成前的复用检查流程 |

---

## 设计 Skills (design/)

| Skill 名称 | 文件 | 描述 |
|-----------|------|------|
| 原型设计 | `prototype-design.md` | 高保真原型界面生成（整合 UI/UX Pro Max 设计规范） |
| API 文档生成 | `api-documentation.md` | API 接口文档生成和维护规范 |
| 数据库设计 | `database-design.md` | 数据库表结构设计规范 |

### 原型设计资源（来自 UI/UX Pro Max）
- **57 种 UI 样式**：Glassmorphism、Neumorphism、Minimalism、Brutalism 等
- **95 种配色方案**：按行业分类（SaaS、电商、医疗、金融科技等）
- **56 种字体配对**：精选 Google Fonts 组合，附带导入代码
- **98 条 UX 指南**：最佳实践、反模式、可访问性规则
- **参考来源**：[UI/UX Pro Max Skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)

---

## 测试 Skills (testing/)

| Skill 名称 | 目录 | 描述 |
|-----------|------|------|
| API 测试 | `api-testing/` | 使用 pytest + httpx 进行 API 接口自动化测试 |
| Web 应用测试 | `webapp-testing/` | 使用 Playwright 进行 Web 应用交互测试 |

---

## 架构关系

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills (知识库)                           │
│  定义"怎么做"的规范、模板和最佳实践                            │
├─────────────────────────────────────────────────────────────┤
│                          ↑ 被引用                            │
├─────────────────────────────────────────────────────────────┤
│                    Agents (智能体)                           │
│  定义"谁来做"，引用 Skills 中的规范                           │
├─────────────────────────────────────────────────────────────┤
│                          ↑ 被调用                            │
├─────────────────────────────────────────────────────────────┤
│                    Commands (命令)                           │
│  定义"做什么"，调用 Agents 执行任务                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 1. 项目初始化

使用 `workflows/project-bootstrap.md` 启动新项目

### 2. 原型设计

使用 `design/prototype-design.md` 快速生成原型界面

### 3. 任务拆分

使用 `workflows/task-splitting.md` 将需求拆分为可执行任务

### 4. 开发实施

- 前端：使用 `development/frontend-development.md`
- 后端：使用 `development/backend-development.md`

### 5. 复杂任务

使用 `workflows/riper5-workflow.md` 进行严格的变更控制

### 6. 代码检查

使用 `development/code-review-checklist.md` 避免重复开发

### 7. 测试验证

- API 测试：使用 `testing/api-testing/`
- E2E 测试：使用 `testing/webapp-testing/`

---

## 核心原则

1. **任务越小越细，代码质量越高**
2. **先出全部页面，再局部调整**
3. **代码生成前必须检查是否有现有功能可复用**
4. **每次完成任务后更新任务状态**
5. **API 变更必须同步更新文档**

---

## 技术栈无关

本 Skills 集合采用**技术栈无关**的设计理念：

- **前端**：适用于 Vue、React、Angular、Svelte 等任何框架
- **后端**：适用于 FastAPI、SpringBoot、Express、Go、Rust 等任何框架
- **数据库**：适用于 MySQL、PostgreSQL、MongoDB 等任何数据库

所有规范和流程都是通用的方法论，不绑定特定技术实现。

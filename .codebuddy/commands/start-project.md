---
description: 启动前后端分离项目的完整流程命令（智能体+Skills协作版 v4.0）
---

# 命令：start-project

## 功能描述

完整的项目启动流程，采用 **智能体 + Skills** 协作模式，从原始需求输入开始，通过调度专业智能体完成各阶段任务。

## 核心特性

- ✅ **智能体协作**：每个阶段由专业智能体负责，使用对应技能
- ✅ **团队协调器**：`team-orchestrator` 负责统筹调度
- ✅ **架构师审核**：`architect` 智能体在关键阶段自动审核
- ✅ **技能增强**：智能体使用 skills 提升输出质量
- ✅ **用户决策**：关键节点由用户选择

## 使用方式

```bash
# 方式1：简单启动，交互式收集需求
/start-project

# 方式2：指定模式启动
/start-project --new        # 新项目（完整10个阶段）
/start-project --iteration  # 迭代项目（跳过脚手架初始化）
```

---

## 智能体角色与职责

| 智能体 | 职责 | 关联技能 |
|--------|------|----------|
| `team-orchestrator` | 流程协调、进度跟踪、智能体调度 | - |
| `product-manager` | 需求分析、任务拆分 | `brainstorm`, `task-splitting` |
| `architect` | 架构设计、各阶段审核 | `architecture-design` |
| `frontend-developer` | 原型设计、前端开发 | `ui-ux-pro-max`, `vue3-frontend-dev` |
| `backend-developer` | 数据库设计、接口设计、后端开发 | `database-design`, `api-documentation`, `java-springboot-dev` |
| `test-automator` | API测试、E2E测试 | `api-testing`, `webapp-testing` |
| `code-reviewer` | 代码审查 | - |
| `deployment-specialist` | 部署上线 | `docker-deploy` |

---

## 完整流程概览（10个阶段）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 阶段1：需求收集                                                              │
│ 执行者：team-orchestrator                                                    │
│ └─ 输出：docs/requirement-raw.md                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段2：需求分析                                                              │
│ 执行者：product-manager + skill:brainstorm                                   │
│ 审核者：architect                                                            │
│ └─ 输出：docs/requirement.md                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段3：技术选型确认 ⭐用户决策点                                              │
│ 执行者：team-orchestrator                                                    │
│ └─ 输出：docs/tech-stack.md                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段4：原型设计 ⭐用户选择产品类型/行业/风格关键词                                │
│ 执行者：frontend-developer + skill:ui-ux-pro-max                            │
│ └─ 输出：prototypes/*.html + 设计系统文档                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段5：数据库设计                                                            │
│ 执行者：backend-developer + skill:database-design                            │
│ 审核者：architect                                                            │
│ └─ 输出：docs/database-design.md + sql/*.sql                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段6：接口设计                                                              │
│ 执行者：backend-developer + skill:api-documentation                          │
│ 审核者：architect                                                            │
│ └─ 输出：docs/api-docs/*.md                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段7：架构设计                                                              │
│ 执行者：architect + skill:architecture-design                                │
│ └─ 输出：docs/architecture.md                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段8：时序图设计                                                            │
│ 执行者：architect                                                            │
│ └─ 输出：docs/sequence-diagrams/*.md                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段9：任务拆分                                                              │
│ 执行者：product-manager + skill:task-splitting                               │
│ 审核者：architect                                                            │
│ └─ 输出：docs/tasks-*.md                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 阶段10：脚手架初始化（仅 --new 模式）                                         │
│ 执行者：frontend-developer + backend-developer                               │
│ └─ 输出：frontend/ + backend/                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⭐ 智能体调用规范（重要）

### 规范1：使用 task 工具调用智能体

```
调用格式：
task(
  subagent_name: "智能体名称",
  description: "任务简述",
  prompt: "详细任务描述，包含：
    1. 当前阶段和任务目标
    2. 输入信息（需求/设计/配置等）
    3. 需要使用的技能
    4. 输出文件路径和格式要求
    5. 验收标准"
)
```

### 规范2：任务 prompt 必须包含完整上下文

**❌ 错误示例**：
```
prompt: "请分析需求"
```

**✅ 正确示例**：
```
prompt: "
【阶段2：需求分析】

## 输入信息
原始需求文件：{project_dir}/docs/requirement-raw.md
技术选型：待定

## 任务要求
1. 使用 `use_skill` 工具加载 `brainstorm` 技能
2. 阅读原始需求文件
3. 输出结构化需求文档

## 输出要求
- 文件路径：{project_dir}/docs/requirement.md
- 文档结构：项目概述、用户角色、功能模块、用户场景、非功能需求
- 文档长度：100-200行（小型项目）

## 验收标准
- [ ] 包含所有必需章节
- [ ] 功能模块完整覆盖原始需求
- [ ] 用户场景可执行
"
```

### 规范3：智能体内部使用 use_skill 加载技能

智能体执行任务时：
```markdown
1. 首先使用 `use_skill` 工具加载对应技能
2. 根据技能指导完成任务
3. 输出文件到指定路径
4. 返回执行结果摘要
```

### 规范4：架构师审核流程

审核阶段（2/5/6/9）完成后，**立即调用架构师审核**：

```
task(
  subagent_name: "architect",
  prompt: "
【架构师审核：阶段N - xxx】

## 审核文件
{file_path}

## 审核要点
- [ ] 要点1
- [ ] 要点2
- [ ] 要点3

## 输出要求
1. 评级：✅通过 / ⚠️需调整
2. 优点（3条）
3. 调整项（如有，需具体说明）
4. 风险提示（如有）

## 如果需调整
直接修改文件，然后输出调整说明
"
)
```

### 规范5：智能体返回结果处理

每个智能体任务完成后，**协调器必须验证输出**：

```markdown
## 阶段N完成验证

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 智能体响应 | ✅/❌ | 是否正常返回 |
| 文件已生成 | ✅/❌ | 检查文件是否存在 |
| 内容完整 | ✅/❌ | 检查关键章节 |
| 架构师审核 | ✅/⚠️/跳过 | 审核结果 |

下一步：进入阶段N+1 / 修复问题后重试
```

---

## 详细执行流程

### 阶段1：需求收集
**执行者**：`team-orchestrator`（协调器自身处理）

#### 执行步骤
1. 询问用户项目名称
2. 收集需求信息（问答/文档/PRD）
3. 生成原始需求文件

#### 问答模板（如需）
```markdown
### 基础信息
1. 项目名称是什么？
2. 项目的目标用户是谁？
3. 预期的用户规模？（小型<100 / 中型100-1000 / 大型>1000）

### 功能需求
4. 主要功能模块有哪些？
5. 是否需要用户认证？
6. 是否需要权限管理？
7. 是否有特殊业务需求？（多租户/审批流程/报表等）
```

#### 输出
- `{project_dir}/docs/requirement-raw.md`

---

### 阶段2：需求分析 + 审核
**执行者**：`product-manager`  
**使用技能**：`brainstorm`  
**审核者**：`architect`

#### 协调器调用产品经理
```
task(
  subagent_name: "product-manager",
  description: "需求分析",
  prompt: "
【阶段2：需求分析】

## 项目信息
- 项目目录：{project_dir}
- 原始需求：{project_dir}/docs/requirement-raw.md

## 任务要求
1. 使用 use_skill 加载 brainstorm 技能
2. 阅读原始需求文件
3. 深度分析需求，输出结构化文档

## 输出文件
路径：{project_dir}/docs/requirement.md

## 文档结构
```markdown
# {项目名称} - 需求文档

## 1. 项目概述（5-10行）
## 2. 用户角色（每角色3-5行）
## 3. 功能模块（每模块10-20行）
## 4. 核心用户场景（3-5个）
## 5. 非功能需求（5-10行）
```

## 验收标准
- [ ] 覆盖原始需求所有要点
- [ ] 功能模块清晰可执行
- [ ] 用户场景包含前置条件、步骤、预期结果
"
)
```

#### 协调器调用架构师审核
```
task(
  subagent_name: "architect",
  description: "审核需求文档",
  prompt: "
【架构师审核：阶段2 - 需求分析】

## 审核文件
{project_dir}/docs/requirement.md

## 审核要点
- [ ] 功能模块是否完整覆盖原始需求
- [ ] 用户场景是否清晰可执行
- [ ] 非功能需求是否合理

## 输出要求
评级 + 优点 + 调整项（如有直接修改文件）
"
)
```

---

### 阶段3：技术选型确认 ⭐
**执行者**：`team-orchestrator`  
**用户操作**：**选择技术栈**

#### 使用 ask_followup_question 收集选择
```json
{
  "questions": [
    {
      "id": "backend",
      "question": "后端技术选择",
      "options": ["Java Spring Boot（推荐）", "Python FastAPI", "Node.js Express"],
      "multiSelect": false
    },
    {
      "id": "frontend", 
      "question": "前端技术选择",
      "options": ["Vue3 + Element Plus（推荐）", "Vue3 + Vant", "React + Ant Design"],
      "multiSelect": false
    },
    {
      "id": "database",
      "question": "数据库选择",
      "options": ["PostgreSQL（推荐）", "MySQL", "MongoDB"],
      "multiSelect": false
    }
  ]
}
```

#### 输出
- `{project_dir}/docs/tech-stack.md`（50行以内）

---

### 阶段4：原型设计 ⭐
**执行者**：`frontend-developer`
**使用技能**：`ui-ux-pro-max`
**用户操作**：**选择产品类型、行业、风格关键词**

#### 协调器调用前端开发者
```
task(
  subagent_name: "frontend-developer",
  description: "原型设计",
  prompt: "
【阶段4：原型设计】

## 项目信息
- 项目目录：{project_dir}
- 需求文档：{project_dir}/docs/requirement.md
- 技术选型：{project_dir}/docs/tech-stack.md
- 产品类型：{product_type}（如：SaaS、电商、仪表板等）
- 行业：{industry}（如：金融科技、医疗、教育等）
- 风格关键词：{style_keywords}（如：minimalism、glassmorphism、dark mode等）

## 任务要求
1. 使用 use_skill 加载 ui-ux-pro-max 技能
2. 使用技能的 search.py 生成设计系统：
   - 执行命令：python3 .codebuddy/skills/design/ui-ux-pro-max/scripts/search.py \"{product_type} {industry} {style_keywords}\" --design-system -p \"{project_name}\"
   - 获取设计系统：风格、配色、字体、效果
3. 根据设计系统生成HTML原型页面
4. 确保支持选定的技术栈（html-tailwind/React/Vue）

## 输出文件
目录：{project_dir}/prototypes/
- design-system.md（设计系统文档，包含风格、配色、字体等）
- css/styles.css（统一样式）
- js/main.js（交互逻辑）
- login.html（登录页）
- index.html（主框架+首页）
- {module}.html（各功能模块页面）

## 设计要求
- 基于生成的设计系统进行设计
- 统一的导航和布局
- 响应式设计
- 表单包含验证提示
- 列表包含分页
- 所有页面可在浏览器中预览
- 遵循UI/UX最佳实践（无emoji图标、SVG图标、适当的对比度等）

## 验收标准
- [ ] 覆盖所有功能模块
- [ ] 设计系统完整（风格、配色、字体、效果）
- [ ] UI风格统一
- [ ] 页面可正常预览
- [ ] 遵循无障碍设计原则
"
)
```

---

### 阶段5：数据库设计 + 审核
**执行者**：`backend-developer`  
**使用技能**：`database-design`  
**审核者**：`architect`

#### 协调器调用后端开发者
```
task(
  subagent_name: "backend-developer",
  description: "数据库设计",
  prompt: "
【阶段5：数据库设计】

## 项目信息
- 项目目录：{project_dir}
- 需求文档：{project_dir}/docs/requirement.md
- 技术选型：{project_dir}/docs/tech-stack.md

## 任务要求
1. 使用 use_skill 加载 database-design 技能
2. 根据需求设计数据库表结构
3. 生成设计文档和SQL脚本

## 输出文件
1. {project_dir}/docs/database-design.md
2. {project_dir}/sql/schema.sql
3. {project_dir}/sql/init-data.sql

## 文档结构
```markdown
# 数据库设计

## 1. ER图（Mermaid）
## 2. 表结构详情
## 3. 索引设计
## 4. 初始化数据
```

## 验收标准
- [ ] ER图完整正确
- [ ] 表结构规范（字段类型、约束、注释）
- [ ] 外键和索引合理
- [ ] SQL脚本可执行
"
)
```

---

### 阶段6：接口设计 + 审核
**执行者**：`backend-developer`  
**使用技能**：`api-documentation`  
**审核者**：`architect`

#### 协调器调用后端开发者
```
task(
  subagent_name: "backend-developer",
  description: "接口设计",
  prompt: "
【阶段6：接口设计】

## 项目信息
- 项目目录：{project_dir}
- 需求文档：{project_dir}/docs/requirement.md
- 数据库设计：{project_dir}/docs/database-design.md

## 任务要求
1. 使用 use_skill 加载 api-documentation 技能
2. 为每个功能模块设计RESTful接口
3. 生成API文档

## 输出文件
目录：{project_dir}/docs/api-docs/
- README.md（通用规范、认证方式、错误码）
- {module}-module.md（各模块接口）

## 接口格式
```markdown
## POST /api/xxx

**描述**：xxx
**权限**：xxx

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |

**响应示例**：
```json
{ "code": 0, "data": {} }
```
```

## 验收标准
- [ ] 覆盖所有功能模块
- [ ] 符合RESTful规范
- [ ] 请求/响应格式统一
- [ ] 包含权限说明
"
)
```

---

### 阶段7：架构设计
**执行者**：`architect`  
**使用技能**：`architecture-design`

#### 协调器调用架构师
```
task(
  subagent_name: "architect",
  description: "架构设计",
  prompt: "
【阶段7：架构设计】

## 项目信息
- 项目目录：{project_dir}
- 需求文档：{project_dir}/docs/requirement.md
- 技术选型：{project_dir}/docs/tech-stack.md
- 数据库设计：{project_dir}/docs/database-design.md
- API设计：{project_dir}/docs/api-docs/

## 任务要求
1. 使用 use_skill 加载 architecture-design 技能
2. 设计系统架构

## 输出文件
{project_dir}/docs/architecture.md

## 文档结构
```markdown
# 架构设计

## 1. 系统架构图（Mermaid）
## 2. 技术架构（分层说明）
## 3. 部署架构（Docker方案）
## 4. 模块划分
## 5. 安全设计
## 6. 缓存策略
```
"
)
```

---

### 阶段8：时序图设计
**执行者**：`architect`

#### 协调器调用架构师
```
task(
  subagent_name: "architect",
  description: "时序图设计",
  prompt: "
【阶段8：时序图设计】

## 项目信息
- 项目目录：{project_dir}
- 需求文档：{project_dir}/docs/requirement.md
- API设计：{project_dir}/docs/api-docs/

## 任务要求
1. 为核心业务流程设计时序图
2. 使用 Mermaid 语法

## 输出文件
目录：{project_dir}/docs/sequence-diagrams/
- README.md（时序图清单）
- login.md（用户登录）
- token-refresh.md（Token刷新）
- {核心CRUD}.md
- permission-check.md（权限校验）

## 验收标准
- [ ] 覆盖核心业务流程
- [ ] 时序正确
- [ ] 包含异常处理
"
)
```

---

### 阶段9：任务拆分 + 审核
**执行者**：`product-manager`  
**使用技能**：`task-splitting`  
**审核者**：`architect`

#### 协调器调用产品经理
```
task(
  subagent_name: "product-manager",
  description: "任务拆分",
  prompt: "
【阶段9：任务拆分】

## 项目信息
- 项目目录：{project_dir}
- 需求文档：{project_dir}/docs/requirement.md
- 技术选型：{project_dir}/docs/tech-stack.md
- API设计：{project_dir}/docs/api-docs/

## 任务要求
1. 使用 use_skill 加载 task-splitting 技能
2. 拆分前端、后端、测试任务

## 输出文件
1. {project_dir}/docs/tasks-frontend.md
2. {project_dir}/docs/tasks-backend.md
3. {project_dir}/docs/tasks-api-testing.md
4. {project_dir}/docs/tasks-e2e-testing.md

## 任务格式
```markdown
| 任务ID | 任务名称 | 优先级 | 工时 | 依赖 | 验收标准 |
|--------|---------|:------:|:----:|------|----------|
| FE-001 | xxx | P0 | 2h | 无 | xxx |
```

## 验收标准
- [ ] 任务颗粒度2-4小时
- [ ] 依赖关系正确
- [ ] 测试任务完整
"
)
```

---

### 阶段10：脚手架初始化
**仅 `--new` 模式执行**  
**执行者**：`frontend-developer` + `backend-developer`

#### 协调器并行调用
```
# 前端初始化
task(
  subagent_name: "frontend-developer",
  description: "前端脚手架初始化",
  prompt: "
【阶段10：前端脚手架初始化】

## 项目信息
- 项目目录：{project_dir}
- 技术选型：{project_dir}/docs/tech-stack.md

## 任务要求
1. 创建 Vue3 + TypeScript 项目
2. 配置路由、状态管理、UI组件库
3. 创建基础目录结构

## 执行命令
```bash
cd {project_dir}
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install element-plus axios pinia vue-router @vueuse/core
```

## 输出
{project_dir}/frontend/（可运行的前端项目）
"
)

# 后端初始化
task(
  subagent_name: "backend-developer",
  description: "后端脚手架初始化",
  prompt: "
【阶段10：后端脚手架初始化】

## 项目信息
- 项目目录：{project_dir}
- 技术选型：{project_dir}/docs/tech-stack.md
- 数据库设计：{project_dir}/docs/database-design.md

## 任务要求
根据技术选型创建后端项目：
- Spring Boot：使用 Spring Initializr 或手动创建
- FastAPI：创建项目结构 + pyproject.toml

## 输出
{project_dir}/backend/（可运行的后端项目）
"
)
```

---

## 最终输出文件结构

```
{project_name}/
├── docs/
│   ├── requirement-raw.md          # 原始需求
│   ├── requirement.md              # 结构化需求
│   ├── tech-stack.md               # 技术选型
│   ├── database-design.md          # 数据库设计
│   ├── architecture.md             # 架构设计
│   ├── tasks-frontend.md           # 前端任务
│   ├── tasks-backend.md            # 后端任务
│   ├── tasks-api-testing.md        # API测试任务
│   ├── tasks-e2e-testing.md        # E2E测试任务
│   ├── api-docs/                   # API文档
│   │   ├── README.md
│   │   └── {module}-module.md
│   └── sequence-diagrams/          # 时序图
│       ├── README.md
│       └── {场景}.md
├── prototypes/                     # HTML原型
│   ├── css/styles.css
│   ├── js/main.js
│   └── *.html
├── sql/
│   ├── schema.sql
│   └── init-data.sql
├── frontend/                       # 前端项目（--new模式）
└── backend/                        # 后端项目（--new模式）
```

---

## 用户决策点汇总

| 阶段 | 决策内容 | 是否必须 | 默认行为 |
|------|---------|---------|---------|
| 阶段1 | 提供原始需求 | ✅ 必须 | - |
| 阶段3 | 选择技术栈 | 推荐 | 使用系统推荐 |
| 阶段4 | 选择UI风格 | 推荐 | 现代简约 |

---

## 相关命令

| 命令 | 功能 | 调用智能体 | 使用技能 |
|------|------|-----------|----------|
| `/analyze-requirement` | 需求分析 | product-manager | brainstorm |
| `/design-prototype` | 原型设计 | frontend-developer | frontend-design |
| `/generate-api-doc` | API文档 | backend-developer | api-documentation |
| `/split-tasks` | 任务拆分 | product-manager | task-splitting |
| `/develop-frontend` | 前端开发 | frontend-developer | vue3-frontend-dev |
| `/develop-backend` | 后端开发 | backend-developer | java-springboot-dev |
| `/test-api` | API测试 | test-automator | api-testing |
| `/test-e2e` | E2E测试 | test-automator | webapp-testing |
| `/deploy` | 部署上线 | deployment-specialist | docker-deploy |

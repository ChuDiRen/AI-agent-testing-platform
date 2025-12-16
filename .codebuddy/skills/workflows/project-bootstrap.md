# 项目启动工作流 Skill

## 概述
本 Skill 提供从零开始启动一个完整项目的标准化工作流，自动引导完成从需求分析到开发准备的全过程。适用于任何技术栈。

## 适用场景
- 新项目启动
- 功能模块重构
- 独立子系统开发

---

## ⚠️ 核心原则（必须遵守）

> 1. **每个阶段必须完成所有输出物并通过检查点验证后，才能进入下一阶段**
> 2. **禁止跳过任何阶段或输出物**
> 3. **禁止在文档中标记"✅完成"但实际未生成文件**
> 4. **每个阶段结束时必须执行检查点验证，列出已生成的文件路径**
> 5. **使用跨平台兼容的命令（见下方命令规范）**

---

## 🖥️ 跨平台命令规范（必须遵守）

### 创建目录

| 操作系统 | 命令格式 |
|---------|---------|
| **Windows (PowerShell)** | `New-Item -ItemType Directory -Force -Path "path1", "path2", "path3"` |
| **macOS / Linux (Bash)** | `mkdir -p "path1" "path2" "path3"` |

**⚠️ 注意：PowerShell 的 `mkdir -p` 不支持多个参数！**

### 推荐方式：使用工具直接创建

**优先使用 `write_to_file` 工具创建文件，目录会自动创建，无需手动执行 mkdir 命令。**

```
# 推荐：直接写入文件，目录自动创建
write_to_file("project/doc/api/user-api.md", content)

# 不推荐：先创建目录再写文件
execute_command("mkdir ...")
write_to_file(...)
```

---

## 使用方式

### 快速启动
```prompt
使用 project-bootstrap skill 启动项目：[项目名称]

项目类型：[管理后台/移动端H5/小程序/API服务]
核心功能：
1. [功能1]
2. [功能2]
3. [功能3]

技术栈：
- 前端：[框架名称]
- 后端：[框架名称]
- 数据库：[数据库名称]
```

---

## 工作流阶段总览

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           项目启动工作流 6 阶段                                  │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  [1] 初始化 ──→ [2] 需求分析 ──→ [3] 原型设计 ──→ [4] 任务拆分                  │
│       ↓              ↓               ↓               ↓                         │
│    检查点1        检查点2         检查点3         检查点4                        │
│                                                                                │
│  [5] API设计 ──→ [6] 开发准备 ──→ 🎉 完成                                       │
│       ↓              ↓                                                         │
│    检查点5        检查点6                                                       │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 阶段输出物汇总

| 阶段 | 输出物 | 存放位置 | 必须 |
|-----|-------|---------|------|
| 1. 初始化 | README.md | 根目录 | ✅ |
| 2. 需求 | PRD.md | doc/PRD.md | ✅ |
| 2. 需求 | 数据库设计 | doc/database-design.md | ✅ |
| 2. 需求 | SQL 脚本 | sql/*.sql | ✅ |
| 3. 原型 | 设计规范 | doc/func.md（设计规范部分） | ✅ |
| 3. 原型 | 样式文件 | prototype/css/styles.css | ✅ |
| 3. 原型 | JS 交互 | prototype/js/main.js | ✅ |
| 3. 原型 | Mock 数据 | prototype/js/mock-data.js | ✅ |
| 3. 原型 | 主入口 | prototype/index.html | ✅ |
| 3. 原型 | 所有页面 | prototype/*.html | ✅ |
| 4. 任务拆分 | 前端任务 | doc/frontend-tasks.md | ✅ |
| 4. 任务拆分 | 后端任务 | doc/backend-tasks.md | ✅ |
| 5. API设计 | 接口文档 | doc/api/*.md | ✅ |
| 5. API设计 | 架构文档 | doc/architecture.md | ✅ |
| 6. 开发准备 | 功能清单 | doc/func.md | ✅ |

---

## 阶段1：项目初始化

### 输入信息收集
```prompt
请提供以下信息：
1. 项目名称：
2. 项目类型：[管理后台/移动端H5/小程序/API服务]
3. 项目规模：[小型/中型/大型]
4. 技术栈选择：
   - 前端框架：[可选]
   - UI组件库：[可选]
   - 后端框架：[可选]
   - 数据库：[可选]
```

### 开发模式选择

| 项目规模 | 推荐模式 | 目录结构 |
|---------|---------|---------|
| 小型 | 统一管理 | `project/frontend/` + `project/backend/` |
| 中大型 | 分离管理 | 独立仓库，不同编辑器窗口 |

### 目录创建方式

**推荐：直接使用 write_to_file 创建文件，目录自动生成**

```
# 直接写入 README.md，doc/ 目录会自动创建
write_to_file("{project}/README.md", content)
write_to_file("{project}/doc/.gitkeep", "")
write_to_file("{project}/sql/.gitkeep", "")
write_to_file("{project}/prototype/css/.gitkeep", "")
```

### 输出物
- [ ] 项目目录结构
- [ ] README.md

### 🔍 检查点1验证
```
执行验证：
□ 项目根目录已创建
□ doc/ 目录已创建
□ README.md 已生成

验证通过后输出：
✅ 阶段1完成 - 已创建文件：
  - {project}/README.md
  - {project}/doc/
```

---

## 阶段2：需求分析

### 需求文档生成提示词
```prompt
我现在需要做一个 {项目类型}，项目名称：{项目名称}

产品的功能包括：
1. {功能1}
2. {功能2}
3. {功能3}
...

请帮我完成一个产品需求文档，需要包含：

## 1. 项目概述
- 项目背景
- 目标用户
- 核心价值

## 2. 功能模块
- 模块划分
- 功能描述
- 优先级排序

## 3. 页面清单（重要！）
- 列出所有需要的页面
- 每个页面的路由
- 页面主要元素

## 4. 数据模型
- 实体关系
- 表结构设计
- 字段说明

## 5. 非功能需求
- 性能要求
- 安全要求
- 兼容性要求

注意：不要包含任何代码
```

### 输出物
- [ ] 产品需求文档 (`doc/PRD.md`)
- [ ] 数据库设计文档 (`doc/database-design.md`)
- [ ] SQL 脚本 (`sql/schema.sql`, `sql/init-data.sql`)

### 🔍 检查点2验证
```
执行验证：
□ doc/PRD.md 文件存在且内容完整
□ doc/database-design.md 文件存在
□ sql/schema.sql 文件存在
□ sql/init-data.sql 文件存在
□ PRD.md 中包含完整的页面清单

验证通过后输出：
✅ 阶段2完成 - 已创建文件：
  - doc/PRD.md
  - doc/database-design.md
  - sql/schema.sql
  - sql/init-data.sql

📋 从 PRD.md 提取的页面清单：
  1. {页面1} ({路由1})
  2. {页面2} ({路由2})
  3. ... (列出所有页面)
```

---

## 阶段3：原型设计（关键阶段！）

### ⚠️ 重要：必须生成所有页面，且包含完整交互

**从阶段2的页面清单中，为每个页面生成对应的 HTML 原型文件。**

---

### 步骤 3.1：🎨 设计风格选择（必须先完成）

**在生成任何页面之前，必须先让用户选择设计风格！**

向用户展示以下选项，等待确认后再继续：

```
请选择原型页面的设计风格：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 【一、UI 样式】请选择 1 个：

| 序号 | 样式名称 | 视觉效果 | 推荐场景 |
|:---:|---------|---------|---------|
| 1 | Minimalism（极简主义） | 大量留白、几何线条、清爽干净 | 企业应用、SaaS 平台、管理后台 |
| 2 | Glassmorphism（毛玻璃） | 透明模糊、层次感强、现代感 | 高端 SaaS、金融仪表盘、科技产品 |
| 3 | Neumorphism（新拟态） | 柔和凸起、内阴影、触感强 | 健康 App、冥想平台、智能家居 |
| 4 | Dark Mode（深色模式） | 深色背景、低对比、护眼 | 开发工具、视频平台、夜间应用 |
| 5 | Bento Grid（便当盒） | 网格布局、模块化卡片、信息密集 | 仪表盘、数据展示、门户首页 |
| 6 | Flat Design（扁平化） | 无阴影、纯色块、简洁明快 | 移动应用、工具类产品 |
| 7 | Claymorphism（粘土风） | 3D 柔和、圆润可爱 | 儿童产品、创意应用、游戏 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 【二、配色方案】请选择 1 个：

| 序号 | 方案名称 | 主色 | 辅色 | 强调色 | 推荐行业 |
|:---:|---------|:----:|:----:|:-----:|---------|
| 1 | SaaS 蓝 | #2563EB | #3B82F6 | #F97316 | SaaS、企业软件、管理系统 |
| 2 | 科技紫 | #7C3AED | #A78BFA | #F59E0B | AI 产品、科技公司、创新平台 |
| 3 | 商务深蓝 | #1E40AF | #3B82F6 | #10B981 | 金融科技、B2B、企业服务 |
| 4 | 清新绿 | #059669 | #10B981 | #F59E0B | 医疗健康、环保、教育 |
| 5 | 活力橙 | #EA580C | #F97316 | #2563EB | 电商、社交、娱乐 |
| 6 | 优雅粉 | #DB2777 | #EC4899 | #8B5CF6 | 美妆、时尚、女性产品 |
| 7 | 暗夜黑 | #1E293B | #334155 | #3B82F6 | 开发工具、专业软件、游戏 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 【三、字体配对】请选择 1 个：

| 序号 | 配对名称 | 标题字体 | 正文字体 | 风格特点 |
|:---:|---------|---------|---------|---------|
| 1 | Modern Professional | Poppins | Open Sans | 现代专业，适合企业 |
| 2 | Tech Startup | Space Grotesk | DM Sans | 科技感，适合创新产品 |
| 3 | Minimal Swiss | Inter | Inter | 极简中性，适合工具类 |
| 4 | Classic Elegant | Playfair Display | Lora | 优雅经典，适合高端品牌 |
| 5 | Developer Mono | JetBrains Mono | IBM Plex Sans | 代码风格，适合开发者 |
| 6 | Friendly Rounded | Nunito | Quicksand | 圆润友好，适合 C 端产品 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请回复您的选择，格式如：1-1-1（UI样式-配色方案-字体配对）

默认推荐：
- 管理后台：1-1-1（极简 + SaaS蓝 + Modern Professional）
- 数据仪表盘：5-3-3（便当盒 + 商务深蓝 + Minimal Swiss）
- 移动端 H5：6-5-6（扁平化 + 活力橙 + Friendly Rounded）
```

**⚠️ 等待用户确认后，必须立即将选择记录到 doc/func.md 中！**

### 步骤 3.1.1：记录用户选择（必须执行）

用户选择后，**立即**创建或更新 `doc/func.md` 文件：

```markdown
# 功能服务清单

## 项目信息
- 项目名称：{project-name}
- 创建时间：{date}

## 设计规范（用户已确认）

| 设计要素 | 用户选择 | 具体值 |
|---------|---------|-------|
| UI 样式 | {序号} - {样式名称} | {视觉效果描述} |
| 配色方案 | {序号} - {方案名称} | 主色: {主色}, 辅色: {辅色}, 强调色: {强调色} |
| 字体配对 | {序号} - {配对名称} | 标题: {标题字体}, 正文: {正文字体} |

### 配色详情（CSS 变量必须使用这些值）
- 主色（--primary-color）：{主色值}
- 主色悬停（--primary-hover）：{深一度的主色}
- 主色浅色（--primary-light）：{浅色背景}
- 辅色（--secondary-color）：{辅色值}
- 强调色（--accent-color）：{强调色值}
- 登录页渐变：{根据主色生成的渐变}
```

**⚠️ CSS 文件中的所有颜色必须严格使用 func.md 中记录的配色值！**

---

### 步骤 3.2：原型文件结构（必须完整）

```
prototype/
├── index.html          # 主入口（平铺展示所有页面）- 必须
├── css/
│   └── styles.css      # 样式文件（应用用户选择的风格）- 必须
├── js/
│   ├── main.js         # 交互逻辑（弹窗、Toast、表单验证）- 必须
│   └── mock-data.js    # Mock 数据（根据 PRD 数据模型定义）- 必须
├── login.html          # 登录页 - 必须（如有认证功能）
├── dashboard.html      # 仪表盘/首页 - 必须
├── {page1}.html        # 页面1 - 按 PRD 页面清单生成
├── {page2}.html        # 页面2 - 按 PRD 页面清单生成
├── ... (根据 PRD 中定义的所有页面)
```

### 步骤 3.3：原型必须包含的交互功能

**⚠️ 原型不仅是静态页面，必须包含完整的交互功能！**

#### 3.3.1 通用交互组件

| 组件 | 说明 | 必须 |
|-----|------|:----:|
| **Toast 提示** | 成功/错误/警告/信息提示 | ✅ |
| **Modal 弹窗** | 新增/编辑/删除确认弹窗 | ✅ |
| **用户下拉菜单** | 个人中心、退出登录（如有） | ✅ |
| **侧边栏/导航** | 菜单展开/收起（如有） | ✅ |
| **Tab 切换** | 多 Tab 页面（如有） | ✅ |
| **表单验证** | 必填项、格式验证 | ✅ |

#### 3.3.2 页面特定交互（根据项目类型选择）

| 页面类型 | 必须交互 |
|---------|---------|
| **登录页** | 验证码刷新、密码显示切换、登录验证 |
| **仪表盘** | 图表展示、统计卡片、快捷入口 |
| **列表页** | 搜索筛选、分页、批量操作、删除确认 |
| **表单页** | 表单验证、下拉选择、日期选择 |
| **树形页** | 树形勾选、全选/反选、展开/收起 |
| **日志页** | 详情弹窗、清空确认、导出功能 |
| **个人中心** | Tab 切换、头像上传、表单保存 |

#### 3.3.3 Mock 数据要求

**必须创建 `prototype/js/mock-data.js` 文件，根据 PRD 数据模型定义：**

```javascript
// Mock 数据模板（根据实际项目调整）
const MockData = {
  // 核心业务数据（根据 PRD 数据模型定义）
  // 每种数据类型至少 5-10 条
  entity1: [
    { id: 1, name: '数据1', status: 1, createTime: '2024-01-01' },
    // ...
  ],
  
  // 树形数据（如有）
  treeData: [
    { id: 1, name: '节点1', children: [...] },
    // ...
  ],
  
  // 下拉选项
  options: {
    status: [{ value: 1, label: '启用' }, { value: 0, label: '禁用' }],
    // ...
  },
  
  // 仪表盘统计数据
  dashboardStats: {
    cards: [...],
    chartData: {...}
  },
  
  // 日志数据（如有，至少 20 条）
  logs: [...]
};
```

### 步骤 3.4：原型设计提示词

```prompt
@prototype-design 

请根据需求文档 @doc/PRD.md 和设计规范 @doc/func.md 生成高保真原型界面。

## 用户选择的设计风格（从 func.md 读取）：
- UI 样式：{用户选择}
- 配色方案：{用户选择}
- 字体配对：{用户选择}

## 必须生成的文件：
1. prototype/css/styles.css - 统一样式（**必须使用 func.md 中的配色值**）
2. prototype/js/main.js - 通用交互逻辑（Toast、Modal、表单验证等）
3. prototype/js/mock-data.js - Mock 数据
4. prototype/index.html - 主入口，使用 iframe 平铺展示所有页面
5. 为 PRD.md 中列出的每个页面生成独立的 HTML 文件

## 页面清单（从 PRD.md 提取）：
1. {页面1} → prototype/{page1}.html
2. {页面2} → prototype/{page2}.html
3. {页面3} → prototype/{page3}.html
... (所有页面)

## 设计要求：
- **严格按照 func.md 中记录的配色方案**
- PC端最小宽度 1200px
- 使用 Lucide Icons 图标库
- 每个页面必须可独立预览
- **必须包含完整的交互功能（弹窗、Toast、表单验证等）**
- **必须使用 Mock 数据填充表格和列表**
```

### 输出物
- [ ] doc/func.md（包含用户选择的设计规范）
- [ ] prototype/css/styles.css（应用用户选择的风格）
- [ ] prototype/js/main.js（通用交互逻辑）
- [ ] prototype/js/mock-data.js（Mock 数据）
- [ ] prototype/index.html（主入口）
- [ ] prototype/{page1}.html
- [ ] prototype/{page2}.html
- [ ] ... (所有页面)

### 🔍 检查点3验证（关键！）
```
执行验证：
□ doc/func.md 存在且包含用户选择的设计规范
□ prototype/css/styles.css 存在且 CSS 变量与 func.md 中的配色一致
□ prototype/js/main.js 存在且包含 Toast、Modal、表单验证等功能
□ prototype/js/mock-data.js 存在且包含完整的 Mock 数据
□ prototype/index.html 存在
□ 对照 PRD.md 页面清单，验证每个页面的 HTML 文件都已生成：
  □ prototype/{page1}.html
  □ prototype/{page2}.html
  □ prototype/{page3}.html
  □ ... (逐一检查 PRD 中定义的所有页面)
□ index.html 中包含所有页面的 iframe 引用
□ 每个页面都包含必要的交互功能

验证通过后输出：
✅ 阶段3完成 - 已创建文件：
  - prototype/index.html
  - prototype/css/styles.css
  - prototype/js/main.js
  - prototype/js/mock-data.js
  - prototype/{page1}.html
  - prototype/{page2}.html
  - ... (列出所有生成的文件)

📊 原型完成统计：
  - PRD 中定义的页面数：N
  - 已生成的原型页面数：N
  - 完成率：100%

⚠️ 如果完成率不是 100%，禁止进入下一阶段！
```

---

## 阶段4：任务拆分

### 调用 task-splitting skill
```prompt
@task-splitting

请根据需求文档 @doc/PRD.md 和原型设计，拆分开发任务：

## 前端任务拆分
- 技术栈：{前端框架}
- 页面数量：{N} 个
- 组件复用策略

## 后端任务拆分
- 技术栈：{后端框架}
- 模块数量：{N} 个
- 分层架构
```

### 任务清单模板

```markdown
# {前端/后端}开发任务清单

## TASK-001 - {任务名称}
**状态：** 计划中
**预估工时：** {N} 小时
**依赖任务：** 无

### 任务描述
{详细描述}

### 验收标准
- [ ] {标准1}
- [ ] {标准2}

### 注意事项
- {注意点1}
- {注意点2}

---
```

### 输出物
- [ ] 前端任务清单 (`doc/frontend-tasks.md`)
- [ ] 后端任务清单 (`doc/backend-tasks.md`)

### 🔍 检查点4验证
```
执行验证：
□ doc/frontend-tasks.md 文件存在
□ doc/backend-tasks.md 文件存在
□ 任务清单包含 TASK 编号
□ 每个任务有验收标准

验证通过后输出：
✅ 阶段4完成 - 已创建文件：
  - doc/frontend-tasks.md (N 个任务)
  - doc/backend-tasks.md (N 个任务)
```

---

## 阶段5：API 接口设计

### 调用 api-documentation skill
```prompt
@api-documentation

请根据需求文档和任务清单，设计完整的 API 接口规范：

## 设计要求
1. 列出所有需要的接口
2. 按模块分组
3. 统一响应格式
4. 定义 Mock 数据结构（JSON 格式，写在文档中）

## 输出格式
- 接口文档：doc/api/{module}-api.md（包含请求/响应示例）
- 架构文档：doc/architecture.md（系统架构图）
```

### 统一响应格式
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 分页响应格式
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```

### 输出物
- [ ] API 接口文档 (`doc/api/*.md`)
- [ ] 系统架构文档 (`doc/architecture.md`)

### 🔍 检查点5验证
```
执行验证：
□ doc/api/ 目录存在
□ 至少有一个 API 文档文件
□ API 文档包含请求/响应示例
□ doc/architecture.md 存在

验证通过后输出：
✅ 阶段5完成 - 已创建文件：
  - doc/api/{module1}-api.md
  - doc/api/{module2}-api.md
  - doc/architecture.md
  - ... (列出所有 API 文档)
```

---

## 阶段6：开发准备

### 更新功能清单文档

在阶段3创建的 `doc/func.md` 基础上，补充完整的功能服务清单：

```markdown
# 功能服务清单

## 项目信息
- 项目名称：{project-name}
- 创建时间：{date}
- 技术栈：{tech-stack}

## API 接口文档

| 模块 | 文档路径 | 接口数量 | 状态 |
|-----|---------|---------|------|
| {模块1} | doc/api/{module1}-api.md | N | ✅ 已完成 |
| {模块2} | doc/api/{module2}-api.md | N | ✅ 已完成 |
| ... | ... | ... | ... |

## 设计规范（用户已确认）
（保留阶段3的内容）

## 页面清单

| 序号 | 页面名称 | 路由路径 | 原型文件 | 状态 |
|-----|---------|---------|---------|------|
| 1 | {页面1} | {路由1} | {page1}.html | ✅ 已完成 |
| 2 | {页面2} | {路由2} | {page2}.html | ✅ 已完成 |
| ... | ... | ... | ... | ... |

## 权限标识清单（如有权限功能）

### {模块名} ({module})
| 权限标识 | 说明 | 类型 |
|---------|------|-----|
| {module}:list | {模块}列表 | 菜单 |
| {module}:add | 新增{模块} | 按钮 |
| ... | ... | ... |

## 前端服务规划

### API 层 (api/)
| 文件 | 功能 | 方法 |
|-----|------|------|
| api/{module1}.ts | {模块1}接口 | getList, create, update, delete |
| api/{module2}.ts | {模块2}接口 | ... |

### Store 层 (stores/)
| 文件 | 功能 | 状态 |
|-----|------|------|
| stores/{module}.ts | {模块}状态 | {状态字段列表} |

### 组件层 (components/)
| 文件 | 功能 | 复用场景 |
|-----|------|---------| 
| components/{Component1} | {功能描述} | {使用场景} |

## 后端服务规划

### Controller 层 (routers/)
| 文件 | 功能 | 路由前缀 |
|-----|------|---------|
| routers/{module1}.py | {模块1}接口 | /api/{module1} |

### Service 层 (services/)
| 文件 | 功能 | 方法 |
|-----|------|------|
| services/{module1}_service.py | {模块1}服务 | get_list, create, update, delete |

### Repository 层 (repositories/)
| 文件 | 功能 | 方法 |
|-----|------|------|
| repositories/{module1}_repo.py | {模块1}数据访问 | get_by_id, get_list |

## 数据库表清单

| 表名 | 说明 | 状态 |
|-----|------|------|
| {table1} | {表1说明} | ✅ 已设计 |
| {table2} | {表2说明} | ✅ 已设计 |
| ... | ... | ... |

## 文档清单

| 文档 | 路径 | 状态 |
|-----|------|------|
| 产品需求文档 | doc/PRD.md | ✅ 已完成 |
| 数据库设计文档 | doc/database-design.md | ✅ 已完成 |
| 功能清单文档 | doc/func.md | ✅ 已完成 |
| 系统架构文档 | doc/architecture.md | ✅ 已完成 |
| 前端任务清单 | doc/frontend-tasks.md | ✅ 已完成 |
| 后端任务清单 | doc/backend-tasks.md | ✅ 已完成 |
| API 接口文档 | doc/api/*.md | ✅ 已完成 |

## 原型清单

| 文件 | 路径 | 状态 |
|-----|------|------|
| 原型主入口 | prototype/index.html | ✅ 已完成 |
| 全局样式 | prototype/css/styles.css | ✅ 已完成 |
| 交互逻辑 | prototype/js/main.js | ✅ 已完成 |
| Mock 数据 | prototype/js/mock-data.js | ✅ 已完成 |
| 页面原型 | prototype/{page}.html | ✅ 已完成 |
```

### 🔍 检查点6验证（最终验证）
```
执行验证：
□ doc/func.md 文件存在且内容完整

最终项目结构验证：
□ README.md
□ doc/PRD.md
□ doc/database-design.md
□ doc/frontend-tasks.md
□ doc/backend-tasks.md
□ doc/func.md
□ doc/architecture.md
□ doc/api/*.md（根据模块数量）
□ sql/schema.sql
□ sql/init-data.sql
□ prototype/index.html
□ prototype/css/styles.css
□ prototype/js/main.js
□ prototype/js/mock-data.js
□ prototype/*.html（根据 PRD 页面清单）

验证通过后输出：
✅ 阶段6完成 - 项目启动流程全部完成！

📁 完整项目结构：
{project}/
├── README.md
├── doc/
│   ├── PRD.md
│   ├── database-design.md
│   ├── frontend-tasks.md
│   ├── backend-tasks.md
│   ├── func.md
│   ├── architecture.md
│   └── api/
│       └── {module}-api.md（按模块生成）
├── sql/
│   ├── schema.sql
│   └── init-data.sql
└── prototype/
    ├── index.html
    ├── css/styles.css
    ├── js/
    │   ├── main.js
    │   └── mock-data.js
    └── {page}.html（按 PRD 页面清单生成）

🎉 可以开始执行开发任务！
```

---

## 后续流程

完成 project-bootstrap 后，进入开发阶段：

```
project-bootstrap 完成
        ↓
┌───────┴───────┐
↓               ↓
前端开发         后端开发
↓               ↓
└───────┬───────┘
        ↓
    前后端联调
        ↓
    测试部署
```

### 开发阶段提示词
```prompt
@frontend-development 执行前端任务 TASK-FE-001

@backend-development 执行后端任务 TASK-BE-001
```

### 联调阶段提示词
```prompt
后端服务地址：http://xxx:8000
请关闭 Mock 模式，开始前后端联调
```

### 测试阶段提示词
```prompt
@api-testing 执行接口自动化测试

@webapp-testing 执行端到端测试
```

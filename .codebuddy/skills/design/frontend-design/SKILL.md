---
name: frontend-design
description: 高质量前端界面设计与高保真原型构建指南。适用于构建 Web 组件、复杂页面、仪表板，或根据 PRD 生成全功能原型。强调现代美学、用户体验、代码质量及完整的工程化结构。
---

# Frontend Design & Prototyping - 前端设计与原型指南

## 1. 核心理念 (Core Philosophy)

**"Code as Design"**：在编写代码之前，必须先确立设计语言。拒绝平庸的 AI 生成感，追求专业、独特且符合用户预期的视觉体验。

### 设计决策四要素
1.  **目标 (Goal)**：是展示型（Landing Page）、功能型（Dashboard）还是沉浸型（Game/Art）？
2.  **受众 (Audience)**：B2B 专业用户需要高效清晰，Gen-Z 用户偏好大胆创新。
3.  **约束 (Constraints)**：技术栈限制、响应式要求、无障碍标准。
4.  **美学 (Aesthetics)**：选择一种明确的视觉风格，不要混搭冲突的元素。

---

## 2. 视觉美学体系 (Visual Aesthetics)

### 风格指南 (Style Guide)

| 风格流派 | 视觉特征 | 推荐技术栈/类名特征 | 适用场景 |
|:---|:---|:---|:---|
| **Modern SaaS** | 清晰层级、微妙阴影、充足留白 | `shadow-sm`, `bg-white`, `text-slate-900` | 管理后台、B2B 工具 |
| **Glassmorphism** | 背景模糊、半透明层、鲜艳背景光 | `backdrop-blur-md`, `bg-white/10`, `border-white/20` | 仪表盘、加密货币、Web3 |
| **Neo-Brutalism** | 粗边框、高饱和度、无阴影、复古字体 | `border-2`, `border-black`, `shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]` | 创意机构、个人博客、DTC 品牌 |
| **Dark Mode Tech** | 深灰背景、霓虹点缀、发光效果 | `bg-slate-900`, `text-cyan-400`, `shadow-cyan-500/50` | 开发者工具、游戏、AI 应用 |
| **Swiss Design** | 强网格系统、巨型排版、无衬线 | `grid`, `text-6xl`, `font-bold`, `tracking-tighter` | 营销页面、画廊 |

### 配色策略 (Color Strategy)

*自动推断规则：若用户未指定，根据项目类型选择：*

- **管理后台**: `SaaS Blue` (#2563EB) + `Slate` (中性灰) → 专业、冷静
- **电商/C端**: `Vibrant Orange` (#EA580C) 或 `Rose` (#E11D48) → 活力、转化
- **AI/科技**: `Violet` (#7C3AED) + `Indigo` (#4F46E5) → 未来感、智慧
- **医疗/教育**: `Teal` (#0D9488) 或 `Sky` (#0EA5E9) → 信任、平和

### 字体系统 (Typography)

- **Heading**: 选用具有个性的字体 (如 `Space Grotesk`, `Outfit`, `Playfair Display`)
- **Body**: 选用高易读性字体 (如 `Inter`, `Plus Jakarta Sans`, `Satoshi`)
- **Code**: 选用现代等宽字体 (如 `JetBrains Mono`, `Fira Code`)

---

## 3. 实施工作流 (Implementation Workflow)

### 场景 A：高保真原型开发 (Prototyping)

*目标：快速生成可交互、结构完整的静态演示站。*

#### 关键原则

1.  **全量生成**：PRD 提及的所有关键页面必须全部产出，严禁"占位符"页面
2.  **数据仿真**：必须创建 `mock-data.js`，使用真实感的 Mock 数据填充界面，拒绝 `Lorem Ipsum`
3.  **独立运行**：产物必须是标准的 HTML/CSS/JS 结构，无需构建工具即可在浏览器打开
4.  **使用文件操作工具**：优先使用 `write_to_file` 和 `replace_in_file` 工具创建和修改文件

#### 文件结构规范

```text
project-root/
├── index.html          # 导航入口/Landing页
├── css/
│   ├── output.css      # (可选) 如果用 Tailwind
│   └── styles.css      # 自定义样式
├── js/
│   ├── main.js         # 通用交互逻辑 (Sidebar, Modal, Toast)
│   ├── mock-data.js    # 仿真数据源 (JSON objects)
│   └── charts.js      # (可选) 图表渲染逻辑
├── assets/             # 图片与图标资源
└── pages/              # 功能页面
    ├── login.html
    ├── dashboard.html
    └── settings.html
```

#### 原型设计检查清单

在交付原型前，必须完成以下检查：

- [ ] **页面完整性**：PRD 中定义的所有页面都已创建
- [ ] **导航结构**：页面之间的导航链接正确
- [ ] **视觉一致性**：所有页面使用统一的设计语言
- [ ] **响应式布局**：在移动端和桌面端都能正常显示
- [ ] **交互实现**：关键交互（如模态框、下拉菜单）可用
- [ ] **Mock 数据**：使用真实感的模拟数据

### 场景 B：前端组件开发 (Component Dev)

*目标：构建可复用、健壮的 UI 组件 (React/Vue/Web Components)。*

#### 关键原则

1.  **Props 定义**：明确组件的接口，包含类型定义 (TypeScript 优先)
2.  **状态管理**：区分内部 UI 状态 (State) 和外部数据 (Props)
3.  **组合性**：优先使用 Composition (Slot/Children) 而非复杂的配置对象

---

## 4. 交互与体验规范 (UX & Interaction)

### 微交互 (Micro-interactions)

- **Hover 态**：所有可点击元素必须有 Hover 效果 (颜色变化、上浮、发光)
- **Active 态**：点击时应有按压效果 (`scale-95` 或 变暗)
- **Focus 态**：键盘聚焦时必须有清晰的轮廓 (`ring-2`)，确保无障碍访问
- **Loading**：数据加载时必须展示 Skeleton (骨架屏) 或 Spinner，禁止留白

### 反馈机制 (Feedback)

- **Toast**: 操作成功/失败的轻量级提示（右上角或底部居中）
- **Modal**: 破坏性操作（删除、退出）必须二次确认
- **Validation**: 表单输入必须有实时或提交时的错误提示，且提示语要具体

### 响应式设计 (Responsive)

- **Mobile First**: 默认样式适配移动端，使用 `@media (min-width)` 适配大屏
- **断点策略**:
    - `< 640px`: 单栏布局，隐藏次要信息，使用汉堡菜单
    - `> 1024px`: 侧边栏展开，多栏 Grid 布局，展示完整数据表格

---

## 5. 反模式警告 (Anti-Patterns)

```diff
❌ 错误做法：
- 使用系统默认字体 (Times New Roman, Arial)
- 纯黑 (#000000) 或纯白 (#FFFFFF) 的高对比度导致视觉疲劳 (应使用 #1a1a1a, #f8fafc)
- 仅依靠颜色传达状态 (红/绿)，忽略色盲用户 (应配合图标/文字)
- "Lorem ipsum" 满天飞，不体现业务上下文
- 按钮没有 hover/active 状态，像一张图片
- 使用命令行创建文件 (如 PowerShell)，应优先使用文件操作工具

✅ 正确做法：
+ 建立 CSS 变量系统 (--primary, --surface, --text-main)
+ 统一的圆角和间距系统 (4px, 8px, 16px, 24px)
+ 语义化的 HTML 标签 (<nav>, <main>, <article>, <button> vs <div>)
+ 图片和媒体元素必须有 alt 属性
+ 使用 `write_to_file` 和 `replace_in_file` 工具创建和修改文件
```

---

## 6. 自查清单 (Self-Check)

在交付代码前，请按以下标准核对：

- [ ] **视觉一致性**：字体、颜色、圆角、阴影是否遵循既定风格？
- [ ] **内容真实性**：是否使用了符合业务场景的 Mock 数据？
- [ ] **交互完整性**：Hover/Active/Focus 状态是否齐全？Toast/Modal 是否可用？
- [ ] **结构完整性**：是否包含了所有必要的 HTML/CSS/JS 文件？入口文件 `index.html` 是否存在？
- [ ] **响应式检查**：在 375px (Mobile) 和 1440px (Desktop) 下是否都布局正常？
- [ ] **文件操作规范**：是否使用了 `write_to_file` 和 `replace_in_file` 工具？

---
description: 使用ui-ux-pro-max技能设计高保真原型的命令
---

# 命令：design-prototype

## 功能描述

使用 **ui-ux-pro-max** 技能根据需求文档快速生成高保真HTML原型界面，支持移动端和PC端设计。该技能提供50+种风格、97种配色方案、57种字体搭配等专业设计指导。

## 核心特性

- ✅ **智能设计系统**：自动生成完整的设计系统（风格、配色、字体、效果）
- ✅ **多风格支持**：glassmorphism、minimalism、dark mode、brutalism等50+种风格
- ✅ **多技术栈**：支持html-tailwind、React、Vue、Next.js等
- ✅ **专业级质量**：遵循无障碍设计原则、响应式设计、最佳UI/UX实践
- ✅ **设计文档**：输出完整的设计系统文档和HTML原型

## 使用方式

```
/design-prototype
```

或

```
/design-prototype <产品类型> <行业> <风格关键词>
```

## 参数说明

**必选参数**：
- 产品类型：SaaS、电商、仪表板、管理后台、登录页、Landing page等
- 行业：金融科技、医疗、教育、游戏、企业服务等
- 风格关键词：minimalism、glassmorphism、dark mode、brutalism等

**可选参数**：
- `--stack=html-tailwind` - 技术栈选择（默认：html-tailwind，可选：react、vue、nextjs、shadcn）
- `--mobile` - 移动端设计
- `--desktop` - PC端设计
- `--with-real-images` - 使用真实图片（需要提供图片URL）

## 执行流程

### 1. 需求分析
- 分析核心功能点
- 识别关键页面
- 确定交互逻辑

### 2. 使用 ui-ux-pro-max 生成设计系统
- 执行命令：`python3 .codebuddy/skills/design/ui-ux-pro-max/scripts/search.py "{product_type} {industry} {style_keywords}" --design-system -p "{project_name}"`
- 获取设计系统：风格、配色、字体、效果、组件建议
- 生成设计系统文档

### 3. 页面规划
- 确定页面列表
- 设计信息架构
- 规划导航结构

### 4. 原型实现
- 根据设计系统生成HTML原型代码
- 应用样式和组件
- 添加交互效果
- 确保无障碍和响应式

### 5. 输出交付
- 生成完整HTML文件
- 提供设计系统文档
- 生成设计说明文档
- 提供预览方式

## 输出格式

生成以下文件保存在 `prototypes/` 目录：

```
prototypes/
├── design-system.md          # 设计系统文档
├── index.html               # 主入口（汇总所有页面）
├── home.html                # 首页
├── login.html               # 登录页
├── product-list.html        # 商品列表
├── product-detail.html      # 商品详情
├── cart.html               # 购物车
├── css/
│   └── styles.css           # 统一样式
└── js/
    └── main.js             # 交互逻辑
```

## 设计规范

### 设计系统（来自 ui-ux-pro-max）
- **风格**：glassmorphism、minimalism、brutalism、neumorphism、bento grid、dark mode等
- **配色**：97种专业配色方案，支持浅色/深色模式
- **字体**：57种字体搭配方案
- **效果**：50+种UI效果和动画
- **组件**：按钮、表单、卡片、表格、图表等

### 移动端设计
- 模拟iPhone 15 Pro尺寸（393x852px）
- 圆角设计，模拟真实手机界面
- 添加iOS状态栏
- 底部Tab导航栏

### PC端设计
- 响应式布局
- 支持主流分辨率（1920x1080、1366x768等）
- 侧边栏导航
- 顶部功能栏

### UI组件
- 使用 Tailwind CSS 进行样式设计
- 集成SVG图标（Heroicons/Lucide）
- 避免使用emoji图标
- 统一的交互状态（hover、focus、active）

### 无障碍设计
- 颜色对比度至少4.5:1
- 所有交互元素可访问
- 键盘导航支持
- ARIA标签和语义化HTML

## 示例

```
/design-prototype SaaS 仪表板 金融科技 minimalism glassmorphism
```

这将：
1. 使用ui-ux-pro-max生成适合"金融科技SaaS仪表板"的设计系统
2. 应用minimalism和glassmorphism风格
3. 生成高保真HTML原型页面

## 设计系统生成流程

### 步骤1：生成设计系统
```bash
python3 .codebuddy/skills/design/ui-ux-pro-max/scripts/search.py \
  "SaaS dashboard fintech minimalism glassmorphism" \
  --design-system \
  -p "My Dashboard"
```

**输出示例**：
- Pattern: Modern SaaS Dashboard
- Style: Glassmorphism + Minimalism
- Colors: Primary (#2563EB), Secondary (#64748B), Accent (#10B981)
- Typography: Inter + JetBrains Mono
- Effects: Glass cards, subtle shadows, smooth transitions
- Anti-patterns to avoid: Overuse of gradients, emojis as icons

### 步骤2：补充详细搜索（可选）
```bash
# 获取UX最佳实践
python3 .codebuddy/skills/design/ui-ux-pro-max/scripts/search.py \
  "accessibility animation" \
  --domain ux

# 获取图表建议
python3 .codebuddy/skills/design/ui-ux-pro-max/scripts/search.py \
  "real-time data" \
  --domain chart
```

### 步骤3：根据技术栈实现
```bash
# 获取技术栈特定指导
python3 .codebuddy/skills/design/ui-ux-pro-max/scripts/search.py \
  "layout responsive form" \
  --stack html-tailwind
```

### 步骤4：生成原型
根据获取的设计系统生成HTML原型页面。

## 交互说明

- **index.html**：使用iframe嵌入所有页面，平铺展示
- **真实图片**：可从Unsplash、Pexels等图库获取
- **交互效果**：按钮点击、页面切换、悬停反馈等基本交互
- **设计文档**：design-system.md包含完整设计规范

## 质量检查清单

交付前验证以下项目：

### 视觉质量
- [ ] 无emoji图标（使用SVG）
- [ ] 图标来自统一集合（Heroicons/Lucide）
- [ ] 悬停状态不导致布局偏移
- [ ] 使用主题颜色直接（不使用var()）

### 交互
- [ ] 所有可点击元素有cursor-pointer
- [ ] 悬停状态提供清晰视觉反馈
- [ ] 过渡平滑（150-300ms）
- [ ] 键盘导航可见焦点状态

### 浅色/深色模式
- [ ] 浅色模式文本对比度≥4.5:1
- [ ] 玻璃/透明元素在浅色模式可见
- [ ] 边框在两种模式下都可见
- [ ] 两种模式都经过测试

### 布局
- [ ] 浮动元素有适当边缘间距
- [ ] 内容不隐藏在固定导航栏后面
- [ ] 响应式在375px、768px、1024px、1440px下正常
- [ ] 移动端无水平滚动

### 无障碍
- [ ] 所有图片有alt文本
- [ ] 表单输入有标签
- [ ] 颜色不是唯一指示器
- [ ] 遵循prefers-reduced-motion

## 相关命令

- `/analyze-requirement` - 分析需求
- `/start-project` - 启动项目（包含原型设计阶段）
- `/split-tasks` - 拆分任务
- `use_skill("ui-ux-pro-max")` - 直接使用技能

## 技术栈支持

ui-ux-pro-max技能支持以下技术栈：

| 技术栈 | 说明 | 推荐场景 |
|--------|------|---------|
| `html-tailwind` | Tailwind工具类、响应式、无障碍（默认）| 原型设计、快速开发 |
| `react` | 状态管理、hooks、性能、模式 | React项目 |
| `nextjs` | SSR、路由、图片、API路由 | Next.js项目 |
| `vue` | Composition API、Pinia、Vue Router | Vue项目 |
| `svelte` | Runes、stores、SvelteKit | Svelte项目 |
| `swiftui` | 视图、状态、导航、动画 | iOS应用 |
| `react-native` | 组件、导航、列表 | 移动应用 |
| `flutter` | 组件、状态、布局、主题 | 移动应用 |
| `shadcn` | shadcn/ui组件、主题、表单、模式 | React + shadcn项目 |

## 注意事项

1. **优先使用ui-ux-pro-max技能**：该技能提供专业级设计指导，质量远超手动设计
2. **生成完整设计系统**：使用--design-system标志获取完整设计规范
3. **遵循最佳实践**：避免常见UI问题（emoji图标、低对比度、布局偏移等）
4. **多技术栈支持**：根据项目需求选择合适的技术栈
5. **迭代优化**：如第一版不符合预期，可尝试不同的关键词组合

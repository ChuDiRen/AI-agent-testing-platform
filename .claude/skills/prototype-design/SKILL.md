# 原型设计技能

## 触发条件
- 关键词：原型、设计稿、UI设计、界面设计、交互设计、Figma
- 场景：当用户需要设计产品原型或界面时

## 核心规范

### 规范1：页面布局结构

```html
<!-- 标准后台管理布局 -->
<div class="layout">
  <!-- 顶部导航 -->
  <header class="header">
    <div class="logo">AI 测试平台</div>
    <nav class="nav-menu">...</nav>
    <div class="user-info">...</div>
  </header>
  
  <div class="main-container">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <nav class="side-menu">...</nav>
    </aside>
    
    <!-- 主内容区 -->
    <main class="content">
      <!-- 面包屑 -->
      <div class="breadcrumb">...</div>
      
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>页面标题</h1>
        <div class="actions">...</div>
      </div>
      
      <!-- 内容区域 -->
      <div class="page-content">
        ...
      </div>
    </main>
  </div>
</div>
```

### 规范2：常用页面模板

```
1. 列表页模板
┌─────────────────────────────────────────────────────┐
│ 页面标题                              [新增] [导出] │
├─────────────────────────────────────────────────────┤
│ 搜索条件区域                                        │
│ [关键词    ] [状态 ▼] [日期范围    ] [搜索] [重置] │
├─────────────────────────────────────────────────────┤
│ □ │ ID │ 名称     │ 状态   │ 创建时间   │ 操作    │
│ □ │ 1  │ 测试用例1│ 启用   │ 2024-01-01 │ 编辑 删除│
│ □ │ 2  │ 测试用例2│ 禁用   │ 2024-01-02 │ 编辑 删除│
├─────────────────────────────────────────────────────┤
│                    < 1 2 3 4 5 >  共 100 条        │
└─────────────────────────────────────────────────────┘

2. 详情页模板
┌─────────────────────────────────────────────────────┐
│ ← 返回  详情页标题                    [编辑] [删除] │
├─────────────────────────────────────────────────────┤
│ 基本信息                                            │
│ ┌─────────────────┬─────────────────┐              │
│ │ 名称：测试用例1  │ 状态：启用       │              │
│ │ 创建人：admin    │ 创建时间：...    │              │
│ └─────────────────┴─────────────────┘              │
├─────────────────────────────────────────────────────┤
│ [基本信息] [执行记录] [关联数据]                    │
│ Tab 内容区域                                        │
└─────────────────────────────────────────────────────┘

3. 表单页模板
┌─────────────────────────────────────────────────────┐
│ ← 返回  新增/编辑                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│     名称 *    [                              ]      │
│                                                     │
│     描述      [                              ]      │
│               [                              ]      │
│                                                     │
│     状态 *    ○ 启用  ○ 禁用                       │
│                                                     │
│     分类      [请选择                        ▼]     │
│                                                     │
│                          [取消]  [保存]             │
└─────────────────────────────────────────────────────┘
```

### 规范3：组件设计规范

```css
/* 颜色规范 */
:root {
  /* 主色 */
  --primary-color: #1890ff;
  --primary-hover: #40a9ff;
  --primary-active: #096dd9;
  
  /* 功能色 */
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #ff4d4f;
  --info-color: #1890ff;
  
  /* 中性色 */
  --text-primary: #262626;
  --text-secondary: #8c8c8c;
  --text-disabled: #bfbfbf;
  --border-color: #d9d9d9;
  --background-color: #f5f5f5;
  
  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* 圆角 */
  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 8px;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.15);
}
```

### 规范4：交互设计规范

```markdown
## 按钮交互
- 主按钮：用于主要操作，每个区域最多一个
- 次按钮：用于次要操作
- 文字按钮：用于弱化操作
- 危险按钮：用于删除等危险操作，需二次确认

## 表单交互
- 必填项标记 * 号
- 实时校验，失去焦点时触发
- 错误提示显示在输入框下方
- 提交时显示 loading 状态

## 列表交互
- 支持多选操作
- 支持批量操作
- 删除需二次确认
- 空状态显示引导

## 反馈交互
- 操作成功：轻提示 (Toast)
- 操作失败：错误提示 + 原因
- 加载中：骨架屏或 loading
- 确认操作：Modal 对话框
```

### 规范5：响应式设计

```css
/* 断点定义 */
/* 移动端: < 768px */
/* 平板: 768px - 1024px */
/* 桌面: > 1024px */

/* 移动端优先 */
.container {
  padding: 16px;
}

@media (min-width: 768px) {
  .container {
    padding: 24px;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* 栅格系统 */
.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -8px;
}

.col {
  padding: 0 8px;
  flex: 0 0 100%;
}

@media (min-width: 768px) {
  .col-md-6 { flex: 0 0 50%; }
  .col-md-4 { flex: 0 0 33.33%; }
  .col-md-3 { flex: 0 0 25%; }
}
```

### 规范6：状态设计

```markdown
## 页面状态
1. 加载中 - 骨架屏/Spinner
2. 空状态 - 插图 + 文案 + 操作按钮
3. 错误状态 - 错误图标 + 文案 + 重试按钮
4. 成功状态 - 成功图标 + 文案

## 组件状态
- 默认状态 (Default)
- 悬停状态 (Hover)
- 聚焦状态 (Focus)
- 激活状态 (Active)
- 禁用状态 (Disabled)
- 加载状态 (Loading)
- 错误状态 (Error)
```

### 规范7：原型工具使用

```markdown
## Figma 组件库结构
├── 🎨 Design System
│   ├── Colors
│   ├── Typography
│   ├── Icons
│   └── Spacing
├── 🧩 Components
│   ├── Buttons
│   ├── Forms
│   ├── Tables
│   ├── Cards
│   └── Modals
├── 📄 Templates
│   ├── List Page
│   ├── Detail Page
│   ├── Form Page
│   └── Dashboard
└── 📱 Pages
    ├── Login
    ├── Dashboard
    ├── User Management
    └── ...

## 命名规范
- 页面: Page / 页面名称
- 组件: Component / 组件名称 / 状态
- 图层: 类型_名称 (btn_submit, input_email)
```

## 禁止事项
- ❌ 颜色使用不统一
- ❌ 间距不遵循规范
- ❌ 交互状态不完整
- ❌ 不考虑响应式
- ❌ 组件不可复用

## 检查清单
- [ ] 是否遵循设计规范
- [ ] 是否覆盖所有页面状态
- [ ] 是否考虑响应式适配
- [ ] 交互流程是否完整
- [ ] 组件是否可复用
- [ ] 是否有设计说明文档

# 原型设计 Skill

## 概述
本 Skill 用于根据需求文档生成高保真的原型界面，支持移动端和 PC 端应用。整合了 UI/UX Pro Max 设计智能库的最佳实践。

**参考来源**: [UI/UX Pro Max Skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)

## ⚠️ 核心原则（必须遵守）

> 1. **必须为 PRD 中定义的每个页面生成对应的 HTML 文件**
> 2. **禁止只生成部分页面（如只有登录页）**
> 3. **必须生成 index.html 主入口文件**
> 4. **必须生成 css/styles.css 样式文件**
> 5. **必须生成 js/main.js 交互逻辑文件**
> 6. **必须生成 js/mock-data.js Mock 数据文件**
> 7. **完成后必须对照 PRD 页面清单核对，确保 100% 覆盖**

## 使用场景
- 快速出原型与老板/客户确认需求
- 为正式页面开发做准备
- UI/UX 设计验证

---

## ⚠️ 重要：执行流程

**原型设计必须按以下流程执行，确保完整性！**

### 执行流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    原型设计执行流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1] 阅读 PRD 文档                                          │
│       ↓                                                     │
│  [2] 提取页面清单（列出所有页面）                              │
│       ↓                                                     │
│  [2.5] 🎨 选择设计风格（用户确认后继续）                       │
│       ↓                                                     │
│  [3] 创建 css/styles.css 基础样式                            │
│       ↓                                                     │
│  [4] 创建 js/main.js 通用交互逻辑                            │
│       ↓                                                     │
│  [5] 创建 js/mock-data.js Mock 数据                          │
│       ↓                                                     │
│  [6] 逐个生成页面（按优先级顺序）                              │
│       ├── login.html                                        │
│       ├── dashboard.html                                    │
│       ├── list-pages...                                     │
│       └── form-pages...                                     │
│       ↓                                                     │
│  [7] 生成 index.html 主入口（平铺展示所有页面）                 │
│       ↓                                                     │
│  [8] 完整性检查（对照 PRD 核对）                               │
│       ↓                                                     │
│  [✓] 完成                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 检查点

| 步骤 | 检查项 | 状态 |
|-----|-------|------|
| 1 | PRD 文档已阅读 | ☐ |
| 2 | 页面清单已确认 | ☐ |
| **2.5** | **🎨 设计风格已选择** | ☐ |
| 3 | styles.css 已创建 | ☐ |
| 4 | main.js 已创建 | ☐ |
| 5 | mock-data.js 已创建 | ☐ |
| 6 | 所有页面已生成 | ☐ |
| 7 | index.html 已创建 | ☐ |
| 8 | 完整性检查通过 | ☐ |

---

## 🎨 步骤 2.5：设计风格选择（必须）

**在生成任何页面之前，必须先让用户选择设计风格！**

### 风格选择提示词模板

向用户展示以下选项，等待用户确认后再继续：

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

请回复您的选择，格式如：
- UI 样式：1（极简主义）
- 配色方案：1（SaaS 蓝）
- 字体配对：1（Modern Professional）

或直接回复数字，如：1-1-1
```

### 默认推荐组合

| 项目类型 | 推荐组合 | 说明 |
|---------|---------|------|
| 管理后台 | 1-1-1 | 极简 + SaaS蓝 + Modern Professional |
| 数据仪表盘 | 5-3-3 | 便当盒 + 商务深蓝 + Minimal Swiss |
| 移动端 H5 | 6-5-6 | 扁平化 + 活力橙 + Friendly Rounded |
| 开发者工具 | 4-7-5 | 深色模式 + 暗夜黑 + Developer Mono |
| 高端 SaaS | 2-2-2 | 毛玻璃 + 科技紫 + Tech Startup |

### 用户确认后

**⚠️ 关键步骤：必须立即将用户选择记录到 `doc/func.md` 文件！**

用户选择后，**立即**将选择结果写入 `doc/func.md`：

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

**示例 - 用户选择 1-1-1（极简 + SaaS蓝 + Modern Professional）：**

```markdown
## 设计规范（用户已确认）

| 设计要素 | 用户选择 | 具体值 |
|---------|---------|-------|
| UI 样式 | 1 - Minimalism（极简主义） | 大量留白、几何线条、清爽干净 |
| 配色方案 | 1 - SaaS 蓝 | 主色: #2563EB, 辅色: #3B82F6, 强调色: #F97316 |
| 字体配对 | 1 - Modern Professional | 标题: Poppins, 正文: Open Sans |

### 配色详情（CSS 变量）
```css
:root {
  /* 主色系 */
  --primary-color: #2563EB;
  --primary-hover: #1D4ED8;
  --primary-light: #DBEAFE;
  
  /* 辅色系 */
  --secondary-color: #3B82F6;
  --accent-color: #F97316;
  
  /* 背景色 */
  --bg-color: #F9FAFB;
  --bg-card: #FFFFFF;
  
  /* 文字色 */
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;
  
  /* 边框色 */
  --border-color: #E5E7EB;
  
  /* 状态色 */
  --success-color: #10B981;
  --warning-color: #F59E0B;
  --danger-color: #EF4444;
  
  /* 登录页渐变 */
  --login-gradient: linear-gradient(135deg, #1E40AF 0%, #3B82F6 50%, #60A5FA 100%);
}
```

**⚠️ 重要：CSS 必须严格使用 func.md 中记录的配色值！**

**确认后才能继续步骤 3！**

---

## 📦 步骤 4：创建 main.js 通用交互逻辑（必须）

**必须创建 `prototype/js/main.js` 文件，包含以下通用交互功能：**

### main.js 模板

```javascript
/**
 * 原型页面通用交互逻辑
 * 包含：Toast、Modal、表单验证、下拉菜单等
 */

// ============================================
// Toast 提示
// ============================================
const Toast = {
  container: null,
  
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.style.cssText = 'position:fixed;top:24px;right:24px;z-index:9999;';
      document.body.appendChild(this.container);
    }
  },
  
  show(message, type = 'info', duration = 3000) {
    this.init();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i data-lucide="${this.getIcon(type)}"></i>
      <span>${message}</span>
    `;
    this.container.appendChild(toast);
    
    // 重新渲染图标
    if (window.lucide) lucide.createIcons();
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },
  
  getIcon(type) {
    const icons = {
      success: 'check-circle',
      error: 'x-circle',
      warning: 'alert-triangle',
      info: 'info'
    };
    return icons[type] || 'info';
  },
  
  success(msg) { this.show(msg, 'success'); },
  error(msg) { this.show(msg, 'error'); },
  warning(msg) { this.show(msg, 'warning'); },
  info(msg) { this.show(msg, 'info'); }
};

// ============================================
// Modal 弹窗
// ============================================
const Modal = {
  show(id) {
    const modal = document.getElementById(id);
    if (modal) {
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  },
  
  hide(id) {
    const modal = document.getElementById(id);
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
    }
  },
  
  confirm(options) {
    const { title, message, onConfirm, onCancel } = options;
    const modalId = 'confirm-modal-' + Date.now();
    
    const modalHtml = `
      <div class="modal-overlay" id="${modalId}">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h3 class="modal-title">${title || '确认操作'}</h3>
            <button class="modal-close" onclick="Modal.hide('${modalId}')">
              <i data-lucide="x"></i>
            </button>
          </div>
          <div class="modal-body">
            <p>${message}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="Modal.hide('${modalId}')">${options.cancelText || '取消'}</button>
            <button class="btn btn-danger" id="${modalId}-confirm">${options.confirmText || '确认'}</button>
          </div>
        </div>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    if (window.lucide) lucide.createIcons();
    this.show(modalId);
    
    document.getElementById(`${modalId}-confirm`).onclick = () => {
      this.hide(modalId);
      setTimeout(() => document.getElementById(modalId)?.remove(), 300);
      if (onConfirm) onConfirm();
    };
  }
};

// ============================================
// 表单验证
// ============================================
const FormValidator = {
  validate(form) {
    const inputs = form.querySelectorAll('[required]');
    let isValid = true;
    
    inputs.forEach(input => {
      const value = input.value.trim();
      const errorEl = input.parentElement.querySelector('.error-message');
      
      if (!value) {
        isValid = false;
        input.classList.add('error');
        if (errorEl) errorEl.style.display = 'block';
      } else {
        input.classList.remove('error');
        if (errorEl) errorEl.style.display = 'none';
      }
    });
    
    return isValid;
  }
};

// ============================================
// 用户下拉菜单
// ============================================
function initUserDropdown() {
  const userInfo = document.querySelector('.user-info');
  if (userInfo) {
    userInfo.addEventListener('click', (e) => {
      e.stopPropagation();
      userInfo.classList.toggle('active');
    });
    
    document.addEventListener('click', () => {
      userInfo.classList.remove('active');
    });
  }
}

// ============================================
// 侧边栏菜单
// ============================================
function initSidebar() {
  // 菜单项点击
  document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
      document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // 子菜单展开/收起
  document.querySelectorAll('.menu-item.has-submenu > a').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentElement.classList.toggle('expanded');
    });
  });
}

// ============================================
// Tab 切换
// ============================================
function initTabs() {
  document.querySelectorAll('.tab-item').forEach(tab => {
    tab.addEventListener('click', function() {
      const tabGroup = this.closest('.tabs');
      const targetId = this.dataset.tab;
      
      // 切换 tab 激活状态
      tabGroup.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      // 切换内容面板
      const container = tabGroup.nextElementSibling || document.querySelector('.tab-content');
      if (container) {
        container.querySelectorAll('.tab-panel').forEach(panel => {
          panel.classList.remove('active');
        });
        const targetPanel = container.querySelector(`#${targetId}`);
        if (targetPanel) targetPanel.classList.add('active');
      }
    });
  });
}

// ============================================
// 页面初始化
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  initUserDropdown();
  initSidebar();
  initTabs();
  
  // 初始化 Lucide 图标
  if (window.lucide) {
    lucide.createIcons();
  }
});

// 导出到全局
window.Toast = Toast;
window.Modal = Modal;
window.FormValidator = FormValidator;
```

---

## 📦 步骤 5：创建 mock-data.js Mock 数据（必须）

**必须创建 `prototype/js/mock-data.js` 文件，包含完整的 Mock 数据。**

### Mock 数据设计原则

1. **根据 PRD.md 中的数据模型设计 Mock 数据结构**
2. **每种数据类型至少提供 5-10 条示例数据**
3. **数据之间的关联关系要正确**
4. **包含各种状态的数据**（启用/禁用、成功/失败等）
5. **时间数据使用合理的时间范围**

### mock-data.js 模板结构

```javascript
/**
 * 原型页面 Mock 数据
 * 根据项目实际数据模型定义
 */

const MockData = {
  // ============================================
  // 核心业务数据（根据 PRD 数据模型定义）
  // ============================================
  
  /**
   * 数据实体1（如：用户、商品、订单等）
   * 字段根据 PRD.md 中的数据模型设计
   * 至少 5-10 条数据
   */
  entity1: [
    { id: 1, name: '示例数据1', status: 1, createTime: '2024-01-01 10:00:00' },
    { id: 2, name: '示例数据2', status: 1, createTime: '2024-01-02 10:00:00' },
    // ... 更多数据
  ],
  
  /**
   * 数据实体2
   */
  entity2: [
    // ... 根据实际业务定义
  ],
  
  // ============================================
  // 树形数据（如：分类、部门、菜单等）
  // ============================================
  treeData: [
    {
      id: 1,
      name: '一级节点',
      children: [
        { id: 2, name: '二级节点1', children: [] },
        { id: 3, name: '二级节点2', children: [] },
      ]
    }
  ],
  
  // ============================================
  // 下拉选项数据
  // ============================================
  options: {
    status: [
      { value: 1, label: '启用' },
      { value: 0, label: '禁用' }
    ],
    // ... 其他选项
  },
  
  // ============================================
  // 仪表盘统计数据
  // ============================================
  dashboardStats: {
    // 统计卡片数据
    cards: [
      { title: '统计项1', value: 100, icon: 'users', trend: '+10%' },
      { title: '统计项2', value: 200, icon: 'shopping-cart', trend: '+5%' },
    ],
    // 图表数据
    chartData: {
      labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      datasets: [100, 120, 115, 134, 90, 230, 210]
    }
  },
  
  // ============================================
  // 日志数据（如有日志功能）
  // ============================================
  logs: [
    { id: 1, action: '操作1', operator: 'admin', time: '2024-01-01 10:00:00', status: 1 },
    // ... 更多日志
  ]
};

// 导出到全局
window.MockData = MockData;
```

### Mock 数据生成指南

| 数据类型 | 数量要求 | 注意事项 |
|---------|---------|---------|
| 列表数据 | 至少 10 条 | 包含不同状态的数据 |
| 树形数据 | 至少 3 层 | 每层 2-5 个节点 |
| 日志数据 | 至少 20 条 | 包含成功和失败记录 |
| 统计数据 | 根据仪表盘设计 | 数据要合理 |
| 下拉选项 | 根据表单需求 | 覆盖所有选项 |

---

## 原型文件结构

### 必须文件（缺一不可）

```
prototype/
├── index.html          # 【必须】主入口，平铺展示所有页面
├── css/
│   └── styles.css      # 【必须】全局样式文件
├── js/
│   ├── main.js         # 【必须】通用交互逻辑
│   └── mock-data.js    # 【必须】Mock 数据
├── login.html          # 【必须】登录页（如有认证功能）
├── dashboard.html      # 【必须】仪表盘/首页
├── {page1}.html        # 页面1（按 PRD 页面清单）
├── {page2}.html        # 页面2（按 PRD 页面清单）
└── ...                 # 其他功能页面（按 PRD 页面清单）
```

### 文件生成顺序

```
1. css/styles.css     ← 首先创建，定义全局样式
2. js/main.js         ← 通用交互逻辑
3. js/mock-data.js    ← Mock 数据（根据 PRD 数据模型）
4. login.html         ← 认证页面（如有）
5. dashboard.html     ← 主页面（含布局框架）
6. 各功能页面         ← 按 PRD 页面清单逐个生成
7. index.html         ← 最后创建，汇总所有页面
```

---

## 页面交互要求

### 通用交互组件

| 组件 | 说明 | 必须 |
|-----|------|:----:|
| **Toast 提示** | 成功/错误/警告/信息提示 | ✅ |
| **Modal 弹窗** | 新增/编辑/删除确认弹窗 | ✅ |
| **用户下拉菜单** | 个人中心、退出登录（如有） | ✅ |
| **侧边栏/导航** | 菜单展开/收起（如有） | ✅ |
| **Tab 切换** | 多 Tab 页面（如有） | ✅ |
| **表单验证** | 必填项、格式验证 | ✅ |

### 页面特定交互（根据项目类型选择）

| 页面类型 | 必须交互 |
|---------|---------|
| **登录页** | 验证码刷新、密码显示切换、登录验证、记住密码 |
| **仪表盘** | 图表展示（Chart.js）、统计卡片、快捷入口、用户下拉菜单 |
| **列表页** | 搜索筛选、分页、批量操作、删除确认弹窗、状态切换 |
| **表单页** | 表单验证、下拉选择、日期选择、文件上传预览 |
| **树形页** | 树形勾选、全选/反选、展开/收起 |
| **日志页** | 详情弹窗、清空确认、导出功能、时间范围筛选 |
| **个人中心** | Tab 切换、头像上传预览、密码修改、表单保存 |

---

## 设计规范

### 移动端规范
| 属性 | 值 |
|-----|-----|
| 界面尺寸 | 模拟 iPhone 15 Pro (393 x 852) |
| 圆角 | 16px |
| 状态栏 | 模拟 iOS 状态栏 |
| 底部导航 | 类似 iOS Tab Bar |
| 安全区域 | 底部 34px |

### PC 端规范
| 属性 | 值 |
|-----|-----|
| 最小宽度 | 1200px |
| 侧边栏宽度 | 240px |
| 内容区域 | 自适应 |
| 表格行高 | 48px |
| 卡片圆角 | 8px |

---

## 专业 UI 设计规则

### 图标与视觉元素
- ❌ 禁止使用表情符号作为图标（使用专业图标库）
- ✅ 使用 Lucide Icons（推荐）
- ✅ 确保图标大小一致（推荐 20px/24px）
- ✅ 悬停状态稳定，避免布局抖动

### 交互与光标
- ✅ 可点击元素需有指针光标 (`cursor: pointer`)
- ✅ 提供悬停反馈（颜色变化、阴影等）
- ✅ 禁用状态使用 `cursor: not-allowed`

### 布局与间距
- ✅ 使用 8px 网格系统
- ✅ 内边距和外边距保持一致
- ✅ 避免内容过于紧凑

---

## 推荐工具和资源

### 图标库
- **Lucide Icons**（推荐）：`https://unpkg.com/lucide@latest`

### 图表库
- **Chart.js**：`https://cdn.jsdelivr.net/npm/chart.js`

### 字体
```html
<!-- Modern Professional -->
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
```

---

## 输出物清单

### 必须输出

| 文件 | 说明 | 检查项 |
|-----|------|-------|
| `prototype/css/styles.css` | 全局样式 | ☐ CSS 变量与 func.md 配色一致 |
| `prototype/js/main.js` | 交互逻辑 | ☐ 包含 Toast、Modal、表单验证 |
| `prototype/js/mock-data.js` | Mock 数据 | ☐ 包含 PRD 中定义的数据模型 |
| `prototype/index.html` | 主入口 | ☐ 能正常预览所有页面 |
| `prototype/login.html` | 登录页 | ☐ 包含验证码、密码切换（如有认证） |
| `prototype/dashboard.html` | 仪表盘 | ☐ 包含图表、统计卡片 |
| PRD 中定义的所有页面 | 功能页面 | ☐ 与 PRD 页面清单一一对应 |

---

## 完成标志

```
✅ css/styles.css 已创建，CSS 变量与 func.md 配色一致
✅ js/main.js 已创建，包含 Toast、Modal、表单验证等
✅ js/mock-data.js 已创建，包含完整的 Mock 数据
✅ index.html 主入口已创建，能平铺展示所有页面
✅ 所有 PRD 定义的页面都已生成（对照页面清单核对）
✅ 每个页面都包含必要的交互功能
✅ 页面可在浏览器中正常预览
✅ 原型已与产品/客户确认
```

### ⚠️ 未完成标志（需要继续）

```
❌ 缺少 index.html 主入口文件
❌ 缺少 js/main.js 交互逻辑
❌ 缺少 js/mock-data.js Mock 数据
❌ 部分页面未生成（对照 PRD 检查）
❌ 样式文件不存在或不完整
❌ 页面无法正常预览
❌ 页面缺少交互功能
```

---

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 只生成了部分页面 | 未按流程逐个生成 | 继续生成剩余页面 |
| 缺少 index.html | 跳过了最后一步 | 使用模板创建 index.html |
| 样式不生效 | CSS 路径错误 | 检查 `href="css/styles.css"` |
| 配色与用户选择不一致 | 未读取 func.md | 检查 func.md 中的配色详情 |
| 图标不显示 | CDN 未加载 | 添加 Lucide Icons CDN |
| 交互不工作 | JS 未引入或报错 | 检查 main.js 引入和控制台错误 |
| 表格无数据 | Mock 数据未加载 | 检查 mock-data.js 引入 |

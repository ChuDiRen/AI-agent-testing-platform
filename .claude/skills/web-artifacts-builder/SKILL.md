---
name: web-artifacts-builder
description: 使用现代前端Web技术（React、Tailwind CSS、shadcn/ui）创建复杂、多组件claude.ai HTML工件的工具套件。用于需要状态管理、路由或shadcn/ui组件的复杂工件 - 不适用于简单的单文件HTML/JSX工件。
license: 完整条款见LICENSE.txt
---

# Web工件构建器

要构建强大的前端claude.ai工件，请按照以下步骤操作：
1. 使用 `scripts/init-artifact.sh` 初始化前端仓库
2. 通过编辑生成的代码来开发你的工件
3. 使用 `scripts/bundle-artifact.sh` 将所有代码捆绑到单个HTML文件中
4. 向用户显示工件
5. （可选）测试工件

**技术栈**: React 18 + TypeScript + Vite + Parcel（捆绑）+ Tailwind CSS + shadcn/ui

## 设计和样式指南

非常重要：为了避免通常被称为"AI垃圾"的内容，避免使用过度的居中布局、紫色渐变、统一的圆角和Inter字体。

## 快速开始

### Step 1: 初始化项目

Run the initialization script to create a new React project:
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a fully configured project with:
- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
- ✅ Path aliases (`@/`) configured
- ✅ 40+ shadcn/ui components pre-installed
- ✅ All Radix UI dependencies included
- ✅ Parcel configured for bundling (via .parcelrc)
- ✅ Node 18+ compatibility (auto-detects and pins Vite version)

### Step 2: Develop Your Artifact

To build the artifact, edit the generated files. See **Common Development Tasks** below for guidance.

### Step 3: Bundle to Single HTML File

To bundle the React app into a single HTML artifact:
```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in Claude conversations as an artifact.

**Requirements**: Your project must have an `index.html` in the root directory.

**What the script does**:
- Installs bundling dependencies (parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline)
- Creates `.parcelrc` config with path alias support
- Builds with Parcel (no source maps)
- Inlines all assets into single HTML using html-inline

### Step 4: Share Artifact with User

Finally, share the bundled HTML file in conversation with the user so they can view it as an artifact.

### Step 5: Testing/Visualizing the Artifact (Optional)

Note: This is a completely optional step. Only perform if necessary or requested.

To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between the request and when the finished artifact can be seen. Test later, after presenting the artifact, if requested or if issues arise.

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components
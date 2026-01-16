---
description: 设计高保真原型的命令
---

# 命令：design-prototype

## 功能描述

根据需求文档快速生成高保真HTML原型界面，支持移动端和PC端设计。

## 使用方式

```
/design-prototype
```

或

```
/design-prototype <页面描述>
```

## 参数说明

- `--style=modern` - 现代简约风格
- `--style=classic` - 经典风格
- `--mobile` - 移动端设计（默认）
- `--desktop` - PC端设计
- `--with-real-images` - 使用真实图片（需要提供图片URL）

## 执行流程

1. **需求分析**：
   - 分析核心功能点
   - 识别关键页面
   - 确定交互逻辑

2. **UI风格设计**：
   - 选择设计风格
   - 确定配色方案
   - 选择字体和图标

3. **页面规划**：
   - 确定页面列表
   - 设计信息架构
   - 规划导航结构

4. **原型实现**：
   - 生成HTML原型代码
   - 应用Tailwind CSS样式
   - 集成UI组件库
   - 添加交互效果

5. **输出交付**：
   - 生成完整HTML文件
   - 提供预览链接
   - 生成设计说明文档

## 输出格式

生成一个或多个HTML原型文件，保存在 `prototypes/` 目录：

```
prototypes/
├── index.html          # 主入口
├── home.html           # 首页
├── product-list.html   # 商品列表
├── product-detail.html # 商品详情
└── cart.html           # 购物车
```

## 设计规范

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
- 使用Tailwind CSS进行样式设计
- 集成Element Plus（PC）或Vant（移动）
- 使用FontAwesome图标库

## 示例

```
/design-prototype 移动端H5商城，包含首页、商品列表、商品详情、购物车四个页面
```

## 交互说明

- **index.html**：使用iframe嵌入所有页面，平铺展示
- **真实图片**：可从Unsplash、Pexels等图库获取
- **交互效果**：按钮点击、页面切换等基本交互

## 相关命令

- `/analyze-requirement` - 分析需求
- `/start-project` - 启动项目
- `/split-tasks` - 拆分任务

# 菜单配置说明

## 概述

本项目已配置了完整的静态菜单系统，基于现有的功能模块生成。菜单系统支持静态配置和动态配置两种模式。

## 文件结构

```
src/config/
├── static-menu.js     # 静态菜单配置
├── menu-config.js     # 菜单行为配置
└── README.md          # 说明文档
```

## 菜单结构

### 主要模块

1. **工作台** (`/workbench`)
   - 默认首页，显示系统概览

2. **API测试** (`/apitest`)
   - 项目管理
   - API信息管理
   - 用例管理
   - 用例集合
   - 关键字管理
   - 消息管理
   - API伴侣

3. **系统管理** (`/system`)
   - 用户管理
   - 角色管理
   - 菜单管理
   - 部门管理
   - API权限
   - 审计日志
   - 系统设置

4. **个人中心** (`/profile`)
   - 个人信息
   - 密码修改

## 配置选项

### 切换菜单模式

在 `src/config/menu-config.js` 中修改：

```javascript
// 静态菜单模式
export const CURRENT_MENU_MODE = MENU_MODE.STATIC

// 动态菜单模式（从后端获取）
export const CURRENT_MENU_MODE = MENU_MODE.DYNAMIC
```

### 菜单主题配置

```javascript
theme: {
  primaryColor: '#2563eb',           // 主色调
  activeBgColor: 'rgba(37, 99, 235, 0.1)',  // 激活背景
  hoverBgColor: '#f3f4f6',           // 悬停背景
  textColor: '#374151',              // 文字颜色
  activeTextColor: '#2563eb'        // 激活文字颜色
}
```

### 菜单行为配置

```javascript
behavior: {
  uniqueOpened: true,                // 只保持一个子菜单展开
  collapseTransition: false,         // 折叠动画
  enableTransition: true             // 路由切换动画
}
```

## 添加新菜单

### 1. 在静态菜单中添加

编辑 `src/config/static-menu.js`：

```javascript
{
  name: '新模块',
  path: '/new-module',
  icon: 'icon-park-outline:new',
  order: 5,
  children: [
    {
      name: '子功能',
      path: '/new-module/sub-feature',
      icon: 'icon-park-outline:feature',
      order: 1,
      component: 'new-module/sub-feature'
    }
  ]
}
```

### 2. 创建对应页面组件

在 `src/views/` 下创建对应的组件文件夹和 `index.vue` 文件。

## 图标使用

项目使用 `icon-park-outline` 图标库。常用图标：

- `icon-park-outline:workbench` - 工作台
- `icon-park-outline:api` - API
- `icon-park-outline:setting` - 设置
- `icon-park-outline:user` - 用户
- `icon-park-outline:folder-close` - 文件夹
- `icon-park-outline:file-text` - 文件
- `icon-park-outline:test-tube` - 测试
- `icon-park-outline:key` - 密钥
- `icon-park-outline:message` - 消息
- `icon-park-outline:robot` - 机器人
- `icon-park-outline:permissions` - 权限
- `icon-park-outline:menu` - 菜单
- `icon-park-outline:organization` - 组织
- `icon-park-outline:api-key` - API密钥
- `icon-park-outline:log` - 日志
- `icon-park-outline:config` - 配置
- `icon-park-outline:chart-line` - 图表
- `icon-park-outline:file-chart` - 图表文件
- `icon-park-outline:speedometer` - 速度计

## 路由生成

静态菜单会自动生成对应的路由配置。路由生成逻辑：

1. 父菜单使用 `Layout` 组件
2. 子菜单动态导入对应的页面组件
3. 支持多级菜单结构
4. 自动处理路由权限和显示状态

## 权限控制

菜单支持以下权限控制：

- `isHidden`: 控制菜单是否隐藏
- `order`: 控制菜单排序
- `keepAlive`: 控制页面是否缓存

## 注意事项

1. 修改菜单配置后需要重新启动项目
2. 确保所有菜单项都有对应的页面组件
3. 路由路径必须唯一
4. 组件路径必须与实际文件路径匹配

## 故障排除

### 菜单不显示

1. 检查 `menu-config.js` 中的配置
2. 确认路由是否正确生成
3. 检查组件文件是否存在

### 页面404

1. 检查组件路径是否正确
2. 确认路由是否正确添加
3. 检查组件文件是否存在

### 图标不显示

1. 确认图标名称是否正确
2. 检查是否已安装图标库
3. 确认图标是否存在于图标库中

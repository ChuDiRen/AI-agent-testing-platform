# IconSelect 图标选择器组件

## 功能特性

- ✅ 支持下拉选择图标
- ✅ 支持搜索图标名称
- ✅ 实时预览图标效果
- ✅ 支持清除图标
- ✅ 集成 60+ 常用 Element Plus 图标
- ✅ 响应式网格布局
- ✅ 美观的悬停效果

## 使用方法

### 基础使用

```vue
<template>
  <IconSelect v-model="iconName" />
</template>

<script setup>
import { ref } from 'vue'
import IconSelect from '~/components/IconSelect.vue'

const iconName = ref('User')
</script>
```

### 在表单中使用

```vue
<template>
  <el-form-item label="图标">
    <IconSelect v-model="formData.icon" />
  </el-form-item>
</template>

<script setup>
import { reactive } from 'vue'
import IconSelect from '~/components/IconSelect.vue'

const formData = reactive({
  icon: 'HomeFilled'
})
</script>
```

## Props

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| modelValue | 图标名称（v-model） | String | '' |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| update:modelValue | 图标变化时触发 | (value: string) |

## 可用图标列表

### 系统图标

User, Lock, Setting, Menu, HomeFilled, Document, Folder, Files, Operation, Tools, Monitor, Management

### 功能图标

Edit, Delete, Plus, Minus, Check, Close, Upload, Download, Share, View, Hide, Refresh

### 方向图标

ArrowLeft, ArrowRight, ArrowUp, ArrowDown, Back, Right, Top, Bottom

### 数据图标

DataLine, DataBoard, Grid, List, TrendCharts, PieChart

### 其他常用图标

Star, StarFilled, Message, Bell, Calendar, Clock, Location, Phone, ChatDotRound, Warning, WarningFilled, InfoFilled, SuccessFilled, CircleClose, CircleCheck, QuestionFilled, Link, Loading, Opportunity, Key, House, Office, School, Shop, Box, Goods, Coin, Trophy, Sunny, Moon, MagicStick, Picture, Camera, VideoCamera, Headset, Service, Promotion, SetUp

## 样式定制

组件使用 Element Plus 的主题变量，自动适配项目主题色。

### 自定义样式示例

```css
/* 修改图标选择器宽度 */
:deep(.icon-select-popover) {
  width: 700px !important;
}

/* 修改图标网格列数 */
:deep(.icon-list) {
  grid-template-columns: repeat(6, 1fr);
}
```

## 注意事项

1. 确保项目已安装 `@element-plus/icons-vue`
2. 图标组件需要全局注册（已在 main.js 中完成）
3. 组件返回的是图标组件名称字符串，如 'User', 'Setting' 等
4. 使用时通过 `<component :is="iconName" />` 动态渲染图标

## 示例场景

### 菜单管理

用于选择菜单项的图标，提升用户体验

### 系统配置

允许用户自定义功能模块的图标

### 内容管理

为文章分类、标签等选择合适的图标

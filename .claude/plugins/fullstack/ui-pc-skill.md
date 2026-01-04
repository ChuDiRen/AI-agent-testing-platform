# UI PC Skill

PC 端 UI 开发技能，提供 Vue 3 + Element Plus 组件开发能力。

## 触发条件
- `/dev --scope frontend` 命令
- `/crud` 命令
- 用户请求开发前端页面

## 开发能力

参考 `@templates/code-patterns.md`：

### 技术栈
- **框架**: Vue 3 + JavaScript
- **UI**: Element Plus
- **状态**: Vuex
- **构建**: Vite
- **样式**: TailwindCSS

### 组件规范

#### 列表页模板
```vue
<template>
  <div class="module-list">
    <el-card>
      <!-- 搜索区域 -->
      <el-form :inline="true" :model="searchForm">...</el-form>
      
      <!-- 操作按钮 -->
      <div class="mb-4">
        <el-button type="primary" @click="handleAdd">新增</el-button>
      </div>
      
      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading">...</el-table>
      
      <!-- 分页 -->
      <el-pagination .../>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
// ... 逻辑代码
</script>
```

#### API 接口规范
```javascript
import axios from '@/axios'

export const queryByPage = (data) => axios.post(`/api/{Module}/queryByPage`, data)
export const queryById = (id) => axios.get(`/api/{Module}/queryById`, { params: { id } })
export const insert = (data) => axios.post(`/api/{Module}/insert`, data)
export const update = (data) => axios.put(`/api/{Module}/update`, data)
export const deleteById = (id) => axios.delete(`/api/{Module}/delete`, { params: { id } })
```

## 输出要求

1. 使用 `<script setup>` 语法
2. 使用 Element Plus 组件
3. 遵循项目目录结构
4. 包含完整的 CRUD 功能
5. 添加 loading 状态和错误处理
6. 使用 ElMessage 提示操作结果

## 检查清单
- [ ] 组件使用 `<script setup>`
- [ ] 表格有 v-loading
- [ ] 删除有确认弹窗
- [ ] 分页功能正常
- [ ] API 调用有错误处理

## 与其他组件协作

- 后端接口 → 调用 `crud-development` Skill
- 深度开发 → 调用 `frontend-developer` Agent

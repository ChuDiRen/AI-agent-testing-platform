# PC 端 UI 开发技能

## 触发条件
- 关键词：PC端、管理后台、Element、表格、表单、后台管理、Vue页面
- 场景：当用户需要开发 PC 端管理后台界面时

## 核心规范

### 规范1：项目技术栈（本项目）
- **框架**: Vue 3 + JavaScript (主体)
- **UI 组件库**: Element Plus
- **状态管理**: Vuex
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios (封装在 @/axios.js)
- **样式**: TailwindCSS + WindiCSS

### 规范2：页面文件结构
```
views/{module}/
├── {Module}List.vue          # 列表页
├── {Module}Form.vue          # 表单弹窗
├── {module}.js               # API 接口定义
└── components/               # 模块私有组件（可选）
```

### 规范3：列表页模板
```vue
<template>
  <div class="common-list-container">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="名称">
          <el-input v-model="searchForm.name" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 操作按钮区域 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增
      </el-button>
    </div>
    
    <!-- 表格区域 -->
    <el-table :data="tableData" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="create_time" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row)">
            <template #reference>
              <el-button link type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页区域 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
    
    <!-- 表单弹窗 -->
    <{Module}Form ref="formRef" @success="loadData" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteById } from './{module}.js'
import {Module}Form from './{Module}Form.vue'

// 搜索表单
const searchForm = reactive({
  name: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 表单弹窗引用
const formRef = ref(null)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      page: pagination.page,
      pageSize: pagination.pageSize,
      ...searchForm
    })
    if (res.data.code === 0) {
      tableData.value = res.data.data.list
      pagination.total = res.data.data.total
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, { name: '' })
  handleSearch()
}

// 新增
const handleAdd = () => {
  formRef.value.open()
}

// 编辑
const handleEdit = (row) => {
  formRef.value.open(row)
}

// 删除
const handleDelete = async (row) => {
  try {
    const res = await deleteById(row.id)
    if (res.data.code === 0) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 分页
const handlePageChange = (page) => {
  pagination.page = page
  loadData()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '@/styles/common-list.css';
</style>
```

### 规范4：表单弹窗模板
```vue
<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑' : '新增'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入名称" />
      </el-form-item>
      <!-- 其他表单项 -->
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { insert, update } from './{module}.js'

const emit = defineEmits(['success'])

const visible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const formData = reactive({
  id: null,
  name: ''
})

const isEdit = computed(() => !!formData.id)

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

// 打开弹窗
const open = (row = null) => {
  if (row) {
    Object.assign(formData, row)
  } else {
    Object.assign(formData, { id: null, name: '' })
  }
  visible.value = true
}

// 关闭弹窗
const handleClose = () => {
  visible.value = false
  formRef.value?.resetFields()
}

// 提交
const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const api = isEdit.value ? update : insert
    const res = await api(formData)
    if (res.data.code === 0) {
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      emit('success')
      handleClose()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

defineExpose({ open })
</script>
```

### 规范5：API 接口定义
```javascript
// {module}.js
import axios from '@/axios'

export function queryByPage(data) {
  return axios.post(`/api/{Module}/queryByPage`, data)
}

export function queryById(id) {
  return axios.get(`/api/{Module}/queryById`, { params: { id } })
}

export function insert(data) {
  return axios.post(`/api/{Module}/insert`, data)
}

export function update(data) {
  return axios.put(`/api/{Module}/update`, data)
}

export function deleteById(id) {
  return axios.delete(`/api/{Module}/delete`, { params: { id } })
}
```

## 禁止事项
- ❌ 直接在组件中写 API 请求 URL
- ❌ 表格不支持 loading 状态
- ❌ 删除操作不做二次确认
- ❌ 表单不做校验
- ❌ 不处理接口错误

## 检查清单
- [ ] 是否使用 Element Plus 组件
- [ ] 是否有 loading 状态
- [ ] 是否有错误处理
- [ ] 表单是否有校验
- [ ] 删除是否有确认
- [ ] API 是否封装在独立文件

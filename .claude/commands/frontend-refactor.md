# 前端重构命令

## 命令说明
使用 `/frontend-refactor` 触发前端代码重构，优化代码结构和规范。

## 重构范围

### 1. API接口标准化
```javascript
// 问题：接口定义不规范，命名不统一
// apiinfo.js 现状
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=apiinfo-page`, data)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=apiinfo-insert`, data)
}

// 重构后：统一命名规范
export const apiInfo = {
    // 分页查询
    queryByPage: (params) => 
        axios.post('/ApiInfo/queryByPage', params),
    
    // 单条查询
    getById: (id) => 
        axios.get(`/ApiInfo/queryById`, { params: { id } }),
    
    // 创建
    create: (data) => 
        axios.post('/ApiInfo/insert', data),
    
    // 更新
    update: (data) => 
        axios.put('/ApiInfo/update', data),
    
    // 删除
    delete: (id) => 
        axios.delete('/ApiInfo/delete', { params: { id } }),
    
    // 批量操作
    batchDelete: (ids) => 
        axios.post('/ApiInfo/batchDelete', { ids }),
    
    // 导入
    import: (data) => 
        axios.post('/ApiInfo/import', data),
    
    // 导出
    export: (params) => 
        axios.get('/ApiInfo/export', { params, responseType: 'blob' })
}
```

### 2. 统一请求拦截器
```javascript
// utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
service.interceptors.request.use(
    config => {
        // 添加认证token
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        
        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = generateRequestId()
        
        // 记录请求开始时间
        config.startTime = Date.now()
        
        return config
    },
    error => {
        console.error('Request error:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
service.interceptors.response.use(
    response => {
        const { data, config } = response
        const duration = Date.now() - config.startTime
        
        // 记录响应时间
        console.log(`API ${config.url} 响应时间: ${duration}ms`)
        
        // 统一响应格式处理
        if (data.code === 200) {
            return data
        } else {
            // 业务错误处理
            ElMessage.error(data.message || '请求失败')
            return Promise.reject(new Error(data.message || '请求失败'))
        }
    },
    error => {
        const { response } = error
        
        // HTTP错误处理
        if (response) {
            switch (response.status) {
                case 401:
                    ElMessage.error('认证失败，请重新登录')
                    // 跳转到登录页
                    router.push('/login')
                    break
                case 403:
                    ElMessage.error('权限不足')
                    break
                case 404:
                    ElMessage.error('请求的资源不存在')
                    break
                case 500:
                    ElMessage.error('服务器内部错误')
                    break
                default:
                    ElMessage.error(response.data?.message || '网络错误')
            }
        } else if (error.code === 'ECONNABORTED') {
            ElMessage.error('请求超时')
        } else {
            ElMessage.error('网络连接失败')
        }
        
        return Promise.reject(error)
    }
)

export default service

// 生成请求ID
function generateRequestId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
}
```

### 3. 组件标准化重构
```vue
<!-- 重构前：ApiInfoList.vue 存在问题 -->
<template>
  <div>
    <!-- 直接操作DOM -->
    <el-table ref="tableRef" :data="tableData">
      <!-- 缺少统一的列定义 -->
    </el-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [],
      loading: false
    }
  },
  methods: {
    async loadData() {
      // 直接调用axios，缺少统一处理
      const response = await axios.post('/ApiInfo/queryByPage', this.queryParams)
      this.tableData = response.data.list
    }
  }
}
</script>

<!-- 重构后：标准化组件 -->
<template>
  <div class="api-info-list">
    <!-- 搜索区域 -->
    <SearchForm 
      v-model="searchForm" 
      :fields="searchFields"
      @search="handleSearch"
      @reset="handleReset"
    />
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新增
      </el-button>
      <el-button @click="handleBatchDelete" :disabled="!selectedRows.length">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
      <el-button @click="handleExport">
        <el-icon><Download /></el-icon>
        导出
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <DataTable
      ref="tableRef"
      :columns="tableColumns"
      :data="tableData"
      :loading="loading"
      :pagination="pagination"
      :selection="true"
      @selection-change="handleSelectionChange"
      @page-change="handlePageChange"
      @sort-change="handleSortChange"
    >
      <!-- 自定义列内容 -->
      <template #status="{ row }">
        <el-tag :type="getStatusType(row.status)">
          {{ getStatusText(row.status) }}
        </el-tag>
      </template>
      
      <template #actions="{ row }">
        <el-button size="small" @click="handleEdit(row)">编辑</el-button>
        <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
      </template>
    </DataTable>
    
    <!-- 表单弹窗 -->
    <ApiInfoForm
      v-model="formVisible"
      :form-data="currentRow"
      :mode="formMode"
      @submit="handleFormSubmit"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiInfo } from './apiinfo'
import SearchForm from '@/components/SearchForm/index.vue'
import DataTable from '@/components/DataTable/index.vue'
import ApiInfoForm from './ApiInfoForm.vue'

// 响应式数据
const tableRef = ref()
const loading = ref(false)
const tableData = ref([])
const selectedRows = ref([])
const formVisible = ref(false)
const formMode = ref('create') // create, edit, view
const currentRow = ref(null)

// 搜索表单
const searchForm = reactive({
    api_name: '',
    request_method: '',
    project_id: null
})

// 搜索字段配置
const searchFields = [
    { prop: 'api_name', label: '接口名称', type: 'input', placeholder: '请输入接口名称' },
    { prop: 'request_method', label: '请求方法', type: 'select', options: [
        { label: 'GET', value: 'GET' },
        { label: 'POST', value: 'POST' },
        { label: 'PUT', value: 'PUT' },
        { label: 'DELETE', value: 'DELETE' }
    ]},
    { prop: 'project_id', label: '项目', type: 'select', options: [] }
]

// 表格列配置
const tableColumns = [
    { type: 'selection', width: '55' },
    { prop: 'api_name', label: '接口名称', sortable: true },
    { prop: 'request_method', label: '请求方法', width: '100' },
    { prop: 'api_url', label: '接口地址', showOverflowTooltip: true },
    { prop: 'status', label: '状态', width: '100', slot: 'status' },
    { prop: 'create_time', label: '创建时间', width: '180', sortable: true },
    { prop: 'actions', label: '操作', width: '150', slot: 'actions' }
]

// 分页配置
const pagination = reactive({
    current: 1,
    pageSize: 20,
    total: 0
})

// 方法
const handleSearch = () => {
    pagination.current = 1
    loadData()
}

const handleReset = () => {
    Object.keys(searchForm).forEach(key => {
        searchForm[key] = key === 'project_id' ? null : ''
    })
    handleSearch()
}

const handleSelectionChange = (selection) => {
    selectedRows.value = selection
}

const handlePageChange = (page) => {
    pagination.current = page
    loadData()
}

const handleSortChange = ({ prop, order }) => {
    // 处理排序
    loadData()
}

const handleCreate = () => {
    formMode.value = 'create'
    currentRow.value = null
    formVisible.value = true
}

const handleEdit = (row) => {
    formMode.value = 'edit'
    currentRow.value = { ...row }
    formVisible.value = true
}

const handleDelete = async (row) => {
    try {
        await ElMessageBox.confirm(`确定要删除接口 "${row.api_name}" 吗？`, '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
        
        await apiInfo.delete(row.id)
        ElMessage.success('删除成功')
        loadData()
    } catch (error) {
        if (error !== 'cancel') {
            console.error('删除失败:', error)
        }
    }
}

const handleBatchDelete = async () => {
    if (!selectedRows.value.length) return
    
    try {
        await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 条记录吗？`, '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
        
        const ids = selectedRows.value.map(row => row.id)
        await apiInfo.batchDelete(ids)
        ElMessage.success('批量删除成功')
        loadData()
    } catch (error) {
        if (error !== 'cancel') {
            console.error('批量删除失败:', error)
        }
    }
}

const handleFormSubmit = async (formData) => {
    try {
        if (formMode.value === 'create') {
            await apiInfo.create(formData)
            ElMessage.success('创建成功')
        } else {
            await apiInfo.update(formData)
            ElMessage.success('更新成功')
        }
        formVisible.value = false
        loadData()
    } catch (error) {
        console.error('保存失败:', error)
    }
}

const loadData = async () => {
    loading.value = true
    try {
        const params = {
            page: pagination.current,
            pageSize: pagination.pageSize,
            ...searchForm
        }
        
        const response = await apiInfo.queryByPage(params)
        tableData.value = response.data.list
        pagination.total = response.data.total
    } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('加载数据失败')
    } finally {
        loading.value = false
    }
}

// 状态格式化
const getStatusType = (status) => {
    const statusMap = {
        1: 'success',
        0: 'danger',
        2: 'warning'
    }
    return statusMap[status] || 'info'
}

const getStatusText = (status) => {
    const statusMap = {
        1: '启用',
        0: '禁用',
        2: '测试中'
    }
    return statusMap[status] || '未知'
}

// 生命周期
onMounted(() => {
    loadData()
})
</script>

<style scoped>
.api-info-list {
    padding: 20px;
}

.toolbar {
    margin: 16px 0;
    display: flex;
    gap: 12px;
}
</style>
```

### 4. 通用组件封装
```javascript
// components/SearchForm/index.vue
<template>
  <el-form :model="model" :inline="inline" class="search-form">
    <el-form-item v-for="field in fields" :key="field.prop" :label="field.label">
      <component
        :is="getComponentType(field.type)"
        v-model="model[field.prop]"
        v-bind="field"
        v-on="field.events || {}"
      />
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
      <el-button @click="handleReset">
        <el-icon><Refresh /></el-icon>
        重置
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    modelValue: { type: Object, default: () => ({}) },
    fields: { type: Array, required: true },
    inline: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const model = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
})

const getComponentType = (type) => {
    const componentMap = {
        input: 'el-input',
        select: 'el-select',
        date: 'el-date-picker',
        checkbox: 'el-checkbox-group',
        radio: 'el-radio-group'
    }
    return componentMap[type] || 'el-input'
}

const handleSearch = () => {
    emit('search', model.value)
}

const handleReset = () => {
    emit('reset')
}
</script>
```

### 5. 状态管理优化
```javascript
// store/modules/apiInfo.js
import { apiInfo } from '@/views/apitest/apiinfo/apiinfo'

export default {
    namespaced: true,
    
    state: {
        list: [],
        total: 0,
        loading: false,
        current: null
    },
    
    mutations: {
        SET_LOADING(state, loading) {
            state.loading = loading
        },
        SET_LIST(state, { list, total }) {
            state.list = list
            state.total = total
        },
        SET_CURRENT(state, current) {
            state.current = current
        }
    },
    
    actions: {
        async queryByPage({ commit }, params) {
            commit('SET_LOADING', true)
            try {
                const response = await apiInfo.queryByPage(params)
                commit('SET_LIST', {
                    list: response.data.list,
                    total: response.data.total
                })
                return response
            } finally {
                commit('SET_LOADING', false)
            }
        },
        
        async create({ dispatch }, data) {
            await apiInfo.create(data)
            await dispatch('queryByPage', {})
        },
        
        async update({ dispatch }, data) {
            await apiInfo.update(data)
            await dispatch('queryByPage', {})
        },
        
        async delete({ dispatch }, id) {
            await apiInfo.delete(id)
            await dispatch('queryByPage', {})
        }
    }
}
```

## 重构步骤

1. **创建统一请求工具**
   - 标准化axios配置
   - 添加请求/响应拦截器
   - 统一错误处理

2. **重构API接口定义**
   - 统一命名规范
   - 标准化参数格式
   - 添加类型定义

3. **组件标准化**
   - 创建通用组件库
   - 标准化组件结构
   - 优化props和events

4. **状态管理优化**
   - 模块化store
   - 统一action处理
   - 添加缓存机制

5. **样式规范化**
   - 统一CSS变量
   - 标准化组件样式
   - 响应式设计优化

## 使用示例

```
/frontend-refactor --module apitest --target api --action refactor
/frontend-refactor --module apitest --target components --action standardize
/frontend-refactor --module apitest --target store --action optimize
/frontend-refactor --module apitest --target All --action full-refactor
```

## 注意事项

1. 保持向后兼容性
2. 逐步替换，避免影响现有功能
3. 更新相关文档
4. 性能优化考虑
5. 移动端适配

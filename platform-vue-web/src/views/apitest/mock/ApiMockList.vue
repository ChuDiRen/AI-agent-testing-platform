<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <div class="search-container">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目">
          <el-select v-model="searchForm.project_id" placeholder="选择项目" clearable @change="handleSearch">
            <el-option v-for="item in projectList" :key="item.id" :label="item.project_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Mock名称">
          <el-input v-model="searchForm.mock_name" placeholder="请输入Mock名称" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="searchForm.mock_method" placeholder="选择方法" clearable>
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="PATCH" value="PATCH" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格区域 -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Mock服务管理</span>
        <div class="table-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增Mock
          </el-button>
          <el-button @click="handleViewLogs">
            <el-icon><Document /></el-icon>查看日志
          </el-button>
        </div>
      </div>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="mock_name" label="Mock名称" min-width="150" />
        <el-table-column prop="mock_method" label="方法" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getMethodTagType(row.mock_method)" size="small">
              {{ row.mock_method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="mock_path" label="Mock路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="response_status" label="状态码" width="80" align="center" />
        <el-table-column prop="delay_ms" label="延迟(ms)" width="90" align="center" />
        <el-table-column prop="is_enabled" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.is_enabled" :active-value="1" :inactive-value="0" 
                       @change="handleToggleEnabled(row)" />
          </template>
        </el-table-column>
        <el-table-column label="Mock URL" min-width="200">
          <template #default="{ row }">
            <div class="mock-url">
              <span>{{ getMockFullUrl(row) }}</span>
              <el-button link type="primary" @click="copyMockUrl(row)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleTest(row)">测试</el-button>
            <el-popconfirm title="确定删除该Mock规则吗？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目" prop="project_id">
              <el-select v-model="formData.project_id" placeholder="选择项目" :disabled="isEdit">
                <el-option v-for="item in projectList" :key="item.id" :label="item.project_name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Mock名称" prop="mock_name">
              <el-input v-model="formData.mock_name" placeholder="请输入Mock名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="请求方法" prop="mock_method">
              <el-select v-model="formData.mock_method" placeholder="选择方法">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="Mock路径" prop="mock_path">
              <el-input v-model="formData.mock_path" placeholder="如: /api/users/{id}" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="响应状态码">
              <el-input-number v-model="formData.response_status" :min="100" :max="599" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="延迟(ms)">
              <el-input-number v-model="formData.delay_ms" :min="0" :max="30000" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级">
              <el-input-number v-model="formData.priority" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="响应类型">
          <el-radio-group v-model="formData.response_body_type">
            <el-radio label="json">JSON</el-radio>
            <el-radio label="xml">XML</el-radio>
            <el-radio label="text">Text</el-radio>
            <el-radio label="html">HTML</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="响应体">
          <div class="response-editor">
            <el-input
              v-model="formData.response_body"
              type="textarea"
              :rows="10"
              placeholder="请输入响应内容"
            />
            <el-button class="format-btn" size="small" @click="formatResponseBody">格式化</el-button>
          </div>
        </el-form-item>

        <el-form-item label="响应头">
          <div class="header-editor">
            <div v-for="(item, index) in responseHeaders" :key="index" class="header-row">
              <el-input v-model="item.key" placeholder="Header名" class="header-key" />
              <el-input v-model="item.value" placeholder="Header值" class="header-value" />
              <el-button type="danger" link @click="removeHeader(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" link @click="addHeader">
              <el-icon><Plus /></el-icon>添加响应头
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="formData.mock_desc" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试对话框 -->
    <el-dialog v-model="testDialogVisible" title="测试Mock" width="700px">
      <div class="test-container">
        <div class="test-url">
          <el-tag :type="getMethodTagType(testData.method)">{{ testData.method }}</el-tag>
          <span>{{ testData.url }}</span>
          <el-button type="primary" size="small" @click="sendTestRequest" :loading="testLoading">
            发送请求
          </el-button>
        </div>
        <div class="test-result" v-if="testResult">
          <div class="result-header">
            <span>状态码: </span>
            <el-tag :type="testResult.status < 400 ? 'success' : 'danger'">{{ testResult.status }}</el-tag>
            <span class="result-time">耗时: {{ testResult.time }}ms</span>
          </div>
          <div class="result-body">
            <pre>{{ testResult.body }}</pre>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 日志对话框 -->
    <el-dialog v-model="logDialogVisible" title="Mock请求日志" width="900px">
      <el-table :data="logList" border max-height="400">
        <el-table-column prop="request_method" label="方法" width="80" />
        <el-table-column prop="request_path" label="路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="response_status" label="状态码" width="80" />
        <el-table-column prop="response_time" label="耗时(ms)" width="90" />
        <el-table-column prop="client_ip" label="客户端IP" width="120" />
        <el-table-column prop="create_time" label="时间" width="170" />
      </el-table>
      <template #footer>
        <el-button type="danger" @click="handleClearLogs">清空日志</el-button>
        <el-button @click="logDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Document, CopyDocument } from '@element-plus/icons-vue'
import { queryByPage, insertData, updateData, deleteData, toggleEnabled, queryLogs, clearLogs } from './apiMock'
import { queryAll as queryAllProjects } from '~/views/apitest/project/apiProject'

// 项目列表
const projectList = ref([])

// 搜索表单
const searchForm = reactive({
  project_id: null,
  mock_name: '',
  mock_method: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10
})
const total = ref(0)

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增Mock')
const isEdit = ref(false)
const formRef = ref(null)
const submitLoading = ref(false)

// 表单数据
const formData = reactive({
  id: null,
  project_id: null,
  mock_name: '',
  mock_desc: '',
  mock_path: '',
  mock_method: 'GET',
  response_status: 200,
  response_headers: '',
  response_body: '{\n  "code": 200,\n  "msg": "success",\n  "data": null\n}',
  response_body_type: 'json',
  delay_ms: 0,
  priority: 0
})

// 响应头
const responseHeaders = ref([])

// 表单验证规则
const formRules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  mock_name: [{ required: true, message: '请输入Mock名称', trigger: 'blur' }],
  mock_method: [{ required: true, message: '请选择请求方法', trigger: 'change' }],
  mock_path: [{ required: true, message: '请输入Mock路径', trigger: 'blur' }]
}

// 测试
const testDialogVisible = ref(false)
const testData = reactive({ method: '', url: '' })
const testResult = ref(null)
const testLoading = ref(false)

// 日志
const logDialogVisible = ref(false)
const logList = ref([])

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await queryAllProjects()
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
      if (projectList.value.length > 0 && !searchForm.project_id) {
        searchForm.project_id = projectList.value[0].id
      }
    }
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      ...searchForm,
      ...pagination
    })
    if (res.data.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.mock_name = ''
  searchForm.mock_method = ''
  handleSearch()
}

// 获取方法标签类型
const getMethodTagType = (method) => {
  const typeMap = {
    GET: 'success',
    POST: 'warning',
    PUT: 'primary',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return typeMap[method] || 'info'
}

// 获取Mock完整URL
const getMockFullUrl = (row) => {
  return `/mock/${row.project_id}${row.mock_path}`
}

// 复制Mock URL
const copyMockUrl = (row) => {
  const url = `${window.location.origin}/api${getMockFullUrl(row)}`
  navigator.clipboard.writeText(url)
  ElMessage.success('已复制到剪贴板')
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增Mock'
  Object.assign(formData, {
    id: null,
    project_id: searchForm.project_id,
    mock_name: '',
    mock_desc: '',
    mock_path: '',
    mock_method: 'GET',
    response_status: 200,
    response_headers: '',
    response_body: '{\n  "code": 200,\n  "msg": "success",\n  "data": null\n}',
    response_body_type: 'json',
    delay_ms: 0,
    priority: 0
  })
  responseHeaders.value = []
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑Mock'
  Object.assign(formData, row)
  
  try {
    responseHeaders.value = row.response_headers ? JSON.parse(row.response_headers) : []
  } catch {
    responseHeaders.value = []
  }
  
  dialogVisible.value = true
}

// 添加响应头
const addHeader = () => {
  responseHeaders.value.push({ key: '', value: '' })
}

// 删除响应头
const removeHeader = (index) => {
  responseHeaders.value.splice(index, 1)
}

// 格式化响应体
const formatResponseBody = () => {
  try {
    const obj = JSON.parse(formData.response_body)
    formData.response_body = JSON.stringify(obj, null, 2)
  } catch {
    ElMessage.warning('JSON格式不正确')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    const submitData = {
      ...formData,
      response_headers: JSON.stringify(responseHeaders.value.filter(h => h.key))
    }
    
    const res = isEdit.value 
      ? await updateData(submitData)
      : await insertData(submitData)
    
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '操作成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    const res = await deleteData(row.id)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 切换启用状态
const handleToggleEnabled = async (row) => {
  try {
    const res = await toggleEnabled(row.id)
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg)
    } else {
      ElMessage.error(res.data.msg || '操作失败')
      row.is_enabled = row.is_enabled === 1 ? 0 : 1
    }
  } catch (error) {
    console.error('操作失败:', error)
    row.is_enabled = row.is_enabled === 1 ? 0 : 1
  }
}

// 测试Mock
const handleTest = (row) => {
  testData.method = row.mock_method
  testData.url = `${window.location.origin}/api${getMockFullUrl(row)}`
  testResult.value = null
  testDialogVisible.value = true
}

// 发送测试请求
const sendTestRequest = async () => {
  testLoading.value = true
  const startTime = Date.now()
  
  try {
    const response = await fetch(testData.url, {
      method: testData.method
    })
    const body = await response.text()
    
    testResult.value = {
      status: response.status,
      time: Date.now() - startTime,
      body: body
    }
  } catch (error) {
    testResult.value = {
      status: 0,
      time: Date.now() - startTime,
      body: error.message
    }
  } finally {
    testLoading.value = false
  }
}

// 查看日志
const handleViewLogs = async () => {
  try {
    const res = await queryLogs({
      project_id: searchForm.project_id,
      page: 1,
      pageSize: 100
    })
    if (res.data.code === 200) {
      logList.value = res.data.data || []
      logDialogVisible.value = true
    }
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

// 清空日志
const handleClearLogs = async () => {
  try {
    const res = await clearLogs(searchForm.project_id, 0)
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg)
      logList.value = []
    }
  } catch (error) {
    console.error('清空日志失败:', error)
  }
}

onMounted(() => {
  loadProjects().then(() => {
    loadData()
  })
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.search-container {
  background: var(--el-bg-color);
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.table-container {
  background: var(--el-bg-color);
  padding: 20px;
  border-radius: 4px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.mock-url {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mock-url span {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: monospace;
  font-size: 12px;
}

.response-editor {
  position: relative;
  width: 100%;
}

.format-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.header-editor {
  width: 100%;
}

.header-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.header-key {
  width: 150px;
}

.header-value {
  flex: 1;
}

.test-container {
  padding: 16px;
}

.test-url {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.test-url span {
  flex: 1;
  font-family: monospace;
}

.test-result {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}

.result-header {
  padding: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-time {
  margin-left: auto;
  color: #909399;
}

.result-body {
  padding: 12px;
  max-height: 300px;
  overflow: auto;
}

.result-body pre {
  margin: 0;
  font-family: monospace;
  font-size: 13px;
  white-space: pre-wrap;
}
</style>

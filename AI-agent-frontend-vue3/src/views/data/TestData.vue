<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="test-data-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试数据管理</span>
          <div class="header-actions">
            <el-button type="primary" :icon="Plus" @click="handleCreate">新增数据</el-button>
            <el-button type="success" :icon="Upload" @click="handleImport">导入数据</el-button>
            <el-button type="warning" :icon="Download" @click="handleExportTemplate">下载模板</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索数据名称或标识"
          clearable
          style="width: 300px"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="searchParams.type" placeholder="数据类型" clearable style="width: 150px; margin-left: 10px">
          <el-option label="用户数据" value="user" />
          <el-option label="测试账号" value="account" />
          <el-option label="API配置" value="api" />
          <el-option label="数据库配置" value="database" />
          <el-option label="其他" value="other" />
        </el-select>
        <el-select v-model="searchParams.environment" placeholder="环境" clearable style="width: 150px; margin-left: 10px">
          <el-option label="开发环境" value="dev" />
          <el-option label="测试环境" value="test" />
          <el-option label="预发环境" value="staging" />
          <el-option label="生产环境" value="prod" />
        </el-select>
        <el-button type="primary" @click="handleSearch" style="margin-left: 10px">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="testDataList"
        v-loading="loading"
        stripe
        border
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="数据名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="identifier" label="标识" width="150" show-overflow-tooltip />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">{{ getTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="环境" width="120">
          <template #default="{ row }">
            <el-tag :type="getEnvColor(row.environment)">{{ getEnvName(row.environment) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="success" @click="handleExport(row)">导出</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="数据名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入数据名称" />
        </el-form-item>
        <el-form-item label="标识" prop="identifier">
          <el-input v-model="formData.identifier" placeholder="请输入唯一标识，如: USER_001" />
        </el-form-item>
        <el-form-item label="数据类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择数据类型">
            <el-option label="用户数据" value="user" />
            <el-option label="测试账号" value="account" />
            <el-option label="API配置" value="api" />
            <el-option label="数据库配置" value="database" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="环境" prop="environment">
          <el-select v-model="formData.environment" placeholder="请选择环境">
            <el-option label="开发环境" value="dev" />
            <el-option label="测试环境" value="test" />
            <el-option label="预发环境" value="staging" />
            <el-option label="生产环境" value="prod" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="8"
            placeholder="请输入JSON格式的数据内容"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog v-model="viewDialogVisible" title="查看数据" width="800px">
      <el-descriptions :column="2" border v-if="currentData">
        <el-descriptions-item label="数据名称" :span="2">{{ currentData.name }}</el-descriptions-item>
        <el-descriptions-item label="标识">{{ currentData.identifier }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="getTypeColor(currentData.type)">{{ getTypeName(currentData.type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="环境">
          <el-tag :type="getEnvColor(currentData.environment)">{{ getEnvName(currentData.environment) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentData.created_at }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentData.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="数据内容" :span="2">
          <pre class="json-content">{{ formatJson(currentData.content) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入数据" width="600px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".json,.xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 JSON 和 Excel 格式，文件大小不超过 10MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importing">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import { Plus, Upload, Download, Search, UploadFilled } from '@element-plus/icons-vue'

interface TestData {
  id: number
  name: string
  identifier: string
  type: string
  environment: string
  content: string
  description?: string
  created_at: string
  updated_at: string
}

const loading = ref(false)
const submitting = ref(false)
const importing = ref(false)
const testDataList = ref<TestData[]>([])
const total = ref(0)

// 搜索参数
const searchParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  type: '',
  environment: ''
})

// 对话框
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const importDialogVisible = ref(false)
const dialogTitle = computed(() => formData.id ? '编辑数据' : '新增数据')

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<TestData>>({
  name: '',
  identifier: '',
  type: '',
  environment: '',
  content: '',
  description: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入数据名称', trigger: 'blur' }],
  identifier: [{ required: true, message: '请输入标识', trigger: 'blur' }],
  type: [{ required: true, message: '请选择数据类型', trigger: 'change' }],
  environment: [{ required: true, message: '请选择环境', trigger: 'change' }],
  content: [{ required: true, message: '请输入数据内容', trigger: 'blur' }]
}

// 当前查看的数据
const currentData = ref<TestData | null>(null)

// 导入文件
const importFile = ref<UploadFile | null>(null)

// 获取类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, any> = {
    user: 'primary',
    account: 'success',
    api: 'warning',
    database: 'danger',
    other: 'info'
  }
  return colors[type] || 'info'
}

// 获取类型名称
const getTypeName = (type: string) => {
  const names: Record<string, string> = {
    user: '用户数据',
    account: '测试账号',
    api: 'API配置',
    database: '数据库配置',
    other: '其他'
  }
  return names[type] || type
}

// 获取环境颜色
const getEnvColor = (env: string) => {
  const colors: Record<string, any> = {
    dev: 'info',
    test: 'warning',
    staging: 'primary',
    prod: 'danger'
  }
  return colors[env] || 'info'
}

// 获取环境名称
const getEnvName = (env: string) => {
  const names: Record<string, string> = {
    dev: '开发环境',
    test: '测试环境',
    staging: '预发环境',
    prod: '生产环境'
  }
  return names[env] || env
}

// 格式化 JSON
const formatJson = (content: string) => {
  try {
    return JSON.stringify(JSON.parse(content), null, 2)
  } catch {
    return content
  }
}

// 加载数据
const loadData = () => {
  loading.value = true
  
  // 模拟数据
  setTimeout(() => {
    testDataList.value = [
      {
        id: 1,
        name: '测试用户001',
        identifier: 'USER_001',
        type: 'user',
        environment: 'test',
        content: '{"username":"test001","password":"123456","email":"test001@example.com"}',
        description: '测试环境的用户数据',
        created_at: '2025-10-03 10:00:00',
        updated_at: '2025-10-03 10:00:00'
      },
      {
        id: 2,
        name: '测试账号002',
        identifier: 'ACCOUNT_002',
        type: 'account',
        environment: 'test',
        content: '{"username":"admin","password":"admin123"}',
        description: '测试环境的管理员账号',
        created_at: '2025-10-03 11:00:00',
        updated_at: '2025-10-03 11:00:00'
      },
      {
        id: 3,
        name: 'API配置-开发环境',
        identifier: 'API_DEV',
        type: 'api',
        environment: 'dev',
        content: '{"baseUrl":"http://localhost:8000","timeout":30000}',
        description: '开发环境的API配置',
        created_at: '2025-10-03 12:00:00',
        updated_at: '2025-10-03 12:00:00'
      }
    ]
    total.value = 3
    loading.value = false
  }, 500)
}

// 搜索
const handleSearch = () => {
  loadData()
}

// 重置
const handleReset = () => {
  searchParams.keyword = ''
  searchParams.type = ''
  searchParams.environment = ''
  searchParams.page = 1
  handleSearch()
}

// 新增
const handleCreate = () => {
  Object.assign(formData, {
    id: undefined,
    name: '',
    identifier: '',
    type: '',
    environment: '',
    content: '',
    description: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: TestData) => {
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 查看
const handleView = (row: TestData) => {
  currentData.value = row
  viewDialogVisible.value = true
}

// 导出单条
const handleExport = (row: TestData) => {
  const data = JSON.stringify(row, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${row.identifier}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

// 删除
const handleDelete = async (row: TestData) => {
  try {
    await ElMessageBox.confirm('确定要删除该测试数据吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('删除成功')
    handleSearch()
  } catch {
    // 用户取消
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      // 验证 JSON 格式
      try {
        JSON.parse(formData.content!)
      } catch {
        ElMessage.error('数据内容必须是有效的 JSON 格式')
        return
      }
      
      submitting.value = true
      try {
        // TODO: 调用API保存数据
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success(formData.id ? '更新成功' : '创建成功')
        dialogVisible.value = false
        handleSearch()
      } catch (error) {
        ElMessage.error('操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 导入
const handleImport = () => {
  importDialogVisible.value = true
}

// 文件选择
const handleFileChange = (file: UploadFile) => {
  importFile.value = file
}

// 导入提交
const handleImportSubmit = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  importing.value = true
  try {
    // TODO: 解析并导入文件
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    handleSearch()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

// 下载模板
const handleExportTemplate = () => {
  const template = {
    name: '示例数据',
    identifier: 'EXAMPLE_001',
    type: 'user',
    environment: 'test',
    content: '{"key":"value"}',
    description: '这是一个示例'
  }
  
  const data = JSON.stringify([template], null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'test_data_template.json'
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('模板下载成功')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.test-data-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.json-content {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>


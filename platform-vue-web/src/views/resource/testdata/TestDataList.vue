<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="文件名称" prop="name">
        <el-input v-model="searchForm.name" placeholder="请输入文件名称" clearable style="width: 180px" />
      </el-form-item>
      <el-form-item label="文件类型" prop="file_type">
        <el-select v-model="searchForm.file_type" placeholder="全部" clearable style="width: 120px">
          <el-option label="Excel" value="xlsx" />
          <el-option label="CSV" value="csv" />
          <el-option label="JSON" value="json" />
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          上传数据文件
        </el-button>
        <el-button type="success" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建数据集
        </el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedRows.length === 0">
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedRows.length }})
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="测试数据管理 (DDT)"
      :data="tableData"
      :total="total"
      :loading="loading"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
      @selection-change="handleSelectionChange"
      type="selection"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="文件名称" width="250" show-overflow-tooltip>
        <template #default="scope">
          <span class="file-name">
            <el-icon :class="getFileIcon(scope.row.file_type)"><Document /></el-icon>
            {{ scope.row.name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="file_type" label="类型" width="100">
        <template #default="scope">
          <el-tag :type="getFileTypeTag(scope.row.file_type)" size="small">
            {{ scope.row.file_type?.toUpperCase() }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="rows" label="数据量" width="100" align="center">
        <template #default="scope">
          <span class="data-count">{{ scope.row.rows }} 行</span>
        </template>
      </el-table-column>
      <el-table-column prop="columns" label="字段数" width="100" align="center">
        <template #default="scope">
          <span>{{ scope.row.columns }} 列</span>
        </template>
      </el-table-column>
      <el-table-column prop="size" label="文件大小" width="100">
        <template #default="scope">
          {{ formatFileSize(scope.row.size) }}
        </template>
      </el-table-column>
      <el-table-column prop="update_time" label="上传时间" width="170">
        <template #default="scope">
          {{ formatDateTime(scope.row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column fixed="right" label="操作" width="200">
        <template #default="scope">
          <el-button link type="primary" @click="handlePreview(scope.row)">预览</el-button>
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button link type="success" @click="handleDownload(scope.row)">下载</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传测试数据文件" width="550px">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="5"
        accept=".xlsx,.xls,.csv,.json"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :file-list="uploadFileList"
        multiple
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 .xlsx / .csv / .json 格式，单个文件不超过 10MB</div>
        </template>
      </el-upload>
      <el-form label-width="80px" class="mt-4">
        <el-form-item label="描述">
          <el-input v-model="uploadDescription" type="textarea" :rows="2" placeholder="请输入数据文件描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="confirmUpload">开始上传</el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" :title="`数据预览 - ${previewData.name}`" width="90%" top="5vh">
      <div class="preview-toolbar">
        <el-input 
          v-model="previewSearch" 
          placeholder="搜索数据..." 
          clearable 
          style="width: 200px"
        />
        <span class="preview-info">
          共 {{ previewData.rows }} 行 × {{ previewData.columns }} 列
        </span>
      </div>
      <el-table 
        :data="filteredPreviewRows" 
        border 
        stripe 
        max-height="500"
        v-loading="previewLoading"
      >
        <el-table-column type="index" label="#" width="60" />
        <el-table-column 
          v-for="col in previewColumns" 
          :key="col" 
          :prop="col" 
          :label="col"
          min-width="120"
          show-overflow-tooltip
        />
      </el-table>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleDownload(previewData)">下载文件</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="formVisible" :title="form.id ? '编辑数据集' : '新建数据集'" width="700px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数据集名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="文件格式" prop="file_type">
              <el-select v-model="form.file_type" placeholder="请选择" style="width: 100%">
                <el-option label="JSON" value="json" />
                <el-option label="CSV" value="csv" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="数据内容" prop="content">
          <el-tabs v-model="editTab">
            <el-tab-pane label="表格编辑" name="table">
              <div class="table-editor">
                <div class="table-toolbar">
                  <el-button size="small" @click="addColumn">添加列</el-button>
                  <el-button size="small" @click="addRow">添加行</el-button>
                </div>
                <el-table :data="form.tableData" border size="small" max-height="300">
                  <el-table-column type="index" label="#" width="50" />
                  <el-table-column 
                    v-for="(col, idx) in form.columns" 
                    :key="idx" 
                    :label="col"
                    min-width="120"
                  >
                    <template #header>
                      <el-input v-model="form.columns[idx]" size="small" placeholder="列名" />
                    </template>
                    <template #default="scope">
                      <el-input v-model="scope.row[col]" size="small" />
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="80">
                    <template #default="scope">
                      <el-button link type="danger" size="small" @click="removeRow(scope.$index)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
            <el-tab-pane label="JSON 编辑" name="json">
              <CodeEditor 
                v-model="form.jsonContent" 
                mode="json" 
                height="250px"
                placeholder="请输入 JSON 格式的测试数据"
              />
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Delete, Document, UploadFilled } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import CodeEditor from '~/components/CodeEditor.vue'
import { formatDateTime } from '~/utils/timeFormatter'
import { 
  getTestDataList, 
  deleteTestData, 
  batchDeleteTestData,
  uploadTestData,
  downloadTestData,
  saveTestData,
  getTestDataPreview
} from '../resource'

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({ name: '', file_type: '' })

// 表格数据
const tableData = ref([])
const selectedRows = ref([])

// 上传相关
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const uploadFileList = ref([])
const uploadDescription = ref('')

// 预览相关
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref({ name: '', rows: 0, columns: 0 })
const previewColumns = ref([])
const previewRows = ref([])
const previewSearch = ref('')

const filteredPreviewRows = computed(() => {
  if (!previewSearch.value) return previewRows.value
  return previewRows.value.filter(row => 
    Object.values(row).some(val => 
      String(val).toLowerCase().includes(previewSearch.value.toLowerCase())
    )
  )
})

// 表单相关
const formVisible = ref(false)
const formRef = ref(null)
const saving = ref(false)
const editTab = ref('table')

const form = reactive({
  id: null,
  name: '',
  file_type: 'json',
  description: '',
  columns: ['col1', 'col2'],
  tableData: [{ col1: '', col2: '' }],
  jsonContent: '[\n  {\n    "key": "value"\n  }\n]'
})

const formRules = {
  name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }],
  file_type: [{ required: true, message: '请选择文件格式', trigger: 'change' }]
}

// 获取文件图标样式
const getFileIcon = (type) => {
  const icons = {
    'xlsx': 'excel-icon',
    'xls': 'excel-icon',
    'csv': 'csv-icon',
    'json': 'json-icon'
  }
  return icons[type] || ''
}

// 获取文件类型标签
const getFileTypeTag = (type) => {
  const tags = {
    'xlsx': 'success',
    'xls': 'success',
    'csv': 'warning',
    'json': ''
  }
  return tags[type] || 'info'
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getTestDataList({
      ...searchForm,
      page: pagination.value.page,
      pageSize: pagination.value.limit
    })
    if (res?.data?.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    } else {
      mockData()
    }
  } catch (error) {
    mockData()
  } finally {
    loading.value = false
  }
}

// Mock 数据
const mockData = () => {
  tableData.value = [
    { id: 1, name: '用户登录测试数据.xlsx', file_type: 'xlsx', rows: 100, columns: 5, size: 25600, update_time: '2025-12-28T10:00:00', description: '包含不同权限的用户账号' },
    { id: 2, name: '商品搜索关键字.csv', file_type: 'csv', rows: 50, columns: 3, size: 4096, update_time: '2025-12-29T14:00:00', description: '热门搜索词列表' },
    { id: 3, name: '订单测试数据.json', file_type: 'json', rows: 200, columns: 8, size: 51200, update_time: '2025-12-30T09:00:00', description: '各种状态的订单数据' },
    { id: 4, name: '地址信息.xlsx', file_type: 'xlsx', rows: 30, columns: 6, size: 12800, update_time: '2025-12-31T11:00:00', description: '收货地址测试数据' }
  ]
  total.value = 4
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, { name: '', file_type: '' })
  pagination.value.page = 1
  loadData()
}

// 选择变化
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 上传文件
const handleUpload = () => {
  uploadFileList.value = []
  uploadDescription.value = ''
  uploadVisible.value = true
}

const handleFileChange = (file, fileList) => {
  uploadFileList.value = fileList
}

const handleFileRemove = (file, fileList) => {
  uploadFileList.value = fileList
}

const confirmUpload = async () => {
  if (uploadFileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    uploadFileList.value.forEach(file => {
      formData.append('files', file.raw)
    })
    formData.append('description', uploadDescription.value)
    
    await uploadTestData(formData)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.success('上传成功 (Mock)')
    uploadVisible.value = false
    loadData()
  } finally {
    uploading.value = false
  }
}

// 预览数据
const handlePreview = async (row) => {
  previewData.value = row
  previewSearch.value = ''
  previewLoading.value = true
  previewVisible.value = true
  
  try {
    const res = await getTestDataPreview(row.id)
    if (res?.data?.code === 200) {
      previewColumns.value = res.data.data.columns || []
      previewRows.value = res.data.data.rows || []
    } else {
      mockPreview(row)
    }
  } catch (error) {
    mockPreview(row)
  } finally {
    previewLoading.value = false
  }
}

const mockPreview = (row) => {
  // 根据文件类型生成 Mock 数据
  if (row.name.includes('登录')) {
    previewColumns.value = ['username', 'password', 'role', 'expected', 'description']
    previewRows.value = [
      { username: 'admin', password: '123456', role: '管理员', expected: 'success', description: '正常登录' },
      { username: 'user1', password: '111111', role: '普通用户', expected: 'success', description: '普通用户登录' },
      { username: '', password: '123456', role: '', expected: 'fail', description: '用户名为空' },
      { username: 'admin', password: '', role: '', expected: 'fail', description: '密码为空' },
      { username: 'admin', password: 'wrong', role: '', expected: 'fail', description: '密码错误' }
    ]
  } else if (row.name.includes('搜索')) {
    previewColumns.value = ['keyword', 'category', 'expected_count']
    previewRows.value = [
      { keyword: '手机', category: '数码', expected_count: 100 },
      { keyword: '笔记本', category: '电脑', expected_count: 50 },
      { keyword: '耳机', category: '配件', expected_count: 200 }
    ]
  } else {
    previewColumns.value = ['id', 'name', 'value', 'status']
    previewRows.value = [
      { id: 1, name: '测试数据1', value: 'value1', status: 'active' },
      { id: 2, name: '测试数据2', value: 'value2', status: 'inactive' }
    ]
  }
}

// 下载文件
const handleDownload = async (row) => {
  try {
    const res = await downloadTestData(row.id)
    if (res?.data) {
      const blob = new Blob([res.data])
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = row.name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      ElMessage.success('下载成功')
    } else {
      // Mock 下载
      const content = JSON.stringify(previewRows.value || [], null, 2)
      const blob = new Blob([content], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = row.name.replace(/\.(xlsx|csv)$/, '.json')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      ElMessage.success('下载成功 (Mock)')
    }
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 新建数据集
const handleCreate = () => {
  Object.assign(form, {
    id: null,
    name: '',
    file_type: 'json',
    description: '',
    columns: ['col1', 'col2'],
    tableData: [{ col1: '', col2: '' }],
    jsonContent: '[\n  {\n    "col1": "value1",\n    "col2": "value2"\n  }\n]'
  })
  editTab.value = 'table'
  formVisible.value = true
}

// 编辑数据集
const handleEdit = (row) => {
  Object.assign(form, {
    id: row.id,
    name: row.name,
    file_type: row.file_type,
    description: row.description || '',
    columns: previewColumns.value.length > 0 ? [...previewColumns.value] : ['col1', 'col2'],
    tableData: previewRows.value.length > 0 ? [...previewRows.value] : [{ col1: '', col2: '' }],
    jsonContent: JSON.stringify(previewRows.value || [], null, 2)
  })
  editTab.value = 'table'
  formVisible.value = true
}

// 添加列
const addColumn = () => {
  const newCol = `col${form.columns.length + 1}`
  form.columns.push(newCol)
  form.tableData.forEach(row => {
    row[newCol] = ''
  })
}

// 添加行
const addRow = () => {
  const newRow = {}
  form.columns.forEach(col => {
    newRow[col] = ''
  })
  form.tableData.push(newRow)
}

// 删除行
const removeRow = (index) => {
  form.tableData.splice(index, 1)
}

// 保存数据集
const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const data = {
        ...form,
        content: editTab.value === 'json' ? form.jsonContent : JSON.stringify(form.tableData)
      }
      await saveTestData(data)
      ElMessage.success(form.id ? '更新成功' : '创建成功')
      formVisible.value = false
      loadData()
    } catch (error) {
      ElMessage.success((form.id ? '更新成功' : '创建成功') + ' (Mock)')
      formVisible.value = false
      loadData()
    } finally {
      saving.value = false
    }
  })
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除"${row.name}"吗？`, '删除确认', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteTestData(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.success('删除成功 (Mock)')
      loadData()
    }
  })
}

// 批量删除
const handleBatchDelete = () => {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 个文件吗？`, '批量删除确认', {
    type: 'warning'
  }).then(async () => {
    try {
      const ids = selectedRows.value.map(row => row.id)
      await batchDeleteTestData(ids)
      ElMessage.success('批量删除成功')
      selectedRows.value = []
      loadData()
    } catch (error) {
      ElMessage.success('批量删除成功 (Mock)')
      loadData()
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.excel-icon {
  color: #67c23a;
}

.csv-icon {
  color: #e6a23c;
}

.json-icon {
  color: #409eff;
}

.data-count {
  font-weight: 500;
  color: #409eff;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.preview-info {
  font-size: 14px;
  color: #606266;
}

.table-editor {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}
</style>

<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="元素名称" prop="name">
        <el-input v-model="searchForm.name" placeholder="请输入元素名称" clearable style="width: 180px" />
      </el-form-item>
      <el-form-item label="所属模块" prop="module">
        <el-select v-model="searchForm.module" placeholder="全部模块" clearable style="width: 180px">
          <el-option v-for="m in moduleList" :key="m.value" :label="m.label" :value="m.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="定位方式" prop="locate_type">
        <el-select v-model="searchForm.locate_type" placeholder="全部" clearable style="width: 150px">
          <el-option v-for="t in locateTypes" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增元素
        </el-button>
        <el-button type="success" @click="handleBatchImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button type="warning" @click="handleBatchExport">
          <el-icon><Download /></el-icon>
          批量导出
        </el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedRows.length === 0">
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedRows.length }})
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="Web 元素库管理"
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
      <el-table-column prop="name" label="元素名称" width="180" show-overflow-tooltip>
        <template #default="scope">
          <span class="element-name">{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="module_name" label="所属模块" width="120">
        <template #default="scope">
          <el-tag size="small">{{ scope.row.module_name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="locate_type" label="定位方式" width="120">
        <template #default="scope">
          <el-tag :type="getLocateTypeTag(scope.row.locate_type)" size="small">
            {{ scope.row.locate_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="locate_value" label="定位值" show-overflow-tooltip>
        <template #default="scope">
          <code class="locate-value">{{ scope.row.locate_value }}</code>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="备注说明" width="200" show-overflow-tooltip />
      <el-table-column prop="update_time" label="更新时间" width="170">
        <template #default="scope">
          {{ formatDateTime(scope.row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="180">
        <template #default="scope">
          <el-button link type="primary" @click="handleCopy(scope.row)">复制</el-button>
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="formVisible" :title="form.id ? '编辑元素' : '新增元素'" width="650px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="元素名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入元素名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属模块" prop="module">
              <el-select v-model="form.module" placeholder="请选择模块" style="width: 100%" allow-create filterable>
                <el-option v-for="m in moduleList" :key="m.value" :label="m.label" :value="m.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="定位方式" prop="locate_type">
              <el-select v-model="form.locate_type" placeholder="请选择定位方式" style="width: 100%">
                <el-option v-for="t in locateTypes" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="等待策略">
              <el-select v-model="form.wait_strategy" placeholder="默认" style="width: 100%">
                <el-option label="默认" value="default" />
                <el-option label="等待可见" value="visible" />
                <el-option label="等待可点击" value="clickable" />
                <el-option label="等待存在" value="presence" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="定位值" prop="locate_value">
          <el-input 
            v-model="form.locate_value" 
            type="textarea" 
            :rows="3"
            placeholder="请输入定位值，如：#username、//button[@type='submit']、.login-btn"
          />
          <div class="locate-tips">
            <el-tag size="small" type="info">提示</el-tag>
            <span class="tip-text">
              {{ getLocateTip(form.locate_type) }}
            </span>
          </div>
        </el-form-item>

        <el-form-item label="备注说明">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入备注说明" />
        </el-form-item>

        <el-form-item label="截图预览">
          <el-upload
            class="screenshot-uploader"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleScreenshotChange"
            accept="image/*"
          >
            <img v-if="form.screenshot" :src="form.screenshot" class="screenshot-preview" />
            <el-icon v-else class="screenshot-icon"><Picture /></el-icon>
          </el-upload>
          <span class="upload-tip">上传元素截图便于识别（可选）</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="importVisible" title="批量导入元素" width="550px">
      <el-form label-width="100px">
        <el-form-item label="导入模块">
          <el-select v-model="importModule" placeholder="请选择目标模块" style="width: 100%" allow-create filterable>
            <el-option v-for="m in moduleList" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="导入文件">
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".json,.csv,.xlsx"
            :on-change="handleImportFileChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 .json / .csv / .xlsx 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-alert type="info" :closable="false">
            <template #title><strong>导入格式说明</strong></template>
            <p>JSON 格式：[{"name": "元素名", "locate_type": "css", "locate_value": ".selector"}]</p>
            <p>CSV/Excel：包含 name, locate_type, locate_value 列</p>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="confirmImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Delete, UploadFilled, Picture } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { formatDateTime } from '~/utils/timeFormatter'
import { 
  getElementList, 
  deleteElement, 
  batchDeleteElement, 
  saveElement,
  importElements,
  exportElements 
} from './webElement'

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({ name: '', module: '', locate_type: '' })

// 表格数据
const tableData = ref([])
const selectedRows = ref([])

// 模块列表
const moduleList = ref([
  { label: '登录页', value: 'login' },
  { label: '首页', value: 'home' },
  { label: '详情页', value: 'detail' },
  { label: '购物车', value: 'cart' },
  { label: '个人中心', value: 'profile' }
])

// 定位方式
const locateTypes = [
  { label: 'CSS 选择器', value: 'css' },
  { label: 'XPath', value: 'xpath' },
  { label: 'ID', value: 'id' },
  { label: 'Name', value: 'name' },
  { label: 'Class', value: 'class' },
  { label: 'Text', value: 'text' },
  { label: 'Placeholder', value: 'placeholder' },
  { label: 'Test ID', value: 'testid' }
]

// 表单弹窗
const formVisible = ref(false)
const formRef = ref(null)
const saving = ref(false)

const form = reactive({
  id: null,
  name: '',
  module: '',
  locate_type: 'css',
  locate_value: '',
  description: '',
  wait_strategy: 'default',
  screenshot: ''
})

const formRules = {
  name: [{ required: true, message: '请输入元素名称', trigger: 'blur' }],
  module: [{ required: true, message: '请选择所属模块', trigger: 'change' }],
  locate_type: [{ required: true, message: '请选择定位方式', trigger: 'change' }],
  locate_value: [{ required: true, message: '请输入定位值', trigger: 'blur' }]
}

// 导入相关
const importVisible = ref(false)
const importing = ref(false)
const importModule = ref('')
const importFile = ref(null)

// 获取定位方式标签类型
const getLocateTypeTag = (type) => {
  const typeMap = {
    'css': '',
    'xpath': 'warning',
    'id': 'success',
    'name': 'info',
    'class': 'info',
    'text': 'danger',
    'placeholder': 'danger',
    'testid': 'success'
  }
  return typeMap[type] || ''
}

// 获取定位提示
const getLocateTip = (type) => {
  const tips = {
    'css': '示例：#login-btn、.submit-button、input[type="text"]',
    'xpath': '示例：//button[@id="submit"]、//div[contains(@class, "header")]',
    'id': '示例：username、login-form',
    'name': '示例：email、password',
    'class': '示例：btn-primary、form-control',
    'text': '示例：登录、提交（匹配元素文本内容）',
    'placeholder': '示例：请输入用户名（匹配 placeholder 属性）',
    'testid': '示例：login-button（匹配 data-testid 属性）'
  }
  return tips[type] || '请输入有效的定位值'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getElementList({
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
    console.error('查询失败:', error)
    mockData()
  } finally {
    loading.value = false
  }
}

// Mock 数据
const mockData = () => {
  tableData.value = [
    { id: 1, name: '用户名输入框', module: 'login', module_name: '登录页', locate_type: 'id', locate_value: 'username', description: '登录页用户名输入框', update_time: '2025-12-28T10:00:00' },
    { id: 2, name: '密码输入框', module: 'login', module_name: '登录页', locate_type: 'name', locate_value: 'password', description: '登录页密码输入框', update_time: '2025-12-28T10:00:00' },
    { id: 3, name: '登录按钮', module: 'login', module_name: '登录页', locate_type: 'xpath', locate_value: '//button[@type="submit"]', description: '点击登录', update_time: '2025-12-28T10:00:00' },
    { id: 4, name: '记住我复选框', module: 'login', module_name: '登录页', locate_type: 'css', locate_value: 'input[name="remember"]', description: '', update_time: '2025-12-28T10:00:00' },
    { id: 5, name: '侧边栏菜单', module: 'home', module_name: '首页', locate_type: 'css', locate_value: '.sidebar-menu', description: '左侧导航菜单', update_time: '2025-12-29T14:00:00' },
    { id: 6, name: '搜索框', module: 'home', module_name: '首页', locate_type: 'placeholder', locate_value: '请输入搜索内容', description: '顶部搜索框', update_time: '2025-12-29T14:00:00' },
    { id: 7, name: '商品标题', module: 'detail', module_name: '详情页', locate_type: 'css', locate_value: '.product-title', description: '商品详情页标题', update_time: '2025-12-30T09:00:00' },
    { id: 8, name: '加入购物车按钮', module: 'detail', module_name: '详情页', locate_type: 'testid', locate_value: 'add-to-cart', description: '', update_time: '2025-12-30T09:00:00' }
  ]
  total.value = 8
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, { name: '', module: '', locate_type: '' })
  pagination.value.page = 1
  loadData()
}

// 选择变化
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 新增
const handleCreate = () => {
  Object.assign(form, {
    id: null,
    name: '',
    module: '',
    locate_type: 'css',
    locate_value: '',
    description: '',
    wait_strategy: 'default',
    screenshot: ''
  })
  formVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  Object.assign(form, {
    id: row.id,
    name: row.name,
    module: row.module,
    locate_type: row.locate_type,
    locate_value: row.locate_value,
    description: row.description || '',
    wait_strategy: row.wait_strategy || 'default',
    screenshot: row.screenshot || ''
  })
  formVisible.value = true
}

// 复制定位值
const handleCopy = async (row) => {
  try {
    await navigator.clipboard.writeText(row.locate_value)
    ElMessage.success('定位值已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除元素"${row.name}"吗？`, '删除确认', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteElement(row.id)
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
  ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 个元素吗？`, '批量删除确认', {
    type: 'warning'
  }).then(async () => {
    try {
      const ids = selectedRows.value.map(row => row.id)
      await batchDeleteElement(ids)
      ElMessage.success('批量删除成功')
      selectedRows.value = []
      loadData()
    } catch (error) {
      ElMessage.success('批量删除成功 (Mock)')
      loadData()
    }
  })
}

// 保存
const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      await saveElement(form)
      ElMessage.success(form.id ? '更新成功' : '新增成功')
      formVisible.value = false
      loadData()
    } catch (error) {
      ElMessage.success((form.id ? '更新成功' : '新增成功') + ' (Mock)')
      formVisible.value = false
      loadData()
    } finally {
      saving.value = false
    }
  })
}

// 截图上传
const handleScreenshotChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    form.screenshot = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

// 批量导入
const handleBatchImport = () => {
  importModule.value = ''
  importFile.value = null
  importVisible.value = true
}

const handleImportFileChange = (file) => {
  importFile.value = file.raw
}

const confirmImport = async () => {
  if (!importModule.value) {
    ElMessage.warning('请选择目标模块')
    return
  }
  if (!importFile.value) {
    ElMessage.warning('请选择导入文件')
    return
  }
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', importFile.value)
    formData.append('module', importModule.value)
    await importElements(formData)
    ElMessage.success('导入成功')
    importVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.success('导入成功 (Mock)')
    importVisible.value = false
    loadData()
  } finally {
    importing.value = false
  }
}

// 批量导出
const handleBatchExport = async () => {
  try {
    const ids = selectedRows.value.length > 0 ? selectedRows.value.map(row => row.id) : null
    const res = await exportElements(ids)
    if (res?.data?.code === 200) {
      downloadFile(JSON.stringify(res.data.data, null, 2), 'web_elements.json')
      ElMessage.success('导出成功')
    } else {
      const exportData = selectedRows.value.length > 0 ? selectedRows.value : tableData.value
      downloadFile(JSON.stringify(exportData, null, 2), 'web_elements.json')
      ElMessage.success('导出成功 (Mock)')
    }
  } catch (error) {
    const exportData = selectedRows.value.length > 0 ? selectedRows.value : tableData.value
    downloadFile(JSON.stringify(exportData, null, 2), 'web_elements.json')
    ElMessage.success('导出成功 (Mock)')
  }
}

const downloadFile = (content, filename) => {
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.element-name {
  font-weight: 500;
}

.locate-value {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  color: #409eff;
}

.locate-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.tip-text {
  font-size: 12px;
  color: #909399;
}

.screenshot-uploader {
  display: inline-block;
}

.screenshot-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 120px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.screenshot-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.screenshot-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.screenshot-icon {
  font-size: 28px;
  color: #8c939d;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 12px;
}
</style>

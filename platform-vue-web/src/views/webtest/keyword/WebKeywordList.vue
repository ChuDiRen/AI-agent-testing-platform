<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="关键字名称" prop="name">
        <el-input v-model="searchForm.name" placeholder="根据关键字名称筛选" clearable style="width: 180px" />
      </el-form-item>
      <el-form-item label="关键字类型" prop="type">
        <el-select v-model="searchForm.type" placeholder="选择类型" clearable style="width: 180px">
          <el-option label="系统关键字" value="system" />
          <el-option label="自定义关键字" value="custom" />
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增关键字
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
      title="Web 关键字库"
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
      <el-table-column prop="name" label="关键字名称" show-overflow-tooltip>
        <template #default="scope">
          <span class="keyword-name">{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="keyword_fun_name" label="函数名" show-overflow-tooltip>
        <template #default="scope">
          <code class="func-name">{{ scope.row.keyword_fun_name }}</code>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.type === 'system' ? 'info' : 'success'" size="small">
            {{ scope.row.type === 'system' ? '系统' : '自定义' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="is_enabled" label="状态" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_enabled === '1' ? 'success' : 'info'" size="small">
            {{ scope.row.is_enabled === '1' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="170">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="180">
        <template #default="scope">
          <el-button link type="primary" @click="showDetail(scope.row)">详情</el-button>
          <el-button link type="primary" @click="handleEdit(scope.row)" :disabled="scope.row.type === 'system'">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)" :disabled="scope.row.type === 'system'">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="关键字详情" width="700px">
      <div v-if="currentKeyword" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="名称">{{ currentKeyword.name }}</el-descriptions-item>
          <el-descriptions-item label="函数名">
            <code class="func-name">{{ currentKeyword.keyword_fun_name }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="currentKeyword.type === 'system' ? 'info' : 'success'" size="small">
              {{ currentKeyword.type === 'system' ? '系统关键字' : '自定义关键字' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentKeyword.is_enabled === '1' ? 'success' : 'info'" size="small">
              {{ currentKeyword.is_enabled === '1' ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentKeyword.description || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="mt-4">
          <h4 class="section-title">参数列表</h4>
          <el-table :data="currentKeyword.param_list || []" size="small" border max-height="200">
            <el-table-column prop="name" label="参数名" width="150" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="required" label="必填" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.required ? 'danger' : 'info'" size="small">
                  {{ scope.row.required ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="desc" label="描述" />
          </el-table>
        </div>

        <div class="mt-4">
          <h4 class="section-title">使用示例 (YAML)</h4>
          <pre class="code-block">{{ currentKeyword.example || '暂无示例' }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="formVisible" :title="form.id ? '编辑关键字' : '新增关键字'" width="900px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关键字名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入关键字名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="函数名" prop="keyword_fun_name">
              <el-input v-model="form.keyword_fun_name" placeholder="请输入函数名（英文）" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否启用" prop="is_enabled">
              <el-radio-group v-model="form.is_enabled">
                <el-radio value="1">启用</el-radio>
                <el-radio value="0">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="描述">
              <el-input v-model="form.description" placeholder="请输入描述" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="代码实现" prop="keyword_value">
          <el-tabs v-model="activeTab" class="code-tabs">
            <el-tab-pane label="代码体" name="code">
              <CodeEditor 
                v-model="form.keyword_value" 
                mode="python" 
                height="350px"
                placeholder="请输入关键字的 Python 代码实现"
              />
              <div class="mt-2">
                <el-button type="primary" size="small" @click="generateExample">生成示例代码</el-button>
                <el-button type="success" size="small" @click="formatCode">格式化代码</el-button>
              </div>
            </el-tab-pane>
            <el-tab-pane label="参数定义" name="params">
              <el-table :data="form.keyword_desc" size="small" border max-height="250">
                <el-table-column prop="name" label="参数名" width="150" />
                <el-table-column prop="placeholder" label="参数描述" />
                <el-table-column label="操作" width="80">
                  <template #default="scope">
                    <el-button link type="danger" size="small" @click="removeParam(scope.$index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div class="param-input-group">
                <el-input v-model="newParam.name" placeholder="参数名" style="width: 150px" />
                <el-input v-model="newParam.placeholder" placeholder="参数描述" style="flex: 1" />
                <el-button type="primary" @click="addParam">添加</el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        <el-button type="success" :loading="saving" @click="handleSaveAndGenerate">保存并生成文件</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="importVisible" title="批量导入关键字" width="500px">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".json,.yaml,.yml"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 .json / .yaml 格式的关键字配置文件</div>
        </template>
      </el-upload>
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
import { Plus, Upload, Download, Delete, UploadFilled } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import CodeEditor from '~/components/CodeEditor.vue'
import { formatDateTime } from '~/utils/timeFormatter'
import { 
  getKeywordList, 
  deleteKeyword, 
  batchDeleteKeyword, 
  saveKeyword, 
  generateKeywordFile,
  importKeywords,
  exportKeywords 
} from './webKeyword'

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({ name: '', type: '' })

// 表格数据
const tableData = ref([])
const selectedRows = ref([])

// 详情弹窗
const detailVisible = ref(false)
const currentKeyword = ref(null)

// 表单弹窗
const formVisible = ref(false)
const formRef = ref(null)
const saving = ref(false)
const activeTab = ref('code')

const form = reactive({
  id: null,
  name: '',
  keyword_fun_name: '',
  keyword_value: '',
  keyword_desc: [],
  description: '',
  is_enabled: '1',
  type: 'custom'
})

const formRules = {
  name: [{ required: true, message: '请输入关键字名称', trigger: 'blur' }],
  keyword_fun_name: [{ required: true, message: '请输入函数名', trigger: 'blur' }]
}

const newParam = reactive({ name: '', placeholder: '' })

// 导入相关
const importVisible = ref(false)
const importing = ref(false)
const uploadRef = ref(null)
const importFile = ref(null)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getKeywordList({
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
    { 
      id: 1, 
      name: 'goto', 
      keyword_fun_name: 'goto', 
      type: 'system', 
      description: '导航到指定 URL', 
      is_enabled: '1', 
      create_time: '2025-01-01T00:00:00',
      param_list: [{ name: 'url', type: 'string', required: true, desc: '目标网址' }],
      example: '- action: goto\n  params:\n    url: "https://www.example.com"'
    },
    { 
      id: 2, 
      name: 'click', 
      keyword_fun_name: 'click', 
      type: 'system', 
      description: '点击页面元素', 
      is_enabled: '1', 
      create_time: '2025-01-01T00:00:00',
      param_list: [{ name: 'selector', type: 'string', required: true, desc: '元素选择器' }],
      example: '- action: click\n  params:\n    selector: "#submit-btn"'
    },
    { 
      id: 3, 
      name: 'fill', 
      keyword_fun_name: 'fill', 
      type: 'system', 
      description: '输入文本内容', 
      is_enabled: '1', 
      create_time: '2025-01-01T00:00:00',
      param_list: [
        { name: 'selector', type: 'string', required: true, desc: '元素选择器' },
        { name: 'text', type: 'string', required: true, desc: '输入内容' }
      ],
      example: '- action: fill\n  params:\n    selector: "input[name=user]"\n    text: "admin"'
    },
    { 
      id: 4, 
      name: 'assert_title', 
      keyword_fun_name: 'assert_title', 
      type: 'system', 
      description: '断言页面标题', 
      is_enabled: '1', 
      create_time: '2025-01-01T00:00:00',
      param_list: [{ name: 'text', type: 'string', required: true, desc: '期望的标题文本' }],
      example: '- action: assert_title\n  params:\n    text: "首页"'
    },
    { 
      id: 5, 
      name: 'wait_for_selector', 
      keyword_fun_name: 'wait_for_selector', 
      type: 'system', 
      description: '等待元素出现', 
      is_enabled: '1', 
      create_time: '2025-01-01T00:00:00',
      param_list: [
        { name: 'selector', type: 'string', required: true, desc: '元素选择器' },
        { name: 'timeout', type: 'number', required: false, desc: '超时时间(ms)' }
      ],
      example: '- action: wait_for_selector\n  params:\n    selector: ".loading"\n    timeout: 5000'
    },
    { 
      id: 101, 
      name: '登录流程', 
      keyword_fun_name: 'login_flow', 
      type: 'custom', 
      description: '执行完整的登录流程', 
      is_enabled: '1', 
      create_time: '2025-12-28T10:00:00',
      param_list: [
        { name: 'username', type: 'string', required: true, desc: '用户名' },
        { name: 'password', type: 'string', required: true, desc: '密码' }
      ],
      example: '- action: login_flow\n  params:\n    username: "admin"\n    password: "123456"'
    }
  ]
  total.value = 6
}

// 重置搜索
const resetSearch = () => {
  searchForm.name = ''
  searchForm.type = ''
  pagination.value.page = 1
  loadData()
}

// 选择变化
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 显示详情
const showDetail = (row) => {
  currentKeyword.value = row
  detailVisible.value = true
}

// 新增
const handleCreate = () => {
  Object.assign(form, {
    id: null,
    name: '',
    keyword_fun_name: '',
    keyword_value: '',
    keyword_desc: [],
    description: '',
    is_enabled: '1',
    type: 'custom'
  })
  activeTab.value = 'code'
  formVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  if (row.type === 'system') {
    ElMessage.warning('系统关键字不可编辑')
    return
  }
  Object.assign(form, {
    id: row.id,
    name: row.name,
    keyword_fun_name: row.keyword_fun_name,
    keyword_value: row.keyword_value || '',
    keyword_desc: row.keyword_desc || [],
    description: row.description || '',
    is_enabled: row.is_enabled,
    type: row.type
  })
  activeTab.value = 'code'
  formVisible.value = true
}

// 删除
const handleDelete = (row) => {
  if (row.type === 'system') {
    ElMessage.warning('系统关键字不可删除')
    return
  }
  ElMessageBox.confirm(`确定要删除关键字"${row.name}"吗？`, '删除确认', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteKeyword(row.id)
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
  const customRows = selectedRows.value.filter(row => row.type !== 'system')
  if (customRows.length === 0) {
    ElMessage.warning('请选择要删除的自定义关键字')
    return
  }
  ElMessageBox.confirm(`确定要删除选中的 ${customRows.length} 个关键字吗？`, '批量删除确认', {
    type: 'warning'
  }).then(async () => {
    try {
      const ids = customRows.map(row => row.id)
      await batchDeleteKeyword(ids)
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
      await saveKeyword({
        ...form,
        keyword_desc: JSON.stringify(form.keyword_desc)
      })
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

// 保存并生成文件
const handleSaveAndGenerate = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const saveRes = await saveKeyword({
        ...form,
        keyword_desc: JSON.stringify(form.keyword_desc)
      })
      await generateKeywordFile(form)
      ElMessage.success('保存并生成关键字文件成功')
      formVisible.value = false
      loadData()
    } catch (error) {
      ElMessage.success('保存并生成关键字文件成功 (Mock)')
      formVisible.value = false
      loadData()
    } finally {
      saving.value = false
    }
  })
}

// 生成示例代码
const generateExample = () => {
  form.keyword_value = `# -*- coding: UTF-8 -*-
# Web 自动化关键字示例
from playwright.sync_api import Page

class ${form.keyword_fun_name || 'custom_keyword'}:
    def __init__(self, page: Page):
        self.page = page

    def ${form.keyword_fun_name || 'custom_keyword'}(self, **kwargs):
        """
        自定义关键字实现
        kwargs: 从 YAML 用例传入的参数
        """
        # 获取参数
        # param1 = kwargs.get('param1', '')
        
        # 执行操作
        # self.page.locator('selector').click()
        
        pass
`
}

// 格式化代码
const formatCode = () => {
  if (!form.keyword_value) {
    ElMessage.warning('请先输入代码')
    return
  }
  // 简单的 Python 代码格式化
  const lines = form.keyword_value.split('\n')
  const formattedLines = []
  let indentLevel = 0
  const indentSize = 4

  for (const line of lines) {
    let trimmed = line.trim()
    if (!trimmed) {
      formattedLines.push('')
      continue
    }
    
    // 减少缩进的情况
    if (trimmed.startsWith('elif ') || trimmed.startsWith('else:') || 
        trimmed.startsWith('except') || trimmed.startsWith('finally:')) {
      indentLevel = Math.max(0, indentLevel - 1)
    }
    
    formattedLines.push(' '.repeat(indentLevel * indentSize) + trimmed)
    
    // 增加缩进的情况
    if (trimmed.endsWith(':')) {
      indentLevel++
    }
  }
  
  form.keyword_value = formattedLines.join('\n')
  ElMessage.success('代码格式化完成')
}

// 添加参数
const addParam = () => {
  if (!newParam.name) {
    ElMessage.warning('请输入参数名')
    return
  }
  form.keyword_desc.push({ ...newParam })
  newParam.name = ''
  newParam.placeholder = ''
}

// 删除参数
const removeParam = (index) => {
  form.keyword_desc.splice(index, 1)
}

// 批量导入
const handleBatchImport = () => {
  importFile.value = null
  importVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const confirmImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', importFile.value)
    await importKeywords(formData)
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
    const res = await exportKeywords(ids)
    if (res?.data?.code === 200) {
      downloadFile(JSON.stringify(res.data.data, null, 2), 'web_keywords.json')
      ElMessage.success('导出成功')
    } else {
      // Mock 导出
      const exportData = selectedRows.value.length > 0 ? selectedRows.value : tableData.value
      downloadFile(JSON.stringify(exportData, null, 2), 'web_keywords.json')
      ElMessage.success('导出成功 (Mock)')
    }
  } catch (error) {
    const exportData = selectedRows.value.length > 0 ? selectedRows.value : tableData.value
    downloadFile(JSON.stringify(exportData, null, 2), 'web_keywords.json')
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

.keyword-name {
  font-weight: 500;
}

.func-name {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.code-block {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  overflow-x: auto;
}

.detail-content {
  padding: 10px;
}

.code-tabs {
  width: 100%;
}

.param-input-group {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}
</style>

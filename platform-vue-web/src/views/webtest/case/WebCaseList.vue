<template>
  <div class="page-container flex h-full gap-4 overflow-hidden">
    <!-- 左侧目录树 -->
    <div class="tree-panel">
      <div class="tree-header">
        <h3 class="tree-title">用例目录</h3>
        <div class="tree-actions">
          <el-button link type="primary" @click="handleAddFolder" title="新建目录">
            <el-icon><FolderAdd /></el-icon>
          </el-button>
          <el-button link type="primary" @click="handleRefreshTree" title="刷新">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
      <el-input
        v-model="filterText"
        placeholder="搜索目录"
        size="small"
        class="tree-search"
        clearable
      />
      <div class="tree-content">
        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="defaultProps"
          highlight-current
          node-key="id"
          default-expand-all
          :filter-node-method="filterNode"
          @node-click="handleNodeClick"
        >
          <template #default="{ node, data }">
            <span class="tree-node">
              <el-icon v-if="data.type === 'folder'" class="folder-icon"><Folder /></el-icon>
              <el-icon v-else class="file-icon"><Document /></el-icon>
              <span class="node-label">{{ node.label }}</span>
              <span v-if="data.type === 'folder'" class="node-count">({{ data.children?.length || 0 }})</span>
            </span>
          </template>
        </el-tree>
      </div>
    </div>

    <!-- 右侧内容区 -->
    <div class="content-panel">
      <!-- 列表视图 -->
      <template v-if="!isEditing">
        <BaseSearch :model="searchForm" :loading="loading" @search="handleSearch" @reset="resetSearch">
          <el-form-item label="用例名称">
            <el-input v-model="searchForm.name" placeholder="请输入用例名称" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item label="文件类型">
            <el-select v-model="searchForm.file_type" placeholder="全部" clearable style="width: 120px">
              <el-option label="YAML" value="yaml" />
              <el-option label="Excel" value="excel" />
            </el-select>
          </el-form-item>
          <template #actions>
            <el-button type="warning" :disabled="selectedRows.length === 0" @click="handleBatchAddToPlan">
              <el-icon><FolderAdd /></el-icon>
              添加到计划 ({{ selectedRows.length }})
            </el-button>
            <el-button type="success" @click="showXMindImport">
              <el-icon><Upload /></el-icon>
              导入XMind
            </el-button>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新增用例
            </el-button>
          </template>
        </BaseSearch>

        <BaseTable
          :title="`用例列表 - ${projectName}`"
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
          <el-table-column prop="name" label="用例名称" show-overflow-tooltip>
            <template #default="scope">
              <span class="case-name" @click="handleEdit(scope.row)">{{ scope.row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="folder_name" label="所属目录" width="120" />
          <el-table-column prop="file_type" label="文件类型" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.file_type === 'yaml' ? 'success' : 'info'" size="small">
                {{ scope.row.file_type?.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="step_count" label="步骤数" width="80" align="center" />
          <el-table-column prop="update_time" label="修改时间" width="170">
            <template #default="scope">
              {{ formatDateTime(scope.row.update_time) }}
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" width="200">
            <template #default="scope">
              <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button link type="success" @click="handleExecute(scope.row)">执行</el-button>
              <el-button link type="warning" @click="handleCopy(scope.row)">复制</el-button>
              <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </BaseTable>
      </template>

      <!-- 编辑视图 -->
      <div v-else class="editor-panel">
        <div class="editor-header">
          <div class="editor-title">
            <el-button circle size="small" @click="isEditing = false">
              <el-icon><Back /></el-icon>
            </el-button>
            <h3>{{ currentCase.id ? '编辑用例' : '新增用例' }}</h3>
            <el-input 
              v-model="currentCase.name" 
              placeholder="请输入用例名称" 
              style="width: 300px; margin-left: 16px"
            />
            <el-select v-model="currentCase.folder_id" placeholder="选择目录" style="width: 150px; margin-left: 12px">
              <el-option v-for="f in folderList" :key="f.id" :label="f.label" :value="f.id" />
            </el-select>
          </div>
          <div class="editor-actions">
            <el-button @click="isEditing = false">取消</el-button>
            <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
            <el-button type="success" :loading="saving" @click="handleSaveAndRun">保存并执行</el-button>
          </div>
        </div>
        <div class="editor-body">
          <el-tabs v-model="editorTab" class="editor-tabs">
            <el-tab-pane label="YAML 编辑器" name="yaml">
              <CodeEditor 
                v-model="currentCase.content" 
                mode="yaml" 
                height="calc(100vh - 280px)" 
                theme="monokai"
              />
            </el-tab-pane>
            <el-tab-pane label="可视化编辑" name="visual">
              <div class="visual-editor">
                <el-alert type="info" :closable="false" class="mb-4">
                  可视化编辑器开发中，目前请使用 YAML 编辑器
                </el-alert>
                <!-- 可视化步骤列表 -->
                <div class="step-list">
                  <div v-for="(step, index) in parsedSteps" :key="index" class="step-item">
                    <span class="step-index">{{ index + 1 }}</span>
                    <span class="step-action">{{ step.action }}</span>
                    <span class="step-name">{{ step.name }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- 批量添加到计划弹窗 -->
    <el-dialog v-model="batchAddDialogVisible" title="添加用例到测试计划" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择计划" required>
          <el-select v-model="selectedPlanId" placeholder="请选择测试计划" filterable style="width: 100%">
            <el-option
              v-for="plan in planList"
              :key="plan.id"
              :label="plan.plan_name"
              :value="plan.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="已选用例">
          <div class="selected-cases">
            <el-tag v-for="row in selectedRows" :key="row.id" size="small" closable @close="removeSelectedCase(row)">
              {{ row.name }}
            </el-tag>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchAddDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchAdding" @click="confirmBatchAdd">确定添加</el-button>
      </template>
    </el-dialog>

    <!-- XMind导入弹窗 -->
    <el-dialog v-model="xmindDialogVisible" title="导入XMind测试用例" width="600px">
      <el-form label-width="100px">
        <el-form-item label="目标目录" required>
          <el-select v-model="xmindFolderId" placeholder="请选择目标目录" filterable style="width: 100%">
            <el-option
              v-for="folder in folderList"
              :key="folder.id"
              :label="folder.label"
              :value="folder.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="XMind文件" required>
          <el-upload
            ref="xmindUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xmind"
            :on-change="handleXMindFileChange"
            :on-remove="handleXMindFileRemove"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传.xmind文件，支持XMind 8及以上版本</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-alert type="info" :closable="false">
            <template #title><strong>XMind结构说明</strong></template>
            <p>• 中心主题：项目/模块名称（忽略）</p>
            <p>• 一级子主题：测试用例名称</p>
            <p>• 二级子主题：测试步骤（action: 操作名）</p>
            <p>• 三级子主题：步骤参数（key: value格式）</p>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="xmindDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="xmindImporting" @click="confirmXMindImport">开始导入</el-button>
      </template>
    </el-dialog>

    <!-- 新建目录弹窗 -->
    <el-dialog v-model="folderDialogVisible" title="新建目录" width="400px">
      <el-form label-width="80px">
        <el-form-item label="目录名称" required>
          <el-input v-model="newFolderName" placeholder="请输入目录名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddFolder">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Folder, Document, Back, FolderAdd, Upload } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import CodeEditor from '~/components/CodeEditor.vue'
import { formatDateTime } from '~/utils/timeFormatter'
import { 
  getWebCaseList, 
  getWebCaseTree, 
  getWebCaseById,
  deleteWebCase, 
  saveWebCase,
  importXMindCase,
  addCasesToPlan,
  createFolder
} from './webCase'

const route = useRoute()
const router = useRouter()

// 项目信息
const projectId = ref(route.query.project_id)
const projectName = ref(route.query.project_name || 'Web 项目')

// 目录树
const treeData = ref([])
const treeRef = ref(null)
const filterText = ref('')
const defaultProps = { children: 'children', label: 'label' }
const currentFolderId = ref(null)

// 表格数据
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const pagination = ref({ page: 1, limit: 10 })
const searchForm = reactive({ name: '', file_type: '' })
const selectedRows = ref([])

// 编辑器
const isEditing = ref(false)
const editorTab = ref('yaml')
const currentCase = reactive({ 
  id: null, 
  name: '', 
  content: '', 
  folder_id: null, 
  file_type: 'yaml' 
})
const saving = ref(false)

// 目录列表（用于下拉选择）
const folderList = computed(() => {
  const folders = []
  const extractFolders = (nodes) => {
    nodes.forEach(node => {
      if (node.type === 'folder') {
        folders.push({ id: node.id, label: node.label })
        if (node.children) {
          extractFolders(node.children)
        }
      }
    })
  }
  extractFolders(treeData.value)
  return folders
})

// 解析的步骤（用于可视化编辑）
const parsedSteps = computed(() => {
  try {
    // 简单解析 YAML 中的 test_steps
    const match = currentCase.content.match(/test_steps:\s*\n([\s\S]*?)(?=\n\w|$)/)
    if (match) {
      const steps = []
      const stepMatches = match[1].matchAll(/- name:\s*(.+)\n\s+action:\s*(\w+)/g)
      for (const m of stepMatches) {
        steps.push({ name: m[1], action: m[2] })
      }
      return steps
    }
  } catch (e) {}
  return []
})

// 批量添加到计划
const batchAddDialogVisible = ref(false)
const selectedPlanId = ref(null)
const planList = ref([])
const batchAdding = ref(false)

// XMind 导入
const xmindDialogVisible = ref(false)
const xmindFolderId = ref(null)
const xmindFile = ref(null)
const xmindImporting = ref(false)

// 新建目录
const folderDialogVisible = ref(false)
const newFolderName = ref('')

// 过滤节点
const filterNode = (value, data) => {
  if (!value) return true
  return data.label.toLowerCase().includes(value.toLowerCase())
}

watch(filterText, (val) => {
  treeRef.value?.filter(val)
})

// 刷新目录树
const handleRefreshTree = async () => {
  try {
    const res = await getWebCaseTree(projectId.value)
    if (res?.data?.code === 200) {
      treeData.value = res.data.data
    } else {
      mockTree()
    }
  } catch (e) {
    mockTree()
  }
}

const mockTree = () => {
  treeData.value = [
    { 
      id: 'f1', 
      label: '冒烟测试', 
      type: 'folder', 
      children: [
        { id: '1', label: '登录页面测试.yaml', type: 'file' },
        { id: '2', label: '首页基础跳转.yaml', type: 'file' }
      ]
    },
    { 
      id: 'f2', 
      label: '核心业务', 
      type: 'folder', 
      children: [
        { id: '3', label: '下单流程.yaml', type: 'file' },
        { id: '4', label: '支付流程.yaml', type: 'file' }
      ]
    },
    { 
      id: 'f3', 
      label: '回归测试', 
      type: 'folder', 
      children: [
        { id: '5', label: '用户中心.yaml', type: 'file' }
      ]
    }
  ]
}

// 点击节点
const handleNodeClick = (data) => {
  if (data.type === 'folder') {
    currentFolderId.value = data.id
    loadData()
  } else {
    handleEdit(data)
  }
}

// 加载用例列表
const loadData = async () => {
  loading.value = true
  try {
    const res = await getWebCaseList({ 
      project_id: projectId.value, 
      folder_id: currentFolderId.value,
      ...searchForm, 
      ...pagination.value 
    })
    if (res?.data?.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    } else {
      mockData()
    }
  } catch (e) {
    mockData()
  } finally {
    loading.value = false
  }
}

const mockData = () => {
  tableData.value = [
    { id: 1, name: '登录页面测试.yaml', folder_name: '冒烟测试', file_type: 'yaml', step_count: 5, update_time: '2025-12-30T10:00:00' },
    { id: 2, name: '首页基础跳转.yaml', folder_name: '冒烟测试', file_type: 'yaml', step_count: 3, update_time: '2025-12-30T11:00:00' },
    { id: 3, name: '下单流程.yaml', folder_name: '核心业务', file_type: 'yaml', step_count: 12, update_time: '2025-12-31T15:30:00' },
    { id: 4, name: '支付流程.yaml', folder_name: '核心业务', file_type: 'yaml', step_count: 8, update_time: '2025-12-31T16:00:00' }
  ]
  total.value = 4
}

// 搜索
const handleSearch = () => { 
  pagination.value.page = 1
  loadData() 
}

const resetSearch = () => { 
  searchForm.name = ''
  searchForm.file_type = ''
  currentFolderId.value = null
  handleSearch() 
}

// 选择变化
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 新增用例
const handleCreate = () => {
  Object.assign(currentCase, { 
    id: null, 
    name: '新建用例.yaml', 
    content: `# Web 自动化测试用例
config:
  name: 新建用例
  description: 用例描述
  variables: {}

test_steps:
  - name: 访问首页
    action: goto
    params:
      url: "https://www.example.com"
  
  - name: 检查标题
    action: assert_title
    params:
      text: "Example Domain"
`, 
    folder_id: currentFolderId.value || (folderList.value[0]?.id), 
    file_type: 'yaml' 
  })
  editorTab.value = 'yaml'
  isEditing.value = true
}

// 编辑用例
const handleEdit = async (row) => {
  try {
    const res = await getWebCaseById(row.id)
    if (res?.data?.code === 200) {
      Object.assign(currentCase, res.data.data)
    } else {
      // Mock
      Object.assign(currentCase, { 
        id: row.id, 
        name: row.label || row.name, 
        content: `# ${row.label || row.name}
config:
  name: ${row.label || row.name}
  description: 自动化测试用例
  variables:
    base_url: "https://www.example.com"

test_steps:
  - name: 访问页面
    action: goto
    params:
      url: "\${base_url}"

  - name: 等待页面加载
    action: wait_for_selector
    params:
      selector: "body"
      timeout: 5000

  - name: 检查标题
    action: assert_title
    params:
      text: "Example Domain"
`, 
        folder_id: currentFolderId.value, 
        file_type: 'yaml' 
      })
    }
  } catch (e) {
    Object.assign(currentCase, { 
      id: row.id, 
      name: row.label || row.name, 
      content: `config:\n  name: ${row.label || row.name}\n\ntest_steps:\n  - name: 示例步骤\n    action: goto\n    params:\n      url: "https://example.com"`, 
      folder_id: currentFolderId.value, 
      file_type: 'yaml' 
    })
  }
  editorTab.value = 'yaml'
  isEditing.value = true
}

// 保存用例
const handleSave = async () => {
  if (!currentCase.name) {
    ElMessage.warning('请输入用例名称')
    return
  }
  saving.value = true
  try {
    await saveWebCase({
      ...currentCase,
      project_id: projectId.value
    })
    ElMessage.success('保存成功')
    isEditing.value = false
    handleRefreshTree()
    loadData()
  } catch (e) {
    ElMessage.success('保存成功 (Mock)')
    isEditing.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

// 保存并执行
const handleSaveAndRun = async () => {
  await handleSave()
  if (!saving.value) {
    router.push({
      path: '/WebExecution',
      query: { project_id: projectId.value, case_id: currentCase.id }
    })
  }
}

// 执行用例
const handleExecute = (row) => {
  router.push({
    path: '/WebExecution',
    query: { project_id: projectId.value, case_id: row.id }
  })
}

// 复制用例
const handleCopy = (row) => {
  Object.assign(currentCase, {
    id: null,
    name: row.name.replace('.yaml', '_copy.yaml'),
    content: row.content || '',
    folder_id: row.folder_id || currentFolderId.value,
    file_type: 'yaml'
  })
  isEditing.value = true
  ElMessage.success('已复制用例，请修改后保存')
}

// 删除用例
const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该用例吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      await deleteWebCase(row.id)
      ElMessage.success('删除成功')
      handleRefreshTree()
      loadData()
    } catch (e) {
      ElMessage.success('删除成功 (Mock)')
      loadData()
    }
  })
}

// 批量添加到计划
const handleBatchAddToPlan = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  selectedPlanId.value = null
  loadPlanList()
  batchAddDialogVisible.value = true
}

const loadPlanList = async () => {
  // Mock 计划列表
  planList.value = [
    { id: 1, plan_name: 'Web 冒烟测试计划' },
    { id: 2, plan_name: '核心流程回归计划' },
    { id: 3, plan_name: '每日巡检计划' }
  ]
}

const removeSelectedCase = (row) => {
  const index = selectedRows.value.findIndex(r => r.id === row.id)
  if (index > -1) {
    selectedRows.value.splice(index, 1)
  }
}

const confirmBatchAdd = async () => {
  if (!selectedPlanId.value) {
    ElMessage.warning('请选择测试计划')
    return
  }
  batchAdding.value = true
  try {
    const caseIds = selectedRows.value.map(row => row.id)
    await addCasesToPlan({
      plan_id: selectedPlanId.value,
      case_ids: caseIds
    })
    ElMessage.success(`成功添加 ${caseIds.length} 个用例到计划`)
    batchAddDialogVisible.value = false
    selectedRows.value = []
  } catch (error) {
    ElMessage.success(`成功添加 ${selectedRows.value.length} 个用例到计划 (Mock)`)
    batchAddDialogVisible.value = false
    selectedRows.value = []
  } finally {
    batchAdding.value = false
  }
}

// XMind 导入
const showXMindImport = () => {
  xmindFolderId.value = currentFolderId.value || (folderList.value[0]?.id)
  xmindFile.value = null
  xmindDialogVisible.value = true
}

const handleXMindFileChange = (file) => {
  xmindFile.value = file.raw
}

const handleXMindFileRemove = () => {
  xmindFile.value = null
}

const confirmXMindImport = async () => {
  if (!xmindFolderId.value) {
    ElMessage.warning('请选择目标目录')
    return
  }
  if (!xmindFile.value) {
    ElMessage.warning('请选择XMind文件')
    return
  }
  
  xmindImporting.value = true
  try {
    const formData = new FormData()
    formData.append('file', xmindFile.value)
    formData.append('project_id', projectId.value)
    formData.append('folder_id', xmindFolderId.value)
    
    const res = await importXMindCase(formData)
    
    if (res?.data?.code === 200) {
      const data = res.data.data || {}
      ElMessage.success(`导入完成：成功${data.imported_count || 0}个，失败${data.failed_count || 0}个`)
    } else {
      ElMessage.success('导入完成 (Mock)')
    }
    xmindDialogVisible.value = false
    handleRefreshTree()
    loadData()
  } catch (error) {
    ElMessage.success('导入完成 (Mock)')
    xmindDialogVisible.value = false
    loadData()
  } finally {
    xmindImporting.value = false
  }
}

// 新建目录
const handleAddFolder = () => {
  newFolderName.value = ''
  folderDialogVisible.value = true
}

const confirmAddFolder = async () => {
  if (!newFolderName.value) {
    ElMessage.warning('请输入目录名称')
    return
  }
  try {
    await createFolder({
      project_id: projectId.value,
      name: newFolderName.value
    })
    ElMessage.success('创建成功')
    folderDialogVisible.value = false
    handleRefreshTree()
  } catch (e) {
    ElMessage.success('创建成功 (Mock)')
    folderDialogVisible.value = false
    treeData.value.push({
      id: 'f' + Date.now(),
      label: newFolderName.value,
      type: 'folder',
      children: []
    })
  }
}

onMounted(() => {
  handleRefreshTree()
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';

.page-container {
  padding: 16px;
  background: #f5f7fa;
}

.tree-panel {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.tree-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.tree-actions {
  display: flex;
  gap: 4px;
}

.tree-search {
  margin: 12px;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 12px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
}

.folder-icon {
  color: #e6a23c;
}

.file-icon {
  color: #909399;
}

.node-label {
  font-size: 13px;
}

.node-count {
  font-size: 12px;
  color: #909399;
}

.content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

.case-name {
  color: #409eff;
  cursor: pointer;
  font-weight: 500;
}

.case-name:hover {
  text-decoration: underline;
}

.editor-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.editor-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.editor-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.editor-body {
  flex: 1;
  overflow: hidden;
}

.editor-tabs {
  height: 100%;
}

.editor-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
  padding: 0;
}

.editor-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.visual-editor {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.step-index {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.step-action {
  font-family: 'Consolas', monospace;
  font-size: 13px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 2px 8px;
  border-radius: 4px;
}

.step-name {
  color: #606266;
}

.selected-cases {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 150px;
  overflow-y: auto;
}
</style>

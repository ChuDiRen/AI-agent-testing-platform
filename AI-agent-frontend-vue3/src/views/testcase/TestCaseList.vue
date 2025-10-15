<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="testcase-list-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="总用例数" :value="statistics.total">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="API用例" :value="statistics.by_type?.API || 0">
            <template #prefix>
              <el-icon><Connection /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="Web用例" :value="statistics.by_type?.Web || 0">
            <template #prefix>
              <el-icon><Monitor /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="App用例" :value="statistics.by_type?.App || 0">
            <template #prefix>
              <el-icon><Iphone /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容 -->
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><List /></el-icon>
            测试用例管理
          </span>
          <div class="actions">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              创建用例
            </el-button>
            <el-button type="success" @click="handleAIGenerate">
              <el-icon><MagicStick /></el-icon>
              AI 生成
            </el-button>
            <el-button
              v-if="selectedIds.length > 0"
              type="success"
              @click="handleBatchExecute"
              :loading="batchExecuting"
            >
              <el-icon><VideoPlay /></el-icon>
              批量执行 ({{ selectedIds.length }})
            </el-button>
            <el-button
              v-if="selectedIds.length > 0"
              type="danger"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filters">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.keyword"
              placeholder="用例名称"
              clearable
              @clear="loadTestCases"
              @keyup.enter="loadTestCases"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="类型">
            <el-select
              v-model="filters.test_type"
              placeholder="全部"
              clearable
              @change="loadTestCases"
            >
              <el-option label="API" value="API" />
              <el-option label="Web" value="Web" />
              <el-option label="App" value="App" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filters.status"
              placeholder="全部"
              clearable
              @change="loadTestCases"
            >
              <el-option label="草稿" value="draft" />
              <el-option label="启用" value="active" />
              <el-option label="废弃" value="deprecated" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select
              v-model="filters.priority"
              placeholder="全部"
              clearable
              @change="loadTestCases"
            >
              <el-option label="P0" value="P0" />
              <el-option label="P1" value="P1" />
              <el-option label="P2" value="P2" />
              <el-option label="P3" value="P3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadTestCases">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="testCases"
        @selection-change="handleSelectionChange"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="testcase_id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="test_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.test_type)">
              {{ row.test_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="120" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              link
              type="success"
              size="small"
              @click="handleExecute(row)"
              :loading="row.executing"
            >
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTestCases"
          @current-change="loadTestCases"
        />
      </div>
    </el-card>

    <!-- 执行结果对话框 -->
    <el-dialog
      v-model="executionDialogVisible"
      title="执行结果"
      width="600px"
    >
      <div v-if="executionResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例名称">
            {{ executionResult.testcase_name }}
          </el-descriptions-item>
          <el-descriptions-item label="执行状态">
            <el-tag :type="getExecutionStatusType(executionResult.status)">
              {{ executionResult.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行时长">
            {{ executionResult.duration }}ms
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ new Date().toLocaleString() }}
          </el-descriptions-item>
        </el-descriptions>
        <div v-if="executionResult.error_message" class="error-message">
          <el-alert
            title="错误信息"
            type="error"
            :description="executionResult.error_message"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </el-dialog>

    <!-- AI 生成对话框 -->
    <AIGenerateDialog
      v-model="aiGenerateDialogVisible"
      @success="handleAIGenerateSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Connection,
  Monitor,
  Iphone,
  List,
  Plus,
  Search,
  RefreshRight,
  Edit,
  Delete,
  View,
  VideoPlay,
  MagicStick
} from '@element-plus/icons-vue'
import AIGenerateDialog from '@/components/testcase/AIGenerateDialog.vue'
import {
  getTestCasesAPI,
  getTestCaseStatisticsAPI,
  deleteTestCaseAPI,
  executeTestCaseAPI,
  batchExecuteTestCasesAPI,
  type TestCase,
  type TestCaseStatistics,
  type TestCaseExecutionResult
} from '@/api/testcase'

const router = useRouter()

// 状态
const loading = ref(false)
const batchExecuting = ref(false)
const testCases = ref<TestCase[]>([])
const selectedIds = ref<number[]>([])
const statistics = ref<TestCaseStatistics>({
  total: 0,
  by_type: {},
  by_status: {},
  by_priority: {}
})

// 筛选条件
const filters = reactive({
  keyword: '',
  test_type: '',
  status: '',
  priority: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 执行结果
const executionDialogVisible = ref(false)
const executionResult = ref<TestCaseExecutionResult | null>(null)

// AI 生成
const aiGenerateDialogVisible = ref(false)

// 加载测试用例列表
const loadTestCases = async () => {
  loading.value = true
  try {
    const response = await getTestCasesAPI({
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    })
    
    if (response.data) {
      testCases.value = response.data.items
      pagination.total = response.data.total
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 加载统计信息
const loadStatistics = async () => {
  try {
    const response = await getTestCaseStatisticsAPI()
    if (response.data) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

// 创建用例
const handleCreate = () => {
  router.push('/testcase/create')
}

// AI 生成
const handleAIGenerate = () => {
  aiGenerateDialogVisible.value = true
}

// AI 生成成功回调
const handleAIGenerateSuccess = () => {
  loadTestCases()
  loadStatistics()
}

// 查看用例
const handleView = (row: TestCase) => {
  router.push(`/testcase/${row.testcase_id}`)
}

// 编辑用例
const handleEdit = (row: TestCase) => {
  router.push(`/testcase/${row.testcase_id}?mode=edit`)
}

// 执行单个用例
const handleExecute = async (row: TestCase) => {
  row.executing = true as any
  try {
    const response = await executeTestCaseAPI(row.testcase_id)
    if (response.data) {
      executionResult.value = response.data
      executionDialogVisible.value = true
      
      if (response.data.status === 'passed') {
        ElMessage.success('用例执行通过')
      } else {
        ElMessage.warning('用例执行失败')
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '执行失败')
  } finally {
    row.executing = false as any
  }
}

// 删除用例
const handleDelete = async (row: TestCase) => {
  await ElMessageBox.confirm(
    `确认删除用例"${row.name}"吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  try {
    await deleteTestCaseAPI(row.testcase_id)
    ElMessage.success('删除成功')
    loadTestCases()
    loadStatistics()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 批量执行
const handleBatchExecute = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要执行的用例')
    return
  }

  batchExecuting.value = true
  try {
    const response = await batchExecuteTestCasesAPI(selectedIds.value)
    if (response.data) {
      const { passed, failed, error, total } = response.data
      ElMessage.success(
        `批量执行完成: 总计${total}个, 通过${passed}个, 失败${failed}个, 错误${error}个`
      )
    }
  } catch (error: any) {
    ElMessage.error(error.message || '批量执行失败')
  } finally {
    batchExecuting.value = false
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的用例')
    return
  }

  await ElMessageBox.confirm(
    `确认删除选中的 ${selectedIds.value.length} 个用例吗？此操作不可恢复。`,
    '批量删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  try {
    for (const id of selectedIds.value) {
      await deleteTestCaseAPI(id)
    }
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadTestCases()
    loadStatistics()
  } catch (error: any) {
    ElMessage.error(error.message || '批量删除失败')
  }
}

// 重置筛选
const handleReset = () => {
  filters.keyword = ''
  filters.test_type = ''
  filters.status = ''
  filters.priority = ''
  pagination.page = 1
  loadTestCases()
}

// 选择变化
const handleSelectionChange = (selection: TestCase[]) => {
  selectedIds.value = selection.map(item => item.testcase_id)
}

// 辅助函数
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, any> = {
    API: 'success',
    Web: 'primary',
    App: 'warning'
  }
  return typeMap[type] || ''
}

const getPriorityTagType = (priority: string) => {
  const priorityMap: Record<string, any> = {
    P0: 'danger',
    P1: 'warning',
    P2: '',
    P3: 'info'
  }
  return priorityMap[priority] || ''
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, any> = {
    draft: 'info',
    active: 'success',
    deprecated: 'danger'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    active: '启用',
    deprecated: '废弃'
  }
  return statusMap[status] || status
}

const getExecutionStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    passed: 'success',
    failed: 'warning',
    error: 'danger'
  }
  return statusMap[status] || ''
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 初始化
onMounted(() => {
  loadTestCases()
  loadStatistics()
})
</script>

<style scoped lang="scss">
.testcase-list-container {
  padding: 20px;

  .stats-row {
    margin-bottom: 20px;
  }

  .main-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 500;
      }

      .actions {
        display: flex;
        gap: 10px;
      }
    }

    .filter-section {
      margin-bottom: 20px;
    }

    .pagination-section {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }

  .error-message {
    margin-top: 20px;
  }
}
</style>


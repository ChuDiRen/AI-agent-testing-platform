<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="unified-testcase-container">
    <!-- 页面标题 -->
    <el-page-header :content="pageTitle" class="page-header" />

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用例名称">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入用例名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="活跃" value="active" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="全部" clearable style="width: 120px">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
          <el-button type="success" @click="handleCreate" :icon="Plus">新增用例</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 批量操作栏 -->
    <el-card v-if="selectedTestCases.length > 0" class="batch-action-card">
      <div class="batch-actions">
        <el-text type="info">已选择 <strong>{{ selectedTestCases.length }}</strong> 个测试用例</el-text>
        <div class="action-buttons">
          <el-button type="primary" @click="handleBatchExecute" :loading="batchExecuting">
            <el-icon><VideoPlay /></el-icon>
            批量执行
          </el-button>
          <el-button type="danger" @click="handleBatchDelete">
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 测试用例列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="testCases"
        border
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="testcase_id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column label="类型" width="100">
          <template #default>
            <el-tag :type="getTypeColor(testType)">{{ testTypeMap[testType] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="所属模块" prop="module">
          <el-input v-model="formData.module" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="用例描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入用例描述"
          />
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input
            v-model="formData.preconditions"
            type="textarea"
            :rows="2"
            placeholder="请输入前置条件"
          />
        </el-form-item>
        <el-form-item label="测试步骤" prop="test_steps">
          <el-input
            v-model="formData.test_steps"
            type="textarea"
            :rows="4"
            placeholder="请输入测试步骤"
          />
        </el-form-item>
        <el-form-item label="预期结果" prop="expected_result">
          <el-input
            v-model="formData.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入预期结果"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" style="width: 100%">
                <el-option label="P0" value="P0" />
                <el-option label="P1" value="P1" />
                <el-option label="P2" value="P2" />
                <el-option label="P3" value="P3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="草稿" value="draft" />
                <el-option label="活跃" value="active" />
                <el-option label="已归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标签">
          <el-input v-model="formData.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情查看对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="测试用例详情"
      width="800px"
    >
      <el-descriptions v-if="currentTestCase" :column="1" border>
        <el-descriptions-item label="用例编号">
          {{ currentTestCase.testcase_id }}
        </el-descriptions-item>
        <el-descriptions-item label="用例名称">
          {{ currentTestCase.name }}
        </el-descriptions-item>
        <el-descriptions-item label="测试类型">
          <el-tag :type="getTypeColor(currentTestCase.test_type)">
            {{ currentTestCase.test_type?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="模块">
          {{ currentTestCase.module || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(currentTestCase.priority)">
            {{ currentTestCase.priority }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentTestCase.status)">
            {{ getStatusText(currentTestCase.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用例描述">
          <div style="white-space: pre-wrap">{{ currentTestCase.description || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="前置条件">
          <div style="white-space: pre-wrap">{{ currentTestCase.preconditions || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="测试步骤">
          <div style="white-space: pre-wrap; max-height: 300px; overflow-y: auto">
            {{ currentTestCase.test_steps }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果">
          <div style="white-space: pre-wrap">{{ currentTestCase.expected_result }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="标签">
          <el-tag
            v-for="tag in (currentTestCase.tags || '').split(',').filter(t => t.trim())"
            :key="tag"
            size="small"
            style="margin-right: 4px"
          >
            {{ tag.trim() }}
          </el-tag>
          <span v-if="!currentTestCase.tags">无</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentTestCase.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ currentTestCase.updated_at }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromDetail">编辑</el-button>
      </template>
    </el-dialog>

    <!-- 批量执行结果对话框 -->
    <el-dialog
      v-model="batchResultVisible"
      title="批量执行结果"
      width="90%"
    >
      <el-alert
        v-if="batchResult"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #title>
          执行完成: 共 <strong>{{ batchResult.total }}</strong> 个用例，
          通过 <strong style="color: #67c23a">{{ batchResult.passed }}</strong> 个，
          失败 <strong style="color: #f56c6c">{{ batchResult.failed }}</strong> 个，
          错误 <strong style="color: #e6a23c">{{ batchResult.error }}</strong> 个，
          总耗时 <strong>{{ batchResult.total_duration }}</strong> 秒
        </template>
      </el-alert>

      <el-table
        v-if="batchResult"
        :data="batchResult.results"
        border
        stripe
        max-height="500"
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="testcase_name" label="用例名称" min-width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.status)">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时(秒)" width="100">
          <template #default="{ row }">
            {{ row.duration.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleViewResult(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="batchResultVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 单个执行结果详情 -->
    <el-dialog
      v-model="resultDetailVisible"
      title="执行结果详情"
      width="800px"
    >
      <el-descriptions v-if="currentResult" :column="1" border>
        <el-descriptions-item label="用例名称">
          {{ currentResult.testcase_name }}
        </el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="getResultType(currentResult.status)">
            {{ currentResult.status.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ currentResult.duration.toFixed(2) }} 秒
        </el-descriptions-item>
        <el-descriptions-item v-if="currentResult.actual_result" label="实际结果">
          <pre class="result-content">{{ currentResult.actual_result }}</pre>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentResult.error_message" label="错误信息">
          <el-alert
            :title="currentResult.error_message"
            type="error"
            :closable="false"
          />
        </el-descriptions-item>
        <el-descriptions-item v-if="currentResult.details" label="详细信息">
          <pre class="result-content">{{ JSON.stringify(currentResult.details, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="resultDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Plus, VideoPlay, Delete } from '@element-plus/icons-vue'
import request from '@/api/request'

// Props
const props = defineProps<{
  testType: 'api' | 'web' | 'app'
}>()

// 页面标题
const testTypeMap: Record<string, string> = {
  api: 'API',
  web: 'WEB',
  app: 'APP'
}

const pageTitle = computed(() => `${testTypeMap[props.testType]}测试用例管理`)

// 状态映射
const statusMap: Record<string, string> = {
  draft: '草稿',
  active: '活跃',
  archived: '已归档'
}

// 状态
const loading = ref(false)
const testCases = ref<any[]>([])
const total = ref(0)
const selectedRows = ref<any[]>([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  priority: '',
  test_type: props.testType
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20
})

// 对话框
const dialogVisible = ref(false)
const detailVisible = ref(false)
const batchResultVisible = ref(false)
const resultDetailVisible = ref(false)
const dialogTitle = ref('新增测试用例')
const formRef = ref<FormInstance>()
const submitting = ref(false)
const currentTestCase = ref<any>(null)

// 批量操作
const selectedTestCases = ref<any[]>([])
const batchExecuting = ref(false)
const batchResult = ref<any>(null)
const currentResult = ref<any>(null)

// 表单数据
const formData = reactive({
  testcase_id: null as number | null,
  name: '',
  module: '',
  description: '',
  preconditions: '',
  test_steps: '',
  expected_result: '',
  priority: 'P2',
  status: 'draft',
  tags: '',
  test_type: props.testType
})

// 表单验证规则
const formRules: FormRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  test_steps: [{ required: true, message: '请输入测试步骤', trigger: 'blur' }],
  expected_result: [{ required: true, message: '请输入预期结果', trigger: 'blur' }]
}

// 获取类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    api: 'primary',
    web: 'success',
    app: 'warning'
  }
  return colors[type] || 'info'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: 'info',
    active: 'success',
    archived: 'warning'
  }
  return types[status] || ''
}

// 加载测试用例列表
const loadTestCases = async () => {
  loading.value = true
  try {
    const response = await request({
      url: '/testcases',
      method: 'get',
      params: {
        page: pagination.page,
        page_size: pagination.page_size,
        test_type: props.testType,
        ...searchForm
      }
    })

    if (response.data) {
      testCases.value = response.data.items || []
      total.value = response.data.total || 0
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadTestCases()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.priority = ''
  handleSearch()
}

// 新增
const handleCreate = () => {
  dialogTitle.value = '新增测试用例'
  resetFormData()
  dialogVisible.value = true
}

// 查看
const handleView = (row: any) => {
  currentTestCase.value = row
  detailVisible.value = true
}

// 从详情进入编辑
const handleEditFromDetail = () => {
  detailVisible.value = false
  handleEdit(currentTestCase.value)
}

// 编辑
const handleEdit = (row: any) => {
  dialogTitle.value = '编辑测试用例'
  Object.assign(formData, {
    testcase_id: row.testcase_id,
    name: row.name,
    module: row.module || '',
    description: row.description || '',
    preconditions: row.preconditions || '',
    test_steps: row.test_steps || '',
    expected_result: row.expected_result || '',
    priority: row.priority || 'P2',
    status: row.status || 'draft',
    tags: row.tags || '',
    test_type: props.testType
  })
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试用例吗？', '提示', {
      type: 'warning'
    })

    await request({
      url: `/testcases/${row.testcase_id}`,
      method: 'delete'
    })

    ElMessage.success('删除成功')
    loadTestCases()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 选择变化
const handleSelectionChange = (rows: any[]) => {
  selectedTestCases.value = rows
}

// 批量执行
const handleBatchExecute = async () => {
  if (selectedTestCases.value.length === 0) {
    ElMessage.warning('请选择要执行的测试用例')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要执行选中的 ${selectedTestCases.value.length} 个测试用例吗？`,
      '批量执行',
      {
        type: 'warning',
        confirmButtonText: '确定执行',
        cancelButtonText: '取消'
      }
    )

    batchExecuting.value = true
    
    const testcaseIds = selectedTestCases.value.map(tc => tc.testcase_id)
    
    const response = await request({
      url: '/testcases/batch-execute',
      method: 'post',
      data: {
        testcase_ids: testcaseIds,
        config: {}
      }
    })

    if (response.data) {
      batchResult.value = response.data
      batchResultVisible.value = true
      ElMessage.success(response.message || '批量执行完成')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量执行失败:', error)
      ElMessage.error(error.message || '批量执行失败')
    }
  } finally {
    batchExecuting.value = false
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedTestCases.value.length === 0) {
    ElMessage.warning('请选择要删除的测试用例')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTestCases.value.length} 个测试用例吗？`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )

    // 逐个删除
    let successCount = 0
    let failCount = 0

    for (const tc of selectedTestCases.value) {
      try {
        await request({
          url: `/testcases/${tc.testcase_id}`,
          method: 'delete'
        })
        successCount++
      } catch (error) {
        failCount++
      }
    }

    if (failCount === 0) {
      ElMessage.success(`成功删除 ${successCount} 个测试用例`)
    } else {
      ElMessage.warning(`成功删除 ${successCount} 个，失败 ${failCount} 个`)
    }

    loadTestCases()
    selectedTestCases.value = []
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error(error.message || '批量删除失败')
    }
  }
}

// 查看执行结果详情
const handleViewResult = (row: any) => {
  currentResult.value = row
  resultDetailVisible.value = true
}

// 获取结果类型
const getResultType = (status: string) => {
  const types: Record<string, any> = {
    passed: 'success',
    failed: 'danger',
    error: 'warning',
    skipped: 'info'
  }
  return types[status] || 'info'
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    submitting.value = true

    const url = formData.testcase_id
      ? `/testcases/${formData.testcase_id}`
      : '/testcases'
    const method = formData.testcase_id ? 'put' : 'post'

    await request({
      url,
      method,
      data: formData
    })

    ElMessage.success(formData.testcase_id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadTestCases()
  } catch (error: any) {
    if (error?.message) {
      ElMessage.error(error.message)
    }
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetFormData()
}

// 重置表单数据
const resetFormData = () => {
  Object.assign(formData, {
    testcase_id: null,
    name: '',
    module: '',
    description: '',
    preconditions: '',
    test_steps: '',
    expected_result: '',
    priority: 'P2',
    status: 'draft',
    tags: '',
    test_type: props.testType
  })
}

// 初始化
onMounted(() => {
  loadTestCases()
})
</script>

<style scoped lang="scss">
.unified-testcase-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;

  .search-form {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
}

.batch-action-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;

  :deep(.el-card__body) {
    padding: 12px 20px;
  }

  .batch-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .el-text {
      color: white;
      font-size: 16px;
    }

    .action-buttons {
      display: flex;
      gap: 12px;
    }
  }
}

.table-card {
  :deep(.el-pagination) {
    display: flex;
  }
}

.result-content {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}
</style>


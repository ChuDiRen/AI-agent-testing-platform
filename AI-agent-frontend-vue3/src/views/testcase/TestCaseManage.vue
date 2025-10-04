<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="testcase-manage">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.total }}</div>
              <div class="stat-label">总用例数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.by_status?.active || 0 }}</div>
              <div class="stat-label">激活用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon :size="32"><Edit /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.by_status?.draft || 0 }}</div>
              <div class="stat-label">草稿用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-icon" style="background: #F56C6C;">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ statistics.by_priority?.P0 || 0 }}</div>
              <div class="stat-label">P0高优先级</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和操作栏 -->
    <el-card style="margin-top: 20px;">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="搜索用例名称或描述" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px;">
            <el-option label="草稿" value="draft" />
            <el-option label="激活" value="active" />
            <el-option label="已废弃" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="全部优先级" clearable style="width: 120px;">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
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
      <div style="margin-top: 10px;">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增用例
        </el-button>
        <el-button @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>

    <!-- 用例列表 -->
    <el-card style="margin-top: 20px;">
      <el-table :data="testcaseList" v-loading="loading" border stripe>
        <el-table-column prop="testcase_id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="module" label="所属模块" width="120" />
        <el-table-column prop="priority" label="优先级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-for="tag in (row.tags || '').split(',')" :key="tag" size="small" style="margin-right: 5px;">
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" size="small" link @click="handleExecute(row)">执行</el-button>
            <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="所属模块" prop="module">
          <el-input v-model="formData.module" placeholder="请输入所属模块" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" placeholder="请选择优先级">
            <el-option label="P0 - 最高" value="P0" />
            <el-option label="P1 - 高" value="P1" />
            <el-option label="P2 - 中" value="P2" />
            <el-option label="P3 - 低" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="激活" value="active" />
            <el-option label="已废弃" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="formData.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="用例描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入用例描述" />
        </el-form-item>
        <el-form-item label="前置条件" prop="preconditions">
          <el-input v-model="formData.preconditions" type="textarea" :rows="3" placeholder="请输入前置条件" />
        </el-form-item>
        <el-form-item label="测试步骤" prop="test_steps">
          <el-input v-model="formData.test_steps" type="textarea" :rows="5" placeholder="请输入测试步骤" />
        </el-form-item>
        <el-form-item label="预期结果" prop="expected_result">
          <el-input v-model="formData.expected_result" type="textarea" :rows="3" placeholder="请输入预期结果" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="用例详情" width="800px">
      <el-descriptions :column="2" border v-if="currentTestCase">
        <el-descriptions-item label="用例ID">{{ currentTestCase.testcase_id }}</el-descriptions-item>
        <el-descriptions-item label="用例名称">{{ currentTestCase.name }}</el-descriptions-item>
        <el-descriptions-item label="测试类型">{{ currentTestCase.test_type }}</el-descriptions-item>
        <el-descriptions-item label="所属模块">{{ currentTestCase.module }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(currentTestCase.priority)">{{ currentTestCase.priority }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentTestCase.status)">{{ getStatusText(currentTestCase.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">{{ currentTestCase.tags }}</el-descriptions-item>
        <el-descriptions-item label="用例描述" :span="2">{{ currentTestCase.description }}</el-descriptions-item>
        <el-descriptions-item label="前置条件" :span="2">{{ currentTestCase.preconditions }}</el-descriptions-item>
        <el-descriptions-item label="测试步骤" :span="2">
          <pre style="white-space: pre-wrap;">{{ currentTestCase.test_steps }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果" :span="2">{{ currentTestCase.expected_result }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentTestCase.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="修改时间">{{ formatTime(currentTestCase.modify_time) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Document, CircleCheck, Edit, Warning, Search, Refresh, Plus
} from '@element-plus/icons-vue'
import {
  getTestCaseList,
  createTestCase,
  updateTestCase,
  deleteTestCase,
  executeTestCase,
  getTestCaseStatistics,
  type TestCase,
  type TestCaseCreate,
  type TestCaseStatistics
} from '@/api/testcase'

// Props
const props = defineProps<{
  testType: string  // API/WEB/APP
}>()

// 统计数据
const statistics = ref<TestCaseStatistics>({
  total: 0,
  by_status: {},
  by_priority: {}
})

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  priority: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 列表数据
const testcaseList = ref<TestCase[]>([])
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => (isEdit.value ? '编辑用例' : '新增用例'))
const isEdit = ref(false)
const submitLoading = ref(false)

// 查看详情
const viewDialogVisible = ref(false)
const currentTestCase = ref<TestCase | null>(null)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<TestCaseCreate>({
  name: '',
  test_type: props.testType,
  module: '',
  description: '',
  preconditions: '',
  test_steps: '',
  expected_result: '',
  priority: 'P2',
  status: 'draft',
  tags: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const response = await getTestCaseList({
      page: pagination.page,
      page_size: pagination.page_size,
      test_type: props.testType,
      keyword: searchForm.keyword || undefined,
      status: searchForm.status || undefined,
      priority: searchForm.priority || undefined
    })
    
    if (response.success && response.data) {
      testcaseList.value = response.data.items
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('加载测试用例失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载统计
const loadStatistics = async () => {
  try {
    const response = await getTestCaseStatistics(props.testType)
    if (response.success && response.data) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.priority = ''
  pagination.page = 1
  loadData()
}

// 分页
const handleSizeChange = () => {
  pagination.page = 1
  loadData()
}

const handlePageChange = () => {
  loadData()
}

// 新增
const handleCreate = () => {
  isEdit.value = false
  Object.assign(formData, {
    name: '',
    test_type: props.testType,
    module: '',
    description: '',
    preconditions: '',
    test_steps: '',
    expected_result: '',
    priority: 'P2',
    status: 'draft',
    tags: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: TestCase) => {
  isEdit.value = true
  currentTestCase.value = row
  Object.assign(formData, {
    name: row.name,
    test_type: row.test_type,
    module: row.module,
    description: row.description,
    preconditions: row.preconditions,
    test_steps: row.test_steps,
    expected_result: row.expected_result,
    priority: row.priority,
    status: row.status,
    tags: row.tags
  })
  dialogVisible.value = true
}

// 查看
const handleView = (row: TestCase) => {
  currentTestCase.value = row
  viewDialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      submitLoading.value = true
      
      if (isEdit.value && currentTestCase.value) {
        const response = await updateTestCase(currentTestCase.value.testcase_id, formData)
        if (response.success) {
          ElMessage.success(response.message || '更新成功')
          dialogVisible.value = false
          loadData()
          loadStatistics()
        }
      } else {
        const response = await createTestCase(formData)
        if (response.success) {
          ElMessage.success(response.message || '创建成功')
          dialogVisible.value = false
          loadData()
          loadStatistics()
        }
      }
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

// 删除
const handleDelete = async (row: TestCase) => {
  try {
    await ElMessageBox.confirm(`确定要删除用例"${row.name}"吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await deleteTestCase(row.testcase_id)
    if (response.success) {
      ElMessage.success(response.message || '删除成功')
      loadData()
      loadStatistics()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 执行
const handleExecute = async (row: TestCase) => {
  try {
    const response = await executeTestCase(row.testcase_id, {})
    if (response.success) {
      ElMessage.success(response.message || '执行成功')
    }
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

// 对话框关闭
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 工具函数
const getPriorityType = (priority: string) => {
  const map: Record<string, any> = {
    P0: 'danger',
    P1: 'warning',
    P2: '',
    P3: 'info'
  }
  return map[priority] || ''
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    draft: 'warning',
    active: 'success',
    deprecated: 'info'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    active: '激活',
    deprecated: '已废弃'
  }
  return map[status] || status
}

const formatTime = (time?: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
  loadStatistics()
})
</script>

<style scoped>
.testcase-manage {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>


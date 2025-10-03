<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="testcase-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用例名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入用例名称"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="活跃" value="active" />
            <el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="请选择优先级" clearable>
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
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
          <el-button type="success" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增用例
          </el-button>
          <el-dropdown split-button type="warning" @click="handleBatchExport" v-if="selectedIds.length > 0">
            批量操作
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleBatchExport">
                  <el-icon><Download /></el-icon>
                  导出选中
                </el-dropdown-item>
                <el-dropdown-item @click="handleBatchChangeStatus">
                  <el-icon><Edit /></el-icon>
                  修改状态
                </el-dropdown-item>
                <el-dropdown-item @click="handleBatchDelete" divided>
                  <el-icon><Delete /></el-icon>
                  批量删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 测试用例列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="testCaseStore.loading"
        :data="testCaseStore.testCases"
        @selection-change="handleSelectionChange"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.type || 'api' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="
                row.status === 'active'
                  ? 'success'
                  : row.status === 'archived'
                  ? 'info'
                  : 'warning'
              "
            >
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-tag
              :type="
                row.priority === 'high'
                  ? 'danger'
                  : row.priority === 'medium'
                  ? 'warning'
                  : 'success'
              "
            >
              {{ priorityMap[row.priority] || row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="success" size="small" @click="handleExecute(row)">
              执行
            </el-button>
            <el-button type="info" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="testCaseStore.total"
          :page-sizes="[10, 20, 50, 100]"
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
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="活跃" value="active" />
            <el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input
            v-model="formData.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入预期结果"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useTestCaseStore } from '@/store/testcase'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Download, Edit, Delete } from '@element-plus/icons-vue'
import type { TestCase } from '@/api/testcase'
import { exportTestCasesToExcel } from '@/utils/export'

const testCaseStore = useTestCaseStore()

// 批量操作相关
const selectedIds = ref<number[]>([])
const selectedRows = ref<TestCase[]>([])

// 状态映射
const statusMap: Record<string, string> = {
  draft: '草稿',
  active: '活跃',
  archived: '归档'
}

// 优先级映射
const priorityMap: Record<string, string> = {
  low: '低',
  medium: '中',
  high: '高'
}

// 搜索表单
const searchForm = reactive({
  name: '',
  status: '',
  priority: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => (formData.id ? '编辑测试用例' : '新增测试用例'))

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<TestCase>>({
  name: '',
  description: '',
  type: 'api',
  status: 'draft',
  priority: 'medium',
  expected_result: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 批量操作相关函数
const handleSelectionChange = (selection: TestCase[]) => {
  selectedRows.value = selection
  selectedIds.value = selection.map(item => item.id)
}

// 批量导出
const handleBatchExport = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要导出的测试用例')
    return
  }
  
  const success = exportTestCasesToExcel(selectedRows.value, 'API测试用例')
  if (success) {
    ElMessage.success(`成功导出 ${selectedRows.value.length} 条测试用例`)
  } else {
    ElMessage.error('导出失败')
  }
}

// 批量修改状态
const handleBatchChangeStatus = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要修改的测试用例')
    return
  }

  try {
    const { value: status } = await ElMessageBox.prompt('请选择新的状态', '批量修改状态', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'select',
      inputOptions: {
        draft: '草稿',
        active: '活跃',
        archived: '归档'
      }
    })

    if (status) {
      // TODO: 调用批量更新API
      ElMessage.success(`已将 ${selectedIds.value.length} 条用例状态修改为 ${statusMap[status]}`)
      handleSearch()
    }
  } catch (error) {
    // 用户取消操作
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的测试用例')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条测试用例吗？此操作不可恢复！`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: 调用批量删除API
    // await batchDeleteTestCases(selectedIds.value)
    
    ElMessage.success(`成功删除 ${selectedIds.value.length} 条测试用例`)
    selectedIds.value = []
    selectedRows.value = []
    handleSearch()
  } catch (error) {
    // 用户取消操作
  }
}

// 初始化
onMounted(() => {
  handleSearch()
})

// 搜索
const handleSearch = () => {
  testCaseStore.fetchTestCaseList({
    ...searchForm,
    type: 'api',
    page: pagination.page,
    page_size: pagination.pageSize
  })
}

// 重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.status = ''
  searchForm.priority = ''
  pagination.page = 1
  handleSearch()
}

// 新增
const handleCreate = () => {
  Object.assign(formData, {
    id: undefined,
    name: '',
    description: '',
    type: 'api',
    status: 'draft',
    priority: 'medium',
    expected_result: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: TestCase) => {
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    description: row.description,
    status: row.status,
    priority: row.priority,
    expected_result: row.expected_result
  })
  dialogVisible.value = true
}

// 查看
const handleView = (row: TestCase) => {
  ElMessage.info('查看详情功能开发中...')
}

// 执行
const handleExecute = async (row: TestCase) => {
  ElMessage.info('执行测试用例功能开发中...')
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async valid => {
    if (!valid) return

    let success = false
    if (formData.id) {
      // 编辑
      success = await testCaseStore.updateTestCase(formData.id, formData)
    } else {
      // 新增
      success = await testCaseStore.createTestCase(formData)
    }

    if (success) {
      dialogVisible.value = false
      handleSearch()
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 删除
const handleDelete = async (row: TestCase) => {
  ElMessageBox.confirm(`确定要删除测试用例 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      const success = await testCaseStore.deleteTestCase(row.id)
      if (success) {
        handleSearch()
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.testcase-container {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 0;
}

.table-card {
  min-height: calc(100vh - 200px);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>

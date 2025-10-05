<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="test-data-management">
    <el-page-header content="测试数据管理" class="page-header" />

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="数据名称">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入数据名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="数据类型">
          <el-select v-model="searchForm.data_type" placeholder="全部" clearable style="width: 150px">
            <el-option label="JSON" value="json" />
            <el-option label="CSV" value="csv" />
            <el-option label="文本" value="text" />
            <el-option label="SQL" value="sql" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleReset" :icon="Refresh">重置</el-button>
          <el-button type="success" @click="handleCreate" :icon="Plus">新增数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="testDataList"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="数据名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="数据类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.data_type)">
              {{ row.data_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="数据大小" width="120">
          <template #default="{ row }">
            {{ getDataSize(row.content) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="success" size="small" @click="handleCopy(row)">复制</el-button>
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
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="数据名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入数据名称" />
        </el-form-item>
        <el-form-item label="数据类型" prop="data_type">
          <el-select v-model="formData.data_type" style="width: 100%">
            <el-option label="JSON" value="json">
              <el-icon><Document /></el-icon>
              <span style="margin-left: 8px">JSON</span>
            </el-option>
            <el-option label="CSV" value="csv">
              <el-icon><List /></el-icon>
              <span style="margin-left: 8px">CSV</span>
            </el-option>
            <el-option label="文本" value="text">
              <el-icon><EditPen /></el-icon>
              <span style="margin-left: 8px">文本</span>
            </el-option>
            <el-option label="SQL" value="sql">
              <el-icon><DataLine /></el-icon>
              <span style="margin-left: 8px">SQL</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述信息"
          />
        </el-form-item>
        <el-form-item label="数据内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="12"
            placeholder="请输入测试数据内容"
            show-word-limit
          />
          <el-text type="info" size="small">
            JSON格式示例: {"key": "value"}
            <br />
            CSV格式示例: name,age,email
          </el-text>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="测试数据详情"
      width="800px"
    >
      <el-descriptions v-if="currentData" :column="1" border>
        <el-descriptions-item label="数据ID">
          {{ currentData.id }}
        </el-descriptions-item>
        <el-descriptions-item label="数据名称">
          {{ currentData.name }}
        </el-descriptions-item>
        <el-descriptions-item label="数据类型">
          <el-tag :type="getTypeColor(currentData.data_type)">
            {{ currentData.data_type.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述">
          {{ currentData.description || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="数据大小">
          {{ getDataSize(currentData.content) }}
        </el-descriptions-item>
        <el-descriptions-item label="数据内容">
          <pre class="data-content">{{ currentData.content }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentData.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ currentData.updated_at }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Plus, Document, List, EditPen, DataLine } from '@element-plus/icons-vue'
import {
  getTestDataListAPI,
  getTestDataDetailAPI,
  createTestDataAPI,
  updateTestDataAPI,
  deleteTestDataAPI,
  type TestData
} from '@/api/test-data'

const testDataList = ref<TestData[]>([])
const loading = ref(false)
const total = ref(0)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('新增测试数据')
const formRef = ref<FormInstance>()
const submitting = ref(false)
const currentData = ref<TestData | null>(null)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  data_type: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20
})

// 表单数据
const formData = reactive({
  id: null as number | null,
  name: '',
  data_type: 'json',
  description: '',
  content: ''
})

// 表单验证规则
const formRules: FormRules = {
  name: [{ required: true, message: '请输入数据名称', trigger: 'blur' }],
  data_type: [{ required: true, message: '请选择数据类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入数据内容', trigger: 'blur' }]
}

// 获取类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    json: 'primary',
    csv: 'success',
    text: 'info',
    sql: 'warning'
  }
  return colors[type] || 'info'
}

// 获取数据大小
const getDataSize = (content: string) => {
  const bytes = new Blob([content]).size
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const response = await getTestDataListAPI({
      keyword: searchForm.keyword,
      data_type: searchForm.data_type,
      page: pagination.page,
      page_size: pagination.page_size
    })

    if (response.data) {
      testDataList.value = response.data.items || []
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
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.data_type = ''
  handleSearch()
}

// 新增
const handleCreate = () => {
  dialogTitle.value = '新增测试数据'
  resetFormData()
  dialogVisible.value = true
}

// 查看
const handleView = async (row: any) => {
  try {
    const response = await getTestDataDetailAPI(row.id)
    if (response.data) {
      currentData.value = response.data
      viewDialogVisible.value = true
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载详情失败')
  }
}

// 从查看进入编辑
const handleEditFromView = () => {
  viewDialogVisible.value = false
  handleEdit(currentData.value)
}

// 编辑
const handleEdit = (row: any) => {
  dialogTitle.value = '编辑测试数据'
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    data_type: row.data_type,
    description: row.description || '',
    content: row.content
  })
  dialogVisible.value = true
}

// 复制
const handleCopy = async (row: any) => {
  try {
    await navigator.clipboard.writeText(row.content)
    ElMessage.success('数据已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试数据吗？', '提示', {
      type: 'warning'
    })

    await deleteTestDataAPI(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    submitting.value = true

    if (formData.id) {
      // 更新
      await updateTestDataAPI(formData.id, {
        name: formData.name,
        data_type: formData.data_type,
        description: formData.description,
        content: formData.content
      })
      ElMessage.success('更新成功')
    } else {
      // 新增
      await createTestDataAPI({
        name: formData.name,
        data_type: formData.data_type,
        description: formData.description,
        content: formData.content
      })
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    resetFormData()
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单数据
const resetFormData = () => {
  Object.assign(formData, {
    id: null,
    name: '',
    data_type: 'json',
    description: '',
    content: ''
  })
  formRef.value?.clearValidate()
}

// 初始化加载
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.test-data-management {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;
  }

  .search-card {
    margin-bottom: 20px;
  }

  .table-card {
    :deep(.el-pagination) {
      display: flex;
    }
  }

  .data-content {
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
}
</style>


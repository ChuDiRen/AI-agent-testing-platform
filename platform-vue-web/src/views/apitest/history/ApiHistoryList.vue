<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="queryForm" :loading="loading" @search="handleQuery" @reset="handleReset">
      <el-form-item label="接口ID" prop="api_info_id">
        <el-input v-model="queryForm.api_info_id" placeholder="接口ID" clearable style="width: 150px" />
      </el-form-item>
      <el-form-item label="项目ID" prop="project_id">
        <el-input v-model="queryForm.project_id" placeholder="项目ID" clearable style="width: 150px" />
      </el-form-item>
      <el-form-item label="测试状态" prop="test_status">
        <el-select v-model="queryForm.test_status" placeholder="请选择" clearable style="width: 120px">
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="运行中" value="running" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="测试历史"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="handleQuery"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="test_name" label="测试名称" show-overflow-tooltip />
      <el-table-column prop="request_url" label="请求URL" show-overflow-tooltip />
      <el-table-column prop="request_method" label="请求方法" width="100" />
      <el-table-column prop="test_status" label="测试状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.test_status === 'success'" type="success">成功</el-tag>
          <el-tag v-else-if="scope.row.test_status === 'failed'" type="danger">失败</el-tag>
          <el-tag v-else type="info">运行中</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status_code" label="状态码" width="100" />
      <el-table-column prop="response_time" label="响应时间(ms)" width="120" />
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="handleView(scope.row)">查看</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="测试详情" width="80%">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="测试名称">{{ currentRow.test_name }}</el-descriptions-item>
        <el-descriptions-item label="测试状态">
          <el-tag v-if="currentRow.test_status === 'success'" type="success">成功</el-tag>
          <el-tag v-else-if="currentRow.test_status === 'failed'" type="danger">失败</el-tag>
          <el-tag v-else type="info">运行中</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="请求URL">{{ currentRow.request_url }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ currentRow.request_method }}</el-descriptions-item>
        <el-descriptions-item label="状态码">{{ currentRow.status_code }}</el-descriptions-item>
        <el-descriptions-item label="响应时间">{{ currentRow.response_time }}ms</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(currentRow.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatDateTime(currentRow.finish_time) }}</el-descriptions-item>
      </el-descriptions>

      <!-- 错误信息 -->
      <div v-if="currentRow.error_message" class="error-section">
        <h4>错误信息</h4>
        <el-alert type="error" :closable="false">
          {{ currentRow.error_message }}
        </el-alert>
      </div>

      <!-- 请求详情 -->
      <div class="detail-section">
        <h4>请求详情</h4>
        <el-tabs>
          <el-tab-pane label="请求头">
            <pre>{{ formatJson(currentRow.request_headers) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="请求参数">
            <pre>{{ formatJson(currentRow.request_params) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="请求体">
            <pre>{{ formatJson(currentRow.request_body) }}</pre>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 响应详情 -->
      <div class="detail-section">
        <h4>响应详情</h4>
        <el-tabs>
          <el-tab-pane label="响应头">
            <pre>{{ formatJson(currentRow.response_headers) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="响应体">
            <pre>{{ formatJson(currentRow.response_body) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="YAML用例" v-if="currentRow.yaml_content">
            <pre>{{ currentRow.yaml_content }}</pre>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryByPage, deleteData } from './apiHistory.js'
import { formatDateTime } from '@/utils/timeFormatter'
import BaseSearch from '@/components/BaseSearch/index.vue'
import BaseTable from '@/components/BaseTable/index.vue'

// 查询表单
const queryForm = reactive({
  api_info_id: '',
  project_id: '',
  test_status: ''
})

// 分页参数
const pagination = ref({ page: 1, limit: 10 })

// 表格数据
const tableData = ref([])
const total = ref(0)
const loading = ref(false)

// 详情对话框
const detailVisible = ref(false)
const currentRow = ref({})

// 查询数据
const handleQuery = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      ...queryForm,
      page: pagination.value.page,
      pageSize: pagination.value.limit,
      api_info_id: queryForm.api_info_id ? parseInt(queryForm.api_info_id) : null,
      project_id: queryForm.project_id ? parseInt(queryForm.project_id) : null
    })
    if (res.data.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    } else {
      ElMessage.error(res.data.msg || '查询失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置
const handleReset = () => {
  queryForm.api_info_id = ''
  queryForm.project_id = ''
  queryForm.test_status = ''
  pagination.value.page = 1
  handleQuery()
}

// 查看详情
const handleView = (row) => {
  currentRow.value = { ...row }
  detailVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该测试历史吗？', '提示', {
      type: 'warning'
    })

    const res = await deleteData(row.id)
    if (res.data.code === 200) {
      handleQuery()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

// 格式化JSON
const formatJson = (data) => {
  if (!data) return ''
  if (typeof data === 'string') {
    try {
      const obj = JSON.parse(data)
      return JSON.stringify(obj, null, 2)
    } catch {
      return data
    }
  } else if (typeof data === 'object') {
    return JSON.stringify(data, null, 2)
  }
  return data
}

onMounted(() => {
  handleQuery()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.error-section,
.detail-section {
  margin-top: 20px;
}

.error-section h4,
.detail-section h4 {
  margin-bottom: 10px;
  color: var(--text-primary);
  font-weight: 600;
}

pre {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  padding: 15px;
  border-radius: 8px;
  overflow: auto;
  max-height: 300px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}
</style>


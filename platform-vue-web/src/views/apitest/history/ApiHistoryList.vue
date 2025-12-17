<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="queryForm" :loading="loading" @search="handleQuery" @reset="handleReset">
      <el-form-item label="计划ID" prop="plan_id">
        <el-input v-model="queryForm.plan_id" placeholder="计划ID" clearable style="width: 120px" />
      </el-form-item>
      <el-form-item label="项目ID" prop="project_id">
        <el-input v-model="queryForm.project_id" placeholder="项目ID" clearable style="width: 120px" />
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
      <el-table-column prop="test_name" label="测试名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="execution_uuid" label="执行批次" width="120" show-overflow-tooltip />
      <el-table-column prop="test_status" label="测试状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.test_status === 'success'" type="success">成功</el-tag>
          <el-tag v-else-if="scope.row.test_status === 'failed'" type="danger">失败</el-tag>
          <el-tag v-else type="info">运行中</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="用例统计" width="150">
        <template #default="scope">
          <template v-if="getCaseSummary(scope.row)">
            <span style="color: #67c23a">{{ getCaseSummary(scope.row).passed }}</span>
            <span> / </span>
            <span style="color: #f56c6c">{{ getCaseSummary(scope.row).failed }}</span>
            <span> / {{ getCaseSummary(scope.row).total }}</span>
          </template>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="handleView(scope.row)">查看</el-button>
          <el-button v-if="scope.row.allure_report_path" link type="success" @click="handleViewReport(scope.row)">报告</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 报告对话框 -->
    <el-dialog v-model="reportVisible" title="测试报告" width="95%" top="2vh" class="report-dialog">
      <div class="report-container">
        <iframe v-if="reportUrl" :src="reportUrl" class="report-iframe" />
        <el-empty v-else description="加载报告中..." />
      </div>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="测试详情" width="85%" top="3vh">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="测试名称">{{ currentRow.test_name }}</el-descriptions-item>
        <el-descriptions-item label="测试状态">
          <el-tag v-if="currentRow.test_status === 'success'" type="success">成功</el-tag>
          <el-tag v-else-if="currentRow.test_status === 'failed'" type="danger">失败</el-tag>
          <el-tag v-else type="info">运行中</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(currentRow.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatDateTime(currentRow.finish_time) }}</el-descriptions-item>
        <el-descriptions-item label="执行批次">{{ currentRow.execution_uuid || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用例统计" v-if="parsedResponseData">
          <span>总计: {{ parsedResponseData.total }} | </span>
          <span style="color: #67c23a">通过: {{ parsedResponseData.passed }}</span>
          <span> | </span>
          <span style="color: #f56c6c">失败: {{ parsedResponseData.failed }}</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 汇总报告按钮 -->
      <div v-if="currentRow.allure_report_path" class="detail-section" style="margin-top: 15px;">
        <el-button type="primary" @click="handleViewReport(currentRow)">
          查看汇总报告
        </el-button>
      </div>

      <!-- 用例执行结果列表（计划执行时显示） -->
      <div v-if="parsedResponseData && parsedResponseData.cases && parsedResponseData.cases.length > 0" class="detail-section">
        <h4>用例执行结果 ({{ parsedResponseData.cases.length }} 个用例)</h4>
        <el-table :data="parsedResponseData.cases" border stripe style="width: 100%" max-height="400">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="case_name" label="用例名称" min-width="250" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.success" type="success" size="small">通过</el-tag>
              <el-tag v-else type="danger" size="small">失败</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="error" label="错误信息" min-width="200" show-overflow-tooltip>
            <template #default="scope">
              <span v-if="scope.row.error" style="color: #f56c6c">{{ scope.row.error }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 错误信息 -->
      <div v-if="currentRow.error_message" class="error-section">
        <h4>错误信息</h4>
        <el-alert type="error" :closable="false">
          {{ currentRow.error_message }}
        </el-alert>
      </div>

      <!-- 单用例请求详情（非计划执行时显示） -->
      <template v-if="!parsedResponseData || !parsedResponseData.cases">
        <div class="detail-section" v-if="currentRow.request_url">
          <h4>请求详情</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="请求URL">{{ currentRow.request_url }}</el-descriptions-item>
            <el-descriptions-item label="请求方法">{{ currentRow.request_method }}</el-descriptions-item>
            <el-descriptions-item label="状态码">{{ currentRow.status_code }}</el-descriptions-item>
            <el-descriptions-item label="响应时间">{{ currentRow.response_time }}ms</el-descriptions-item>
          </el-descriptions>
          <el-tabs style="margin-top: 10px">
            <el-tab-pane label="请求头">
              <JsonViewer :data="currentRow.request_headers" :show-toolbar="false" />
            </el-tab-pane>
            <el-tab-pane label="请求参数">
              <JsonViewer v-if="currentRow.request_params" :data="currentRow.request_params" :show-toolbar="false" />
              <el-empty v-else description="无请求参数" :image-size="60" />
            </el-tab-pane>
            <el-tab-pane label="请求体">
              <JsonViewer v-if="currentRow.request_body" :data="currentRow.request_body" :show-toolbar="false" />
              <el-empty v-else description="无请求体" :image-size="60" />
            </el-tab-pane>
          </el-tabs>
        </div>

        <div class="detail-section" v-if="currentRow.response_body || currentRow.response_headers">
          <h4>响应详情</h4>
          <el-tabs>
            <el-tab-pane label="响应头">
              <JsonViewer v-if="currentRow.response_headers" :data="currentRow.response_headers" :show-toolbar="false" />
              <el-empty v-else description="无响应头" :image-size="60" />
            </el-tab-pane>
            <el-tab-pane label="响应体">
              <JsonViewer v-if="currentRow.response_body" :data="currentRow.response_body" :show-toolbar="false" />
              <el-empty v-else description="无响应体" :image-size="60" />
            </el-tab-pane>
          </el-tabs>
        </div>
      </template>

      <!-- YAML用例 -->
      <div class="detail-section" v-if="currentRow.yaml_content">
        <h4>YAML用例</h4>
        <YamlViewer :content="currentRow.yaml_content" :show-toolbar="false" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryByPage, deleteData } from './apiHistory.js'
import { formatDateTime } from '~/utils/timeFormatter'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import JsonViewer from '~/components/JsonViewer.vue'
import YamlViewer from '~/components/YamlViewer.vue'

const route = useRoute()

// 查询表单
const queryForm = reactive({
  api_info_id: '',
  project_id: '',
  plan_id: '',
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

// 报告对话框
const reportVisible = ref(false)
const reportUrl = ref('')

// 解析 response_data（计划执行时包含多个用例结果）
const parsedResponseData = computed(() => {
  if (!currentRow.value.response_data) return null
  try {
    const data = typeof currentRow.value.response_data === 'string' 
      ? JSON.parse(currentRow.value.response_data) 
      : currentRow.value.response_data
    // 检查是否是计划执行的结果格式
    if (data && typeof data.total === 'number' && Array.isArray(data.cases)) {
      return data
    }
    return null
  } catch {
    return null
  }
})

// 获取用例统计（用于表格列表显示）
const getCaseSummary = (row) => {
  if (!row.response_data) return null
  try {
    const data = typeof row.response_data === 'string' 
      ? JSON.parse(row.response_data) 
      : row.response_data
    if (data && typeof data.total === 'number') {
      return {
        total: data.total,
        passed: data.passed || 0,
        failed: data.failed || 0
      }
    }
    return null
  } catch {
    return null
  }
}

// 查询数据
const handleQuery = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      ...queryForm,
      page: pagination.value.page,
      pageSize: pagination.value.limit,
      api_info_id: queryForm.api_info_id ? parseInt(queryForm.api_info_id) : null,
      project_id: queryForm.project_id ? parseInt(queryForm.project_id) : null,
      plan_id: queryForm.plan_id ? parseInt(queryForm.plan_id) : null
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
  queryForm.plan_id = ''
  queryForm.test_status = ''
  pagination.value.page = 1
  handleQuery()
}

// 查看详情
const handleView = (row) => {
  currentRow.value = { ...row }
  detailVisible.value = true
}

// 构建报告URL
const buildReportUrl = (path, historyId) => {
  // 使用后端 API 查看报告（智能查找报告文件）
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
  
  if (historyId) {
    return `${apiBase}/ApiReportViewer/view?history_id=${historyId}`
  }
  
  // 备用：如果没有 historyId，尝试静态文件方式
  if (path) {
    let reportPath = path
      .replace(/^temp[\\/]/, '')
      .replace(/\\/g, '/')
    return `/api/reports/${reportPath}/complete.html`
  }
  
  return null
}

// 查看报告
const handleViewReport = (row) => {
  if (row.allure_report_path || row.id) {
    reportUrl.value = buildReportUrl(row.allure_report_path, row.id)
    reportVisible.value = true
  } else {
    ElMessage.warning('暂无报告')
  }
}

// 查看单个用例的报告
const handleViewCaseReport = (caseRow) => {
  if (caseRow.temp_dir) {
    reportUrl.value = buildReportUrl(caseRow.temp_dir)
    reportVisible.value = true
  } else {
    ElMessage.warning('暂无报告')
  }
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
  // 从URL获取plan_id参数
  if (route.query.plan_id) {
    queryForm.plan_id = route.query.plan_id
  }
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

.yaml-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-all;
}

.report-container {
  width: 100%;
  height: calc(90vh - 100px);
}

.report-iframe {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 8px;
}
</style>


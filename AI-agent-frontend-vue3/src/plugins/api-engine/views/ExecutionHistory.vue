<template>
  <div class="execution-history-container">
    <div class="header">
      <h2>执行历史</h2>
    </div>

    <div class="filter-bar">
      <el-select v-model="filters.suite_id" placeholder="选择套件" clearable style="width: 200px">
        <el-option
          v-for="suite in store.suites"
          :key="suite.suite_id"
          :label="suite.name"
          :value="suite.suite_id"
        />
      </el-select>
      <el-select v-model="filters.case_id" placeholder="选择用例" clearable style="width: 200px">
        <el-option
          v-for="caseItem in store.cases"
          :key="caseItem.case_id"
          :label="caseItem.name"
          :value="caseItem.case_id"
        />
      </el-select>
      <el-select v-model="filters.status" placeholder="执行状态" clearable style="width: 150px">
        <el-option label="等待中" value="pending" />
        <el-option label="执行中" value="running" />
        <el-option label="通过" value="passed" />
        <el-option label="失败" value="failed" />
        <el-option label="错误" value="error" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <el-table
      v-loading="store.executionsLoading"
      :data="store.executions"
      border
      style="width: 100%"
    >
      <el-table-column prop="execution_id" label="ID" width="80" />
      <el-table-column prop="case_id" label="用例ID" width="100" />
      <el-table-column label="用例名称" min-width="200">
        <template #default="{ row }">
          {{ getCaseName(row.case_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时(秒)" width="120">
        <template #default="{ row }">
          {{ row.duration ? row.duration.toFixed(2) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="180">
        <template #default="{ row }">{{ formatDate(row.start_time) }}</template>
      </el-table-column>
      <el-table-column prop="end_time" label="结束时间" width="180">
        <template #default="{ row }">{{ formatDate(row.end_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">
            <el-icon><View /></el-icon>
            查看详情
          </el-button>
          <el-button
            v-if="row.report_url"
            size="small"
            @click="openReport(row.report_url)"
          >
            <el-icon><Document /></el-icon>
            报告
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="store.executionsTotal"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>

    <!-- 执行详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="执行详情"
      width="800px"
      destroy-on-close
    >
      <el-descriptions :column="2" border v-if="currentExecution">
        <el-descriptions-item label="执行ID">{{ currentExecution.execution_id }}</el-descriptions-item>
        <el-descriptions-item label="任务ID">{{ currentExecution.celery_task_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentExecution.status)">
            {{ getStatusLabel(currentExecution.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ currentExecution.duration ? currentExecution.duration.toFixed(2) : '-' }}s
        </el-descriptions-item>
        <el-descriptions-item label="开始时间" :span="2">
          {{ formatDate(currentExecution.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间" :span="2">
          {{ formatDate(currentExecution.end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结果摘要" :span="2">
          <pre class="result-summary">{{ formatJson(currentExecution.result_summary) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="执行日志" :span="2">
          <div class="log-viewer">
            <pre>{{ currentExecution.log_output || '暂无日志' }}</pre>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Document } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'

const store = useApiEngineStore()

const filters = reactive({
  suite_id: undefined,
  case_id: undefined,
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20
})

const showDetailDialog = ref(false)
const currentExecution = ref<any>(null)

const getCaseName = (caseId: number) => {
  const caseItem = store.cases.find(c => c.case_id === caseId)
  return caseItem?.name || `用例${caseId}`
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    passed: 'success',
    failed: 'danger',
    error: 'danger'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    running: '执行中',
    passed: '通过',
    failed: '失败',
    error: '错误'
  }
  return map[status] || status
}

const handleSearch = () => {
  store.fetchExecutions({
    page: pagination.page,
    page_size: pagination.page_size,
    suite_id: filters.suite_id,
    case_id: filters.case_id,
    status: filters.status || undefined
  })
}

const viewDetail = (execution: any) => {
  currentExecution.value = execution
  showDetailDialog.value = true
}

const openReport = (reportUrl: string) => {
  window.open(reportUrl, '_blank')
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatJson = (data: any) => {
  if (!data) return '-'
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchSuites(),
    store.fetchCases()
  ])
  handleSearch()
})
</script>

<style scoped lang="scss">
.execution-history-container {
  padding: 20px;

  .header {
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }

  .result-summary {
    margin: 0;
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    font-size: 12px;
    overflow-x: auto;
    max-height: 200px;
    overflow-y: auto;
  }

  .log-viewer {
    max-height: 400px;
    overflow-y: auto;
    background: #1e1e1e;
    border-radius: 4px;
    padding: 16px;

    pre {
      margin: 0;
      color: #d4d4d4;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}
</style>


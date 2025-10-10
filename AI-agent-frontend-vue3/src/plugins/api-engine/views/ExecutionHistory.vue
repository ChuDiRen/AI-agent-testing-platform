<template>
  <div class="execution-history-container">
    <div class="header">
      <h2>执行历史</h2>
    </div>

    <div class="filter-bar">
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
        <el-option label="成功" value="success" />
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
      <el-table-column label="步骤统计" width="150">
        <template #default="{ row }">
          <span v-if="row.steps_total">
            {{ row.steps_passed }}/{{ row.steps_total }}
            <el-tag v-if="row.steps_failed > 0" type="danger" size="small">失败{{ row.steps_failed }}</el-tag>
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时(秒)" width="120">
        <template #default="{ row }">
          {{ row.duration ? row.duration.toFixed(2) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="executed_at" label="执行时间" width="180">
        <template #default="{ row }">{{ formatDate(row.executed_at) }}</template>
      </el-table-column>
      <el-table-column prop="finished_at" label="完成时间" width="180">
        <template #default="{ row }">{{ formatDate(row.finished_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">
            <el-icon><View /></el-icon>
            查看详情
          </el-button>
          <el-dropdown @command="(format) => handleExport(row, format)" style="margin-left: 8px;">
            <el-button size="small" type="primary">
              <el-icon><Download /></el-icon>
              导出
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="json">JSON格式</el-dropdown-item>
                <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
                <el-dropdown-item command="excel">Excel格式</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(row)"
            style="margin-left: 8px;"
          >
            <el-icon><Delete /></el-icon>
            删除
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
        <el-descriptions-item label="任务ID">{{ currentExecution.task_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentExecution.status)">
            {{ getStatusLabel(currentExecution.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ currentExecution.duration ? currentExecution.duration.toFixed(2) : '-' }}s
        </el-descriptions-item>
        <el-descriptions-item label="步骤统计" :span="2">
          总计: {{ currentExecution.steps_total || 0 }} |
          通过: {{ currentExecution.steps_passed || 0 }} |
          失败: {{ currentExecution.steps_failed || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="执行时间" :span="2">
          {{ formatDate(currentExecution.executed_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间" :span="2">
          {{ formatDate(currentExecution.finished_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="执行结果" :span="2" v-if="currentExecution.result">
          <pre class="result-summary">{{ formatJson(currentExecution.result) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2" v-if="currentExecution.error_message">
          <el-alert type="error" :closable="false">
            {{ currentExecution.error_message }}
          </el-alert>
        </el-descriptions-item>
        <el-descriptions-item label="执行日志" :span="2">
          <div class="log-viewer">
            <pre>{{ currentExecution.logs || '暂无日志' }}</pre>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Download, ArrowDown } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import { executionAPI } from '../api'

const store = useApiEngineStore()

const filters = reactive({
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
    success: 'success',
    failed: 'danger',
    error: 'danger'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    running: '执行中',
    success: '成功',
    failed: '失败',
    error: '错误'
  }
  return map[status] || status
}

const handleSearch = () => {
  store.fetchExecutions({
    page: pagination.page,
    page_size: pagination.page_size,
    case_id: filters.case_id,
    status: filters.status || undefined
  })
}

const viewDetail = async (execution: any) => {
  try {
    // 获取最新的执行详情
    const detail = await store.fetchExecutionById(execution.execution_id)
    currentExecution.value = detail
    showDetailDialog.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取执行详情失败')
  }
}

const handleDelete = async (execution: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除执行记录 #${execution.execution_id} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await executionAPI.deleteExecution(execution.execution_id)
    ElMessage.success('删除成功')
    handleSearch() // 刷新列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
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

const handleExport = async (execution: any, format: 'pdf' | 'excel' | 'json') => {
  try {
    ElMessage.info('正在准备导出文件...')

    // 调用导出API
    const response = await executionAPI.exportExecutionReport(
      execution.execution_id,
      format
    )

    // 从响应头获取文件名，如果没有则生成默认文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `execution-report-${execution.execution_id}.${format}`

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }

    // 创建下载链接
    const blob = new Blob([response.data], {
      type: response.headers['content-type'] || 'application/octet-stream'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('报告导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '报告导出失败')
  }
}

onMounted(async () => {
  await store.fetchCases()
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


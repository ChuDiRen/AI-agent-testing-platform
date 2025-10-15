<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="report-list-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="总报告数" :value="statistics.total_reports || 0">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="已完成" :value="statistics.completed_reports || 0">
            <template #prefix>
              <el-icon><Select /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="平均通过率" :value="statistics.average_pass_rate || 0" suffix="%">
            <template #prefix>
              <el-icon><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic title="总用例数" :value="statistics.total_test_cases || 0">
            <template #prefix>
              <el-icon><List /></el-icon>
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
            <el-icon><Document /></el-icon>
            测试报告列表
          </span>
          <el-button type="primary" @click="handleGenerate">
            <el-icon><Plus /></el-icon>
            生成报告
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filters">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.keyword"
              placeholder="报告名称"
              clearable
              @clear="loadReports"
              @keyup.enter="loadReports"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="报告类型">
            <el-select
              v-model="filters.report_type"
              placeholder="全部"
              clearable
              @change="loadReports"
            >
              <el-option label="API测试报告" value="API" />
              <el-option label="Web测试报告" value="Web" />
              <el-option label="App测试报告" value="App" />
              <el-option label="综合测试报告" value="Integrated" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filters.status"
              placeholder="全部"
              clearable
              @change="loadReports"
            >
              <el-option label="待处理" value="pending" />
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadReports">
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
        :data="reports"
        stripe
        border
      >
        <el-table-column prop="report_id" label="ID" width="80" />
        <el-table-column prop="name" label="报告名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="report_type" label="报告类型" width="140">
          <template #default="{ row }">
            <el-tag>{{ row.report_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用例统计" width="180">
          <template #default="{ row }">
            <div class="case-stats">
              <el-tag type="success" size="small">通过: {{ row.passed_cases }}</el-tag>
              <el-tag type="danger" size="small">失败: {{ row.failed_cases }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.pass_rate"
              :color="getProgressColor(row.pass_rate)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button link type="success" size="small" @click="handleExport(row, 'excel')">
              <el-icon><Download /></el-icon>
              Excel
            </el-button>
            <el-button link type="success" size="small" @click="handleExport(row, 'pdf')">
              <el-icon><Download /></el-icon>
              PDF
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
          @size-change="loadReports"
          @current-change="loadReports"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Select,
  TrendCharts,
  List,
  Plus,
  Search,
  RefreshRight,
  View,
  Download,
  Delete
} from '@element-plus/icons-vue'
import {
  getReportsAPI,
  getReportStatisticsAPI,
  deleteReportAPI,
  downloadReportFile,
  type TestReport,
  type TestReportStatistics
} from '@/api/report'

const router = useRouter()

// 状态
const loading = ref(false)
const reports = ref<TestReport[]>([])
const statistics = ref<TestReportStatistics>({
  total_reports: 0,
  by_type: {},
  by_status: {},
  avg_pass_rate: 0,
  total_test_cases: 0
})

// 筛选条件
const filters = reactive({
  keyword: '',
  report_type: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 加载报告列表
const loadReports = async () => {
  loading.value = true
  try {
    const response = await getReportsAPI({
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    })
    
    if (response.data) {
      reports.value = response.data.items
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
    const response = await getReportStatisticsAPI()
    if (response.data) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

// 生成报告
const handleGenerate = () => {
  router.push('/report/generate')
}

// 查看报告
const handleView = (row: TestReport) => {
  router.push(`/report/${row.report_id}`)
}

// 导出报告
const handleExport = async (row: TestReport, format: 'pdf' | 'excel') => {
  try {
    ElMessage.info(`正在导出${format.toUpperCase()}...`)
    await downloadReportFile(row.report_id, format, `${row.name}.${format === 'pdf' ? 'pdf' : 'xlsx'}`)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

// 删除报告
const handleDelete = async (row: TestReport) => {
  await ElMessageBox.confirm(
    `确认删除报告"${row.name}"吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  try {
    await deleteReportAPI(row.report_id)
    ElMessage.success('删除成功')
    loadReports()
    loadStatistics()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 重置筛选
const handleReset = () => {
  filters.keyword = ''
  filters.report_type = ''
  filters.status = ''
  pagination.page = 1
  loadReports()
}

// 辅助函数
const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 初始化
onMounted(() => {
  loadReports()
  loadStatistics()
})
</script>

<style scoped lang="scss">
.report-list-container {
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
    }

    .filter-section {
      margin-bottom: 20px;
    }

    .case-stats {
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
    }

    .pagination-section {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>


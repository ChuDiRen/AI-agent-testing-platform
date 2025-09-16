<!-- 测试报告管理页面 -->
<template>
  <div class="test-report">
    <div class="page-header">
      <h1>测试报告管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><DocumentAdd /></el-icon>
        创建报告
      </el-button>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <el-row :gutter="16">
        <el-col :span="6" v-for="stat in statistics" :key="stat.key">
          <div class="stat-card">
            <div class="stat-icon" :class="stat.type">
              <el-icon><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索过滤 -->
    <div class="search-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-input v-model="searchForm.keyword" placeholder="搜索报告标题" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="状态" clearable>
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.test_type" placeholder="测试类型" clearable>
            <el-option label="功能测试" value="functional" />
            <el-option label="性能测试" value="performance" />
            <el-option label="安全测试" value="security" />
            <el-option label="集成测试" value="integration" />
            <el-option label="单元测试" value="unit" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="onDateRangeChange"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 报告列表 -->
    <el-table :data="reportList" v-loading="loading" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="title" label="报告标题" min-width="200" />
      <el-table-column prop="test_type" label="测试类型" width="100">
        <template #default="{ row }">
          <el-tag>{{ getTestTypeLabel(row.test_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行情况" width="150">
        <template #default="{ row }">
          <div class="execution-info">
            <div>总计: {{ row.total_cases }}</div>
            <div class="success-rate">
              成功率: {{ row.success_rate }}%
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="execution_time" label="执行时间" width="100">
        <template #default="{ row }">
          {{ formatDuration(row.execution_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button @click="viewReport(row)" size="small">查看</el-button>
          <el-button @click="exportReport(row)" size="small">导出</el-button>
          <el-button @click="rerunReport(row)" size="small" type="primary">重跑</el-button>
          <el-button @click="deleteReport(row)" type="danger" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadReportList"
        @current-change="loadReportList"
      />
    </div>

    <!-- 创建报告对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建测试报告" width="600px">
      <el-form :model="reportForm" :rules="reportRules" ref="reportFormRef" label-width="100px">
        <el-form-item label="报告标题" prop="title">
          <el-input v-model="reportForm.title" placeholder="请输入报告标题" />
        </el-form-item>
        <el-form-item label="测试类型" prop="test_type">
          <el-select v-model="reportForm.test_type" placeholder="选择测试类型">
            <el-option label="功能测试" value="functional" />
            <el-option label="性能测试" value="performance" />
            <el-option label="安全测试" value="security" />
            <el-option label="集成测试" value="integration" />
            <el-option label="单元测试" value="unit" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试用例" prop="test_case_ids">
          <el-select v-model="reportForm.test_case_ids" multiple placeholder="选择测试用例" style="width: 100%">
            <el-option
              v-for="testCase in availableTestCases"
              :key="testCase.id"
              :label="testCase.title"
              :value="testCase.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行代理">
          <el-select v-model="reportForm.agent_id" placeholder="选择执行代理" clearable>
            <el-option
              v-for="agent in availableAgents"
              :key="agent.id"
              :label="agent.name"
              :value="agent.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateReport" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 批量操作 -->
    <div v-if="selectedReports.length" class="batch-actions">
      <el-card>
        <div class="batch-content">
          <span>已选择 {{ selectedReports.length }} 个报告</span>
          <div class="batch-buttons">
            <el-button @click="batchExport">批量导出</el-button>
            <el-button type="danger" @click="batchDelete">批量删除</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentAdd, Search, Document, Clock, TrendCharts, SuccessFilled } from '@element-plus/icons-vue'
import { testReportApi } from '@/api/modules/testreport'
import { testCaseApi } from '@/api/modules/testcase'
import { agentApi } from '@/api/modules/agent'
import { formatDateTime } from '@/utils/dateFormat'

const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const reportFormRef = ref()
const reportList = ref([])
const selectedReports = ref([])
const availableTestCases = ref([])
const availableAgents = ref([])
const dateRange = ref([])

const searchForm = reactive({
  keyword: '',
  status: '',
  test_type: '',
  start_date: '',
  end_date: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const reportForm = reactive({
  title: '',
  test_type: '',
  test_case_ids: [],
  agent_id: null
})

const reportRules = {
  title: [{ required: true, message: '请输入报告标题', trigger: 'blur' }],
  test_type: [{ required: true, message: '请选择测试类型', trigger: 'change' }],
  test_case_ids: [{ required: true, message: '请选择测试用例', trigger: 'change' }]
}

const statisticsData = ref({
  total_reports: 0,
  completed_reports: 0,
  running_reports: 0,
  overall_success_rate: 0
})

const statistics = computed(() => [
  { key: 'total', label: '总报告数', value: statisticsData.value.total_reports, icon: Document, type: 'total' },
  { key: 'completed', label: '已完成', value: statisticsData.value.completed_reports, icon: SuccessFilled, type: 'success' },
  { key: 'running', label: '运行中', value: statisticsData.value.running_reports, icon: Clock, type: 'warning' },
  { key: 'rate', label: '平均成功率', value: `${statisticsData.value.overall_success_rate}%`, icon: TrendCharts, type: 'info' }
])

onMounted(() => {
  loadStatistics()
  loadReportList()
  loadAvailableData()
})

const loadStatistics = async () => {
  try {
    const response = await testReportApi.getStatistics()
    if (response.success) {
      statisticsData.value = response.data
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadReportList = async () => {
  loading.value = true
  try {
    const params = { ...pagination, ...searchForm }
    const response = await testReportApi.getTestReportList(params)
    if (response.success) {
      reportList.value = response.data.test_reports
      pagination.total = response.data.total
    }
  } catch (error) {
    ElMessage.error('加载报告列表失败')
  } finally {
    loading.value = false
  }
}

const loadAvailableData = async () => {
  try {
    const [testCasesRes, agentsRes] = await Promise.all([
      testCaseApi.getTestCaseList({ status: 'active' }),
      agentApi.getAgentList({ status: 'active' })
    ])
    
    if (testCasesRes.success) {
      availableTestCases.value = testCasesRes.data.test_cases
    }
    if (agentsRes.success) {
      availableAgents.value = agentsRes.data.agents
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadReportList()
}

const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: '',
    test_type: '',
    start_date: '',
    end_date: ''
  })
  dateRange.value = []
  handleSearch()
}

const onDateRangeChange = (dates) => {
  if (dates && dates.length === 2) {
    searchForm.start_date = dates[0]
    searchForm.end_date = dates[1]
  } else {
    searchForm.start_date = ''
    searchForm.end_date = ''
  }
}

const handleCreateReport = async () => {
  await reportFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    creating.value = true
    try {
      const response = await testReportApi.generateReport(reportForm)
      if (response.success) {
        ElMessage.success('报告创建成功，正在执行中...')
        showCreateDialog.value = false
        loadReportList()
        loadStatistics()
      }
    } catch (error) {
      ElMessage.error('创建报告失败')
    } finally {
      creating.value = false
    }
  })
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}分${secs}秒`
}

const getTestTypeLabel = (type) => {
  const labels = {
    functional: '功能',
    performance: '性能',
    security: '安全',
    integration: '集成',
    unit: '单元'
  }
  return labels[type] || type
}

const getStatusTagType = (status) => {
  const types = {
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return labels[status] || status
}
</script>

<style scoped>
.test-report { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.stats-overview { margin-bottom: 24px; }
.stat-card { display: flex; align-items: center; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.stat-icon { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; font-size: 24px; }
.stat-icon.total { background: #e6f4ff; color: #1890ff; }
.stat-icon.success { background: #f6ffed; color: #52c41a; }
.stat-icon.warning { background: #fff7e6; color: #fa8c16; }
.stat-icon.info { background: #f0f0f0; color: #666; }
.stat-number { font-size: 24px; font-weight: 600; color: #1f2329; }
.stat-label { font-size: 14px; color: #646a73; margin-top: 4px; }
.search-section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 16px; }
.execution-info { font-size: 12px; }
.success-rate { color: #52c41a; }
.pagination { display: flex; justify-content: center; margin-top: 20px; }
.batch-actions { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 100; }
.batch-content { display: flex; align-items: center; justify-content: space-between; min-width: 400px; }
.batch-buttons { display: flex; gap: 8px; }
</style>
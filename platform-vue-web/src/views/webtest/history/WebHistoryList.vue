<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="项目" prop="project_id">
        <el-select v-model="searchForm.project_id" placeholder="全部项目" clearable filterable style="width: 180px">
          <el-option v-for="p in projectList" :key="p.id" :label="p.project_name" :value="p.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="执行状态" prop="status">
        <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="执行中" value="running" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item label="执行时间" prop="date_range">
        <el-date-picker
          v-model="searchForm.date_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
        />
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="Web 测试执行历史"
      :data="tableData"
      :total="total"
      :loading="loading"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
    >
      <el-table-column prop="id" label="执行ID" width="180">
        <template #default="scope">
          <span class="execution-id">{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="project_name" label="项目" width="180" show-overflow-tooltip />
      <el-table-column prop="env" label="环境" width="100">
        <template #default="scope">
          <el-tag :type="getEnvTag(scope.row.env)" size="small">{{ getEnvLabel(scope.row.env) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusTag(scope.row.status)" size="small">
            <el-icon v-if="scope.row.status === 'running'" class="is-loading"><Loading /></el-icon>
            {{ getStatusLabel(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行结果" width="200">
        <template #default="scope">
          <div class="result-stats">
            <span class="stat total">{{ scope.row.total }}</span>
            <span class="stat success">{{ scope.row.passed }}</span>
            <span class="stat fail">{{ scope.row.failed }}</span>
            <el-progress 
              :percentage="scope.row.pass_rate" 
              :status="scope.row.pass_rate === 100 ? 'success' : (scope.row.pass_rate < 80 ? 'exception' : '')"
              :stroke-width="6"
              style="width: 80px"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时" width="100">
        <template #default="scope">
          {{ formatDuration(scope.row.duration) }}
        </template>
      </el-table-column>
      <el-table-column prop="executor" label="执行人" width="100" />
      <el-table-column prop="start_time" label="开始时间" width="170">
        <template #default="scope">
          {{ formatDateTime(scope.row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="180">
        <template #default="scope">
          <el-button link type="primary" @click="viewDetail(scope.row)">详情</el-button>
          <el-button link type="primary" @click="viewReport(scope.row)" :disabled="scope.row.status === 'running'">报告</el-button>
          <el-button link type="warning" @click="rerun(scope.row)" :disabled="scope.row.status === 'running'">重跑</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="执行详情" width="900px" top="5vh">
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="执行ID">{{ currentDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="项目">{{ currentDetail.project_name }}</el-descriptions-item>
          <el-descriptions-item label="环境">
            <el-tag :type="getEnvTag(currentDetail.env)" size="small">{{ getEnvLabel(currentDetail.env) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(currentDetail.status)" size="small">{{ getStatusLabel(currentDetail.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="浏览器">{{ currentDetail.browsers?.join(', ') || '-' }}</el-descriptions-item>
          <el-descriptions-item label="并发数">{{ currentDetail.threads }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDateTime(currentDetail.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDateTime(currentDetail.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ formatDuration(currentDetail.duration) }}</el-descriptions-item>
        </el-descriptions>

        <div class="mt-4">
          <h4 class="section-title">用例执行明细</h4>
          <el-table :data="currentDetail.cases || []" border size="small" max-height="300">
            <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'passed' ? 'success' : 'danger'" size="small">
                  {{ scope.row.status === 'passed' ? '通过' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时" width="100">
              <template #default="scope">
                {{ formatDuration(scope.row.duration) }}
              </template>
            </el-table-column>
            <el-table-column prop="error" label="错误信息" show-overflow-tooltip>
              <template #default="scope">
                <span class="error-msg">{{ scope.row.error || '-' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="viewReport(currentDetail)">查看报告</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { formatDateTime } from '~/utils/timeFormatter'
import { 
  getExecutionHistory, 
  getExecutionDetail, 
  getExecutionCases,
  deleteExecutionHistory,
  batchDeleteExecutionHistory
} from './webHistory'

const route = useRoute()
const router = useRouter()

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({ 
  project_id: route.query.project_id ? Number(route.query.project_id) : null, 
  status: '', 
  date_range: null 
})

// 项目列表
const projectList = ref([])

// 表格数据
const tableData = ref([])

// 详情弹窗
const detailVisible = ref(false)
const currentDetail = ref(null)

// 获取环境标签
const getEnvTag = (env) => {
  const tags = { 'dev': 'info', 'test': 'warning', 'prod': 'danger' }
  return tags[env] || ''
}

const getEnvLabel = (env) => {
  const labels = { 'dev': '开发', 'test': '测试', 'prod': '生产' }
  return labels[env] || env
}

// 获取状态标签
const getStatusTag = (status) => {
  const tags = { 'success': 'success', 'failed': 'danger', 'running': 'warning', 'cancelled': 'info' }
  return tags[status] || ''
}

const getStatusLabel = (status) => {
  const labels = { 'success': '成功', 'failed': '失败', 'running': '执行中', 'cancelled': '已取消' }
  return labels[status] || status
}

// 格式化耗时
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`
  return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`
}

// 加载项目列表
const loadProjects = () => {
  projectList.value = [
    { id: 1, project_name: '商城系统 Web 测试' },
    { id: 2, project_name: '用户中心 UI 校验' },
    { id: 3, project_name: '后台管理系统自动化' }
  ]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const queryParams = {
      page: pagination.value.page,
      pageSize: pagination.value.limit,
      ...searchForm
    }
    
    // 处理日期范围
    if (searchForm.date_range && searchForm.date_range.length === 2) {
      queryParams.start_date = searchForm.date_range[0]
      queryParams.end_date = searchForm.date_range[1]
    }
    
    const res = await getExecutionHistory(queryParams)
    if (res?.data?.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    } else {
      mockData()
    }
  } catch (error) {
    console.error('加载执行历史失败:', error)
    mockData()
  } finally {
    loading.value = false
  }
}

// Mock 数据
const mockData = () => {
  tableData.value = [
    { id: 'exec_20260106_001', project_name: '商城系统 Web 测试', env: 'test', status: 'success', total: 15, passed: 15, failed: 0, pass_rate: 100, duration: 180, executor: 'admin', start_time: '2026-01-06T10:00:00', browsers: ['chromium'], threads: 2 },
    { id: 'exec_20260106_002', project_name: '用户中心 UI 校验', env: 'test', status: 'failed', total: 10, passed: 8, failed: 2, pass_rate: 80, duration: 120, executor: 'tester', start_time: '2026-01-06T11:30:00', browsers: ['chromium', 'firefox'], threads: 1 },
    { id: 'exec_20260105_001', project_name: '商城系统 Web 测试', env: 'prod', status: 'success', total: 20, passed: 19, failed: 1, pass_rate: 95, duration: 300, executor: 'admin', start_time: '2026-01-05T14:00:00', browsers: ['chromium'], threads: 3 },
    { id: 'exec_20260105_002', project_name: '后台管理系统自动化', env: 'dev', status: 'cancelled', total: 5, passed: 2, failed: 0, pass_rate: 40, duration: 45, executor: 'dev', start_time: '2026-01-05T16:00:00', browsers: ['webkit'], threads: 1 }
  ]
  total.value = 4
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, { project_id: null, status: '', date_range: null })
  pagination.value.page = 1
  loadData()
}

// 查看详情
const viewDetail = async (row) => {
  try {
    const res = await getExecutionDetail(row.id)
    if (res?.data?.code === 200) {
      currentDetail.value = res.data.data
    } else {
      mockDetail(row)
    }
  } catch (error) {
    mockDetail(row)
  }
  detailVisible.value = true
}

const mockDetail = (row) => {
  currentDetail.value = {
    ...row,
    end_time: new Date(new Date(row.start_time).getTime() + row.duration * 1000).toISOString(),
    cases: [
      { name: '登录页面测试.yaml', status: 'passed', duration: 25, error: null },
      { name: '首页基础跳转.yaml', status: 'passed', duration: 15, error: null },
      { name: '下单流程.yaml', status: row.failed > 0 ? 'failed' : 'passed', duration: 45, error: row.failed > 0 ? '元素定位超时：#submit-btn' : null },
      { name: '支付流程.yaml', status: 'passed', duration: 35, error: null }
    ]
  }
}

// 查看报告
const viewReport = (row) => {
  router.push({ path: '/WebReportViewer', query: { id: row.id } })
}

// 重跑
const rerun = (row) => {
  router.push({ 
    path: '/WebExecution', 
    query: { project_id: row.project_id, rerun: row.id } 
  })
  ElMessage.info('正在跳转到执行页面...')
}

onMounted(() => {
  loadProjects()
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';

.execution-id {
  font-family: 'Consolas', monospace;
  font-size: 12px;
  color: #409eff;
}

.result-stats {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-stats .stat {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.result-stats .stat.total {
  background: #f0f0f0;
  color: #606266;
}

.result-stats .stat.success {
  background: #f0f9eb;
  color: #67c23a;
}

.result-stats .stat.fail {
  background: #fef0f0;
  color: #f56c6c;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.error-msg {
  color: #f56c6c;
  font-size: 12px;
}

.detail-content {
  padding: 10px;
}
</style>

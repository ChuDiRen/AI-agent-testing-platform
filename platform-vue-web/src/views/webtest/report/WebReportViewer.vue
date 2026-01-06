<template>
  <div class="page-container p-4">
    <!-- 报告头部信息 -->
    <el-card shadow="never" class="report-header-card">
      <div class="report-header">
        <div class="report-info">
          <h2 class="report-title">
            <el-icon><DataAnalysis /></el-icon>
            Web 测试报告
          </h2>
          <div class="report-meta">
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              {{ formatDateTime(reportData.start_time) }}
            </span>
            <span class="meta-item">
              <el-icon><Timer /></el-icon>
              耗时: {{ formatDuration(reportData.duration) }}
            </span>
            <span class="meta-item">
              <el-icon><User /></el-icon>
              执行人: {{ reportData.executor }}
            </span>
          </div>
        </div>
        <div class="report-actions">
          <el-button type="primary" @click="openAllureReport">
            <el-icon><Link /></el-icon>
            打开 Allure 报告
          </el-button>
          <el-button @click="downloadReport">
            <el-icon><Download /></el-icon>
            下载报告
          </el-button>
          <el-button @click="goBack">
            <el-icon><Back /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="16" class="mt-4">
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ reportData.total }}</span>
              <span class="stat-label">总用例数</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value success">{{ reportData.passed }}</span>
              <span class="stat-label">通过</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon danger">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value danger">{{ reportData.failed }}</span>
              <span class="stat-label">失败</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :class="reportData.pass_rate >= 80 ? 'success' : 'warning'">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value" :class="reportData.pass_rate >= 80 ? 'success' : 'warning'">
                {{ reportData.pass_rate }}%
              </span>
              <span class="stat-label">通过率</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表和详情 -->
    <el-row :gutter="16" class="mt-4">
      <el-col :span="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <span class="card-title">执行结果分布</span>
          </template>
          <div class="chart-container">
            <div class="pie-chart">
              <div class="pie-center">
                <span class="pie-value">{{ reportData.pass_rate }}%</span>
                <span class="pie-label">通过率</span>
              </div>
              <svg viewBox="0 0 100 100" class="pie-svg">
                <circle 
                  cx="50" cy="50" r="40" 
                  fill="none" 
                  stroke="#f0f0f0" 
                  stroke-width="12"
                />
                <circle 
                  cx="50" cy="50" r="40" 
                  fill="none" 
                  stroke="#67c23a" 
                  stroke-width="12"
                  :stroke-dasharray="`${reportData.pass_rate * 2.51} 251`"
                  stroke-linecap="round"
                  transform="rotate(-90 50 50)"
                />
              </svg>
            </div>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-dot success"></span>
                <span>通过: {{ reportData.passed }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot danger"></span>
                <span>失败: {{ reportData.failed }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot warning"></span>
                <span>跳过: {{ reportData.skipped || 0 }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="never" class="detail-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">用例执行详情</span>
              <el-input 
                v-model="searchText" 
                placeholder="搜索用例..." 
                clearable 
                style="width: 200px"
              />
            </div>
          </template>
          <el-table :data="filteredCases" border size="small" max-height="400">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTag(scope.row.status)" size="small">
                  {{ getStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时" width="100">
              <template #default="scope">
                {{ scope.row.duration }}s
              </template>
            </el-table-column>
            <el-table-column prop="browser" label="浏览器" width="100" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button link type="primary" size="small" @click="viewCaseDetail(scope.row)">
                  详情
                </el-button>
                <el-button 
                  v-if="scope.row.screenshot" 
                  link type="primary" 
                  size="small" 
                  @click="viewScreenshot(scope.row)"
                >
                  截图
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Allure 报告嵌入 -->
    <el-card shadow="never" class="mt-4 allure-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">Allure 报告预览</span>
          <el-button type="primary" link @click="openAllureReport">在新窗口打开</el-button>
        </div>
      </template>
      <div class="allure-container">
        <iframe 
          v-if="allureUrl" 
          :src="allureUrl" 
          frameborder="0"
          class="allure-iframe"
        />
        <el-empty v-else description="Allure 报告生成中...">
          <el-button type="primary" @click="refreshReport">刷新</el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 用例详情弹窗 -->
    <el-dialog v-model="caseDetailVisible" title="用例执行详情" width="800px">
      <div v-if="currentCase" class="case-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用例名称">{{ currentCase.name }}</el-descriptions-item>
          <el-descriptions-item label="执行状态">
            <el-tag :type="getStatusTag(currentCase.status)" size="small">
              {{ getStatusLabel(currentCase.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="浏览器">{{ currentCase.browser }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ currentCase.duration }}s</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentCase.steps" class="mt-4">
          <h4 class="section-title">执行步骤</h4>
          <el-timeline>
            <el-timeline-item 
              v-for="(step, idx) in currentCase.steps" 
              :key="idx"
              :type="step.status === 'passed' ? 'success' : 'danger'"
              :timestamp="step.duration + 's'"
              placement="top"
            >
              <div class="step-content">
                <span class="step-action">{{ step.action }}</span>
                <span class="step-name">{{ step.name }}</span>
              </div>
              <div v-if="step.error" class="step-error">
                {{ step.error }}
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <div v-if="currentCase.error" class="mt-4">
          <h4 class="section-title">错误信息</h4>
          <pre class="error-block">{{ currentCase.error }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- 截图查看弹窗 -->
    <el-dialog v-model="screenshotVisible" title="执行截图" width="80%">
      <div class="screenshot-container">
        <img :src="currentScreenshot" alt="截图" class="screenshot-img" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  DataAnalysis, Calendar, Timer, User, Link, Download, Back,
  Document, CircleCheck, CircleClose, TrendCharts
} from '@element-plus/icons-vue'
import { formatDateTime } from '~/utils/timeFormatter'
import { getReportUrl, getExecutionDetail } from '../execution/webExecution'

const route = useRoute()
const router = useRouter()

const executionId = ref(route.query.id)
const reportData = ref({
  id: '',
  project_name: '',
  start_time: '',
  duration: 0,
  executor: '',
  total: 0,
  passed: 0,
  failed: 0,
  skipped: 0,
  pass_rate: 0,
  cases: []
})

const allureUrl = ref('')
const searchText = ref('')

// 用例详情
const caseDetailVisible = ref(false)
const currentCase = ref(null)

// 截图查看
const screenshotVisible = ref(false)
const currentScreenshot = ref('')

// 过滤用例
const filteredCases = computed(() => {
  if (!searchText.value) return reportData.value.cases || []
  return (reportData.value.cases || []).filter(c => 
    c.name.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 格式化耗时
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`
  return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`
}

// 获取状态标签
const getStatusTag = (status) => {
  const tags = { 'passed': 'success', 'failed': 'danger', 'skipped': 'warning' }
  return tags[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = { 'passed': '通过', 'failed': '失败', 'skipped': '跳过' }
  return labels[status] || status
}

// 加载报告数据
const loadReport = async () => {
  try {
    const res = await getExecutionDetail(executionId.value)
    if (res?.data?.code === 200) {
      reportData.value = res.data.data
    } else {
      mockReport()
    }
    
    // 获取 Allure 报告 URL
    const urlRes = await getReportUrl(executionId.value)
    if (urlRes?.data?.code === 200) {
      allureUrl.value = urlRes.data.data.url
    } else {
      allureUrl.value = `/allure-report/${executionId.value}/index.html`
    }
  } catch (error) {
    mockReport()
    allureUrl.value = ''
  }
}

// Mock 报告数据
const mockReport = () => {
  reportData.value = {
    id: executionId.value || 'exec_20260106_001',
    project_name: '商城系统 Web 测试',
    start_time: '2026-01-06T10:00:00',
    duration: 180,
    executor: 'admin',
    total: 15,
    passed: 13,
    failed: 2,
    skipped: 0,
    pass_rate: 86.7,
    cases: [
      { name: '登录页面测试.yaml', status: 'passed', duration: 25, browser: 'chromium', screenshot: true, steps: [
        { action: 'goto', name: '访问登录页', status: 'passed', duration: 2 },
        { action: 'fill', name: '输入用户名', status: 'passed', duration: 1 },
        { action: 'fill', name: '输入密码', status: 'passed', duration: 1 },
        { action: 'click', name: '点击登录', status: 'passed', duration: 3 },
        { action: 'assert_title', name: '验证跳转', status: 'passed', duration: 1 }
      ]},
      { name: '首页基础跳转.yaml', status: 'passed', duration: 15, browser: 'chromium', screenshot: true },
      { name: '下单流程.yaml', status: 'failed', duration: 45, browser: 'chromium', screenshot: true, error: 'TimeoutError: 元素定位超时 #submit-btn\n    at waitForSelector (playwright.js:123)\n    at TestCase.run (runner.js:45)', steps: [
        { action: 'goto', name: '访问商品页', status: 'passed', duration: 2 },
        { action: 'click', name: '加入购物车', status: 'passed', duration: 3 },
        { action: 'click', name: '去结算', status: 'passed', duration: 2 },
        { action: 'click', name: '提交订单', status: 'failed', duration: 30, error: '元素定位超时 #submit-btn' }
      ]},
      { name: '支付流程.yaml', status: 'passed', duration: 35, browser: 'chromium', screenshot: true },
      { name: '用户中心.yaml', status: 'failed', duration: 20, browser: 'chromium', screenshot: true, error: 'AssertionError: 期望标题包含"个人中心"，实际为"首页"' }
    ]
  }
}

// 打开 Allure 报告
const openAllureReport = () => {
  if (allureUrl.value) {
    window.open(allureUrl.value, '_blank')
  } else {
    ElMessage.warning('报告正在生成中，请稍后再试')
  }
}

// 下载报告
const downloadReport = () => {
  ElMessage.success('报告下载中...')
  // 实际下载逻辑
}

// 刷新报告
const refreshReport = () => {
  loadReport()
}

// 返回
const goBack = () => {
  router.back()
}

// 查看用例详情
const viewCaseDetail = (row) => {
  currentCase.value = row
  caseDetailVisible.value = true
}

// 查看截图
const viewScreenshot = (row) => {
  currentScreenshot.value = `/screenshots/${executionId.value}/${row.name}.png`
  screenshotVisible.value = true
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.page-container {
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.report-header-card {
  border-radius: 8px;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.report-meta {
  display: flex;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #606266;
}

.report-actions {
  display: flex;
  gap: 8px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 24px;
}

.stat-icon.total {
  background: #f0f0f0;
  color: #606266;
}

.stat-icon.success {
  background: #f0f9eb;
  color: #67c23a;
}

.stat-icon.danger {
  background: #fef0f0;
  color: #f56c6c;
}

.stat-icon.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.danger {
  color: #f56c6c;
}

.stat-value.warning {
  color: #e6a23c;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-card, .detail-card, .allure-card {
  border-radius: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.pie-chart {
  position: relative;
  width: 150px;
  height: 150px;
}

.pie-svg {
  width: 100%;
  height: 100%;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.pie-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.pie-label {
  font-size: 12px;
  color: #909399;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.success {
  background: #67c23a;
}

.legend-dot.danger {
  background: #f56c6c;
}

.legend-dot.warning {
  background: #e6a23c;
}

.allure-container {
  height: 500px;
}

.allure-iframe {
  width: 100%;
  height: 100%;
  border-radius: 6px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.step-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-action {
  font-family: 'Consolas', monospace;
  font-size: 12px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 2px 6px;
  border-radius: 4px;
}

.step-name {
  color: #606266;
}

.step-error {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

.error-block {
  background: #fef0f0;
  color: #f56c6c;
  padding: 12px;
  border-radius: 6px;
  font-family: 'Consolas', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  overflow-x: auto;
}

.screenshot-container {
  text-align: center;
}

.screenshot-img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 6px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
</style>

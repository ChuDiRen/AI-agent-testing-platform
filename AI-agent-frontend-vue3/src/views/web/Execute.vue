<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="execute-container">
    <el-row :gutter="20">
      <!-- 左侧：测试用例选择 -->
      <el-col :span="8">
        <el-card class="case-selection-card">
          <template #header>
            <div class="card-header">
              <span>选择测试用例</span>
              <el-button type="primary" size="small" @click="handleSelectAll">
                {{ allSelected ? '取消全选' : '全选' }}
              </el-button>
            </div>
          </template>

          <!-- 搜索框 -->
          <el-input
            v-model="searchKeyword"
            placeholder="搜索测试用例"
            clearable
            style="margin-bottom: 15px"
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <!-- 筛选条件 -->
          <div class="filter-bar">
            <el-select v-model="filterStatus" placeholder="状态" size="small" clearable style="width: 100px">
              <el-option label="活跃" value="active" />
              <el-option label="草稿" value="draft" />
            </el-select>
            <el-select v-model="filterPriority" placeholder="优先级" size="small" clearable style="width: 100px; margin-left: 10px">
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
          </div>

          <!-- 测试用例列表 -->
          <div class="case-list" v-loading="loading">
            <el-checkbox-group v-model="selectedCaseIds">
              <div
                v-for="testCase in filteredCases"
                :key="testCase.id"
                class="case-item"
                :class="{ selected: selectedCaseIds.includes(testCase.id) }"
              >
                <el-checkbox :label="testCase.id">
                  <div class="case-info">
                    <div class="case-name">{{ testCase.name }}</div>
                    <div class="case-meta">
                      <el-tag :type="getPriorityType(testCase.priority)" size="small">
                        {{ testCase.priority }}
                      </el-tag>
                      <el-tag :type="getStatusType(testCase.status)" size="small" style="margin-left: 5px">
                        {{ testCase.status }}
                      </el-tag>
                    </div>
                  </div>
                </el-checkbox>
              </div>
            </el-checkbox-group>
            
            <el-empty v-if="filteredCases.length === 0" description="暂无测试用例" />
          </div>

          <!-- 底部统计 -->
          <div class="selection-summary">
            <el-divider />
            <div class="summary-text">
              已选择 <span class="highlight">{{ selectedCaseIds.length }}</span> / {{ testCases.length }} 个测试用例
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：执行控制和结果展示 -->
      <el-col :span="16">
        <!-- 执行控制面板 -->
        <el-card class="control-card">
          <template #header>
            <div class="card-header">
              <span>执行控制</span>
              <div class="control-buttons">
                <el-button
                  type="success"
                  :icon="VideoPlay"
                  :disabled="selectedCaseIds.length === 0 || isExecuting"
                  :loading="isExecuting"
                  @click="handleStartExecution"
                >
                  {{ isExecuting ? '执行中...' : '开始执行' }}
                </el-button>
                <el-button
                  type="warning"
                  :icon="VideoPause"
                  :disabled="!isExecuting"
                  @click="handlePauseExecution"
                >
                  暂停
                </el-button>
                <el-button
                  type="danger"
                  :icon="CircleClose"
                  :disabled="!isExecuting"
                  @click="handleStopExecution"
                >
                  停止
                </el-button>
              </div>
            </div>
          </template>

          <!-- 执行配置 -->
          <el-form :model="executeConfig" label-width="100px" style="margin-bottom: 20px">
            <el-form-item label="执行环境">
              <el-select v-model="executeConfig.environment" placeholder="请选择环境">
                <el-option label="开发环境" value="dev" />
                <el-option label="测试环境" value="test" />
                <el-option label="预发环境" value="staging" />
                <el-option label="生产环境" value="prod" />
              </el-select>
            </el-form-item>
            <el-form-item label="并发数">
              <el-input-number v-model="executeConfig.concurrency" :min="1" :max="10" />
            </el-form-item>
            <el-form-item label="失败重试">
              <el-switch v-model="executeConfig.retryOnFailure" />
              <span style="margin-left: 10px; color: #909399">失败后自动重试</span>
            </el-form-item>
            <el-form-item label="生成报告">
              <el-switch v-model="executeConfig.generateReport" active-text="自动" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 执行进度 -->
        <el-card class="progress-card" v-if="executionStarted">
          <template #header>
            <div class="card-header">
              <span>执行进度</span>
              <div class="progress-stats">
                <el-tag type="success">通过: {{ executionStats.passed }}</el-tag>
                <el-tag type="danger" style="margin-left: 10px">失败: {{ executionStats.failed }}</el-tag>
                <el-tag type="info" style="margin-left: 10px">跳过: {{ executionStats.skipped }}</el-tag>
              </div>
            </div>
          </template>

          <!-- 总体进度 -->
          <div class="overall-progress">
            <div class="progress-label">
              <span>总体进度</span>
              <span class="progress-percent">{{ overallProgress }}%</span>
            </div>
            <el-progress
              :percentage="overallProgress"
              :color="progressColor"
              :status="executionStatus === 'failed' ? 'exception' : undefined"
            />
          </div>

          <!-- 当前执行用例 -->
          <div class="current-execution" v-if="currentExecutingCase">
            <el-divider content-position="left">当前执行</el-divider>
            <div class="current-case-info">
              <div class="case-name-large">{{ currentExecutingCase.name }}</div>
              <div class="case-status">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>执行中...</span>
              </div>
            </div>
          </div>

          <!-- 执行详情列表 -->
          <el-divider content-position="left">执行详情</el-divider>
          <div class="execution-list">
            <div
              v-for="result in executionResults"
              :key="result.caseId"
              class="execution-item"
              :class="result.status"
            >
              <div class="item-header">
                <div class="item-name">
                  <el-icon v-if="result.status === 'passed'"><CircleCheck /></el-icon>
                  <el-icon v-else-if="result.status === 'failed'"><CircleClose /></el-icon>
                  <el-icon v-else-if="result.status === 'running'" class="is-loading"><Loading /></el-icon>
                  <el-icon v-else><Remove /></el-icon>
                  <span>{{ result.caseName }}</span>
                </div>
                <div class="item-meta">
                  <span class="duration">{{ result.duration }}ms</span>
                  <el-button link type="primary" size="small" @click="handleViewLog(result)">
                    查看日志
                  </el-button>
                </div>
              </div>
              <div class="item-message" v-if="result.message">
                {{ result.message }}
              </div>
            </div>
          </div>

          <!-- 执行完成后的操作 -->
          <div class="execution-actions" v-if="executionStatus === 'completed' || executionStatus === 'failed'">
            <el-divider />
            <div class="action-buttons">
              <el-button type="primary" @click="handleViewReport">
                <el-icon><Document /></el-icon>
                查看报告
              </el-button>
              <el-button @click="handleExportResults">
                <el-icon><Download /></el-icon>
                导出结果
              </el-button>
              <el-button @click="handleResetExecution">
                <el-icon><RefreshRight /></el-icon>
                重新执行
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 日志查看对话框 -->
    <el-dialog v-model="logDialogVisible" title="执行日志" width="900px" :close-on-click-modal="false">
      <div class="log-viewer">
        <div class="log-header">
          <span class="log-case-name">{{ currentLog?.caseName }}</span>
          <div class="log-actions">
            <el-button size="small" @click="handleCopyLog">复制日志</el-button>
            <el-button size="small" @click="handleDownloadLog">下载日志</el-button>
          </div>
        </div>
        <div class="log-content" ref="logContentRef">
          <div v-for="(log, index) in currentLog?.logs" :key="index" class="log-line" :class="log.level">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-level">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  VideoPlay,
  VideoPause,
  CircleClose,
  CircleCheck,
  Loading,
  Remove,
  Document,
  Download,
  RefreshRight
} from '@element-plus/icons-vue'
import { useTestCaseStore } from '@/store/testcase'
import type { TestCase } from '@/api/testcase'

const router = useRouter()
const testCaseStore = useTestCaseStore()

// 测试用例相关
const testCases = ref<TestCase[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const selectedCaseIds = ref<number[]>([])

// 执行配置
const executeConfig = reactive({
  environment: 'test',
  concurrency: 3,
  retryOnFailure: true,
  generateReport: true
})

// 执行状态
const isExecuting = ref(false)
const isPaused = ref(false)
const executionStarted = ref(false)
const executionStatus = ref<'running' | 'paused' | 'completed' | 'failed' | 'stopped'>('running')

// 当前执行的用例
const currentExecutingCase = ref<TestCase | null>(null)

// 执行统计
const executionStats = reactive({
  total: 0,
  passed: 0,
  failed: 0,
  skipped: 0,
  executed: 0
})

// 执行结果
interface ExecutionResult {
  caseId: number
  caseName: string
  status: 'pending' | 'running' | 'passed' | 'failed' | 'skipped'
  duration: number
  message?: string
  startTime?: string
  endTime?: string
}

const executionResults = ref<ExecutionResult[]>([])

// 日志相关
const logDialogVisible = ref(false)
const currentLog = ref<any>(null)
const logContentRef = ref<HTMLElement>()

// 计算属性
const filteredCases = computed(() => {
  return testCases.value.filter(testCase => {
    const matchKeyword = !searchKeyword.value || testCase.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
    const matchStatus = !filterStatus.value || testCase.status === filterStatus.value
    const matchPriority = !filterPriority.value || testCase.priority === filterPriority.value
    return matchKeyword && matchStatus && matchPriority
  })
})

const allSelected = computed(() => {
  return selectedCaseIds.value.length > 0 && selectedCaseIds.value.length === filteredCases.value.length
})

const overallProgress = computed(() => {
  if (executionStats.total === 0) return 0
  return Math.round((executionStats.executed / executionStats.total) * 100)
})

const progressColor = computed(() => {
  const percent = overallProgress.value
  if (percent < 30) return '#409eff'
  if (percent < 70) return '#e6a23c'
  return '#67c23a'
})

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const typeMap: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return typeMap[priority] || 'info'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    active: 'success',
    draft: 'warning',
    archived: 'info'
  }
  return typeMap[status] || 'info'
}

// 加载测试用例
const loadTestCases = async () => {
  loading.value = true
  try {
    await testCaseStore.fetchTestCaseList({
      type: 'web',
      page: 1,
      page_size: 100
    })
    testCases.value = testCaseStore.testCases
  } catch (error) {
    ElMessage.error('加载测试用例失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

// 全选/取消全选
const handleSelectAll = () => {
  if (allSelected.value) {
    selectedCaseIds.value = []
  } else {
    selectedCaseIds.value = filteredCases.value.map(c => c.id)
  }
}

// 开始执行
const handleStartExecution = async () => {
  if (selectedCaseIds.value.length === 0) {
    ElMessage.warning('请至少选择一个测试用例')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要执行选中的 ${selectedCaseIds.value.length} 个测试用例吗？`,
      '执行确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    isExecuting.value = true
    executionStarted.value = true
    executionStatus.value = 'running'
    
    // 初始化执行统计
    executionStats.total = selectedCaseIds.value.length
    executionStats.passed = 0
    executionStats.failed = 0
    executionStats.skipped = 0
    executionStats.executed = 0

    // 初始化执行结果
    executionResults.value = selectedCaseIds.value.map(id => {
      const testCase = testCases.value.find(c => c.id === id)!
      return {
        caseId: id,
        caseName: testCase.name,
        status: 'pending',
        duration: 0
      }
    })

    // 模拟执行过程
    await simulateExecution()

    executionStatus.value = 'completed'
    ElMessage.success('测试执行完成')
  } catch (error) {
    if (error !== 'cancel') {
      executionStatus.value = 'failed'
      ElMessage.error('测试执行失败')
    }
  } finally {
    isExecuting.value = false
  }
}

// 模拟执行过程
const simulateExecution = async () => {
  for (let i = 0; i < executionResults.value.length; i++) {
    if (!isExecuting.value) break

    const result = executionResults.value[i]
    const testCase = testCases.value.find(c => c.id === result.caseId)!
    
    currentExecutingCase.value = testCase
    result.status = 'running'
    result.startTime = new Date().toLocaleTimeString()

    // 模拟执行时间（1-3秒）
    const duration = Math.random() * 2000 + 1000
    await new Promise(resolve => setTimeout(resolve, duration))

    // 模拟执行结果（80%通过率）
    const passed = Math.random() > 0.2
    result.status = passed ? 'passed' : 'failed'
    result.duration = Math.round(duration)
    result.endTime = new Date().toLocaleTimeString()
    result.message = passed ? '测试通过' : '断言失败: 期望值与实际值不匹配'

    if (passed) {
      executionStats.passed++
    } else {
      executionStats.failed++
    }
    executionStats.executed++

    // 滚动到最新结果
    await new Promise(resolve => setTimeout(resolve, 100))
  }

  currentExecutingCase.value = null
}

// 暂停执行
const handlePauseExecution = () => {
  isPaused.value = true
  executionStatus.value = 'paused'
  ElMessage.info('测试已暂停')
}

// 停止执行
const handleStopExecution = async () => {
  try {
    await ElMessageBox.confirm('确定要停止测试执行吗？', '停止确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    isExecuting.value = false
    executionStatus.value = 'stopped'
    currentExecutingCase.value = null
    ElMessage.warning('测试已停止')
  } catch (error) {
    // 用户取消
  }
}

// 查看日志
const handleViewLog = (result: ExecutionResult) => {
  // 模拟日志数据
  currentLog.value = {
    caseName: result.caseName,
    logs: [
      { time: result.startTime, level: 'INFO', message: '开始执行测试用例' },
      { time: result.startTime, level: 'INFO', message: `环境: ${executeConfig.environment}` },
      { time: result.startTime, level: 'DEBUG', message: '初始化测试环境' },
      { time: result.startTime, level: 'DEBUG', message: '发送HTTP请求: GET /api/test' },
      { time: result.startTime, level: 'INFO', message: '响应状态码: 200' },
      { time: result.startTime, level: 'DEBUG', message: '响应数据: {"status":"success"}' },
      { time: result.startTime, level: result.status === 'passed' ? 'INFO' : 'ERROR', 
        message: result.status === 'passed' ? '断言通过' : '断言失败: 期望值与实际值不匹配' },
      { time: result.endTime, level: 'INFO', message: `测试${result.status === 'passed' ? '通过' : '失败'}，耗时: ${result.duration}ms` }
    ]
  }
  logDialogVisible.value = true
}

// 复制日志
const handleCopyLog = () => {
  const logText = currentLog.value?.logs.map((log: any) => 
    `[${log.time}] ${log.level}: ${log.message}`
  ).join('\n')
  
  navigator.clipboard.writeText(logText || '')
  ElMessage.success('日志已复制到剪贴板')
}

// 下载日志
const handleDownloadLog = () => {
  const logText = currentLog.value?.logs.map((log: any) => 
    `[${log.time}] ${log.level}: ${log.message}`
  ).join('\n')
  
  const blob = new Blob([logText || ''], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${currentLog.value?.caseName}_log.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('日志下载成功')
}

// 查看报告
const handleViewReport = () => {
  router.push('/web/report')
}

// 导出结果
const handleExportResults = () => {
  ElMessage.success('结果导出成功')
}

// 重新执行
const handleResetExecution = () => {
  executionStarted.value = false
  executionStatus.value = 'running'
  executionResults.value = []
  Object.assign(executionStats, {
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0,
    executed: 0
  })
  currentExecutingCase.value = null
}

onMounted(() => {
  loadTestCases()
})

onUnmounted(() => {
  isExecuting.value = false
})
</script>

<style scoped>
.execute-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.case-selection-card {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

.case-selection-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-bar {
  margin-bottom: 15px;
}

.case-list {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 15px;
}

.case-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
  transition: all 0.3s;
  cursor: pointer;
}

.case-item:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.case-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.case-info {
  flex: 1;
  margin-left: 10px;
}

.case-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.case-meta {
  display: flex;
  gap: 5px;
}

.selection-summary {
  margin-top: auto;
}

.summary-text {
  text-align: center;
  color: #606266;
}

.highlight {
  color: #409eff;
  font-weight: 600;
  font-size: 16px;
}

.control-card,
.progress-card {
  margin-bottom: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.progress-stats {
  display: flex;
  gap: 10px;
}

.overall-progress {
  margin-bottom: 20px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-weight: 500;
}

.progress-percent {
  color: #409eff;
  font-size: 18px;
}

.current-execution {
  margin: 20px 0;
}

.current-case-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.case-name-large {
  font-size: 16px;
  font-weight: 600;
}

.case-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
}

.execution-list {
  max-height: 400px;
  overflow-y: auto;
}

.execution-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
}

.execution-item.passed {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.execution-item.failed {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.execution-item.running {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #909399;
  font-size: 12px;
}

.item-message {
  margin-top: 8px;
  color: #606266;
  font-size: 13px;
  padding-left: 26px;
}

.execution-actions {
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.log-viewer {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.log-case-name {
  font-weight: 600;
  font-size: 16px;
}

.log-actions {
  display: flex;
  gap: 10px;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-line {
  margin-bottom: 2px;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-time {
  color: #858585;
  margin-right: 10px;
}

.log-level {
  display: inline-block;
  width: 50px;
  margin-right: 10px;
  font-weight: 600;
}

.log-line.INFO .log-level {
  color: #4ec9b0;
}

.log-line.DEBUG .log-level {
  color: #9cdcfe;
}

.log-line.ERROR .log-level {
  color: #f48771;
}

.log-line.WARN .log-level {
  color: #dcdcaa;
}

.log-message {
  color: #d4d4d4;
}
</style>


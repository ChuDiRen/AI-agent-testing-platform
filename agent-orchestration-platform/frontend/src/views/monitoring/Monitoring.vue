<template>
  <div class="monitoring-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title text-glow">执行监控</h1>
          <p class="page-description">实时监控 AI 工作流执行状态与性能指标</p>
        </div>
        <div class="header-actions">
          <div class="connection-status glass-card" :class="{ connected: wsConnected }">
            <div class="status-dot"></div>
            <span>{{ wsConnected ? '已连接' : '已断开' }}</span>
          </div>
          <button class="btn btn-secondary-glow" @click="refreshData">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
              <path d="M23 4v6h-6M1 20v-6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0120.49 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            刷新数据
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper primary-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M13 2L3 14h9l-1 8 10-12-9-4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalExecutions }}</div>
          <div class="stat-label">总执行数</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper success-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ successCount }}</div>
          <div class="stat-label">成功执行</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper warning-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ failedCount }}</div>
          <div class="stat-label">失败/异常</div>
        </div>
        <div class="stat-decoration"></div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrapper accent-glow">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="stat-icon">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ avgExecutionTime }}s</div>
          <div class="stat-label">平均耗时</div>
        </div>
        <div class="stat-decoration"></div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Execution Logs -->
      <div class="card glass-panel logs-section">
        <div class="card-header">
          <h2 class="card-title">执行日志流</h2>
          <div class="card-actions">
            <div class="search-wrapper glass-input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="search-icon">
                <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="搜索日志关键字..."
              />
            </div>
          </div>
        </div>

        <div class="logs-container custom-scrollbar" ref="logsContainer">
          <TransitionGroup name="list">
            <div
              v-for="log in filteredLogs"
              :key="log.id"
              class="log-item"
              :class="`log-${log.type}`"
            >
              <div class="log-time">{{ formatTime(log.timestamp) }}</div>
              <div class="log-content">
                <div class="log-header-row">
                  <span class="log-id">#{{ log.execution_id }}</span>
                  <span class="log-badge" :class="log.type">{{ log.type.toUpperCase() }}</span>
                  <span v-if="log.node_id" class="log-node">Node: {{ log.node_id }}</span>
                </div>
                <div class="log-message">{{ log.message }}</div>
              </div>
            </div>
          </TransitionGroup>

          <div v-if="filteredLogs.length === 0" class="empty-state">
            <div class="empty-icon-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <p>暂无日志数据</p>
          </div>
        </div>
      </div>

      <!-- Execution Status -->
      <div class="card glass-panel status-section">
        <div class="card-header">
          <h2 class="card-title">实时执行状态</h2>
        </div>

        <div v-if="currentExecution" class="execution-details">
          <div class="detail-group">
            <div class="detail-item">
              <span class="detail-label">执行 ID</span>
              <span class="detail-value mono">{{ currentExecution.id }}</span>
            </div>

            <div class="detail-item">
              <span class="detail-label">状态</span>
              <span class="status-badge-lg" :class="`status-${currentExecution.status}`">
                <span class="status-dot"></span>
                {{ currentExecution.status }}
              </span>
            </div>
          </div>

          <div class="detail-separator"></div>

          <div class="detail-item">
            <span class="detail-label">当前节点</span>
            <span class="detail-value highlight">{{ currentExecution.node_id || '-' }}</span>
          </div>

          <div class="metrics-grid">
            <div class="metric-item">
              <span class="metric-label">Token 消耗</span>
              <span class="metric-value">{{ currentExecution.tokens_used || 0 }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">运行时长</span>
              <span class="metric-value">{{ currentExecution.execution_time || 0 }}s</span>
            </div>
          </div>

          <div class="progress-section">
            <div class="progress-header">
              <span class="detail-label">总体进度</span>
              <span class="progress-value">{{ currentExecution.progress || 0 }}%</span>
            </div>
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{ width: `${currentExecution.progress || 0}%` }"
                :class="`progress-${currentExecution.status}`"
              >
                <div class="progress-glow"></div>
              </div>
            </div>
          </div>

          <div class="execution-actions">
            <button
              v-if="currentExecution.status === 'running'"
              class="btn btn-danger-glow btn-block"
              @click="cancelExecution"
            >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="btn-icon">
                <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              终止执行
            </button>
          </div>
        </div>

        <div v-else class="no-execution">
          <div class="empty-icon-wrapper large">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="empty-icon">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/>
              <path d="M10 9l5 3-5 3V9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>等待执行</h3>
          <p>当前没有正在运行的工作流</p>
          <button class="btn btn-primary-glow" @click="$router.push('/workflows')">
            去启动工作流
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/api/index'

const executionLogs = ref([])
const currentExecution = ref(null)
const searchQuery = ref('')
const wsConnected = ref(false)
const logsContainer = ref(null)
const totalExecutions = ref(0)
const successCount = ref(0)
const failedCount = ref(0)
const avgExecutionTime = ref(0)

const filteredLogs = computed(() => {
  if (!searchQuery.value) return executionLogs.value

  const query = searchQuery.value.toLowerCase()
  return executionLogs.value.filter(log =>
    log.message.toLowerCase().includes(query) ||
    log.execution_id.toString().includes(query) ||
    (log.node_id && log.node_id.toLowerCase().includes(query))
  )
})

// 加载执行统计
async function loadExecutionStats() {
  try {
    const response = await axios.get('/v1/Execution/')
    if (response.data && response.data.code === 200) {
      totalExecutions.value = response.data.total || 0
      
      // 计算成功和失败数量
      const executions = response.data.data || []
      successCount.value = executions.filter(e => e.status === 'completed').length
      failedCount.value = executions.filter(e => e.status === 'failed').length
      
      // 计算平均执行时间
      const times = executions.filter(e => e.execution_time).map(e => e.execution_time)
      if (times.length > 0) {
        avgExecutionTime.value = (times.reduce((a, b) => a + b, 0) / times.length).toFixed(2)
      }
    }
  } catch (error) {
    console.error('Failed to load execution stats:', error)
  }
}

// 加载执行日志
async function loadExecutionLogs() {
  try {
    const response = await axios.get('/v1/Execution/', { params: { skip: 0, limit: 50 } })
    if (response.data && response.data.code === 200) {
      const executions = response.data.data || []
      executionLogs.value = executions.map(execution => ({
        id: execution.id,
        execution_id: execution.id,
        timestamp: execution.created_at,
        type: execution.status === 'completed' ? 'success' : execution.status === 'failed' ? 'error' : 'info',
        message: `执行 ${execution.status === 'completed' ? '成功' : execution.status === 'failed' ? '失败' : '进行中'}`,
        node_id: execution.workflow_id,
        execution_time: execution.execution_time
      }))
    }
  } catch (error) {
    console.error('Failed to load execution logs:', error)
  }
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

async function refreshData() {
  ElMessage.info('正在刷新数据...')
  await loadExecutionStats()
  await loadExecutionLogs()
  ElMessage.success('数据已刷新')
}

async function cancelExecution() {
  if (currentExecution.value) {
    try {
      await axios.post(`/v1/Execution/${currentExecution.value.id}/cancel`)
      ElMessage.success('执行已取消')
      currentExecution.value = null
      await refreshData()
    } catch (error) {
      console.error('Failed to cancel execution:', error)
      ElMessage.error('取消执行失败')
    }
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  // 加载初始数据
  loadExecutionStats()
  loadExecutionLogs()
  
  // Initialize WebSocket connection
  // wsConnected.value = true
  scrollToBottom()
})

onUnmounted(() => {
  // Close WebSocket connection
  wsConnected.value = false
})
</script>

<style scoped>
.monitoring-container {
  max-width: var(--container-xl);
  margin: 0 auto;
  position: relative;
  min-height: 80vh;
}

/* Background Decoration */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.orb-1 {
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background: var(--color-primary);
  animation: float 20s infinite ease-in-out;
}

.orb-2 {
  bottom: 10%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: var(--color-secondary);
  animation: float 25s infinite ease-in-out reverse;
}

@keyframes float {
  0% { transform: translate(0, 0); }
  50% { transform: translate(30px, 50px); }
  100% { transform: translate(0, 0); }
}

/* Page Header */
.page-header {
  margin-bottom: var(--space-8);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-4);
}

.page-title {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  background: linear-gradient(135deg, var(--color-text-primary) 0%, var(--color-text-secondary) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 var(--space-2);
}

.page-description {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.connection-status.connected {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border-color: rgba(16, 185, 129, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
}

.connection-status.connected .status-dot {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.stat-card {
  padding: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  border-color: var(--color-primary-light);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.primary-glow { background: rgba(139, 92, 246, 0.15); color: var(--color-primary); }
.success-glow { background: rgba(16, 185, 129, 0.15); color: var(--color-success); }
.warning-glow { background: rgba(245, 158, 11, 0.15); color: var(--color-warning); }
.accent-glow { background: rgba(6, 182, 212, 0.15); color: var(--color-accent); }

.stat-icon {
  width: 28px;
  height: 28px;
}

.stat-content {
  flex: 1;
  z-index: 1;
}

.stat-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.stat-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-6);
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

/* Logs Section */
.logs-section {
  display: flex;
  flex-direction: column;
  height: 600px;
  overflow: hidden;
}

.card-header {
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border-glass);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.glass-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-lg);
  padding: 0 var(--space-3);
  width: 240px;
  height: 36px;
  transition: all 0.2s ease;
}

.glass-input-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
  width: 280px;
}

.search-icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-muted);
  margin-right: var(--space-2);
}

.search-input {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: var(--text-sm);
  outline: none;
}

.logs-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.log-item {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.log-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--color-border-glass);
}

.log-time {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  min-width: 80px;
  padding-top: 2px;
}

.log-content {
  flex: 1;
}

.log-header-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-1);
}

.log-id {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-primary-light);
}

.log-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.log-badge.success { background: rgba(16, 185, 129, 0.2); color: var(--color-success); }
.log-badge.error { background: rgba(239, 68, 68, 0.2); color: var(--color-error); }
.log-badge.info { background: rgba(6, 182, 212, 0.2); color: var(--color-accent); }

.log-node {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.log-message {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.log-error .log-message { color: #fca5a5; }

/* Status Section */
.status-section {
  height: fit-content;
}

.execution-details {
  padding: var(--space-6);
}

.detail-group {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.detail-item {
  flex: 1;
}

.detail-label {
  display: block;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-bottom: var(--space-1);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: var(--text-base);
  color: var(--color-text-primary);
  font-weight: 500;
}

.detail-value.mono {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.detail-value.highlight {
  color: var(--color-primary-light);
  font-weight: 600;
}

.detail-separator {
  height: 1px;
  background: var(--color-border-glass);
  margin: var(--space-4) 0;
}

.status-badge-lg {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 600;
}

.status-badge-lg.status-running { background: rgba(6, 182, 212, 0.2); color: var(--color-accent); }
.status-badge-lg.status-completed { background: rgba(16, 185, 129, 0.2); color: var(--color-success); }
.status-badge-lg.status-failed { background: rgba(239, 68, 68, 0.2); color: var(--color-error); }

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-top: var(--space-4);
  background: rgba(0, 0, 0, 0.2);
  padding: var(--space-3);
  border-radius: var(--radius-md);
}

.metric-item {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.metric-value {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.progress-section {
  margin-top: var(--space-6);
  margin-bottom: var(--space-6);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.progress-value {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-primary-light);
}

.progress-track {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  position: relative;
  transition: width 0.3s ease;
}

.progress-glow {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 10px;
  background: white;
  opacity: 0.5;
  filter: blur(3px);
  box-shadow: 0 0 10px white;
}

.progress-completed { background: var(--color-success); }
.progress-failed { background: var(--color-error); }

.execution-actions {
  margin-top: var(--space-4);
}

.btn-danger-glow {
  background: rgba(239, 68, 68, 0.2);
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger-glow:hover {
  background: rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
}

.btn-secondary-glow {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--color-border-glass);
  color: var(--color-text-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary-glow:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: var(--color-text-muted);
}

.no-execution {
  padding: var(--space-8) var(--space-4);
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-icon-wrapper.large {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-4);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}

.empty-icon-wrapper.large svg {
  width: 40px;
  height: 40px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  color: var(--color-text-muted);
  gap: var(--space-2);
}

.empty-icon {
  width: 48px;
  height: 48px;
  opacity: 0.5;
}

/* Animations */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}


.log-timestamp {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.log-id {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}

.log-type-badge {
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  border-radius: var(--radius-full);
  background: var(--color-bg-muted);
  color: var(--color-text-secondary);
}

.log-message {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
  word-break: break-word;
}

.log-node {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--color-text-muted);
}

.empty-logs svg {
  width: 64px;
  height: 64px;
  margin-bottom: var(--space-4);
  opacity: 0.5;
}

/* Status Section */
.status-section {
  display: flex;
  flex-direction: column;
}

.execution-details {
  padding: var(--space-6);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
}

.detail-value {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
  font-family: var(--font-mono);
}

.status-badge {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  border-radius: var(--radius-full);
  text-transform: capitalize;
}

.status-running {
  background: var(--color-primary);
  color: white;
}

.status-completed {
  background: var(--color-success);
  color: white;
}

.status-failed {
  background: var(--color-error);
  color: white;
}

.status-pending {
  background: var(--color-warning);
  color: white;
}

.progress-section {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) 0;
  border-top: 1px solid var(--color-border-light);
  margin-top: var(--space-4);
}

.progress-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
  min-width: 60px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.3s ease-out;
}

.progress-running {
  background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-accent) 100%);
}

.progress-completed {
  background: var(--color-success);
}

.progress-failed {
  background: var(--color-error);
}

.progress-value {
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  min-width: 40px;
  text-align: right;
  font-family: var(--font-mono);
}

.execution-actions {
  margin-top: var(--space-6);
}

.no-execution {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
  color: var(--color-text-muted);
}

.no-execution svg {
  width: 64px;
  height: 64px;
  margin-bottom: var(--space-4);
}

.no-execution h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.no-execution p {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

/* Scrollbar */
.logs-container::-webkit-scrollbar {
  width: 8px;
}

.logs-container::-webkit-scrollbar-track {
  background: var(--color-bg-muted);
  border-radius: var(--radius-full);
}

.logs-container::-webkit-scrollbar-thumb {
  background: var(--color-primary-300);
  border-radius: var(--radius-full);
}

.logs-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary-400);
}

/* Responsive */
@media (max-width: var(--breakpoint-lg)) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .logs-section {
    max-height: 400px;
  }
}

@media (max-width: var(--breakpoint-md)) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-wrap: wrap;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: var(--breakpoint-sm)) {
  .page-title {
    font-size: var(--text-3xl);
  }
}
</style>

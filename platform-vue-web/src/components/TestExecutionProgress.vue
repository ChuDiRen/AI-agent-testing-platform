<template>
  <div class="test-execution-progress">
    <!-- 连接状态 -->
    <div class="connection-status" :class="{ connected: isConnected, error: hasError }">
      <el-icon v-if="isConnected"><Connection /></el-icon>
      <el-icon v-else-if="hasError"><Close /></el-icon>
      <el-icon v-else class="loading"><Loading /></el-icon>
      <span>{{ connectionStatusText }}</span>
    </div>

    <!-- 执行进度 -->
    <div v-if="executionStatus" class="execution-status">
      <el-card shadow="never">
        <template #header>
          <div class="status-header">
            <h4>测试执行状态</h4>
            <el-tag :type="getStatusType(executionStatus.status)">
              {{ getStatusText(executionStatus.status) }}
            </el-tag>
          </div>
        </template>

        <!-- 进度条 -->
        <el-progress
          v-if="executionStatus.total > 0"
          :percentage="progressPercentage"
          :status="getProgressStatus(executionStatus.status)"
          :stroke-width="20"
        >
          <span class="progress-text">
            {{ executionStatus.completed }} / {{ executionStatus.total }}
          </span>
        </el-progress>

        <!-- 统计信息 -->
        <div class="statistics">
          <div class="stat-item">
            <span class="label">总用例数：</span>
            <span class="value">{{ executionStatus.total }}</span>
          </div>
          <div class="stat-item">
            <span class="label">已完成：</span>
            <span class="value success">{{ executionStatus.completed }}</span>
          </div>
          <div class="stat-item">
            <span class="label">成功：</span>
            <span class="value success">{{ executionStatus.passed }}</span>
          </div>
          <div class="stat-item">
            <span class="label">失败：</span>
            <span class="value error">{{ executionStatus.failed }}</span>
          </div>
          <div class="stat-item">
            <span class="label">跳过：</span>
            <span class="value warning">{{ executionStatus.skipped }}</span>
          </div>
        </div>

        <!-- 当前执行信息 -->
        <div v-if="currentTest" class="current-test">
          <el-divider content-position="left">当前执行</el-divider>
          <div class="test-info">
            <div class="info-row">
              <span class="label">用例名称：</span>
              <span class="value">{{ currentTest.test_name }}</span>
            </div>
            <div class="info-row">
              <span class="label">开始时间：</span>
              <span class="value">{{ formatTime(currentTest.start_time) }}</span>
            </div>
          </div>
        </div>

        <!-- 执行时间 -->
        <div v-if="executionStatus.start_time" class="execution-time">
          <el-divider content-position="left">执行时间</el-divider>
          <div class="time-info">
            <div class="info-row">
              <span class="label">开始时间：</span>
              <span class="value">{{ formatTime(executionStatus.start_time) }}</span>
            </div>
            <div v-if="executionStatus.end_time" class="info-row">
              <span class="label">结束时间：</span>
              <span class="value">{{ formatTime(executionStatus.end_time) }}</span>
            </div>
            <div v-if="executionStatus.duration" class="info-row">
              <span class="label">总耗时：</span>
              <span class="value">{{ executionStatus.duration }}秒</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 实时日志 -->
    <div v-if="showLogs" class="execution-logs">
      <el-card shadow="never">
        <template #header>
          <div class="logs-header">
            <h4>执行日志</h4>
            <div class="actions">
              <el-button size="small" @click="clearLogs">清空</el-button>
              <el-button size="small" @click="scrollToBottom">滚动到底部</el-button>
            </div>
          </div>
        </template>

        <div ref="logsContainer" class="logs-container">
          <div
            v-for="(log, index) in logs"
            :key="index"
            class="log-item"
            :class="getLogClass(log)"
          >
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-type">{{ getLogTypeText(log.type) }}</span>
            <span class="log-content">{{ log.content || log.message }}</span>
          </div>
          <div v-if="logs.length === 0" class="empty-logs">
            暂无日志
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Connection, Close, Loading } from '@element-plus/icons-vue'
import { useWebSocket } from '~/composables/useWebSocket'

const props = defineProps({
  executionId: {
    type: String,
    required: true
  },
  showLogs: {
    type: Boolean,
    default: true
  },
  autoConnect: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['status-change', 'completed', 'error'])

// WebSocket连接
const { isConnected, messages, error, connect, disconnect, clearMessages } = useWebSocket(props.executionId)

// 日志容器
const logsContainer = ref(null)

// 执行状态
const executionStatus = ref(null)
const currentTest = ref(null)

// 连接状态文本
const connectionStatusText = computed(() => {
  if (isConnected.value) return '已连接'
  if (error.value) return '连接失败'
  return '连接中...'
})

const hasError = computed(() => !!error.value)

// 进度百分比
const progressPercentage = computed(() => {
  if (!executionStatus.value || executionStatus.value.total === 0) return 0
  return Math.round((executionStatus.value.completed / executionStatus.value.total) * 100)
})

// 日志列表
const logs = computed(() => {
  return messages.value.filter(msg => msg.type === 'log' || msg.type === 'info' || msg.type === 'error' || msg.type === 'warning')
})

// 监听消息更新
watch(messages, (newMessages) => {
  if (newMessages.length === 0) return

  const latestMessage = newMessages[newMessages.length - 1]

  // 更新执行状态
  if (latestMessage.type === 'status') {
    executionStatus.value = latestMessage.data
    emit('status-change', latestMessage.data)

    // 检查是否完成
    if (latestMessage.data.status === 'completed' || latestMessage.data.status === 'failed') {
      emit('completed', latestMessage.data)
    }
  }

  // 更新当前测试
  if (latestMessage.type === 'test_start') {
    currentTest.value = latestMessage.data
  }

  // 测试完成，清除当前测试
  if (latestMessage.type === 'test_end') {
    currentTest.value = null
  }

  // 错误消息
  if (latestMessage.type === 'error') {
    emit('error', latestMessage)
  }

  // 自动滚动到底部
  if (props.showLogs) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}, { deep: true })

// 自动连接
if (props.autoConnect) {
  connect()
}

// 方法
const clearLogs = () => {
  clearMessages()
}

const scrollToBottom = () => {
  if (logsContainer.value) {
    logsContainer.value.scrollTop = logsContainer.value.scrollHeight
  }
}

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '等待中',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

const getLogClass = (log) => {
  return `log-${log.type || 'info'}`
}

const getLogTypeText = (type) => {
  const map = {
    info: '[信息]',
    log: '[日志]',
    warning: '[警告]',
    error: '[错误]',
    test_start: '[开始]',
    test_end: '[结束]'
  }
  return map[type] || '[日志]'
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 暴露方法
defineExpose({
  connect,
  disconnect,
  clearLogs,
  scrollToBottom
})
</script>

<style scoped>
.test-execution-progress {
  width: 100%;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #606266;
}

.connection-status.connected {
  background-color: #f0f9ff;
  color: #409eff;
}

.connection-status.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.connection-status .loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.execution-status {
  margin-bottom: 16px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-header h4 {
  margin: 0;
  font-size: 16px;
}

.statistics {
  display: flex;
  gap: 24px;
  margin-top: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item .label {
  font-size: 12px;
  color: #909399;
}

.stat-item .value {
  font-size: 20px;
  font-weight: 600;
}

.stat-item .value.success {
  color: #67c23a;
}

.stat-item .value.error {
  color: #f56c6c;
}

.stat-item .value.warning {
  color: #e6a23c;
}

.current-test,
.execution-time {
  margin-top: 16px;
}

.test-info,
.time-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.info-row .label {
  color: #909399;
  min-width: 80px;
}

.info-row .value {
  color: #606266;
  font-weight: 500;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
}

.execution-logs {
  margin-top: 16px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logs-header h4 {
  margin: 0;
  font-size: 16px;
}

.logs-header .actions {
  display: flex;
  gap: 8px;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  background-color: #1e1e1e;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-item {
  display: flex;
  gap: 12px;
  margin-bottom: 4px;
  color: #d4d4d4;
}

.log-time {
  color: #858585;
  flex-shrink: 0;
}

.log-type {
  flex-shrink: 0;
  font-weight: 600;
}

.log-content {
  flex: 1;
  word-break: break-all;
}

.log-info .log-type {
  color: #4fc3f7;
}

.log-warning .log-type {
  color: #ffb74d;
}

.log-error .log-type {
  color: #f44336;
}

.empty-logs {
  text-align: center;
  color: #858585;
  padding: 20px;
}
</style>

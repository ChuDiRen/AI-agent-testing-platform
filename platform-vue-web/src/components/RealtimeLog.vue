<template>
  <div class="realtime-log">
    <div class="log-header">
      <h4>{{ title }}</h4>
      <div class="actions">
        <el-button size="small" :icon="isConnected ? Close : Connection" @click="toggleConnection">
          {{ isConnected ? '断开' : '连接' }}
        </el-button>
        <el-button size="small" @click="handleClear">清空</el-button>
        <el-button size="small" @click="handleExport">导出</el-button>
      </div>
    </div>

    <div class="log-stats">
      <el-tag size="small" :type="isConnected ? 'success' : 'info'">
        {{ isConnected ? '已连接' : '未连接' }}
      </el-tag>
      <span class="log-count">日志数: {{ logs.length }}</span>
      <span v-if="error" class="error-text">{{ error }}</span>
    </div>

    <div ref="logContainer" class="log-container" :class="{ 'auto-scroll': autoScroll }">
      <div
        v-for="(log, index) in displayLogs"
        :key="index"
        class="log-line"
        :class="`log-${log.level || 'info'}`"
      >
        <span class="log-timestamp">{{ formatTimestamp(log.timestamp) }}</span>
        <span class="log-level">[{{ getLevelText(log.level) }}]</span>
        <span class="log-message">{{ log.message || log.content }}</span>
      </div>
      <div v-if="logs.length === 0" class="empty-log">
        暂无日志数据
      </div>
    </div>

    <div class="log-footer">
      <el-checkbox v-model="autoScroll">自动滚动</el-checkbox>
      <el-checkbox v-model="showTimestamp">显示时间戳</el-checkbox>
      <el-select v-model="filterLevel" size="small" placeholder="过滤级别" style="width: 120px">
        <el-option label="全部" value="" />
        <el-option label="信息" value="info" />
        <el-option label="警告" value="warning" />
        <el-option label="错误" value="error" />
      </el-select>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Connection, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useWebSocket } from '~/composables/useWebSocket'

const props = defineProps({
  executionId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: '实时日志'
  },
  maxLines: {
    type: Number,
    default: 1000
  }
})

// WebSocket
const { isConnected, messages, error, connect, disconnect, clearMessages } = useWebSocket(props.executionId)

// 状态
const logContainer = ref(null)
const autoScroll = ref(true)
const showTimestamp = ref(true)
const filterLevel = ref('')

// 日志列表
const logs = computed(() => {
  return messages.value
    .filter(msg => msg.type === 'log' || msg.message || msg.content)
    .slice(-props.maxLines) // 只保留最新的N条
})

// 过滤后的日志
const displayLogs = computed(() => {
  if (!filterLevel.value) return logs.value
  return logs.value.filter(log => log.level === filterLevel.value)
})

// 监听日志更新，自动滚动
watch(logs, () => {
  if (autoScroll.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}, { deep: true })

// 方法
const toggleConnection = () => {
  if (isConnected.value) {
    disconnect()
  } else {
    connect()
  }
}

const handleClear = () => {
  clearMessages()
  ElMessage.success('日志已清空')
}

const handleExport = () => {
  const content = logs.value
    .map(log => `${formatTimestamp(log.timestamp)} [${getLevelText(log.level)}] ${log.message || log.content}`)
    .join('\n')
  
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test-log-${props.executionId}-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('日志已导出')
}

const scrollToBottom = () => {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  if (!showTimestamp.value) return ''
  
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

const getLevelText = (level) => {
  const map = {
    info: 'INFO',
    warning: 'WARN',
    error: 'ERROR',
    debug: 'DEBUG'
  }
  return map[level] || 'INFO'
}

// 自动连接
connect()

// 暴露方法
defineExpose({
  connect,
  disconnect,
  clearMessages,
  scrollToBottom
})
</script>

<style scoped>
.realtime-log {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #dcdfe6;
  background-color: #f5f7fa;
}

.log-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.log-header .actions {
  display: flex;
  gap: 8px;
}

.log-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-bottom: 1px solid #dcdfe6;
  font-size: 13px;
}

.log-count {
  color: #606266;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
}

.log-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background-color: #1e1e1e;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-line {
  display: flex;
  gap: 8px;
  margin-bottom: 2px;
  color: #d4d4d4;
}

.log-timestamp {
  color: #858585;
  flex-shrink: 0;
  min-width: 80px;
}

.log-level {
  flex-shrink: 0;
  min-width: 60px;
  font-weight: 600;
}

.log-message {
  flex: 1;
  word-break: break-all;
}

.log-info .log-level {
  color: #4fc3f7;
}

.log-warning .log-level {
  color: #ffb74d;
}

.log-error .log-level {
  color: #f44336;
}

.log-debug .log-level {
  color: #9e9e9e;
}

.empty-log {
  text-align: center;
  color: #858585;
  padding: 40px;
}

.log-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  border-top: 1px solid #dcdfe6;
  background-color: #f5f7fa;
}
</style>

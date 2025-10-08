<template>
  <div class="execution-console-container">
    <el-page-header @back="goBack">
      <template #content>
        <span>执行控制台</span>
      </template>
      <template #extra>
        <el-tag :type="getStatusType(executionStatus)">{{ executionStatus }}</el-tag>
      </template>
    </el-page-header>

    <el-card class="case-info-card">
      <h3>用例信息</h3>
      <el-descriptions :column="3" border v-if="currentCase">
        <el-descriptions-item label="用例名称">{{ currentCase.name }}</el-descriptions-item>
        <el-descriptions-item label="优先级">{{ currentCase.priority }}</el-descriptions-item>
        <el-descriptions-item label="配置模式">
          <el-tag :type="currentCase.config_mode === 'form' ? 'success' : 'info'">
            {{ currentCase.config_mode === 'form' ? '表单' : 'YAML' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="3">
          {{ currentCase.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="execution-controls">
      <div class="control-bar">
        <el-button
          type="primary"
          :loading="executing"
          :disabled="executionStatus === 'running'"
          @click="handleExecute"
        >
          <el-icon><VideoPlay /></el-icon>
          {{ executing ? '执行中...' : '开始执行' }}
        </el-button>
        <el-button @click="clearLogs">
          <el-icon><Delete /></el-icon>
          清空日志
        </el-button>
      </div>

      <el-divider />

      <div class="context-config">
        <h4>全局变量配置 (可选)</h4>
        <el-input
          v-model="contextJson"
          type="textarea"
          :rows="4"
          placeholder='{"key": "value"}'
        />
      </div>
    </el-card>

    <el-card class="logs-card">
      <template #header>
        <div class="logs-header">
          <h3>执行日志</h3>
          <div class="logs-info">
            <span v-if="executionDuration">耗时: {{ executionDuration }}s</span>
            <el-tag v-if="taskId" type="info" size="small">任务ID: {{ taskId }}</el-tag>
          </div>
        </div>
      </template>

      <div class="logs-container" ref="logsContainerRef">
        <pre class="logs-content">{{ logs }}</pre>
      </div>
    </el-card>

    <el-card class="result-card" v-if="executionResult">
      <template #header>
        <h3>执行结果</h3>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(executionResult.status)">
            {{ executionResult.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ executionResult.duration }}s
        </el-descriptions-item>
        <el-descriptions-item label="开始时间" :span="2">
          {{ formatDate(executionResult.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间" :span="2">
          {{ formatDate(executionResult.end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结果摘要" :span="2">
          <pre>{{ JSON.stringify(executionResult.result_summary, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, Delete } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import { executionAPI } from '../api'

const route = useRoute()
const router = useRouter()
const store = useApiEngineStore()

const caseId = computed(() => Number(route.params.id))

const currentCase = ref<any>(null)
const executing = ref(false)
const executionStatus = ref('pending')
const logs = ref('')
const taskId = ref('')
const executionDuration = ref(0)
const executionResult = ref<any>(null)
const contextJson = ref('{}')
const logsContainerRef = ref<HTMLElement>()

let eventSource: EventSource | null = null
let statusCheckTimer: any = null

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

const handleExecute = async () => {
  executing.value = true
  logs.value = ''
  executionResult.value = null
  executionStatus.value = 'pending'
  executionDuration.value = 0

  try {
    // 解析context
    let context = {}
    if (contextJson.value.trim()) {
      try {
        context = JSON.parse(contextJson.value)
      } catch (e) {
        ElMessage.warning('全局变量格式错误,将使用空对象')
      }
    }

    // 发起执行请求
    const res = await store.executeCase(caseId.value, context)
    taskId.value = res.celery_task_id
    executionStatus.value = 'running'

    logs.value += `[INFO] 任务已创建: ${taskId.value}\n`
    logs.value += `[INFO] 正在执行测试用例...\n\n`

    // 启动SSE日志流
    startLogStream()

    // 启动状态轮询
    startStatusCheck()
  } catch (error: any) {
    ElMessage.error(error.message || '执行失败')
    executionStatus.value = 'error'
    executing.value = false
  }
}

const startLogStream = () => {
  if (!taskId.value) return

  const url = executionAPI.getLogStreamUrl(taskId.value)
  eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.log) {
      logs.value += data.log + '\n'
      scrollToBottom()
    }

    if (data.status) {
      executionStatus.value = data.status
    }
  }

  eventSource.onerror = () => {
    console.error('SSE connection error')
    eventSource?.close()
  }
}

const startStatusCheck = () => {
  statusCheckTimer = setInterval(async () => {
    if (!taskId.value) return

    try {
      const result = await store.getExecutionStatus(taskId.value)
      executionStatus.value = result.status
      executionDuration.value = result.duration || 0

      if (['passed', 'failed', 'error'].includes(result.status)) {
        // 执行完成
        executionResult.value = result
        executing.value = false
        stopStatusCheck()
        eventSource?.close()
        
        ElMessage.success('执行完成')
      }
    } catch (error) {
      console.error('Status check error:', error)
    }
  }, 2000)
}

const stopStatusCheck = () => {
  if (statusCheckTimer) {
    clearInterval(statusCheckTimer)
    statusCheckTimer = null
  }
}

const clearLogs = () => {
  logs.value = ''
}

const scrollToBottom = () => {
  nextTick(() => {
    if (logsContainerRef.value) {
      logsContainerRef.value.scrollTop = logsContainerRef.value.scrollHeight
    }
  })
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const goBack = () => {
  router.go(-1)
}

onMounted(async () => {
  try {
    currentCase.value = await store.fetchCaseById(caseId.value)
  } catch (error: any) {
    ElMessage.error(error.message || '加载用例失败')
    goBack()
  }
})

onUnmounted(() => {
  stopStatusCheck()
  eventSource?.close()
})
</script>

<style scoped lang="scss">
.execution-console-container {
  padding: 20px;

  .case-info-card,
  .execution-controls,
  .logs-card,
  .result-card {
    margin-top: 20px;

    h3, h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .execution-controls {
    .control-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
    }

    .context-config {
      h4 {
        font-size: 14px;
        margin-bottom: 12px;
      }
    }
  }

  .logs-card {
    .logs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .logs-info {
        display: flex;
        gap: 12px;
        align-items: center;
        font-size: 14px;
        color: #666;
      }
    }

    .logs-container {
      max-height: 500px;
      overflow-y: auto;
      background: #1e1e1e;
      border-radius: 4px;
      padding: 16px;

      .logs-content {
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

  .result-card {
    pre {
      margin: 0;
      background: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      font-size: 12px;
      overflow-x: auto;
    }
  }
}
</style>


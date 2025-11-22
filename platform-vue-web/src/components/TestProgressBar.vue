<template>
  <div class="test-progress-container">
    <!-- 进度条 -->
    <el-progress 
      :percentage="progress" 
      :status="progressStatus"
      :stroke-width="20"
      :show-text="true"
    >
      <template #default="{ percentage }">
        <span class="progress-text">{{ percentage }}%</span>
      </template>
    </el-progress>

    <!-- 当前步骤信息 -->
    <div class="step-info" v-if="currentStep">
      <el-icon class="step-icon" :class="statusIconClass">
        <Loading v-if="isRunning" />
        <CircleCheck v-else-if="isCompleted" />
        <CircleClose v-else-if="isFailed" />
        <Clock v-else />
      </el-icon>
      <span class="step-text">{{ currentStep }}</span>
      <span class="step-count" v-if="totalSteps > 0">
        ({{ currentStepIndex }}/{{ totalSteps }})
      </span>
    </div>

    <!-- 执行时间 -->
    <div class="execution-time" v-if="duration > 0">
      <el-icon><Timer /></el-icon>
      <span>执行时间: {{ formatDuration }}</span>
    </div>

    <!-- WebSocket连接状态 -->
    <div class="connection-status">
      <el-tag 
        :type="isConnected ? 'success' : 'danger'" 
        size="small"
        effect="plain"
      >
        <el-icon><Connection /></el-icon>
        {{ isConnected ? '已连接' : '未连接' }}
      </el-tag>
    </div>

    <!-- 错误信息 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      :closable="false"
      show-icon
      class="error-alert"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Loading, 
  CircleCheck, 
  CircleClose, 
  Clock, 
  Timer,
  Connection 
} from '@element-plus/icons-vue'

const props = defineProps({
  progress: {
    type: Number,
    default: 0
  },
  currentStep: {
    type: String,
    default: ''
  },
  currentStepIndex: {
    type: Number,
    default: 0
  },
  totalSteps: {
    type: Number,
    default: 0
  },
  status: {
    type: String,
    default: 'idle' // idle | running | completed | failed
  },
  duration: {
    type: Number,
    default: 0
  },
  formatDuration: {
    type: String,
    default: '0秒'
  },
  isConnected: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

// 计算进度条状态
const progressStatus = computed(() => {
  if (props.status === 'completed') return 'success'
  if (props.status === 'failed') return 'exception'
  return undefined
})

// 计算状态
const isRunning = computed(() => props.status === 'running')
const isCompleted = computed(() => props.status === 'completed')
const isFailed = computed(() => props.status === 'failed')

// 状态图标样式
const statusIconClass = computed(() => {
  return {
    'running': isRunning.value,
    'completed': isCompleted.value,
    'failed': isFailed.value
  }
})
</script>

<style scoped>
.test-progress-container {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.progress-text {
  font-weight: bold;
  color: #409eff;
}

.step-info {
  display: flex;
  align-items: center;
  margin-top: 15px;
  font-size: 14px;
  color: #606266;
}

.step-icon {
  margin-right: 8px;
  font-size: 18px;
}

.step-icon.running {
  color: #409eff;
  animation: rotate 1s linear infinite;
}

.step-icon.completed {
  color: #67c23a;
}

.step-icon.failed {
  color: #f56c6c;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.step-text {
  flex: 1;
  font-weight: 500;
}

.step-count {
  color: #909399;
  margin-left: 8px;
}

.execution-time {
  display: flex;
  align-items: center;
  margin-top: 10px;
  font-size: 13px;
  color: #909399;
}

.execution-time .el-icon {
  margin-right: 5px;
}

.connection-status {
  margin-top: 10px;
}

.error-alert {
  margin-top: 15px;
}
</style>

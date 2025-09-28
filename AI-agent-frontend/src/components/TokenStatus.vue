<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div v-if="showStatus" class="token-status" :class="statusClass">
    <el-icon class="status-icon">
      <component :is="statusIcon" />
    </el-icon>
    <span class="status-text">{{ statusText }}</span>
    <el-button 
      v-if="showRefreshButton" 
      type="text" 
      size="small" 
      @click="handleRefresh"
      :loading="refreshing"
    >
      刷新
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElIcon, ElButton } from 'element-plus'
import { SuccessFilled, WarningFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { getToken, getRefreshToken } from '@/utils/auth'
import { isTokenValid, isTokenExpired, parseJWT } from '@/utils/tokenValidator'
import { useUserStore } from '@/store'

// Props定义
interface Props {
  showInDev?: boolean // 是否仅在开发环境显示
  position?: 'top-right' | 'bottom-right' | 'top-left' | 'bottom-left' // 显示位置
  autoHide?: boolean // 是否自动隐藏
  hideDelay?: number // 自动隐藏延迟时间(ms)
}

const props = withDefaults(defineProps<Props>(), {
  showInDev: true,
  position: 'top-right',
  autoHide: true,
  hideDelay: 5000
})

// 响应式数据
const refreshing = ref(false)
const visible = ref(true)
const userStore = useUserStore()

// 计算属性
const showStatus = computed(() => {
  if (props.showInDev && import.meta.env.PROD) return false
  return visible.value
})

const tokenStatus = computed(() => {
  const token = getToken()
  const refreshToken = getRefreshToken()
  
  if (!token) {
    return {
      status: 'none',
      text: '未登录',
      icon: CircleCloseFilled,
      class: 'status-none'
    }
  }
  
  if (!isTokenValid(token)) {
    return {
      status: 'invalid',
      text: 'Token无效',
      icon: CircleCloseFilled,
      class: 'status-invalid'
    }
  }
  
  if (isTokenExpired(token)) {
    if (refreshToken && isTokenValid(refreshToken)) {
      return {
        status: 'expired',
        text: 'Token已过期，可刷新',
        icon: WarningFilled,
        class: 'status-expired'
      }
    } else {
      return {
        status: 'expired-no-refresh',
        text: 'Token已过期，需重新登录',
        icon: CircleCloseFilled,
        class: 'status-expired-no-refresh'
      }
    }
  }
  
  // 优化：不再显示"即将过期"状态，因为已有无感刷新机制
  // 只在token真正有问题时才显示状态
  try {
    const payload = parseJWT(token)
    const exp = payload.exp * 1000
    const now = Date.now()
    const timeLeft = exp - now
    
    // 只有在token即将在1分钟内过期时才显示警告（极端情况）
    if (timeLeft < 60 * 1000) { // 1分钟
      return {
        status: 'expiring',
        text: `Token即将过期 (${Math.floor(timeLeft / 1000)}秒)`,
        icon: WarningFilled,
        class: 'status-expiring'
      }
    }
  } catch (error) {
    console.warn('Failed to parse token expiration:', error)
  }
  
  return {
    status: 'valid',
    text: 'Token有效',
    icon: SuccessFilled,
    class: 'status-valid'
  }
})

const statusText = computed(() => tokenStatus.value.text)
const statusIcon = computed(() => tokenStatus.value.icon)
const statusClass = computed(() => [
  tokenStatus.value.class,
  `position-${props.position}`
])

// 优化：只在真正需要手动刷新时才显示刷新按钮
const showRefreshButton = computed(() => {
  return ['expired', 'expiring'].includes(tokenStatus.value.status)
})

// 方法
const handleRefresh = async () => {
  refreshing.value = true
  try {
    const success = await userStore.refreshToken()
    if (!success) {
      console.warn('Token refresh failed')
    }
  } catch (error) {
    console.error('Token refresh error:', error)
  } finally {
    refreshing.value = false
  }
}

// 优化自动隐藏逻辑：token有效时快速隐藏，减少干扰
let hideTimer: number | null = null

const startHideTimer = () => {
  if (props.autoHide && tokenStatus.value.status === 'valid') {
    hideTimer = setTimeout(() => {
      visible.value = false
    }, 2000) // 缩短为2秒，减少干扰
  }
}

const clearHideTimer = () => {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

// 生命周期
onMounted(() => {
  startHideTimer()
})

onUnmounted(() => {
  clearHideTimer()
})

// 优化token状态检查：减少检查频率，因为已有无感刷新
const checkTokenStatus = () => {
  clearHideTimer()
  visible.value = true
  startHideTimer()
}

// 降低检查频率：从1分钟改为5分钟，因为无感刷新已经处理了大部分情况
let statusCheckInterval: number | null = null

onMounted(() => {
  statusCheckInterval = setInterval(checkTokenStatus, 5 * 60 * 1000) // 每5分钟检查一次
})

onUnmounted(() => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }
})
</script>

<style scoped>
.token-status {
  position: fixed;
  z-index: 9999;
  padding: 8px 12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.position-top-right {
  top: 20px;
  right: 20px;
}

.position-bottom-right {
  bottom: 20px;
  right: 20px;
}

.position-top-left {
  top: 20px;
  left: 20px;
}

.position-bottom-left {
  bottom: 20px;
  left: 20px;
}

.status-valid {
  background: rgba(103, 194, 58, 0.1);
  border: 1px solid rgba(103, 194, 58, 0.3);
  color: #67c23a;
}

.status-expiring {
  background: rgba(230, 162, 60, 0.1);
  border: 1px solid rgba(230, 162, 60, 0.3);
  color: #e6a23c;
}

.status-expired {
  background: rgba(230, 162, 60, 0.1);
  border: 1px solid rgba(230, 162, 60, 0.3);
  color: #e6a23c;
}

.status-invalid,
.status-expired-no-refresh {
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.3);
  color: #f56c6c;
}

.status-none {
  background: rgba(144, 147, 153, 0.1);
  border: 1px solid rgba(144, 147, 153, 0.3);
  color: #909399;
}

.status-icon {
  font-size: 14px;
}

.status-text {
  white-space: nowrap;
}

.token-status:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
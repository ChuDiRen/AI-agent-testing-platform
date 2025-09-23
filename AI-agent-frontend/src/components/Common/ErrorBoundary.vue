<!-- 全局错误边界组件 -->
<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <div class="error-icon">
        <el-icon size="64" color="#f56c6c">
          <Warning />
        </el-icon>
      </div>
      
      <h2 class="error-title">页面出现了一些问题</h2>
      
      <div class="error-message">
        <p v-if="userFriendlyMessage">{{ userFriendlyMessage }}</p>
        <p v-else>抱歉，页面遇到了意外错误，请尝试刷新页面或联系技术支持。</p>
      </div>

      <div class="error-details" v-if="showDetails">
        <el-collapse>
          <el-collapse-item title="错误详情" name="details">
            <div class="error-stack">
              <p><strong>错误信息:</strong> {{ error?.message }}</p>
              <p v-if="error?.stack"><strong>错误堆栈:</strong></p>
              <pre v-if="error?.stack">{{ error.stack }}</pre>
              <p><strong>发生时间:</strong> {{ errorTime }}</p>
              <p><strong>页面路径:</strong> {{ errorPath }}</p>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <div class="error-actions">
        <el-button type="primary" @click="reload">
          <el-icon><Refresh /></el-icon>
          刷新页面
        </el-button>
        
        <el-button @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        
        <el-button @click="reportError" v-if="canReport">
          <el-icon><Warning /></el-icon>
          报告问题
        </el-button>
        
        <el-button 
          @click="showDetails = !showDetails" 
          type="info" 
          text
        >
          {{ showDetails ? '隐藏' : '显示' }}详情
        </el-button>
      </div>
    </div>
  </div>
  
  <!-- 正常内容 -->
  <slot v-else />

  <!-- 错误报告对话框 -->
  <el-dialog
    v-model="showReportDialog"
    title="报告错误"
    width="600px"
    @close="closeReportDialog"
  >
    <el-form :model="reportForm" label-width="80px">
      <el-form-item label="问题描述">
        <el-input
          v-model="reportForm.description"
          type="textarea"
          :rows="4"
          placeholder="请描述遇到的问题..."
        />
      </el-form-item>
      
      <el-form-item label="联系方式">
        <el-input
          v-model="reportForm.contact"
          placeholder="邮箱或手机号（可选）"
        />
      </el-form-item>
      
      <el-form-item label="包含详情">
        <el-checkbox v-model="reportForm.includeDetails">
          包含错误技术详情
        </el-checkbox>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="closeReportDialog">取消</el-button>
      <el-button type="primary" @click="submitReport" :loading="reportLoading">
        提交报告
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onErrorCaptured, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Warning, Refresh, HomeFilled } from '@element-plus/icons-vue'
import { errorHandler } from '@/utils/errorHandler'

// Props
interface Props {
  fallback?: string
  showReportButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  fallback: '',
  showReportButton: true
})

// Router
const router = useRouter()

// 状态
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorTime = ref('')
const errorPath = ref('')
const showDetails = ref(false)
const showReportDialog = ref(false)
const reportLoading = ref(false)

// 报告表单
const reportForm = reactive({
  description: '',
  contact: '',
  includeDetails: false
})

// 计算属性
const userFriendlyMessage = computed(() => {
  if (!error.value) return ''
  
  // 根据错误类型返回用户友好的消息
  const message = error.value.message
  
  if (message.includes('Network Error') || message.includes('timeout')) {
    return '网络连接出现问题，请检查网络后重试'
  }
  
  if (message.includes('404')) {
    return '请求的资源不存在'
  }
  
  if (message.includes('500')) {
    return '服务器出现了临时问题，请稍后重试'
  }
  
  if (message.includes('401') || message.includes('403')) {
    return '登录状态已过期，请重新登录'
  }
  
  return ''
})

const canReport = computed(() => {
  return props.showReportButton && !import.meta.env.DEV
})

// 错误捕获
onErrorCaptured((err: Error, instance, info) => {
  console.error('ErrorBoundary caught error:', err, info)
  
  hasError.value = true
  error.value = err
  errorTime.value = new Date().toLocaleString()
  errorPath.value = router.currentRoute.value.fullPath
  
  // 记录到错误处理器
  errorHandler.handleApiError(err, {
    showMessage: false,
    showModal: false,
    autoRedirect: false
  })
  
  // 阻止错误继续向上传播
  return false
})

// 全局错误监听
onMounted(() => {
  // 监听未捕获的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
    
    hasError.value = true
    error.value = event.reason instanceof Error ? event.reason : new Error(String(event.reason))
    errorTime.value = new Date().toLocaleString()
    errorPath.value = router.currentRoute.value.fullPath
    
    // 阻止默认的控制台错误输出
    event.preventDefault()
  })

  // 监听JavaScript运行时错误
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error)
    
    hasError.value = true
    error.value = event.error || new Error(event.message)
    errorTime.value = new Date().toLocaleString()
    errorPath.value = router.currentRoute.value.fullPath
  })
})

// 方法
const reload = () => {
  window.location.reload()
}

const goHome = () => {
  hasError.value = false
  error.value = null
  router.push('/')
}

const reportError = () => {
  showReportDialog.value = true
  
  // 预填充错误信息
  if (error.value) {
    reportForm.description = `页面出现错误: ${error.value.message}`
  }
}

const closeReportDialog = () => {
  showReportDialog.value = false
  reportForm.description = ''
  reportForm.contact = ''
  reportForm.includeDetails = false
}

const submitReport = async () => {
  if (!reportForm.description.trim()) {
    ElMessage.warning('请描述遇到的问题')
    return
  }
  
  reportLoading.value = true
  
  try {
    const reportData = {
      description: reportForm.description,
      contact: reportForm.contact,
      errorTime: errorTime.value,
      errorPath: errorPath.value,
      userAgent: navigator.userAgent,
      url: window.location.href,
      ...(reportForm.includeDetails && error.value && {
        errorMessage: error.value.message,
        errorStack: error.value.stack
      })
    }
    
    // 这里可以调用实际的错误报告API
    console.log('Error report:', reportData)
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('错误报告已提交，感谢您的反馈')
    closeReportDialog()
    
  } catch (error) {
    console.error('Failed to submit error report:', error)
    ElMessage.error('提交报告失败，请稍后重试')
  } finally {
    reportLoading.value = false
  }
}

// 重置错误状态的方法
const resetError = () => {
  hasError.value = false
  error.value = null
  errorTime.value = ''
  errorPath.value = ''
  showDetails.value = false
}

// 暴露方法给父组件
defineExpose({
  resetError
})
</script>

<style scoped lang="scss">
.error-boundary {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.error-content {
  text-align: center;
  max-width: 600px;
  width: 100%;
}

.error-icon {
  margin-bottom: 20px;
}

.error-title {
  color: #303133;
  font-size: 24px;
  margin-bottom: 16px;
  font-weight: 600;
}

.error-message {
  color: #606266;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 24px;
  
  p {
    margin: 0 0 8px 0;
  }
}

.error-details {
  margin-bottom: 24px;
  text-align: left;
  
  .error-stack {
    color: #606266;
    font-size: 14px;
    
    p {
      margin: 8px 0;
    }
    
    pre {
      background: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      font-size: 12px;
      line-height: 1.4;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  
  .el-button {
    min-width: 100px;
  }
}

@media (max-width: 768px) {
  .error-boundary {
    padding: 16px;
  }
  
  .error-title {
    font-size: 20px;
  }
  
  .error-message {
    font-size: 14px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
    
    .el-button {
      width: 200px;
    }
  }
}
</style>

<template>
  <div class="agent-chat-container">
    <!-- 顶部工具栏 -->
    <div class="chat-header">
      <div class="header-left">
        <h3 class="header-title">
          <el-icon><ChatDotRound /></el-icon>
          AI 智能体聊天
        </h3>
        <el-tag v-if="isConfigured" type="success" size="small" effect="plain">
          <el-icon><CircleCheckFilled /></el-icon>
          已配置
        </el-tag>
        <el-tag v-else type="warning" size="small" effect="plain">
          <el-icon><WarningFilled /></el-icon>
          未配置
        </el-tag>
      </div>
      
      <div class="header-actions">
        <el-button 
          size="small"
          :icon="Setting"
          @click="showConfigDialog = true"
        >
          配置
        </el-button>
      </div>
    </div>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      title="AI 智能体聊天配置"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="config" label-width="140px" label-position="left">
        <el-form-item label="部署 URL" required>
          <el-input
            v-model="config.deploymentUrl"
            placeholder="http://localhost:2024"
            clearable
          >
            <template #prepend>
              <el-icon><Link /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            这是您的 LangGraph 部署 URL。可以是本地或生产环境部署。
          </div>
        </el-form-item>

        <el-form-item label="智能体/图谱 ID" required>
          <el-input
            v-model="config.assistantId"
            placeholder="agent"
            clearable
          >
            <template #prepend>
              <el-icon><Service /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            这是要获取并运行在执行操作时调用的图谱 ID（可以是图谱名称）或智能体 ID。
          </div>
        </el-form-item>

        <el-form-item label="LangSmith API 密钥">
          <el-input
            v-model="config.langsmithApiKey"
            placeholder="lsv2_pt_..."
            type="password"
            show-password
            clearable
          >
            <template #prepend>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            如果使用本地 LangGraph 服务器，则不需要此项。此值仅存储在浏览器的本地存储中，仅用于验证发送到 LangGraph 服务器的请求。
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :icon="Select">
          保存配置
        </el-button>
      </template>
    </el-dialog>

    <!-- Agent 聊天界面 -->
    <div v-if="isConfigured" class="agent-chat-content">
      <AgentChatAppVue />
    </div>

    <!-- 未配置提示 -->
    <div v-else class="config-prompt">
      <el-empty description="">
        <template #image>
          <el-icon :size="80" color="#409eff">
            <Setting />
          </el-icon>
        </template>
        <template #description>
          <div class="empty-description">
            <h3>欢迎使用 AI 智能体聊天！</h3>
            <p>在开始之前，您需要输入部署 URL 和智能体/图谱 ID。</p>
          </div>
        </template>
        <el-button type="primary" size="large" @click="showConfigDialog = true" :icon="Setting">
          打开配置
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Setting, 
  Link, 
  Service, 
  Key, 
  Select,
  ChatDotRound,
  CircleCheckFilled,
  WarningFilled
} from '@element-plus/icons-vue'
import { applyReactInVue } from 'veaury'
import AgentChatApp from '@/agent-react/AgentChatApp'
// 导入完整的 Agent Chat 样式
import '~/agent-react/globals.css'
// 导入 markdown 样式
import '~/agent-react/components/thread/markdown-styles.css'

// 配置对话框
const showConfigDialog = ref(false)

// 配置数据
const config = reactive({
  deploymentUrl: '',
  assistantId: '',
  langsmithApiKey: ''
})

// 是否已配置
const isConfigured = computed(() => {
  return config.deploymentUrl && config.assistantId
})

// 加载配置
const loadConfig = () => {
  try {
    const savedConfig = localStorage.getItem('agent-chat-config')
    if (savedConfig) {
      const parsed = JSON.parse(savedConfig)
      config.deploymentUrl = parsed.deploymentUrl || ''
      config.assistantId = parsed.assistantId || ''
      config.langsmithApiKey = parsed.langsmithApiKey || ''
    } else {
      // 从环境变量读取默认配置，默认使用后端FastAPI的LangGraph兼容API
      config.deploymentUrl = import.meta.env.VITE_AGENT_API_URL || 'http://localhost:5000/api/langgraph'
      config.assistantId = import.meta.env.VITE_AGENT_ASSISTANT_ID || 'testcase'
      config.langsmithApiKey = import.meta.env.VITE_AGENT_LANGSMITH_API_KEY || ''
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.warning('加载配置失败，使用默认配置')
  }
}

// 保存配置
const saveConfig = () => {
  // 验证必填项
  if (!config.deploymentUrl) {
    ElMessage.error('请输入部署 URL')
    return
  }
  if (!config.assistantId) {
    ElMessage.error('请输入智能体/图谱 ID')
    return
  }

  try {
    // 保存到 localStorage
    localStorage.setItem('agent-chat-config', JSON.stringify({
      deploymentUrl: config.deploymentUrl,
      assistantId: config.assistantId,
      langsmithApiKey: config.langsmithApiKey
    }))

    // 设置全局配置（供 React 组件使用）
    window.AGENT_CHAT_CONFIG = {
      NEXT_PUBLIC_API_URL: config.deploymentUrl,
      NEXT_PUBLIC_ASSISTANT_ID: config.assistantId,
      LANGSMITH_API_KEY: config.langsmithApiKey
    }

    ElMessage.success('配置保存成功')
    showConfigDialog.value = false
    
    // 刷新页面以应用新配置
    location.reload()
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}

// 初始化
onMounted(() => {
  loadConfig()
  
  // 如果未配置，自动打开配置对话框
  if (!isConfigured.value) {
    setTimeout(() => {
      showConfigDialog.value = true
    }, 500)
  }
})

// 使用 veaury 将 React 组件转换为 Vue 组件
const AgentChatAppVue = applyReactInVue(AgentChatApp)
</script>

<style scoped>
.agent-chat-container {
  width: 100%;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: hsl(var(--background));
  color: hsl(var(--foreground));
}

/* 顶部工具栏 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 聊天内容区域 */
.agent-chat-content {
  flex: 1;
  overflow: hidden;
  background: hsl(var(--background));
}

/* 确保 React 组件使用正确的字体 */
.agent-chat-content :deep(*) {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 未配置提示 */
.config-prompt {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.empty-description {
  margin-bottom: 20px;
}

.empty-description h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.empty-description p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

/* 表单提示文字 */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}

/* 对话框样式优化 */
:deep(.el-dialog__body) {
  padding: 20px 30px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-input-group__prepend) {
  padding: 0 15px;
  background-color: var(--el-fill-color-light);
}

/* 状态标签样式 */
:deep(.el-tag) {
  height: 24px;
}
</style>

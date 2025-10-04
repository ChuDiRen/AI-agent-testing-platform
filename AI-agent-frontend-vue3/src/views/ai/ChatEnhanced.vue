<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="ai-chat-enhanced">
    <el-card class="chat-card">
      <template #header>
        <div class="chat-header">
          <div class="header-left">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 智能助手</span>
            <el-tag :type="isLoading ? 'warning' : 'success'" size="small">
              {{ isLoading ? '思考中...' : '在线' }}
            </el-tag>
          </div>
          <div class="header-right">
            <!-- 模型选择 -->
            <el-select
              v-model="selectedModel"
              placeholder="选择模型"
              size="small"
              style="width: 200px; margin-right: 10px"
              @change="handleModelChange"
            >
              <el-option
                v-for="model in availableModels"
                :key="model.model_id"
                :label="model.name"
                :value="model.model_key"
                :disabled="!model.is_enabled"
              >
                <span>{{ model.name }}</span>
                <el-tag v-if="!model.is_enabled" type="info" size="small" style="margin-left: 8px">
                  未启用
                </el-tag>
              </el-option>
            </el-select>
            
            <!-- 流式开关 -->
            <el-tooltip content="流式响应" placement="top">
              <el-switch
                v-model="useStream"
                active-text="流式"
                inactive-text="普通"
                size="small"
                style="margin-right: 10px"
              />
            </el-tooltip>
            
            <!-- 操作按钮 -->
            <el-button-group size="small">
              <el-button @click="handleClear">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
              <el-button @click="handleExport">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <el-empty v-if="messages.length === 0" description="开始与AI助手对话吧" />
        
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message-item"
          :class="message.role"
        >
          <div class="message-avatar">
            <el-avatar v-if="message.role === 'user'">
              <el-icon><User /></el-icon>
            </el-avatar>
            <el-avatar v-else class="ai-avatar">
              <el-icon><Service /></el-icon>
            </el-avatar>
          </div>
          
          <div class="message-content">
            <div class="message-header">
              <span class="message-name">
                {{ message.role === 'user' ? '我' : 'AI 助手' }}
              </span>
              <span class="message-time">{{ message.timestamp }}</span>
            </div>
            
            <div class="message-text">
              {{ message.content }}
              <span v-if="message.isStreaming" class="cursor-blink">▊</span>
            </div>
            
            <div class="message-actions" v-if="message.role === 'assistant' && !message.isStreaming">
              <el-button link size="small" @click="copyMessage(message.content)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
              <el-button link size="small" @click="handleRegenerate">
                <el-icon><RefreshRight /></el-icon>
                重新生成
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入消息... (Ctrl+Enter 发送)"
          @keydown.ctrl.enter="handleSend"
          :disabled="isLoading"
        />
        <div class="input-actions">
          <div class="input-info">
            <el-text size="small" type="info">
              当前模型: {{ currentModelName }}
            </el-text>
          </div>
          <div class="input-buttons">
            <el-button
              v-if="isLoading"
              @click="handleStop"
              type="danger"
              size="default"
            >
              <el-icon><Close /></el-icon>
              停止生成
            </el-button>
            <el-button
              v-else
              type="primary"
              @click="handleSend"
              :disabled="!inputMessage.trim()"
              size="default"
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound,
  User,
  Service,
  CopyDocument,
  RefreshRight,
  Delete,
  Download,
  Promotion,
  Close
} from '@element-plus/icons-vue'
import { useAIChat } from '@/composables/useAIChat'
import { getModelsAPI, type AIModel } from '@/api/ai-enhanced'

// 使用AI聊天组合式函数
const {
  messages,
  isLoading,
  sendMessage,
  sendMessageStream,
  stopStreaming,
  clearMessages,
  regenerateLastMessage
} = useAIChat()

// 状态
const inputMessage = ref('')
const messageListRef = ref<HTMLElement>()
const selectedModel = ref('gpt-3.5-turbo')
const useStream = ref(true)
const availableModels = ref<AIModel[]>([])

// 当前模型名称
const currentModelName = computed(() => {
  const model = availableModels.value.find(m => m.model_key === selectedModel.value)
  return model?.name || '未选择'
})

// 加载可用模型
const loadModels = async () => {
  try {
    const response = await getModelsAPI()
    if (response.data) {
      availableModels.value = response.data
      
      // 选择第一个启用的模型
      const enabledModel = response.data.find(m => m.is_enabled)
      if (enabledModel) {
        selectedModel.value = enabledModel.model_key
      }
    }
  } catch (error: any) {
    console.error('加载模型失败:', error)
    ElMessage.warning('加载模型列表失败,使用默认模型')
  }
}

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const content = inputMessage.value
  inputMessage.value = ''
  
  await nextTick()
  scrollToBottom()
  
  if (useStream.value) {
    await sendMessageStream(content, {
      model: selectedModel.value
    })
  } else {
    await sendMessage(content, {
      model: selectedModel.value
    })
  }
  
  await nextTick()
  scrollToBottom()
}

// 停止生成
const handleStop = () => {
  stopStreaming()
  ElMessage.info('已停止生成')
}

// 清空对话
const handleClear = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有对话吗?', '提示', {
      type: 'warning'
    })
    clearMessages()
    ElMessage.success('已清空对话')
  } catch {
    // 用户取消
  }
}

// 导出对话
const handleExport = () => {
  const content = messages.value
    .map(m => `[${m.timestamp}] ${m.role === 'user' ? '我' : 'AI'}: ${m.content}`)
    .join('\n\n')
  
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ai-chat-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('对话已导出')
}

// 复制消息
const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 重新生成
const handleRegenerate = async () => {
  await regenerateLastMessage({
    model: selectedModel.value,
    useStream: useStream.value
  })
}

// 模型切换
const handleModelChange = () => {
  ElMessage.info(`已切换到 ${currentModelName.value}`)
}

// 滚动到底部
const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 监听消息变化,自动滚动
watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

// 初始化
onMounted(() => {
  loadModels()
})
</script>

<style scoped lang="scss">
.ai-chat-enhanced {
  height: 100%;
  padding: 20px;
  
  .chat-card {
    height: calc(100vh - 140px);
    display: flex;
    flex-direction: column;
    
    :deep(.el-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
  }
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 600;
    }
    
    .header-right {
      display: flex;
      align-items: center;
    }
  }
  
  .message-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px 0;
    
    .message-item {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      
      &.user {
        flex-direction: row-reverse;
        
        .message-content {
          align-items: flex-end;
        }
        
        .message-text {
          background: #409eff;
          color: white;
        }
      }
      
      .message-avatar {
        flex-shrink: 0;
        
        .ai-avatar {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
      }
      
      .message-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .message-header {
          display: flex;
          gap: 10px;
          font-size: 12px;
          color: #909399;
          
          .message-name {
            font-weight: 600;
          }
        }
        
        .message-text {
          padding: 12px 16px;
          border-radius: 8px;
          background: #f4f4f5;
          line-height: 1.6;
          white-space: pre-wrap;
          word-break: break-word;
          
          .cursor-blink {
            animation: blink 1s infinite;
          }
        }
        
        .message-actions {
          display: flex;
          gap: 8px;
        }
      }
    }
  }
  
  .input-area {
    border-top: 1px solid #ebeef5;
    padding-top: 16px;
    
    .input-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 12px;
      
      .input-info {
        flex: 1;
      }
      
      .input-buttons {
        display: flex;
        gap: 8px;
      }
    }
  }
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>


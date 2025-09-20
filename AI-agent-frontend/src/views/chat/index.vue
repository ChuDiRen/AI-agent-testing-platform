<!-- AI智能对话页面 -->
<template>
  <div class="chat-container">
    <!-- 侧边栏 - 会话列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <h3>对话历史</h3>
        <el-button type="primary" size="small" @click="createNewSession">
          <el-icon><Plus /></el-icon>
          新建对话
        </el-button>
      </div>
      
      <div class="session-list">
        <div 
          v-for="session in sessions" 
          :key="session.session_id"
          class="session-item"
          :class="{ active: currentSessionId === session.session_id }"
          @click="selectSession(session.session_id)"
        >
          <div class="session-title">{{ session.title }}</div>
          <div class="session-meta">
            <span class="message-count">{{ session.message_count }}条消息</span>
            <span class="session-time">{{ formatTime(session.updated_at) }}</span>
          </div>
          <div class="session-actions">
            <el-button 
              type="text" 
              size="small" 
              @click.stop="editSession(session)"
            >
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click.stop="deleteSession(session.session_id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="chat-title">
          <h2>{{ currentSession?.title || 'AI智能对话' }}</h2>
          <div class="model-info">
            <el-tag size="small">{{ currentModel?.name || '请选择模型' }}</el-tag>
          </div>
        </div>
        
        <div class="chat-controls">
          <el-select 
            v-model="selectedModelId" 
            placeholder="选择AI模型"
            @change="onModelChange"
            style="width: 200px"
          >
            <el-option
              v-for="model in availableModels"
              :key="model.id"
              :label="model.display_name"
              :value="model.id"
            />
          </el-select>
          
          <el-button @click="showSettings = true">
            <el-icon><Setting /></el-icon>
            设置
          </el-button>
          
          <el-button @click="clearMessages" :disabled="!currentSessionId">
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div v-if="messages.length === 0" class="empty-state">
          <el-empty description="开始您的AI对话吧！" />
        </div>
        
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message-item"
          :class="message.role"
        >
          <div class="message-avatar">
            <el-avatar v-if="message.role === 'user'" :size="32">
              <el-icon><User /></el-icon>
            </el-avatar>
            <el-avatar v-else :size="32" style="background-color: #409eff">
              <el-icon><Robot /></el-icon>
            </el-avatar>
          </div>
          
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">
                {{ message.role === 'user' ? '您' : 'AI助手' }}
              </span>
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
            </div>
            
            <div class="message-text" v-html="formatMessage(message.content)"></div>
            
            <div v-if="message.metadata" class="message-meta">
              <el-tag v-if="message.metadata.tokens_used" size="small" type="info">
                {{ message.metadata.tokens_used }} tokens
              </el-tag>
              <el-tag v-if="message.metadata.cost" size="small" type="warning">
                ¥{{ (message.metadata.cost || 0).toFixed(4) }}
              </el-tag>
            </div>
          </div>
          
          <div class="message-actions">
            <el-button type="text" size="small" @click="copyMessage(message.content)">
              <el-icon><DocumentCopy /></el-icon>
            </el-button>
          </div>
        </div>
        
        <!-- 正在输入指示器 -->
        <div v-if="isTyping" class="message-item assistant typing">
          <div class="message-avatar">
            <el-avatar :size="32" style="background-color: #409eff">
              <el-icon><Robot /></el-icon>
            </el-avatar>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input">
        <div class="input-toolbar">
          <el-slider
            v-model="temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-tooltip
            style="width: 120px"
          />
          <span class="toolbar-label">温度: {{ temperature }}</span>
          
          <el-input-number
            v-model="maxTokens"
            :min="1"
            :max="4000"
            size="small"
            style="width: 120px"
          />
          <span class="toolbar-label">最大Token</span>
        </div>
        
        <div class="input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入您的问题..."
            @keydown.ctrl.enter="sendMessage"
            :disabled="isLoading"
          />
          
          <div class="input-actions">
            <el-button 
              type="primary" 
              @click="sendMessage"
              :loading="isLoading"
              :disabled="!inputMessage.trim() || !selectedModelId"
            >
              <el-icon><Promotion /></el-icon>
              发送 (Ctrl+Enter)
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 会话编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑会话" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="会话标题">
          <el-input v-model="editForm.title" placeholder="请输入会话标题" />
        </el-form-item>
        <el-form-item label="系统提示">
          <el-input
            v-model="editForm.system_prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入系统提示词（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSession">保存</el-button>
      </template>
    </el-dialog>

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="对话设置" width="600px">
      <el-form label-width="120px">
        <el-form-item label="默认温度">
          <el-slider v-model="defaultTemperature" :min="0" :max="2" :step="0.1" show-tooltip />
        </el-form-item>
        <el-form-item label="默认最大Token">
          <el-input-number v-model="defaultMaxTokens" :min="1" :max="4000" />
        </el-form-item>
        <el-form-item label="流式响应">
          <el-switch v-model="streamResponse" />
        </el-form-item>
        <el-form-item label="自动保存对话">
          <el-switch v-model="autoSave" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Edit, Delete, User, Robot, Setting, 
  DocumentCopy, Promotion 
} from '@element-plus/icons-vue'

// 响应式数据
const sessions = ref([])
const messages = ref([])
const availableModels = ref([])
const currentSessionId = ref('')
const selectedModelId = ref(null)
const inputMessage = ref('')
const isLoading = ref(false)
const isTyping = ref(false)
const showEditDialog = ref(false)
const showSettings = ref(false)

// 设置参数
const temperature = ref(0.7)
const maxTokens = ref(1000)
const defaultTemperature = ref(0.7)
const defaultMaxTokens = ref(1000)
const streamResponse = ref(true)
const autoSave = ref(true)

// 编辑表单
const editForm = reactive({
  title: '',
  system_prompt: ''
})

// 引用
const messageListRef = ref()

// 计算属性
const currentSession = computed(() => {
  return sessions.value.find(s => s.session_id === currentSessionId.value)
})

const currentModel = computed(() => {
  return availableModels.value.find(m => m.id === selectedModelId.value)
})

// 生命周期
onMounted(() => {
  loadSessions()
  loadModels()
  loadSettings()
})

// 方法
const loadSessions = async () => {
  // TODO: 调用API加载会话列表
  console.log('Loading sessions...')
}

const loadModels = async () => {
  // TODO: 调用API加载可用模型
  console.log('Loading models...')
}

const loadSettings = () => {
  // TODO: 从本地存储加载设置
  console.log('Loading settings...')
}

const createNewSession = async () => {
  if (!selectedModelId.value) {
    ElMessage.warning('请先选择AI模型')
    return
  }
  
  // TODO: 调用API创建新会话
  console.log('Creating new session...')
}

const selectSession = async (sessionId: string) => {
  currentSessionId.value = sessionId
  await loadMessages(sessionId)
}

const loadMessages = async (sessionId: string) => {
  // TODO: 调用API加载消息
  console.log('Loading messages for session:', sessionId)
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || !selectedModelId.value) return
  
  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  
  // 添加用户消息到界面
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userMessage,
    created_at: new Date().toISOString()
  })
  
  scrollToBottom()
  
  isLoading.value = true
  isTyping.value = true
  
  try {
    // TODO: 调用API发送消息
    console.log('Sending message:', userMessage)
    
    // 模拟AI响应
    setTimeout(() => {
      messages.value.push({
        id: Date.now() + 1,
        role: 'assistant',
        content: '这是一个模拟的AI响应。实际实现中，这里会调用真实的AI API。',
        created_at: new Date().toISOString(),
        metadata: {
          tokens_used: 25,
          cost: 0.0001
        }
      })
      
      isLoading.value = false
      isTyping.value = false
      scrollToBottom()
    }, 2000)
    
  } catch (error) {
    console.error('Error sending message:', error)
    ElMessage.error('发送消息失败')
    isLoading.value = false
    isTyping.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}

const formatMessage = (content: string) => {
  // 简单的markdown渲染
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const copyMessage = (content: string) => {
  navigator.clipboard.writeText(content)
  ElMessage.success('已复制到剪贴板')
}

const editSession = (session: any) => {
  editForm.title = session.title
  editForm.system_prompt = session.system_prompt || ''
  showEditDialog.value = true
}

const saveSession = async () => {
  // TODO: 调用API保存会话
  console.log('Saving session...')
  showEditDialog.value = false
}

const deleteSession = async (sessionId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这个会话吗？', '确认删除', {
      type: 'warning'
    })
    
    // TODO: 调用API删除会话
    console.log('Deleting session:', sessionId)
    
  } catch {
    // 用户取消删除
  }
}

const clearMessages = async () => {
  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？', '确认清空', {
      type: 'warning'
    })
    
    messages.value = []
    // TODO: 调用API清空消息
    
  } catch {
    // 用户取消清空
  }
}

const onModelChange = () => {
  // TODO: 处理模型切换
  console.log('Model changed to:', selectedModelId.value)
}

const saveSettings = () => {
  // TODO: 保存设置到本地存储
  temperature.value = defaultTemperature.value
  maxTokens.value = defaultMaxTokens.value
  showSettings.value = false
  ElMessage.success('设置已保存')
}
</script>

<style scoped lang="scss">
.chat-container {
  display: flex;
  height: calc(100vh - 120px);
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}

.chat-sidebar {
  width: 300px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;

  .sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 16px;
      color: #303133;
    }
  }

  .session-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;

    .session-item {
      padding: 12px;
      margin-bottom: 8px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
      position: relative;

      &:hover {
        background: #f0f9ff;
      }

      &.active {
        background: #e1f5fe;
        border-left: 3px solid #409eff;
      }

      .session-title {
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .session-meta {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #909399;

        .message-count {
          color: #67c23a;
        }
      }

      .session-actions {
        position: absolute;
        top: 8px;
        right: 8px;
        opacity: 0;
        transition: opacity 0.2s;
      }

      &:hover .session-actions {
        opacity: 1;
      }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;

  .chat-header {
    padding: 16px 20px;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .chat-title {
      h2 {
        margin: 0 0 4px 0;
        font-size: 18px;
        color: #303133;
      }

      .model-info {
        font-size: 12px;
      }
    }

    .chat-controls {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .message-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px;

    .empty-state {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .message-item {
      display: flex;
      margin-bottom: 20px;
      animation: fadeIn 0.3s ease-in;

      &.user {
        flex-direction: row-reverse;

        .message-content {
          background: #409eff;
          color: white;
          margin-right: 12px;
        }
      }

      &.assistant {
        .message-content {
          background: #f4f4f5;
          color: #303133;
          margin-left: 12px;
        }
      }

      &.typing {
        .message-content {
          padding: 16px 20px;
        }
      }

      .message-avatar {
        flex-shrink: 0;
      }

      .message-content {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 12px;
        position: relative;

        .message-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          font-size: 12px;
          opacity: 0.8;
        }

        .message-text {
          line-height: 1.6;
          word-wrap: break-word;

          code {
            background: rgba(0, 0, 0, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
          }
        }

        .message-meta {
          margin-top: 8px;
          display: flex;
          gap: 8px;
        }
      }

      .message-actions {
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-left: 8px;
        opacity: 0;
        transition: opacity 0.2s;
      }

      &:hover .message-actions {
        opacity: 1;
      }
    }
  }

  .chat-input {
    border-top: 1px solid #e4e7ed;
    padding: 16px 20px;

    .input-toolbar {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 12px;
      font-size: 12px;
      color: #606266;

      .toolbar-label {
        white-space: nowrap;
      }
    }

    .input-area {
      display: flex;
      gap: 12px;
      align-items: flex-end;

      .el-textarea {
        flex: 1;
      }

      .input-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
    }
  }
}

// 打字动画
.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;

  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #409eff;
    animation: typing 1.4s infinite ease-in-out;

    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .chat-container {
    flex-direction: column;
    height: calc(100vh - 60px);
  }

  .chat-sidebar {
    width: 100%;
    height: 200px;
  }

  .message-item .message-content {
    max-width: 85%;
  }
}
</style>

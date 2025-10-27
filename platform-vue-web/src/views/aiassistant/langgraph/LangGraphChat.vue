<template>
  <div class="langgraph-chat-container">
    <!-- 侧边栏：对话列表 -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <el-button 
          v-if="!sidebarCollapsed"
          type="primary" 
          style="width: 100%"
          @click="handleCreateThread"
          :loading="threadLoading"
        >
          <el-icon><Plus /></el-icon>
          新对话
        </el-button>
        <el-button 
          v-else
          type="primary" 
          circle
          @click="handleCreateThread"
          :loading="threadLoading"
        >
          <el-icon><Plus /></el-icon>
        </el-button>
      </div>

      <div v-if="!sidebarCollapsed" class="thread-list">
        <div 
          v-for="thread in threads" 
          :key="thread.id"
          class="thread-item"
          :class="{ active: thread.id === currentThreadId }"
          @click="handleSwitchThread(thread.id)"
        >
          <div class="thread-title">{{ thread.title }}</div>
          <div class="thread-actions">
            <el-button 
              text 
              size="small"
              @click.stop="handleDeleteThread(thread.id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <el-empty 
          v-if="threads.length === 0" 
          description="暂无对话"
          :image-size="80"
        />
      </div>

      <div class="sidebar-footer">
        <el-button 
          text 
          @click="sidebarCollapsed = !sidebarCollapsed"
        >
          <el-icon>
            <DArrowLeft v-if="!sidebarCollapsed" />
            <DArrowRight v-else />
          </el-icon>
        </el-button>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <!-- 顶部工具栏 -->
      <div class="chat-header">
        <div class="header-title">
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ currentThread?.title || 'LangGraph 智能对话' }}</span>
        </div>
        <div class="header-actions">
          <el-button size="small" @click="showSettings = true">
            <el-icon><Setting /></el-icon>
            设置
          </el-button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div ref="messagesContainer" class="messages-container">
        <!-- 欢迎消息 -->
        <div v-if="!hasMessages" class="welcome-message">
          <div class="welcome-icon">🤖</div>
          <h2>欢迎使用 LangGraph 智能对话</h2>
          <p>基于 LangGraph SDK 的高级 AI 对话助手，支持工具调用、流式输出、中断处理等功能</p>
          <div class="feature-tags">
            <el-tag>流式对话</el-tag>
            <el-tag type="success">工具调用</el-tag>
            <el-tag type="warning">中断处理</el-tag>
            <el-tag type="info">对话历史</el-tag>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-for="(message, index) in messages" :key="message.id" class="message-wrapper">
          <Bubble 
            :type="message.role === 'human' ? 'user' : 'ai'"
            :avatar="message.role === 'human' ? '👤' : '🤖'"
            :time="formatTime(message.timestamp)"
          >
            <!-- 流式输出 -->
            <Typewriter 
              v-if="message.streaming"
              :text="message.content"
              :speed="30"
            />
            
            <!-- 静态内容 -->
            <div v-else class="message-content">
              {{ message.content }}
            </div>

            <!-- 工具调用展示 -->
            <ToolCallDisplay 
              v-if="message.toolCalls"
              :calls="message.toolCalls"
            />
          </Bubble>
        </div>

        <!-- 思考中状态 -->
        <div v-if="isThinking" class="thinking-indicator">
          <Thinking />
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <EditorSender
          ref="editorSenderRef"
          v-model="inputContent"
          :loading="isSending"
          :disabled="!currentThreadId"
          clearable
          placeholder="💬 输入你的问题... (Enter 发送，Shift+Enter 换行)"
          @submit="handleSend"
        >
          <template #prefix>
            <el-tooltip content="附件上传（开发中）" placement="top">
              <el-button circle size="small" disabled>
                <el-icon><Paperclip /></el-icon>
              </el-button>
            </el-tooltip>
          </template>

          <template #action-list>
            <div class="custom-actions">
              <el-button 
                v-if="isSending"
                type="danger"
                circle
                @click="handleStop"
              >
                <el-icon><VideoPause /></el-icon>
              </el-button>
            </div>
          </template>
        </EditorSender>

        <div v-if="!currentThreadId" class="input-hint">
          <el-alert 
            type="info" 
            :closable="false"
            show-icon
          >
            请先创建或选择一个对话
          </el-alert>
        </div>
      </div>
    </div>

    <!-- Artifact 侧边栏 -->
    <ArtifactPanel
      v-model="showArtifact"
      :title="artifactTitle"
      :content="artifactContent"
      :content-type="artifactType"
      @close="showArtifact = false"
    />

    <!-- 中断处理对话框 -->
    <InterruptHandler
      :interrupt="interrupt"
      @confirm="handleInterruptConfirm"
      @cancel="handleInterruptCancel"
    />

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="LangGraph 设置" width="600px">
      <el-form label-width="120px">
        <el-form-item label="API URL">
          <el-input 
            :value="langGraphConfig.apiUrl" 
            readonly 
            placeholder="http://localhost:2024"
          />
        </el-form-item>
        <el-form-item label="Assistant ID">
          <el-input 
            :value="langGraphConfig.assistantId" 
            readonly 
            placeholder="agent"
          />
        </el-form-item>
        <el-form-item label="连接状态">
          <el-tag :type="isConnected ? 'success' : 'danger'">
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSettings = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { 
  Plus, 
  Delete, 
  ChatDotRound, 
  Setting,
  Paperclip,
  VideoPause,
  DArrowLeft,
  DArrowRight
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  EditorSender, 
  Bubble, 
  Typewriter,
  Thinking
} from 'vue-element-plus-x'

import { useLangGraphStream } from '@/composables/useLangGraphStream'
import { useLangGraphThread } from '@/composables/useLangGraphThread'
import ToolCallDisplay from './components/ToolCallDisplay.vue'
import InterruptHandler from './components/InterruptHandler.vue'
import ArtifactPanel from './components/ArtifactPanel.vue'

// 状态管理
const sidebarCollapsed = ref(false)
const messagesContainer = ref(null)
const editorSenderRef = ref(null)
const inputContent = ref('')
const showSettings = ref(false)
const showArtifact = ref(false)
const artifactTitle = ref('')
const artifactContent = ref('')
const artifactType = ref('text')
const isConnected = ref(false)

// LangGraph 配置
const langGraphConfig = computed(() => ({
  apiUrl: import.meta.env.VITE_LANGGRAPH_API_URL || 'http://localhost:2024',
  assistantId: import.meta.env.VITE_LANGGRAPH_ASSISTANT_ID || 'agent'
}))

// LangGraph 功能
const {
  threads,
  currentThreadId,
  currentThread,
  loading: threadLoading,
  initClient: initThreadClient,
  fetchThreads,
  createNewThread,
  switchThread,
  removeThread
} = useLangGraphThread()

const {
  messages,
  isSending,
  isThinking,
  interrupt,
  hasMessages,
  initClient: initStreamClient,
  sendMessage,
  stopGeneration,
  clearMessages,
  loadThreadHistory
} = useLangGraphStream()

// 初始化
onMounted(async () => {
  // 初始化客户端
  const streamClientOk = initStreamClient()
  const threadClientOk = initThreadClient()
  
  isConnected.value = streamClientOk && threadClientOk

  if (isConnected.value) {
    // 加载线程列表
    await fetchThreads()
    
    // 如果有线程，选择第一个
    if (threads.value.length > 0) {
      await handleSwitchThread(threads.value[0].id)
    } else {
      // 否则创建新线程
      await handleCreateThread()
    }
  } else {
    ElMessage.error('初始化 LangGraph 客户端失败，请检查配置')
  }
})

// 监听消息变化，自动滚动到底部
watch(messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// 创建新线程
const handleCreateThread = async () => {
  const thread = await createNewThread()
  if (thread) {
    clearMessages()
  }
}

// 切换线程
const handleSwitchThread = async (threadId) => {
  switchThread(threadId)
  clearMessages()
  await loadThreadHistory(threadId)
}

// 删除线程
const handleDeleteThread = async (threadId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个对话吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await removeThread(threadId)
  } catch (error) {
    // 用户取消删除
  }
}

// 发送消息
const handleSend = async (value) => {
  if (!value || !value.text || !value.text.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }

  if (!currentThreadId.value) {
    ElMessage.error('请先创建或选择一个对话')
    return
  }

  await sendMessage(value.text, currentThreadId.value)
  inputContent.value = ''
  
  // 清空编辑器
  if (editorSenderRef.value) {
    editorSenderRef.value.clear()
  }
}

// 停止生成
const handleStop = () => {
  stopGeneration()
  ElMessage.info('已停止生成')
}

// 中断确认
const handleInterruptConfirm = async (response) => {
  console.log('Interrupt confirmed:', response)
  // TODO: 实现中断响应逻辑
  ElMessage.success('已确认')
}

// 中断取消
const handleInterruptCancel = () => {
  console.log('Interrupt cancelled')
  ElMessage.info('已取消')
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // 1分钟内
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 1小时内
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  
  // 今天
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  
  // 其他
  return date.toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}
</script>

<style scoped>
.langgraph-chat-container {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.thread-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.thread-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.thread-item:hover {
  background-color: #f5f7fa;
}

.thread-item.active {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.thread-title {
  flex: 1;
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.thread-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.thread-item:hover .thread-actions {
  opacity: 1;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid #e4e7ed;
  text-align: center;
}

/* 主聊天区域样式 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

.welcome-message {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.welcome-message h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 12px;
}

.welcome-message p {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
  line-height: 1.6;
}

.feature-tags {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.message-wrapper {
  margin-bottom: 16px;
}

.message-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.thinking-indicator {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.input-area {
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  background-color: #fff;
}

.input-hint {
  margin-top: 12px;
}

.custom-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar:not(.collapsed) {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }
}
</style>


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
            style="width: 280px"
          >
            <el-option-group
              v-for="provider in groupedModels"
              :key="provider.name"
              :label="provider.label"
            >
              <el-option
                v-for="model in provider.models"
                :key="model.id"
                :label="model.display_name"
                :value="model.id"
              >
                <div class="model-option">
                  <div class="model-info">
                    <span class="model-name">{{ model.display_name }}</span>
                    <el-tag :type="getModelTypeColor(model.provider)" size="small">
                      {{ model.provider }}
                    </el-tag>
                  </div>
                  <div class="model-meta">
                    <span class="model-cost">{{ formatModelCost(model.pricing) }}</span>
                    <span class="model-speed">{{ getModelSpeed(model.provider) }}</span>
                  </div>
                </div>
              </el-option>
            </el-option-group>
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
            
            <!-- 文件附件显示 -->
            <div v-if="message.metadata?.files && message.metadata.files.length > 0" class="message-files">
              <div v-for="file in message.metadata.files" :key="file.name" class="message-file-item">
                <img v-if="file.type === 'image' && file.preview" 
                     :src="file.preview" 
                     :alt="file.name"
                     class="message-file-image"
                     @click="previewImage(file.preview)"
                />
                <div v-else class="message-file-info">
                  <el-icon class="file-icon"><Document /></el-icon>
                  <div class="file-details">
                    <span class="file-name">{{ file.name }}</span>
                    <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI生成图片显示 -->
            <div v-if="message.metadata?.type === 'ai_painting' && message.metadata.image_url" class="message-ai-painting">
              <img :src="message.metadata.image_url" 
                   :alt="message.metadata.prompt"
                   class="ai-generated-image"
                   @click="previewImage(message.metadata.image_url)"
              />
              <div class="painting-meta">
                <div class="meta-row">
                  <el-tag size="small" :type="aiPaintingUtils.getStyleTagType(message.metadata.style)">
                    {{ message.metadata.style }}
                  </el-tag>
                  <el-tag size="small">{{ message.metadata.size }}</el-tag>
                  <el-tag size="small" type="info">
                    {{ message.metadata.steps }} 步
                  </el-tag>
                </div>
                <div class="meta-row" v-if="message.metadata.generation_time || message.metadata.cost">
                  <span v-if="message.metadata.generation_time" class="meta-info">
                    耗时: {{ aiPaintingUtils.formatGenerationTime(message.metadata.generation_time) }}
                  </span>
                  <span v-if="message.metadata.cost" class="meta-info">
                    成本: ¥{{ message.metadata.cost.toFixed(4) }}
                  </span>
                </div>
                <div class="painting-actions">
                  <el-button size="small" text @click="regeneratePainting(message.metadata)">
                    <el-icon><Refresh /></el-icon>
                    重新生成
                  </el-button>
                  <el-button size="small" text @click="copyPaintingPrompt(message.metadata.prompt)">
                    <el-icon><DocumentCopy /></el-icon>
                    复制提示词
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 兼容旧版图片显示 -->
            <div v-else-if="message.metadata?.type === 'image' && message.metadata.image_url" class="message-ai-image">
              <img :src="message.metadata.image_url" 
                   :alt="message.metadata.prompt"
                   class="ai-generated-image"
                   @click="previewImage(message.metadata.image_url)"
              />
              <div class="image-meta">
                <el-tag size="small">{{ message.metadata.size }}</el-tag>
                <el-tag size="small" type="success">{{ message.metadata.style }}</el-tag>
              </div>
            </div>
            
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
          <!-- 文件预览区域 -->
          <div v-if="attachedFiles.length > 0" class="file-preview-area">
            <div class="file-list">
              <div v-for="(file, index) in attachedFiles" :key="file.id" class="file-item">
                <img v-if="file.type === 'image'" :src="file.preview" alt="预览" class="file-preview-img" />
                <div v-else class="file-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="file-info">
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                </div>
                <el-button 
                  size="small" 
                  type="danger" 
                  text 
                  @click="removeFile(index)"
                  class="file-remove"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </div>
          </div>

          <!-- 主输入区域 -->
          <div class="main-input-area">
            <div class="input-container">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="3"
                placeholder="输入您的问题...支持 @ 调用知识库"
                @keydown.ctrl.enter="sendMessage"
                @input="handleInputChange"
                :disabled="isLoading"
                class="message-input"
              />
              
              <!-- 功能按钮栏 -->
              <div class="function-buttons">
                <!-- 文件上传 -->
                <el-upload
                  ref="uploadRef"
                  :show-file-list="false"
                  :auto-upload="false"
                  :on-change="handleFileSelect"
                  multiple
                  accept="image/*,.pdf,.doc,.docx,.txt,.md"
                  style="display: inline-block;"
                >
                  <el-button size="small" text title="上传文件">
                    <el-icon><Paperclip /></el-icon>
                  </el-button>
                </el-upload>

                <!-- 拍照 -->
                <el-button size="small" text @click="openCamera" title="拍照">
                  <el-icon><Camera /></el-icon>
                </el-button>

                <!-- 语音输入 -->
                <el-button 
                  size="small" 
                  text 
                  @click="toggleVoiceInput" 
                  :class="{ 'voice-recording': isRecording }"
                  title="语音输入"
                >
                  <el-icon><Microphone /></el-icon>
                </el-button>

                <!-- AI绘画 -->
                <el-button size="small" text @click="openDrawingDialog" title="AI绘画">
                  <el-icon><Brush /></el-icon>
                </el-button>

                <!-- 知识库 -->
                <el-button size="small" text @click="openKnowledgeBase" title="知识库">
                  <el-icon><Collection /></el-icon>
                </el-button>

                <!-- 模型切换快捷按钮 -->
                <el-dropdown @command="quickModelChange" size="small">
                  <el-button size="small" text title="快速切换模型">
                    <el-icon><Cpu /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item 
                        v-for="model in favoriteModels" 
                        :key="model.id"
                        :command="model.id"
                      >
                        {{ model.display_name }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <div class="input-actions">
              <!-- 清空输入 -->
              <el-button 
                size="small"
                @click="clearInput"
                :disabled="!inputMessage.trim() && attachedFiles.length === 0"
                title="清空输入"
              >
                <el-icon><RefreshLeft /></el-icon>
              </el-button>

              <!-- 发送按钮 -->
              <el-button 
                type="primary" 
                @click="sendMessage"
                :loading="isLoading"
                :disabled="(!inputMessage.trim() && attachedFiles.length === 0) || !selectedModelId"
              >
                <el-icon><Promotion /></el-icon>
                发送 (Ctrl+Enter)
              </el-button>
            </div>
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

    <!-- AI绘画对话框 -->
    <el-dialog v-model="drawingDialogVisible" title="AI绘画" width="600px">
      <el-form label-width="100px">
        <el-form-item label="绘画描述">
          <el-input
            v-model="drawingPrompt"
            type="textarea"
            :rows="4"
            placeholder="请描述您想要生成的图片内容..."
          />
        </el-form-item>
        <el-form-item label="图片尺寸">
          <el-select v-model="drawingSize" placeholder="选择图片尺寸">
            <el-option label="512x512" value="512x512" />
            <el-option label="768x768" value="768x768" />
            <el-option label="1024x1024" value="1024x1024" />
            <el-option label="1024x768 (横版)" value="1024x768" />
            <el-option label="768x1024 (竖版)" value="768x1024" />
          </el-select>
        </el-form-item>
        <el-form-item label="艺术风格">
          <el-select v-model="drawingStyle" placeholder="选择艺术风格">
            <el-option label="写实风格" value="realistic" />
            <el-option label="卡通风格" value="cartoon" />
            <el-option label="油画风格" value="oil-painting" />
            <el-option label="水彩风格" value="watercolor" />
            <el-option label="素描风格" value="sketch" />
            <el-option label="科幻风格" value="sci-fi" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="drawingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="generateImage" :loading="isGeneratingImage">
          <el-icon><Brush /></el-icon>
          生成图片
        </el-button>
      </template>
    </el-dialog>

    <!-- 知识库选择器 -->
    <div 
      v-if="showKnowledgeSelector" 
      class="knowledge-selector"
      :style="{
        position: 'fixed',
        top: knowledgeSelectorPosition.top + 'px',
        left: knowledgeSelectorPosition.left + 'px',
        zIndex: 9999
      }"
    >
      <div class="selector-content">
        <div class="selector-header">
          <span>选择知识库</span>
          <el-button size="small" text @click="showKnowledgeSelector = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="selector-list">
          <div 
            v-for="kb in availableKnowledgeBases" 
            :key="kb.id" 
            class="kb-item"
            @click="selectKnowledgeBase(kb)"
          >
            <div class="kb-info">
              <span class="kb-name">{{ kb.name }}</span>
              <span class="kb-desc">{{ kb.description || '暂无描述' }}</span>
            </div>
            <div class="kb-meta">
              <el-tag size="small">{{ kb.document_count }} 文档</el-tag>
            </div>
          </div>
          <div v-if="availableKnowledgeBases.length === 0" class="empty-kb">
            <span>暂无可用知识库</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识库对话框 -->
    <el-dialog v-model="knowledgeBaseVisible" title="知识库" width="800px">
      <div class="knowledge-base-content">
        <el-alert
          title="知识库功能"
          type="info"
          description="此功能正在开发中，敬请期待。未来将支持本地文档上传、在线知识库检索等功能。"
          show-icon
          :closable="false"
        />
        
        <div class="knowledge-base-placeholder" style="margin-top: 20px; text-align: center; padding: 40px;">
          <el-icon size="64" color="#e4e7ed"><Collection /></el-icon>
          <p style="margin-top: 16px; color: #909399;">知识库功能即将上线</p>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="knowledgeBaseVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Edit, Delete, User, Robot, Setting, 
  DocumentCopy, Promotion, Document, Close, Paperclip,
  Camera, Microphone, Brush, Collection, Cpu, RefreshLeft, Refresh
} from '@element-plus/icons-vue'
import { chatApi, chatUtils } from '@/api/modules/chat'
import { knowledgeApi } from '@/api/modules/knowledge'
import { aiPaintingApi, aiPaintingUtils } from '@/api/modules/aiPainting'

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

// 多模态功能数据
const attachedFiles = ref([])
const isRecording = ref(false)
const uploadRef = ref()

// 知识库相关
const knowledgeBaseVisible = ref(false)
const selectedKnowledgeBase = ref(null)
const availableKnowledgeBases = ref([])
const showKnowledgeSelector = ref(false)
const knowledgeSelectorPosition = ref({ top: 0, left: 0 })

// 绘画相关
const drawingDialogVisible = ref(false)
const drawingPrompt = ref('')
const drawingSize = ref('512x512')
const drawingStyle = ref('realistic')
const isGeneratingImage = ref(false)

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

// 常用模型（用于快速切换）
const favoriteModels = computed(() => {
  return availableModels.value.filter(m => 
    ['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro'].some(name => 
      m.model_name.toLowerCase().includes(name)
    )
  ).slice(0, 5)
})

// 生命周期
onMounted(() => {
  loadSessions()
  loadModels()
  loadSettings()
})

// 方法
const loadSessions = async () => {
  try {
    const response = await chatApi.getSessions(1, 50)
    if (response.data.success) {
      sessions.value = response.data.data.sessions
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
    ElMessage.error('加载会话列表失败')
  }
}

const loadModels = async () => {
  try {
    const response = await chatApi.getAvailableModels()
    if (response.data.success) {
      availableModels.value = response.data.data.models
      // 如果没有选择模型，默认选择第一个可用模型
      if (!selectedModelId.value && availableModels.value.length > 0) {
        selectedModelId.value = availableModels.value[0].id
      }
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  }
}

const loadSettings = () => {
  try {
    // 从本地存储加载设置
    const savedSettings = localStorage.getItem('chat-settings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      temperature.value = settings.temperature || 0.7
      maxTokens.value = settings.maxTokens || 2000
      streamEnabled.value = settings.streamEnabled !== false
      if (settings.selectedModelId) {
        selectedModelId.value = settings.selectedModelId
      }
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

const createNewSession = async () => {
  if (!selectedModelId.value) {
    ElMessage.warning('请先选择AI模型')
    return
  }
  
  try {
    const response = await chatApi.createSession({
      title: '新对话',
      model_id: selectedModelId.value
    })
    
    if (response.data.success) {
      const newSession = response.data.data
      sessions.value.unshift(newSession)
      currentSessionId.value = newSession.session_id
      messages.value = []
      ElMessage.success('创建新对话成功')
    }
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error('创建新对话失败')
  }
}

const selectSession = async (sessionId: string) => {
  currentSessionId.value = sessionId
  await loadMessages(sessionId)
}

const loadMessages = async (sessionId: string) => {
  try {
    const response = await chatApi.getSessionMessages(sessionId, 1, 100)
    if (response.data.success) {
      messages.value = response.data.data.messages
    }
  } catch (error) {
    console.error('加载消息失败:', error)
    ElMessage.error('加载消息失败')
  }
}

const sendMessage = async () => {
  if ((!inputMessage.value.trim() && attachedFiles.value.length === 0) || !selectedModelId.value) return
  
  const userMessage = inputMessage.value.trim()
  const messageFiles = [...attachedFiles.value]
  
  // 检查是否包含知识库引用
  const kbMatch = userMessage.match(/@(\S+)/)
  let useKnowledgeBase = null
  let cleanQuery = userMessage
  
  if (kbMatch && selectedKnowledgeBase.value) {
    useKnowledgeBase = selectedKnowledgeBase.value
    cleanQuery = userMessage.replace(/@\S+\s*/, '').trim()
  }
  
  // 清空输入
  inputMessage.value = ''
  attachedFiles.value = []
  selectedKnowledgeBase.value = null
  
  // 添加用户消息到界面
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userMessage || (messageFiles.length > 0 ? '[发送了文件]' : ''),
    created_at: new Date().toISOString(),
    metadata: {
      files: messageFiles.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type,
        preview: file.preview
      }))
    }
  })
  
  scrollToBottom()
  
  isLoading.value = true
  isTyping.value = true
  
  try {
    // 确保有当前会话
    if (!currentSessionId.value) {
      await createNewSession()
      if (!currentSessionId.value) {
        throw new Error('无法创建会话')
      }
    }

    // 调用API发送消息
    const chatRequest = {
      model_id: selectedModelId.value,
      messages: messages.value.map(msg => ({
        role: msg.role as 'user' | 'assistant' | 'system',
        content: msg.content
      })),
      temperature: temperature.value,
      max_tokens: maxTokens.value,
      stream: streamEnabled.value,
      session_id: currentSessionId.value
    }

    // 如果使用知识库，则调用知识库对话API
    if (useKnowledgeBase) {
      try {
        const kbResponse = await chatWithKnowledge(cleanQuery, useKnowledgeBase.id)
        
        messages.value.push({
          id: Date.now() + 1,
          role: 'assistant',
          content: kbResponse.response,
          created_at: new Date().toISOString(),
          metadata: {
            type: 'knowledge_based',
            knowledge_base: useKnowledgeBase.name,
            relevant_chunks: kbResponse.relevant_chunks,
            tokens_used: kbResponse.tokens_used,
            cost: kbResponse.cost,
            response_time: kbResponse.response_time
          }
        })
        
        isLoading.value = false
        isTyping.value = false
        scrollToBottom()
        
      } catch (error) {
        ElMessage.error('知识库对话失败，尝试普通对话')
        // 如果知识库对话失败，回退到普通对话
        useKnowledgeBase = null
      }
    }
    
    // 普通对话流程（仅在非知识库对话或知识库对话失败时执行）
    if (!useKnowledgeBase) {
      if (streamEnabled.value) {
        // 流式响应
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: '',
          created_at: new Date().toISOString(),
          metadata: {}
        }
        messages.value.push(assistantMessage)
        
        const response = await chatApi.sendStreamMessage(chatRequest)
        
        await chatUtils.handleStreamResponse(
          response,
          (chunk: string) => {
            assistantMessage.content += chunk
            scrollToBottom()
          },
          () => {
            isLoading.value = false
            isTyping.value = false
            scrollToBottom()
          },
          (error: string) => {
            console.error('Stream error:', error)
            ElMessage.error(`发送消息失败: ${error}`)
            isLoading.value = false
            isTyping.value = false
          }
        )
      } else {
        // 普通响应
        const response = await chatApi.sendMessage(chatRequest)
        
        if (response.data.success) {
          messages.value.push({
            id: Date.now() + 1,
            role: 'assistant',
            content: response.data.data.content,
            created_at: new Date().toISOString(),
            metadata: {
              tokens_used: response.data.data.tokens_used,
              cost: response.data.data.cost,
              response_time: response.data.data.response_time
            }
          })
          
          // 如果是会话的第一条消息，更新会话标题
          if (messages.value.length <= 2) {
            const title = chatUtils.generateSessionTitle(userMessage)
            await updateSessionTitle(currentSessionId.value, title)
          }
        }
        
        isLoading.value = false
        isTyping.value = false
        scrollToBottom()
      }
    }
    
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
  if (!currentSessionId.value) return
  
  try {
    const response = await chatApi.updateSession(currentSessionId.value, {
      title: editForm.title,
      system_prompt: editForm.system_prompt
    })
    
    if (response.data.success) {
      // 更新本地会话信息
      const session = sessions.value.find(s => s.session_id === currentSessionId.value)
      if (session) {
        session.title = editForm.title
        session.system_prompt = editForm.system_prompt
      }
      ElMessage.success('会话保存成功')
    }
  } catch (error) {
    console.error('保存会话失败:', error)
    ElMessage.error('保存会话失败')
  }
  
  showEditDialog.value = false
}

const deleteSession = async (sessionId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这个会话吗？', '确认删除', {
      type: 'warning'
    })
    
    const response = await chatApi.deleteSession(sessionId)
    
    if (response.data.success) {
      // 从列表中移除会话
      sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
      
      // 如果删除的是当前会话，清空消息
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = ''
        messages.value = []
      }
      
      ElMessage.success('会话删除成功')
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除会话失败:', error)
      ElMessage.error('删除会话失败')
    }
  }
}

const clearMessages = async () => {
  if (!currentSessionId.value) return
  
  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？', '确认清空', {
      type: 'warning'
    })
    
    const response = await chatApi.clearSessionMessages(currentSessionId.value)
    
    if (response.data.success) {
      messages.value = []
      ElMessage.success('对话已清空')
    }
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空消息失败:', error)
      ElMessage.error('清空消息失败')
    }
  }
}

const onModelChange = () => {
  // 保存模型选择到本地存储
  saveSettings()
}

const updateSessionTitle = async (sessionId: string, title: string) => {
  try {
    await chatApi.updateSession(sessionId, { title })
    const session = sessions.value.find(s => s.session_id === sessionId)
    if (session) {
      session.title = title
    }
  } catch (error) {
    console.error('更新会话标题失败:', error)
  }
}

const saveSettings = () => {
  try {
    const settings = {
      temperature: temperature.value,
      maxTokens: maxTokens.value,
      streamEnabled: streamEnabled.value,
      selectedModelId: selectedModelId.value
    }
    localStorage.setItem('chat-settings', JSON.stringify(settings))
  } catch (error) {
    console.error('保存设置失败:', error)
  }
  showSettings.value = false
  ElMessage.success('设置已保存')
}

// 多模态功能函数
// 文件处理
const handleFileSelect = (file: any, fileList: any) => {
  const { raw } = file
  if (!raw) return

  // 文件大小限制 (10MB)
  if (raw.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }

  const fileId = Date.now() + Math.random()
  const fileInfo = {
    id: fileId,
    name: raw.name,
    size: raw.size,
    type: getFileType(raw.type || raw.name),
    file: raw,
    preview: null
  }

  // 如果是图片，生成预览
  if (fileInfo.type === 'image') {
    const reader = new FileReader()
    reader.onload = (e) => {
      fileInfo.preview = e.target?.result as string
    }
    reader.readAsDataURL(raw)
  }

  attachedFiles.value.push(fileInfo)
}

const getFileType = (mimeTypeOrName: string): string => {
  if (mimeTypeOrName.startsWith('image/')) return 'image'
  if (mimeTypeOrName.includes('.pdf') || mimeTypeOrName === 'application/pdf') return 'pdf'
  if (mimeTypeOrName.includes('.doc') || mimeTypeOrName.includes('.docx')) return 'document'
  if (mimeTypeOrName.includes('.txt') || mimeTypeOrName === 'text/plain') return 'text'
  if (mimeTypeOrName.includes('.md')) return 'markdown'
  return 'file'
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const removeFile = (index: number) => {
  attachedFiles.value.splice(index, 1)
}

// 拍照功能
const openCamera = () => {
  // 创建文件输入元素来调用摄像头
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.capture = 'environment' // 使用后置摄像头
  input.onchange = (e: any) => {
    const file = e.target.files[0]
    if (file) {
      handleFileSelect({ raw: file }, null)
    }
  }
  input.click()
}

// 语音输入功能
const toggleVoiceInput = async () => {
  if (!isRecording.value) {
    startVoiceRecording()
  } else {
    stopVoiceRecording()
  }
}

const startVoiceRecording = async () => {
  try {
    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      ElMessage.error('您的浏览器不支持语音录制功能')
      return
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    isRecording.value = true
    ElMessage.info('开始录音...')
    
    // 这里应该集成语音识别API，比如Web Speech API
    // 为了演示，我们简单模拟
    setTimeout(() => {
      if (isRecording.value) {
        stopVoiceRecording()
      }
    }, 5000) // 5秒后自动停止
    
  } catch (error) {
    console.error('无法访问麦克风:', error)
    ElMessage.error('无法访问麦克风，请检查权限设置')
  }
}

const stopVoiceRecording = () => {
  isRecording.value = false
  ElMessage.success('录音结束')
  // 这里应该调用语音转文字API
  // 模拟转换结果
  if (inputMessage.value) {
    inputMessage.value += ' '
  }
  inputMessage.value += '[语音转换：这是模拟的语音转文字结果]'
}

// AI绘画功能
const openDrawingDialog = () => {
  drawingDialogVisible.value = true
}

const generateImage = async () => {
  if (!drawingPrompt.value.trim()) {
    ElMessage.error('请输入绘画描述')
    return
  }

  const validation = aiPaintingUtils.validatePrompt(drawingPrompt.value)
  if (!validation.valid) {
    ElMessage.error(validation.message)
    return
  }

  isGeneratingImage.value = true
  
  try {
    // 构建绘画请求
    const paintingRequest = {
      prompt: drawingPrompt.value.trim(),
      style: drawingStyle.value,
      size: drawingSize.value,
      model_name: 'stable-diffusion',
      seed: aiPaintingUtils.generateRandomSeed(),
      ...aiPaintingUtils.getRecommendedSettings(drawingStyle.value)
    }

    // 调用AI绘画API
    const response = await aiPaintingApi.generateImage(paintingRequest)
    
    if (response.data.success) {
      const paintingResult = response.data.data
      
      // 添加生成的图片消息到聊天
      const imageMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `根据您的描述 "${drawingPrompt.value}" 生成的图片：`,
        created_at: new Date().toISOString(),
        metadata: {
          type: 'ai_painting',
          painting_id: paintingResult.id,
          prompt: paintingResult.prompt,
          style: paintingResult.style,
          size: paintingResult.size,
          image_url: paintingResult.image_url,
          thumbnail_url: paintingResult.thumbnail_url,
          generation_time: paintingResult.generation_time,
          cost: paintingResult.cost,
          seed: paintingResult.seed,
          steps: paintingResult.steps,
          cfg_scale: paintingResult.cfg_scale
        }
      }
      
      messages.value.push(imageMessage)
      
      drawingDialogVisible.value = false
      drawingPrompt.value = ''
      scrollToBottom()
      
      ElMessage.success(`图片生成成功！耗时 ${aiPaintingUtils.formatGenerationTime(paintingResult.generation_time || 0)}`)
    } else {
      throw new Error(response.data.message || '生成失败')
    }
    
  } catch (error) {
    console.error('生成图片失败:', error)
    ElMessage.error('生成图片失败')
  } finally {
    isGeneratingImage.value = false
  }
}

// 知识库功能
const loadKnowledgeBases = async () => {
  try {
    const response = await knowledgeApi.getKnowledgeBases({ page_size: 50 })
    if (response.data.success) {
      availableKnowledgeBases.value = response.data.data.knowledge_bases || []
    }
  } catch (error) {
    console.error('加载知识库列表失败:', error)
  }
}

const openKnowledgeBase = () => {
  knowledgeBaseVisible.value = true
}

// @符号触发知识库选择
const handleInputChange = (event: any) => {
  const inputEl = event.target
  const value = inputEl.value
  const cursorPos = inputEl.selectionStart
  
  // 检查是否输入了@符号
  if (value[cursorPos - 1] === '@') {
    const rect = inputEl.getBoundingClientRect()
    knowledgeSelectorPosition.value = {
      top: rect.bottom + window.scrollY,
      left: rect.left + window.scrollX
    }
    showKnowledgeSelector.value = true
    loadKnowledgeBases()
  } else {
    showKnowledgeSelector.value = false
  }
}

const selectKnowledgeBase = (kb: any) => {
  // 替换@符号为知识库名称
  const currentText = inputMessage.value
  const atIndex = currentText.lastIndexOf('@')
  if (atIndex !== -1) {
    inputMessage.value = currentText.substring(0, atIndex) + `@${kb.name} ` + currentText.substring(atIndex + 1)
  }
  selectedKnowledgeBase.value = kb
  showKnowledgeSelector.value = false
}

// 基于知识库的对话
const chatWithKnowledge = async (query: string, kbId: string) => {
  try {
    const response = await knowledgeApi.chatWithKnowledge({
      kb_id: kbId,
      query: query,
      model_id: selectedModelId.value,
      temperature: temperature.value
    })
    
    if (response.data.success) {
      return response.data.data
    }
  } catch (error) {
    console.error('知识库对话失败:', error)
    throw error
  }
}

// 快速模型切换
const quickModelChange = (modelId: string) => {
  selectedModelId.value = modelId
  ElMessage.success(`已切换到 ${availableModels.value.find(m => m.id === modelId)?.display_name}`)
  saveSettings()
}

// 清空输入
const clearInput = () => {
  inputMessage.value = ''
  attachedFiles.value = []
}

// 图片预览
const previewImage = (imageUrl: string) => {
  // 创建图片预览弹窗
  const img = new Image()
  img.src = imageUrl
  img.onload = () => {
    ElMessageBox.alert('', '图片预览', {
      dangerouslyUseHTMLString: true,
      message: `<div style="text-align: center;"><img src="${imageUrl}" style="max-width: 100%; max-height: 400px;" /></div>`,
      showConfirmButton: true,
      confirmButtonText: '关闭'
    })
  }
}

// 重新生成绘画
const regeneratePainting = async (metadata: any) => {
  if (!metadata.painting_id) {
    ElMessage.error('无法重新生成：缺少绘画ID')
    return
  }

  try {
    ElMessage.info('正在重新生成图片...')
    const response = await aiPaintingApi.regenerateImage(metadata.painting_id)
    
    if (response.data.success) {
      const newPainting = response.data.data
      
      // 添加新的绘画消息
      const imageMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `重新生成的图片：`,
        created_at: new Date().toISOString(),
        metadata: {
          type: 'ai_painting',
          painting_id: newPainting.id,
          prompt: newPainting.prompt,
          style: newPainting.style,
          size: newPainting.size,
          image_url: newPainting.image_url,
          thumbnail_url: newPainting.thumbnail_url,
          generation_time: newPainting.generation_time,
          cost: newPainting.cost,
          seed: newPainting.seed,
          steps: newPainting.steps,
          cfg_scale: newPainting.cfg_scale
        }
      }
      
      messages.value.push(imageMessage)
      scrollToBottom()
      
      ElMessage.success('图片重新生成成功！')
    }
  } catch (error) {
    console.error('重新生成失败:', error)
    ElMessage.error('重新生成失败')
  }
}

// 复制绘画提示词
const copyPaintingPrompt = async (prompt: string) => {
  try {
    await navigator.clipboard.writeText(prompt)
    ElMessage.success('提示词已复制到剪贴板')
  } catch (error) {
    // 如果剪贴板API不可用，使用传统方法
    const textArea = document.createElement('textarea')
    textArea.value = prompt
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('提示词已复制到剪贴板')
  }
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

        // 文件附件样式
        .message-files {
          margin-top: 12px;
          display: flex;
          flex-direction: column;
          gap: 8px;

          .message-file-item {
            .message-file-image {
              max-width: 200px;
              max-height: 200px;
              object-fit: cover;
              border-radius: 8px;
              cursor: pointer;
              transition: transform 0.2s;

              &:hover {
                transform: scale(1.02);
              }
            }

            .message-file-info {
              display: flex;
              align-items: center;
              gap: 8px;
              padding: 8px 12px;
              background: rgba(255, 255, 255, 0.1);
              border-radius: 6px;
              border: 1px solid rgba(255, 255, 255, 0.2);

              .file-icon {
                color: rgba(255, 255, 255, 0.8);
              }

              .file-details {
                display: flex;
                flex-direction: column;
                
                .file-name {
                  font-size: 13px;
                  color: rgba(255, 255, 255, 0.9);
                }

                .file-size {
                  font-size: 12px;
                  color: rgba(255, 255, 255, 0.7);
                }
              }
            }
          }
        }

        // AI生成图片样式
        .message-ai-painting {
          margin-top: 12px;

          .ai-generated-image {
            max-width: 350px;
            max-height: 350px;
            object-fit: cover;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

            &:hover {
              transform: scale(1.02);
              box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
            }
          }

          .painting-meta {
            margin-top: 12px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);

            .meta-row {
              display: flex;
              gap: 8px;
              margin-bottom: 8px;
              align-items: center;

              &:last-child {
                margin-bottom: 0;
              }

              .meta-info {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.8);
                margin-right: 12px;
              }
            }

            .painting-actions {
              display: flex;
              gap: 8px;
              margin-top: 8px;

              .el-button {
                padding: 4px 8px;
                height: auto;
                font-size: 12px;
              }
            }
          }
        }

        // 兼容旧版AI图片样式
        .message-ai-image {
          margin-top: 12px;

          .ai-generated-image {
            max-width: 300px;
            max-height: 300px;
            object-fit: cover;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s;

            &:hover {
              transform: scale(1.02);
            }
          }

          .image-meta {
            margin-top: 8px;
            display: flex;
            gap: 6px;
          }
        }

        // 助手消息中的绘画样式调整
        &.assistant {
          .message-ai-painting .painting-meta {
            background: rgba(0, 0, 0, 0.03);
            border: 1px solid rgba(0, 0, 0, 0.08);

            .meta-info {
              color: #666;
            }
          }
        }
      }

      // 助手消息中的文件样式调整
      &.assistant {
        .message-files .message-file-item .message-file-info {
          background: rgba(0, 0, 0, 0.05);
          border: 1px solid rgba(0, 0, 0, 0.1);

          .file-icon {
            color: #606266;
          }

          .file-details {
            .file-name {
              color: #303133;
            }

            .file-size {
              color: #909399;
            }
          }
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
      flex-direction: column;
      gap: 12px;

      // 文件预览区域
      .file-preview-area {
        .file-list {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e4e7ed;

          .file-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: white;
            border-radius: 6px;
            border: 1px solid #dcdfe6;
            position: relative;

            .file-preview-img {
              width: 40px;
              height: 40px;
              object-fit: cover;
              border-radius: 4px;
            }

            .file-icon {
              width: 40px;
              height: 40px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #f0f2f5;
              border-radius: 4px;
              color: #606266;
            }

            .file-info {
              display: flex;
              flex-direction: column;
              
              .file-name {
                font-size: 13px;
                color: #303133;
                max-width: 120px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }

              .file-size {
                font-size: 12px;
                color: #909399;
              }
            }

            .file-remove {
              position: absolute;
              top: -6px;
              right: -6px;
              width: 18px;
              height: 18px;
              border-radius: 50%;
              padding: 0;
              min-height: unset;
            }
          }
        }
      }

      // 主输入区域
      .main-input-area {
        display: flex;
        gap: 12px;
        align-items: flex-end;

        .input-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 8px;

          .message-input {
            .el-textarea__inner {
              border-radius: 12px;
              border: 1px solid #dcdfe6;
              resize: none;
              
              &:focus {
                border-color: #409eff;
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
              }
            }
          }

          // 功能按钮栏
          .function-buttons {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;

            .el-button {
              padding: 6px;
              min-height: unset;
              border: none;
              color: #606266;
              
              &:hover {
                background: #f5f7fa;
                color: #409eff;
              }

              &.voice-recording {
                color: #f56c6c;
                animation: pulse 1s infinite;
              }
            }

            .el-dropdown {
              .el-button {
                border: none;
              }
            }
          }
        }

        .input-actions {
          display: flex;
          flex-direction: column;
          gap: 8px;

          .el-button {
            min-width: 80px;
          }
        }
      }
    }
  }
}

// 知识库选择器样式
.knowledge-selector {
  .selector-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    border: 1px solid #e4e7ed;
    max-width: 300px;
    max-height: 200px;
    overflow: hidden;

    .selector-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid #e4e7ed;
      background: #f8f9fa;
      
      span {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
    }

    .selector-list {
      max-height: 150px;
      overflow-y: auto;

      .kb-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        cursor: pointer;
        border-bottom: 1px solid #f0f2f5;

        &:hover {
          background: #f5f7fa;
        }

        &:last-child {
          border-bottom: none;
        }

        .kb-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          flex: 1;

          .kb-name {
            font-size: 14px;
            color: #303133;
            font-weight: 500;
          }

          .kb-desc {
            font-size: 12px;
            color: #909399;
            max-width: 180px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }

        .kb-meta {
          flex-shrink: 0;
        }
      }

      .empty-kb {
        padding: 20px;
        text-align: center;
        color: #909399;
        font-size: 14px;
      }
    }
  }
}

// 动画效果
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
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

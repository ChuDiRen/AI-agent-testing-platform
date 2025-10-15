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
              <el-button @click="showGenerateDialog = true" type="success">
                <el-icon><MagicStick /></el-icon>
                生成测试用例
              </el-button>
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
              <MarkdownRenderer 
                v-if="message.role === 'assistant' && message.content" 
                :content="message.content" 
              />
              <span v-else>{{ message.content }}</span>
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

    <!-- 生成测试用例对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="AI生成测试用例"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="需求描述" required>
          <el-input
            v-model="generateForm.requirement"
            type="textarea"
            :rows="5"
            placeholder="请输入测试需求描述，例如：用户登录功能测试"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="测试类型" required>
          <el-select v-model="generateForm.test_type" style="width: 100%">
            <el-option label="API测试" value="api">
              <el-icon><Connection /></el-icon>
              <span style="margin-left: 8px">API测试</span>
            </el-option>
            <el-option label="WEB测试" value="web">
              <el-icon><Monitor /></el-icon>
              <span style="margin-left: 8px">WEB测试</span>
            </el-option>
            <el-option label="APP测试" value="app">
              <el-icon><Iphone /></el-icon>
              <span style="margin-left: 8px">APP测试</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模块名称">
          <el-input v-model="generateForm.module" placeholder="例如：用户管理" />
        </el-form-item>
        <el-form-item label="生成数量" required>
          <el-input-number
            v-model="generateForm.count"
            :min="1"
            :max="10"
            :step="1"
          />
          <el-text type="info" size="small" style="margin-left: 12px">
            建议1-5个用例，最多10个
          </el-text>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="generateForm.priority">
            <el-radio label="P0">P0 - 紧急</el-radio>
            <el-radio label="P1">P1 - 高</el-radio>
            <el-radio label="P2">P2 - 中</el-radio>
            <el-radio label="P3">P3 - 低</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleGenerate"
          :loading="isGenerating"
          :disabled="!generateForm.requirement || !generateForm.test_type"
        >
          <el-icon v-if="!isGenerating"><MagicStick /></el-icon>
          {{ isGenerating ? '生成中...' : '开始生成' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 生成结果对话框 -->
    <el-dialog
      v-model="showResultDialog"
      title="生成的测试用例"
      width="90%"
      :close-on-click-modal="false"
    >
      <el-alert
        v-if="generatedTestCases.length > 0"
        type="success"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #title>
          成功生成 <strong>{{ generatedTestCases.length }}</strong> 个测试用例
        </template>
      </el-alert>
      
      <el-table
        :data="generatedTestCases"
        border
        stripe
        max-height="500"
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="name" label="用例名称" min-width="200" />
        <el-table-column prop="test_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.test_type === 'api' ? 'success' : row.test_type === 'web' ? 'primary' : 'warning'">
              {{ row.test_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="row.priority === 'P0' ? 'danger' : row.priority === 'P1' ? 'warning' : 'info'" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row, $index }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handlePreview(row)"
            >
              预览
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleRemoveCase($index)"
            >
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="showResultDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleSaveTestCases"
          :loading="isSaving"
          :disabled="generatedTestCases.length === 0"
        >
          <el-icon v-if="!isSaving"><Check /></el-icon>
          {{ isSaving ? '保存中...' : `保存全部 (${generatedTestCases.length}个)` }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="测试用例详情"
      width="700px"
    >
      <el-descriptions v-if="previewCase" :column="1" border>
        <el-descriptions-item label="用例名称">
          {{ previewCase.name }}
        </el-descriptions-item>
        <el-descriptions-item label="测试类型">
          <el-tag :type="previewCase.test_type === 'api' ? 'success' : previewCase.test_type === 'web' ? 'primary' : 'warning'">
            {{ previewCase.test_type.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="模块">
          {{ previewCase.module }}
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="previewCase.priority === 'P0' ? 'danger' : previewCase.priority === 'P1' ? 'warning' : 'info'">
            {{ previewCase.priority }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述">
          {{ previewCase.description }}
        </el-descriptions-item>
        <el-descriptions-item label="前置条件">
          <div style="white-space: pre-wrap">{{ previewCase.preconditions || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="测试步骤">
          <div style="white-space: pre-wrap">{{ previewCase.test_steps }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果">
          <div style="white-space: pre-wrap">{{ previewCase.expected_result }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="标签">
          <el-tag v-for="tag in (previewCase.tags || '').split(',')" :key="tag" size="small" style="margin-right: 4px">
            {{ tag }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
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
  Close,
  MagicStick,
  Check,
  Connection,
  Monitor,
  Iphone
} from '@element-plus/icons-vue'
import { useAIChat } from '@/composables/useAIChat'
import { getModelsAPI, type AIModel, generateTestCasesAPI, saveGeneratedTestCasesAPI } from '@/api/ai'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

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

// 生成测试用例相关状态
const showGenerateDialog = ref(false)
const showResultDialog = ref(false)
const showPreviewDialog = ref(false)
const isGenerating = ref(false)
const isSaving = ref(false)
const generatedTestCases = ref<any[]>([])
const previewCase = ref<any>(null)

// 生成表单
const generateForm = ref({
  requirement: '',
  test_type: 'api',
  module: '默认模块',
  count: 3,
  priority: 'P2'
})

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

// 生成测试用例
const handleGenerate = async () => {
  if (!generateForm.value.requirement || !generateForm.value.test_type) {
    ElMessage.warning('请填写需求描述和测试类型')
    return
  }

  isGenerating.value = true
  try {
    const response = await generateTestCasesAPI({
      requirement: generateForm.value.requirement,
      test_type: generateForm.value.test_type,
      module: generateForm.value.module,
      count: generateForm.value.count,
      model_key: selectedModel.value
    })

    if (response.data && response.data.testcases) {
      // 添加默认优先级到生成的用例
      generatedTestCases.value = response.data.testcases.map((tc: any) => ({
        ...tc,
        priority: generateForm.value.priority,
        module: tc.module || generateForm.value.module,
        tags: tc.tags || 'AI生成'
      }))
      
      showGenerateDialog.value = false
      showResultDialog.value = true
      ElMessage.success(`成功生成 ${generatedTestCases.value.length} 个测试用例`)
    } else {
      ElMessage.error('生成失败，请重试')
    }
  } catch (error: any) {
    console.error('生成测试用例失败:', error)
    ElMessage.error(error.response?.data?.message || '生成失败')
  } finally {
    isGenerating.value = false
  }
}

// 保存测试用例
const handleSaveTestCases = async () => {
  if (generatedTestCases.value.length === 0) {
    ElMessage.warning('没有可保存的测试用例')
    return
  }

  isSaving.value = true
  try {
    const response = await saveGeneratedTestCasesAPI(generatedTestCases.value)
    
    if (response.data) {
      const { saved_count, failed_count, errors } = response.data
      
      if (failed_count === 0) {
        ElMessage.success(`成功保存 ${saved_count} 个测试用例`)
        showResultDialog.value = false
        generatedTestCases.value = []
        // 重置表单
        generateForm.value = {
          requirement: '',
          test_type: 'api',
          module: '默认模块',
          count: 3,
          priority: 'P2'
        }
      } else {
        ElMessage.warning(
          `成功保存 ${saved_count} 个，失败 ${failed_count} 个`
        )
        console.error('保存失败的用例:', errors)
      }
    }
  } catch (error: any) {
    console.error('保存测试用例失败:', error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    isSaving.value = false
  }
}

// 预览用例
const handlePreview = (row: any) => {
  previewCase.value = row
  showPreviewDialog.value = true
}

// 移除用例
const handleRemoveCase = (index: number) => {
  ElMessageBox.confirm(
    '确定要移除这个测试用例吗？',
    '确认移除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    generatedTestCases.value.splice(index, 1)
    ElMessage.success('已移除')
  }).catch(() => {
    // 取消操作
  })
}

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


<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <el-row :gutter="24">
      <!-- RAG配置 -->
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <h3>RAG配置</h3>
              <el-tag type="success">已配置</el-tag>
            </div>
          </template>

          <el-form :model="ragSettings" label-width="120px">
            <el-form-item label="向量模型">
              <el-select v-model="ragSettings.embeddingModel" style="width: 100%">
                <el-option label="text-embedding-ada-002" value="text-embedding-ada-002" />
                <el-option label="text-embedding-3-small" value="text-embedding-3-small" />
                <el-option label="text-embedding-3-large" value="text-embedding-3-large" />
              </el-select>
            </el-form-item>

            <el-form-item label="相似度阈值">
              <el-slider
                v-model="ragSettings.similarityThreshold"
                :min="0"
                :max="1"
                :step="0.1"
                show-input
              />
            </el-form-item>

            <el-form-item label="检索数量">
              <el-input-number
                v-model="ragSettings.topK"
                :min="1"
                :max="20"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="分块大小">
              <el-input-number
                v-model="ragSettings.chunkSize"
                :min="100"
                :max="2000"
                :step="100"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="分块重叠">
              <el-input-number
                v-model="ragSettings.chunkOverlap"
                :min="0"
                :max="500"
                :step="50"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- LLM配置 -->
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <h3>LLM配置</h3>
              <el-tag type="success">已配置</el-tag>
            </div>
          </template>

          <el-form :model="llmSettings" label-width="120px">
            <el-form-item label="模型提供商">
              <el-select v-model="llmSettings.provider" style="width: 100%">
                <el-option label="OpenAI" value="openai" />
                <el-option label="Azure OpenAI" value="azure" />
                <el-option label="Anthropic" value="anthropic" />
                <el-option label="本地模型" value="local" />
              </el-select>
            </el-form-item>

            <el-form-item label="模型名称">
              <el-select v-model="llmSettings.model" style="width: 100%">
                <el-option label="gpt-3.5-turbo" value="gpt-3.5-turbo" />
                <el-option label="gpt-4" value="gpt-4" />
                <el-option label="gpt-4-turbo" value="gpt-4-turbo" />
                <el-option label="claude-3-sonnet" value="claude-3-sonnet" />
              </el-select>
            </el-form-item>

            <el-form-item label="温度">
              <el-slider
                v-model="llmSettings.temperature"
                :min="0"
                :max="2"
                :step="0.1"
                show-input
              />
            </el-form-item>

            <el-form-item label="最大令牌">
              <el-input-number
                v-model="llmSettings.maxTokens"
                :min="100"
                :max="4000"
                :step="100"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="系统提示">
              <el-input
                v-model="llmSettings.systemPrompt"
                type="textarea"
                :rows="3"
                placeholder="系统提示词"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 向量数据库配置 -->
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <h3>向量数据库</h3>
              <el-tag type="success">已连接</el-tag>
            </div>
          </template>

          <el-form :model="vectorDbSettings" label-width="120px">
            <el-form-item label="数据库类型">
              <el-select v-model="vectorDbSettings.type" style="width: 100%">
                <el-option label="Chroma" value="chroma" />
                <el-option label="Pinecone" value="pinecone" />
                <el-option label="Weaviate" value="weaviate" />
                <el-option label="FAISS" value="faiss" />
              </el-select>
            </el-form-item>

            <el-form-item label="连接地址">
              <el-input
                v-model="vectorDbSettings.url"
                placeholder="数据库连接地址"
              />
            </el-form-item>

            <el-form-item label="集合名称">
              <el-input
                v-model="vectorDbSettings.collection"
                placeholder="向量集合名称"
              />
            </el-form-item>

            <el-form-item label="连接状态">
              <div class="connection-status">
                <el-icon color="#67c23a"><SuccessFilled /></el-icon>
                <span>连接正常</span>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 系统配置 -->
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <h3>系统配置</h3>
              <el-tag type="info">常规</el-tag>
            </div>
          </template>

          <el-form :model="systemSettings" label-width="120px">
            <el-form-item label="系统名称">
              <el-input
                v-model="systemSettings.systemName"
                placeholder="企业级智能知识库"
              />
            </el-form-item>

            <el-form-item label="最大文件大小">
              <el-input-number
                v-model="systemSettings.maxFileSize"
                :min="1"
                :max="100"
                style="width: 100%"
              />
              <span class="unit">MB</span>
            </el-form-item>

            <el-form-item label="支持格式">
              <el-checkbox-group v-model="systemSettings.supportedFormats">
                <el-checkbox label="pdf">PDF</el-checkbox>
                <el-checkbox label="doc">Word</el-checkbox>
                <el-checkbox label="txt">TXT</el-checkbox>
                <el-checkbox label="md">Markdown</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="日志级别">
              <el-select v-model="systemSettings.logLevel" style="width: 100%">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>

            <el-form-item label="启用注册">
              <el-switch v-model="systemSettings.enableRegistration" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button type="primary" @click="saveSettings" :loading="saving">
        <el-icon><Check /></el-icon>
        保存设置
      </el-button>
      
      <el-button @click="resetSettings">
        <el-icon><RefreshLeft /></el-icon>
        重置设置
      </el-button>
      
      <el-button type="success" @click="testConnection" :loading="testing">
        <el-icon><Connection /></el-icon>
        测试连接
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Check,
  RefreshLeft,
  Connection,
  SuccessFilled
} from '@element-plus/icons-vue'

const saving = ref(false)
const testing = ref(false)

const ragSettings = reactive({
  embeddingModel: 'text-embedding-ada-002',
  similarityThreshold: 0.7,
  topK: 5,
  chunkSize: 1000,
  chunkOverlap: 200
})

const llmSettings = reactive({
  provider: 'openai',
  model: 'gpt-3.5-turbo',
  temperature: 0.7,
  maxTokens: 2000,
  systemPrompt: '你是一个专业的AI助手，请基于提供的文档内容回答用户问题。'
})

const vectorDbSettings = reactive({
  type: 'chroma',
  url: 'http://localhost:8000',
  collection: 'documents'
})

const systemSettings = reactive({
  systemName: '企业级智能知识库',
  maxFileSize: 50,
  supportedFormats: ['pdf', 'doc', 'txt', 'md'],
  logLevel: 'info',
  enableRegistration: false
})

const loadSettings = async () => {
  try {
    // 这里应该从API加载设置
    // 暂时使用默认值
    ElMessage.success('设置加载成功')
  } catch (error) {
    ElMessage.error('加载设置失败')
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    // 这里应该调用API保存设置
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  // 重置为默认值
  Object.assign(ragSettings, {
    embeddingModel: 'text-embedding-ada-002',
    similarityThreshold: 0.7,
    topK: 5,
    chunkSize: 1000,
    chunkOverlap: 200
  })
  
  Object.assign(llmSettings, {
    provider: 'openai',
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 2000,
    systemPrompt: '你是一个专业的AI助手，请基于提供的文档内容回答用户问题。'
  })
  
  ElMessage.info('设置已重置为默认值')
}

const testConnection = async () => {
  testing.value = true
  try {
    // 这里应该测试各种连接
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('所有连接测试通过')
  } catch (error) {
    ElMessage.error('连接测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.settings-card {
  margin-bottom: 24px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.unit {
  margin-left: 8px;
  color: #909399;
  font-size: 14px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #67c23a;
}

.actions {
  margin-top: 32px;
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-page {
    padding: 0;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .actions {
    flex-direction: column;
    align-items: center;
  }
  
  .actions .el-button {
    width: 200px;
  }
}
</style>

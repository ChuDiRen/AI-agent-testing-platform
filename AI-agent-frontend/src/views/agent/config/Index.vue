<!-- AI代理配置页面 -->
<template>
  <div class="agent-config">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>
              <router-link to="/agent">代理管理</router-link>
            </el-breadcrumb-item>
            <el-breadcrumb-item>代理配置</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="title-section">
          <h1>{{ agentInfo?.name || '代理配置' }}</h1>
          <div class="agent-meta">
            <el-tag :type="agentUtils.formatStatus(agentInfo?.status || '').type">
              {{ agentUtils.formatStatus(agentInfo?.status || '').text }}
            </el-tag>
            <span class="version">v{{ agentInfo?.version }}</span>
            <span class="type">{{ agentUtils.formatType(agentInfo?.type || '').text }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="handleTest" :loading="testing">
          <el-icon><Connection /></el-icon>
          测试连接
        </el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
    </div>

    <!-- 配置内容 -->
    <div class="config-content" v-loading="loading">
      <el-row :gutter="24">
        <!-- 左侧配置表单 -->
        <el-col :span="16">
          <el-card class="config-form-card">
            <template #header>
              <div class="card-header">
                <h3>基础配置</h3>
                <el-button size="small" @click="showConfigTemplates = true">
                  <el-icon><Document /></el-icon>
                  配置模板
                </el-button>
              </div>
            </template>
            
            <el-form
              ref="configFormRef"
              :model="configForm"
              :rules="configFormRules"
              label-width="120px"
              size="default"
            >
              <!-- 基础信息 -->
              <el-form-item label="代理名称" prop="name">
                <el-input v-model="configForm.name" placeholder="请输入代理名称" />
              </el-form-item>
              
              <el-form-item label="代理描述">
                <el-input
                  v-model="configForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入代理描述"
                />
              </el-form-item>
              
              <el-form-item label="版本号" prop="version">
                <el-input v-model="configForm.version" placeholder="例如: 1.0.0" />
              </el-form-item>
              
              <!-- 模型配置 -->
              <el-divider>模型配置</el-divider>
              
            <el-form-item label="AI模型" prop="large_model_id">
                <el-select
                  v-model="configForm.config.large_model_id"
                  placeholder="请选择AI模型"
                  filterable
                  @change="handleModelChange"
                >
                  <el-option
                    v-for="model in modelList"
                    :key="model.id"
                    :label="model.display_name || model.name"
                    :value="model.id"
                  >
                    <div class="model-option">
                      <span class="model-name">{{ model.display_name || model.name }}</span>
                      <span class="model-provider">{{ model.provider }}</span>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="温度参数">
                <el-slider
                  v-model="configForm.config.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  show-input
                  :show-input-controls="false"
                />
                <div class="param-tip">
                  <el-text type="info" size="small">
                    控制生成文本的随机性，0-2之间，值越高越随机
                  </el-text>
                </div>
              </el-form-item>
              
              <el-form-item label="最大Token数">
                <el-input-number
                  v-model="configForm.config.max_tokens"
                  :min="1"
                  :max="32000"
                  :step="100"
                  placeholder="最大生成Token数"
                />
              </el-form-item>
              
              <!-- 系统提示词 -->
              <el-form-item label="系统提示词">
                <el-input
                  v-model="configForm.config.system_prompt"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入系统提示词，定义代理的角色和行为"
                />
                <div class="param-tip">
                  <el-button size="small" text @click="showPromptTemplates = true">
                    <el-icon><MagicStick /></el-icon>
                    使用模板
                  </el-button>
                </div>
              </el-form-item>
              
              <!-- 高级配置 -->
              <el-divider>高级配置</el-divider>
              
              <el-form-item label="流式输出">
                <el-switch
                  v-model="configForm.config.stream"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              
              <el-form-item label="超时时间(秒)">
                <el-input-number
                  v-model="configForm.config.timeout"
                  :min="1"
                  :max="300"
                  placeholder="请求超时时间"
                />
              </el-form-item>
              
              <el-form-item label="重试次数">
                <el-input-number
                  v-model="configForm.config.retry_count"
                  :min="0"
                  :max="5"
                  placeholder="失败重试次数"
                />
              </el-form-item>
              
              <!-- 自定义配置 -->
              <el-form-item label="自定义配置">
                <div class="custom-config">
                  <el-button size="small" @click="addCustomConfig">
                    <el-icon><Plus /></el-icon>
                    添加配置项
                  </el-button>
                  
                  <div v-for="(item, index) in customConfigs" :key="index" class="config-item">
                    <el-input
                      v-model="item.key"
                      placeholder="配置键"
                      style="width: 200px"
                    />
                    <el-input
                      v-model="item.value"
                      placeholder="配置值"
                      style="width: 300px; margin-left: 8px"
                    />
                    <el-button
                      size="small"
                      type="danger"
                      @click="removeCustomConfig(index)"
                      style="margin-left: 8px"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <!-- 右侧信息面板 -->
        <el-col :span="8">
          <!-- 代理状态 -->
          <el-card class="status-card">
            <template #header>
              <h3>代理状态</h3>
            </template>
            
            <div class="status-content">
              <div class="status-item">
                <span class="label">当前状态:</span>
                <el-tag :type="agentUtils.formatStatus(agentInfo?.status || '').type">
                  {{ agentUtils.formatStatus(agentInfo?.status || '').text }}
                </el-tag>
              </div>
              
              <div class="status-item">
                <span class="label">运行次数:</span>
                <span class="value">{{ agentInfo?.run_count || 0 }} 次</span>
              </div>
              
              <div class="status-item">
                <span class="label">成功率:</span>
                <span class="value">{{ agentInfo?.success_rate || 0 }}%</span>
              </div>
              
              <div class="status-item">
                <span class="label">创建时间:</span>
                <span class="value">{{ formatDateTime(agentInfo?.created_at) }}</span>
              </div>
              
              <div class="status-item">
                <span class="label">更新时间:</span>
                <span class="value">{{ formatDateTime(agentInfo?.updated_at) }}</span>
              </div>
            </div>
            
            <div class="status-actions">
              <el-button
                v-if="agentInfo?.status === 'active'"
                type="success"
                @click="handleStart"
                :loading="starting"
              >
                <el-icon><VideoPlay /></el-icon>
                启动代理
              </el-button>
              
              <el-button
                v-if="agentInfo?.status === 'running'"
                type="warning"
                @click="handleStop"
                :loading="stopping"
              >
                <el-icon><VideoPause /></el-icon>
                停止代理
              </el-button>
              
              <el-button
                v-if="agentInfo?.status === 'inactive'"
                type="primary"
                @click="handleActivate"
                :loading="activating"
              >
                <el-icon><CircleCheck /></el-icon>
                激活代理
              </el-button>
            </div>
          </el-card>
          
          <!-- 性能指标 -->
          <el-card class="metrics-card">
            <template #header>
              <h3>性能指标</h3>
            </template>
            
            <div class="metrics-content" v-loading="metricsLoading">
              <div class="metric-item">
                <div class="metric-label">平均响应时间</div>
                <div class="metric-value">{{ metrics.avg_response_time || 0 }}ms</div>
              </div>
              
              <div class="metric-item">
                <div class="metric-label">总成本</div>
                <div class="metric-value">{{ agentUtils.formatCost(metrics.cost_stats?.total_cost || 0) }}</div>
              </div>
              
              <div class="metric-item">
                <div class="metric-label">Token使用量</div>
                <div class="metric-value">{{ (metrics.cost_stats?.total_tokens || 0).toLocaleString() }}</div>
              </div>
              
              <div class="metric-item">
                <div class="metric-label">错误次数</div>
                <div class="metric-value">{{ metrics.error_count || 0 }}</div>
              </div>
            </div>
          </el-card>
          
          <!-- 最近运行日志 -->
          <el-card class="logs-card">
            <template #header>
              <div class="card-header">
                <h3>最近运行</h3>
                <el-button size="small" @click="viewAllLogs">
                  查看全部
                </el-button>
              </div>
            </template>
            
            <div class="logs-content" v-loading="logsLoading">
              <div v-if="recentLogs.length === 0" class="empty-logs">
                <el-empty description="暂无运行记录" :image-size="80" />
              </div>
              
              <div v-else class="log-list">
                <div
                  v-for="log in recentLogs"
                  :key="log.id"
                  class="log-item"
                  @click="viewLogDetail(log)"
                >
                  <div class="log-header">
                    <el-tag :type="getLogStatusType(log.status)" size="small">
                      {{ getLogStatusText(log.status) }}
                    </el-tag>
                    <span class="log-time">{{ formatDateTime(log.start_time) }}</span>
                  </div>
                  
                  <div class="log-details">
                    <div v-if="log.execution_time" class="log-detail">
                      <span class="detail-label">耗时:</span>
                      <span class="detail-value">{{ log.execution_time }}ms</span>
                    </div>
                    
                    <div v-if="log.tokens_used" class="log-detail">
                      <span class="detail-label">Token:</span>
                      <span class="detail-value">{{ log.tokens_used }}</span>
                    </div>
                    
                    <div v-if="log.cost" class="log-detail">
                      <span class="detail-label">成本:</span>
                      <span class="detail-value">{{ agentUtils.formatCost(log.cost) }}</span>
                    </div>
                  </div>
                  
                  <div v-if="log.error_message" class="log-error">
                    <el-text type="danger" size="small">{{ log.error_message }}</el-text>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 配置模板对话框 -->
    <el-dialog v-model="showConfigTemplates" title="配置模板" width="800px">
      <div class="template-grid">
        <div
          v-for="template in configTemplates"
          :key="template.id"
          class="template-card"
          @click="applyConfigTemplate(template)"
        >
          <div class="template-header">
            <h4>{{ template.name }}</h4>
            <el-tag :type="template.type">{{ template.category }}</el-tag>
          </div>
          <p class="template-description">{{ template.description }}</p>
        </div>
      </div>
    </el-dialog>
    
    <!-- 提示词模板对话框 -->
    <el-dialog v-model="showPromptTemplates" title="提示词模板" width="800px">
      <div class="prompt-templates">
        <el-tabs v-model="activePromptTab">
          <el-tab-pane label="聊天代理" name="chat">
            <div class="prompt-list">
              <div
                v-for="prompt in chatPrompts"
                :key="prompt.id"
                class="prompt-item"
                @click="applyPromptTemplate(prompt.content)"
              >
                <h5>{{ prompt.name }}</h5>
                <p>{{ prompt.description }}</p>
                <pre class="prompt-preview">{{ prompt.content }}</pre>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="任务代理" name="task">
            <div class="prompt-list">
              <div
                v-for="prompt in taskPrompts"
                :key="prompt.id"
                class="prompt-item"
                @click="applyPromptTemplate(prompt.content)"
              >
                <h5>{{ prompt.name }}</h5>
                <p>{{ prompt.description }}</p>
                <pre class="prompt-preview">{{ prompt.content }}</pre>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="分析代理" name="analysis">
            <div class="prompt-list">
              <div
                v-for="prompt in analysisPrompts"
                :key="prompt.id"
                class="prompt-item"
                @click="applyPromptTemplate(prompt.content)"
              >
                <h5>{{ prompt.name }}</h5>
                <p>{{ prompt.description }}</p>
                <pre class="prompt-preview">{{ prompt.content }}</pre>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import {
  Connection,
  Check,
  Document,
  MagicStick,
  Plus,
  Delete,
  VideoPlay,
  VideoPause,
  CircleCheck
} from '@element-plus/icons-vue'
import { agentApi, agentUtils } from '@/api/modules/agent'
import { modelApi } from '@/api/modules/model'
import { formatDateTime } from '@/utils/dateFormat'
import type { AgentInfo, AgentRunLog } from '@/api/modules/agent'
import type { ModelInfo } from '@/api/modules/model'

const route = useRoute()
const router = useRouter()

// 模式检测：创建模式或编辑模式
const isCreateMode = computed(() => route.name === 'AgentCreate')
const agentId = computed(() => isCreateMode.value ? null : Number(route.params.id))

// 响应式数据
const loading = ref(true)
const saving = ref(false)
const testing = ref(false)
const starting = ref(false)
const stopping = ref(false)
const activating = ref(false)
const metricsLoading = ref(false)
const logsLoading = ref(false)

const agentInfo = ref<AgentInfo | null>(null)
const modelList = ref<ModelInfo[]>([])
const configFormRef = ref<FormInstance>()

const showConfigTemplates = ref(false)
const showPromptTemplates = ref(false)
const activePromptTab = ref('chat')

// 表单数据
const configForm = reactive({
  name: '',
  description: '',
  version: '',
  config: {
    large_model_id: null,
    temperature: 0.7,
    max_tokens: 2000,
    system_prompt: '',
    stream: true,
    timeout: 30,
    retry_count: 3
  }
})

// 自定义配置
const customConfigs = ref<Array<{ key: string; value: string }>>([])

// 表单验证规则
const configFormRules = {
  name: [
    { required: true, message: '请输入代理名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' }
  ]
}

// 性能指标
const metrics = ref({
  avg_response_time: 0,
  success_rate: 0,
  total_runs: 0,
  error_count: 0,
  cost_stats: {
    total_cost: 0,
    avg_cost: 0,
    total_tokens: 0
  }
})

// 最近运行日志
const recentLogs = ref<AgentRunLog[]>([])

// 配置模板
const configTemplates = ref([
  {
    id: 1,
    name: '基础聊天代理',
    category: '聊天',
    type: 'primary',
    description: '适用于一般对话场景的基础配置',
    config: {
      temperature: 0.7,
      max_tokens: 2000,
      stream: true,
      timeout: 30,
      retry_count: 3,
      system_prompt: '你是一个有用的AI助手，请友好、准确地回答用户的问题。'
    }
  },
  {
    id: 2,
    name: '客服代理',
    category: '服务',
    type: 'success',
    description: '专门用于客户服务的配置，更加礼貌和专业',
    config: {
      temperature: 0.5,
      max_tokens: 1500,
      stream: true,
      timeout: 25,
      retry_count: 2,
      system_prompt: '你是一个专业的客服代表，请以礼貌、耐心、专业的态度为客户提供帮助。'
    }
  },
  {
    id: 3,
    name: '代码助手',
    category: '开发',
    type: 'warning',
    description: '专门用于编程相关任务的配置',
    config: {
      temperature: 0.3,
      max_tokens: 4000,
      stream: true,
      timeout: 45,
      retry_count: 3,
      system_prompt: '你是一个专业的编程助手，请提供准确的代码建议和解决方案。'
    }
  }
])

// 提示词模板
const chatPrompts = ref([
  {
    id: 1,
    name: '通用助手',
    description: '适用于一般对话的通用提示词',
    content: '你是一个有用的AI助手，请友好、准确地回答用户的问题。'
  },
  {
    id: 2,
    name: '专业顾问',
    description: '提供专业建议的提示词',
    content: '你是一个经验丰富的专业顾问，请根据用户的问题提供深入、专业的建议和分析。'
  }
])

const taskPrompts = ref([
  {
    id: 1,
    name: '任务规划师',
    description: '帮助用户规划和分解任务',
    content: '你是一个专业的任务规划师，请帮助用户将复杂任务分解为可执行的步骤。'
  }
])

const analysisPrompts = ref([
  {
    id: 1,
    name: '数据分析师',
    description: '专门用于数据分析的提示词',
    content: '你是一个专业的数据分析师，请对用户提供的数据进行深入分析并提供洞察。'
  }
])

// 计算属性 - agentId已在上面定义

// 生命周期
onMounted(() => {
  loadAgentInfo()
  loadModelList()
  loadMetrics()
  loadRecentLogs()
})

// 监听代理ID变化
watch(() => route.params.id, () => {
  if (route.params.id) {
    loadAgentInfo()
    loadMetrics()
    loadRecentLogs()
  }
})

// 方法定义
const loadAgentInfo = async () => {
  if (!agentId.value) return
  
  loading.value = true
  try {
    const response = await agentApi.getAgentDetail(agentId.value)
    if (response.data.success) {
      agentInfo.value = response.data.data
      
      // 填充表单数据
      Object.assign(configForm, {
        name: agentInfo.value.name,
        description: agentInfo.value.description,
        version: agentInfo.value.version,
        config: {
          ...configForm.config,
          ...agentInfo.value.config
        }
      })
      
      // 解析自定义配置
      parseCustomConfigs(agentInfo.value.config || {})
    }
  } catch (error) {
    console.error('加载代理信息失败:', error)
    ElMessage.error('加载代理信息失败')
  } finally {
    loading.value = false
  }
}

const loadModelList = async () => {
  try {
    const response = await modelApi.getModelList()
    if (response.data.success) {
      modelList.value = response.data.data.models || []
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
  }
}

const loadMetrics = async () => {
  if (!agentId.value) return
  
  metricsLoading.value = true
  try {
    const response = await agentApi.getAgentMetrics(agentId.value)
    if (response.data.success) {
      metrics.value = response.data.data
    }
  } catch (error) {
    console.error('加载性能指标失败:', error)
  } finally {
    metricsLoading.value = false
  }
}

const loadRecentLogs = async () => {
  if (!agentId.value) return
  
  logsLoading.value = true
  try {
    const response = await agentApi.getAgentRunLogs(agentId.value, {
      page: 1,
      page_size: 5
    })
    if (response.data.success) {
      recentLogs.value = response.data.data.logs || []
    }
  } catch (error) {
    console.error('加载运行日志失败:', error)
  } finally {
    logsLoading.value = false
  }
}

const parseCustomConfigs = (config: Record<string, any>) => {
  const standardKeys = ['large_model_id', 'temperature', 'max_tokens', 'system_prompt', 'stream', 'timeout', 'retry_count']
  const custom = Object.entries(config)
    .filter(([key]) => !standardKeys.includes(key))
    .map(([key, value]) => ({ key, value: String(value) }))
  
  customConfigs.value = custom
}

const buildFullConfig = () => {
  const fullConfig = { ...configForm.config }
  
  // 添加自定义配置
  customConfigs.value.forEach(item => {
    if (item.key && item.value) {
      fullConfig[item.key] = item.value
    }
  })
  
  return fullConfig
}

const handleModelChange = () => {
  // 模型变化时可以做一些配置调整
}

const addCustomConfig = () => {
  customConfigs.value.push({ key: '', value: '' })
}

const removeCustomConfig = (index: number) => {
  customConfigs.value.splice(index, 1)
}

const applyConfigTemplate = (template: any) => {
  Object.assign(configForm.config, template.config)
  showConfigTemplates.value = false
  ElMessage.success('配置模板应用成功')
}

const applyPromptTemplate = (content: string) => {
  configForm.config.system_prompt = content
  showPromptTemplates.value = false
  ElMessage.success('提示词模板应用成功')
}

const handleTest = async () => {
  if (!agentId.value) return
  
  testing.value = true
  try {
    const response = await agentApi.testAgentConnection(agentId.value, {
      message: '测试连接'
    })
    
    if (response.data.success) {
      ElMessage.success(`连接测试成功，响应时间: ${response.data.data.response_time}ms`)
    } else {
      ElMessage.error(`连接测试失败: ${response.data.data.error_message}`)
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('测试连接失败')
  } finally {
    testing.value = false
  }
}

const handleSave = async () => {
  if (!configFormRef.value || !agentId.value) return
  
  await configFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      const fullConfig = buildFullConfig()
      
      const response = await agentApi.updateAgent(agentId.value, {
        name: configForm.name,
        description: configForm.description,
        version: configForm.version,
        config: fullConfig
      })
      
      if (response.data.success) {
        ElMessage.success('配置保存成功')
        await loadAgentInfo()
      }
    } catch (error) {
      console.error('保存配置失败:', error)
      ElMessage.error('保存配置失败')
    } finally {
      saving.value = false
    }
  })
}

const handleStart = async () => {
  if (!agentId.value) return
  
  starting.value = true
  try {
    const response = await agentApi.startAgent(agentId.value)
    if (response.data.success) {
      ElMessage.success('代理启动成功')
      await loadAgentInfo()
      await loadMetrics()
    }
  } catch (error) {
    console.error('启动代理失败:', error)
    ElMessage.error('启动代理失败')
  } finally {
    starting.value = false
  }
}

const handleStop = async () => {
  if (!agentId.value) return
  
  stopping.value = true
  try {
    const response = await agentApi.stopAgent(agentId.value)
    if (response.data.success) {
      ElMessage.success('代理停止成功')
      await loadAgentInfo()
      await loadMetrics()
    }
  } catch (error) {
    console.error('停止代理失败:', error)
    ElMessage.error('停止代理失败')
  } finally {
    stopping.value = false
  }
}

const handleActivate = async () => {
  if (!agentId.value) return
  
  activating.value = true
  try {
    const response = await agentApi.activateAgent(agentId.value)
    if (response.data.success) {
      ElMessage.success('代理激活成功')
      await loadAgentInfo()
    }
  } catch (error) {
    console.error('激活代理失败:', error)
    ElMessage.error('激活代理失败')
  } finally {
    activating.value = false
  }
}

const viewAllLogs = () => {
  // 可以跳转到专门的日志页面
  router.push(`/agent/${agentId.value}/logs`)
}

const viewLogDetail = (log: AgentRunLog) => {
  // 查看日志详情
  router.push(`/agent/${agentId.value}/logs/${log.id}`)
}

const getLogStatusType = (status: string) => {
  const typeMap = {
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    stopped: 'warning'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

const getLogStatusText = (status: string) => {
  const textMap = {
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    stopped: '已停止'
  }
  return textMap[status as keyof typeof textMap] || status
}
</script>

<style scoped lang="scss">
.agent-config {
  padding: 20px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
    .header-content {
      .breadcrumb {
        margin-bottom: 8px;
      }
      
      .title-section {
        h1 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
          color: #1f2329;
        }
        
        .agent-meta {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .version, .type {
            font-size: 14px;
            color: #646a73;
          }
        }
      }
    }
    
    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .config-content {
    .config-form-card {
      margin-bottom: 24px;
      
      :deep(.el-card__header) {
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
          }
        }
      }
      
      .model-option {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .model-name {
          font-weight: 500;
        }
        
        .model-provider {
          font-size: 12px;
          color: #909399;
        }
      }
      
      .param-tip {
        margin-top: 4px;
      }
      
      .custom-config {
        .config-item {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
        }
      }
    }
    
    .status-card {
      margin-bottom: 24px;
      
      .status-content {
        .status-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #f0f0f0;
          
          &:last-child {
            border-bottom: none;
          }
          
          .label {
            font-size: 14px;
            color: #646a73;
          }
          
          .value {
            font-size: 14px;
            color: #1f2329;
            font-weight: 500;
          }
        }
      }
      
      .status-actions {
        margin-top: 16px;
        text-align: center;
      }
    }
    
    .metrics-card {
      margin-bottom: 24px;
      
      .metrics-content {
        .metric-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #f0f0f0;
          
          &:last-child {
            border-bottom: none;
          }
          
          .metric-label {
            font-size: 14px;
            color: #646a73;
          }
          
          .metric-value {
            font-size: 16px;
            color: #1f2329;
            font-weight: 600;
          }
        }
      }
    }
    
    .logs-card {
      .logs-content {
        .empty-logs {
          text-align: center;
          padding: 20px;
        }
        
        .log-list {
          .log-item {
            padding: 12px;
            border: 1px solid #f0f0f0;
            border-radius: 6px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.3s;
            
            &:hover {
              border-color: #409eff;
              background-color: #f8f9fa;
            }
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .log-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 8px;
              
              .log-time {
                font-size: 12px;
                color: #909399;
              }
            }
            
            .log-details {
              display: flex;
              gap: 12px;
              
              .log-detail {
                font-size: 12px;
                
                .detail-label {
                  color: #909399;
                }
                
                .detail-value {
                  color: #606266;
                  font-weight: 500;
                  margin-left: 4px;
                }
              }
            }
            
            .log-error {
              margin-top: 8px;
            }
          }
        }
      }
    }
  }
  
  .template-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
    
    .template-card {
      padding: 16px;
      border: 1px solid #f0f0f0;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        border-color: #409eff;
        background-color: #f8f9fa;
      }
      
      .template-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        h4 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
        }
      }
      
      .template-description {
        margin: 0;
        font-size: 13px;
        color: #646a73;
        line-height: 1.4;
      }
    }
  }
  
  .prompt-templates {
    .prompt-list {
      .prompt-item {
        padding: 16px;
        border: 1px solid #f0f0f0;
        border-radius: 8px;
        margin-bottom: 16px;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          border-color: #409eff;
          background-color: #f8f9fa;
        }
        
        h5 {
          margin: 0 0 8px 0;
          font-size: 14px;
          font-weight: 600;
        }
        
        p {
          margin: 0 0 12px 0;
          font-size: 13px;
          color: #646a73;
        }
        
        .prompt-preview {
          margin: 0;
          padding: 12px;
          background-color: #f5f7fa;
          border-radius: 4px;
          font-size: 12px;
          line-height: 1.4;
          max-height: 100px;
          overflow-y: auto;
        }
      }
    }
  }
}

:deep(.el-card__header) {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
  }
}
</style>
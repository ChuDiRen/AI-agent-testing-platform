<!-- AI测试用例生成页面 -->
<template>
  <div class="testcase-generate">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>
            <el-icon class="header-icon"><MagicStick /></el-icon>
            AI智能测试用例生成
          </h1>
          <p>基于需求描述，使用多智能体协作自动生成高质量测试用例</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-number">{{ totalGenerated }}</div>
            <div class="stat-label">总生成数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ successRate }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 需求输入区域 -->
    <el-card class="requirement-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon class="header-icon"><Document /></el-icon>
                <span>需求描述</span>
              </div>
              <div class="header-right">
                <el-button type="primary" size="small" @click="loadTemplate">
                  <el-icon><Collection /></el-icon>
                  使用模板
                </el-button>
                <el-button type="text" size="small" @click="clearRequirement">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
              </div>
            </div>
          </template>
          
          <el-form :model="generateForm" :rules="generateRules" ref="generateFormRef" label-position="top">
            <el-form-item prop="requirement_text">
              <div class="requirement-input-wrapper">
                <div class="requirement-label">
                  <el-icon><EditPen /></el-icon>
                  <span>需求描述</span>
                  <el-tag type="warning" size="small">必填</el-tag>
                </div>
                <el-input
                  v-model="generateForm.requirement_text"
                  type="textarea"
                  :rows="12"
                  placeholder="请详细描述功能需求、业务场景和期望的测试覆盖范围..."
                  show-word-limit
                  maxlength="2000"
                  :autosize="{ minRows: 12, maxRows: 25 }"
                  resize="vertical"
                  class="requirement-textarea"
                />
                <div class="requirement-examples">
                  <div class="examples-header">
                    <el-icon><StarFilled /></el-icon>
                    <span>需求描述示例</span>
                  </div>
                  <div class="examples-content">
                    <div class="example-item" @click="loadExample('login')">
                      <div class="example-title">用户登录功能</div>
                      <div class="example-desc">包含用户名密码验证、记住密码、验证码等</div>
                    </div>
                    <div class="example-item" @click="loadExample('payment')">
                      <div class="example-title">支付功能</div>
                      <div class="example-desc">支持多种支付方式、订单管理、退款处理</div>
                    </div>
                    <div class="example-item" @click="loadExample('upload')">
                      <div class="example-title">文件上传功能</div>
                      <div class="example-desc">支持多种格式、大小限制、批量上传</div>
                    </div>
                  </div>
                </div>
                <div class="requirement-tips">
                  <el-icon><InfoFilled /></el-icon>
                  <span>详细的需求描述有助于AI生成更准确的测试用例</span>
                </div>
              </div>
            </el-form-item>
            
    <!-- 配置选项区域 -->
    <div class="config-section">
      <div class="config-header">
        <el-icon><Setting /></el-icon>
        <span>生成配置</span>
      </div>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <div class="config-item">
            <div class="config-label">
              <el-icon><Document /></el-icon>
              <span>测试类型</span>
            </div>
            <el-select v-model="generateForm.test_type" placeholder="选择测试类型" style="width: 100%">
              <el-option label="功能测试" value="functional">
                <div class="option-content">
                  <div class="option-title">功能测试</div>
                  <div class="option-desc">验证功能是否按预期工作</div>
                </div>
              </el-option>
              <el-option label="性能测试" value="performance">
                <div class="option-content">
                  <div class="option-title">性能测试</div>
                  <div class="option-desc">验证系统性能指标</div>
                </div>
              </el-option>
              <el-option label="安全测试" value="security">
                <div class="option-content">
                  <div class="option-title">安全测试</div>
                  <div class="option-desc">验证系统安全性</div>
                </div>
              </el-option>
              <el-option label="集成测试" value="integration">
                <div class="option-content">
                  <div class="option-title">集成测试</div>
                  <div class="option-desc">验证模块间集成</div>
                </div>
              </el-option>
              <el-option label="单元测试" value="unit">
                <div class="option-content">
                  <div class="option-title">单元测试</div>
                  <div class="option-desc">验证最小功能单元</div>
                </div>
              </el-option>
            </el-select>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="config-item">
            <div class="config-label">
              <el-icon><PriceTag /></el-icon>
              <span>优先级</span>
            </div>
            <el-select v-model="generateForm.priority" placeholder="选择优先级" style="width: 100%">
              <el-option label="低" value="low">
                <el-tag type="info" size="small">低</el-tag>
              </el-option>
              <el-option label="中" value="medium">
                <el-tag type="" size="small">中</el-tag>
              </el-option>
              <el-option label="高" value="high">
                <el-tag type="warning" size="small">高</el-tag>
              </el-option>
              <el-option label="关键" value="critical">
                <el-tag type="danger" size="small">关键</el-tag>
              </el-option>
            </el-select>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <div class="config-item">
            <div class="config-label">
              <el-icon><StarFilled /></el-icon>
              <span>生成数量</span>
            </div>
            <div class="count-input-wrapper">
              <el-input-number 
                v-model="generateForm.count" 
                :min="1" 
                :max="50" 
                :step="1"
                controls-position="right"
                style="width: 100%"
              />
              <div class="count-tips">建议5-20个，过多可能影响质量</div>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="config-item">
            <div class="config-label">
              <el-icon><MagicStick /></el-icon>
              <span>AI代理</span>
            </div>
            <el-select 
              v-model="generateForm.agent_ids" 
              multiple 
              placeholder="选择参与生成的AI代理"
              style="width: 100%"
              collapse-tags
              collapse-tags-tooltip
            >
              <el-option
                v-for="agent in availableAgents"
                :key="agent.id"
                :label="agent.name"
                :value="agent.id"
              >
                <div class="agent-option">
                  <div class="agent-info">
                    <div class="agent-name">{{ agent.name }}</div>
                    <div class="agent-type">{{ agent.type }}</div>
                  </div>
                  <div class="agent-status">
                    <el-tag :type="getAgentStatusType(agent.status)" size="small">
                      {{ getAgentStatusLabel(agent.status) }}
                    </el-tag>
                  </div>
                </div>
              </el-option>
            </el-select>
            <div class="agent-tips">
              <el-icon><InfoFilled /></el-icon>
              <span>选择多个代理可以协作生成，提高测试用例质量</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
            
    <!-- 操作按钮区域 -->
    <div class="action-section">
      <div class="action-buttons">
        <el-button 
          type="primary" 
          @click="startGeneration" 
          :loading="generating"
          size="large"
          :disabled="!generateForm.requirement_text.trim()"
          class="primary-action"
        >
          <el-icon><MagicStick /></el-icon>
          {{ generating ? '生成中...' : '开始AI生成' }}
        </el-button>
        <div class="secondary-actions">
          <el-button @click="saveDraft" size="default" type="info">
            <el-icon><Document /></el-icon>
            保存草稿
          </el-button>
          <el-button @click="resetForm" size="default">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </div>
      </div>
    </div>
          </el-form>
        </el-card>

    <!-- 生成状态和结果区域 -->
    <div class="result-section">
      <!-- 生成进度卡片 -->
      <el-card v-if="currentTask" class="progress-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon class="header-icon"><Loading /></el-icon>
              <span>生成进度</span>
            </div>
            <div class="header-right">
              <el-tag :type="getTaskStatusType(currentTask.status)" size="small">
                {{ getTaskStatusLabel(currentTask.status) }}
              </el-tag>
            </div>
          </div>
        </template>
        
        <div class="progress-content">
          <div class="progress-circle">
            <el-progress 
              type="circle" 
              :percentage="currentTask.progress" 
              :status="currentTask.status === 'failed' ? 'exception' : undefined"
              :width="120"
              :stroke-width="8"
            />
          </div>
          <div class="progress-info">
            <p class="progress-text">{{ getProgressText() }}</p>
            <div class="progress-details">
              <div class="detail-item">
                <span class="detail-label">已生成:</span>
                <span class="detail-value">{{ currentTask.generated_count }} 个用例</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预计总数:</span>
                <span class="detail-value">{{ currentTask.total_expected }} 个用例</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">当前阶段:</span>
                <span class="detail-value">{{ currentTask.current_stage }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="currentTask.status === 'running'" class="progress-actions">
            <el-button @click="cancelGeneration" type="danger" size="small">
              <el-icon><Close /></el-icon>
              取消生成
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 生成结果卡片 -->
      <el-card v-if="generatedCases.length" class="result-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon class="header-icon"><Document /></el-icon>
              <span>生成结果 ({{ generatedCases.length }})</span>
            </div>
            <div class="header-right">
              <el-button @click="exportCases" size="small" type="primary">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <el-button @click="showAllCases" size="small">
                <el-icon><View /></el-icon>
                查看全部
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="case-list">
          <div 
            v-for="(testCase, index) in generatedCases.slice(0, 3)" 
            :key="testCase.id"
            class="case-item"
            @click="viewTestCase(testCase)"
          >
            <div class="case-header">
              <div class="case-title-wrapper">
                <span class="case-title">{{ testCase.title }}</span>
                <el-tag :type="getPriorityTagType(testCase.priority)" size="small">
                  {{ getPriorityLabel(testCase.priority) }}
                </el-tag>
              </div>
              <div class="case-actions">
                <el-button type="text" size="small" @click.stop="editTestCase(testCase)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </div>
            </div>
            <p class="case-desc">{{ testCase.description }}</p>
            <div class="case-meta">
              <div class="meta-item">
                <el-icon><List /></el-icon>
                <span>{{ testCase.steps?.length || 0 }} 个步骤</span>
              </div>
              <div class="meta-item">
                <el-icon><PriceTag /></el-icon>
                <span>{{ testCase.tags?.join(', ') || '无标签' }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="generatedCases.length > 3" class="show-more">
            <el-button @click="showAllCases" type="text" size="small">
              查看全部 {{ generatedCases.length }} 个用例
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 历史记录 -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><Clock /></el-icon>
            <span>生成历史</span>
          </div>
          <div class="header-right">
            <el-button @click="loadGenerationHistory" size="small" :loading="loadingHistory">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="generationHistory" v-loading="loadingHistory" stripe>
        <el-table-column prop="created_at" label="生成时间" width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <div class="time-date">{{ formatDate(row.created_at) }}</div>
              <div class="time-time">{{ formatTime(row.created_at) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="requirement_summary" label="需求摘要" min-width="200">
          <template #default="{ row }">
            <div class="requirement-cell">
              <div class="requirement-title">{{ row.requirement_summary }}</div>
              <div class="requirement-preview">{{ row.requirement_text?.substring(0, 100) }}...</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="test_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTestTypeTagType(row.test_type)">{{ getTestTypeLabel(row.test_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="generated_count" label="生成数量" width="100">
          <template #default="{ row }">
            <div class="count-cell">
              <span class="count-number">{{ row.generated_count }}</span>
              <span class="count-total">/ {{ row.count }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button @click="viewHistory(row)" size="small" type="text">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button @click="regenerate(row)" size="small" type="text">
                <el-icon><Refresh /></el-icon>
                重新生成
              </el-button>
              <el-button @click="deleteHistory(row)" size="small" type="text" class="danger-btn">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!generationHistory.length && !loadingHistory" class="empty-history">
        <el-empty description="暂无生成历史">
          <el-button type="primary" @click="startGeneration">开始生成测试用例</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  MagicStick, 
  Document, 
  Collection, 
  Delete, 
  InfoFilled, 
  Refresh, 
  Loading, 
  Close, 
  Download, 
  View, 
  Edit, 
  List, 
  PriceTag, 
  ArrowRight, 
  Clock,
  EditPen,
  StarFilled,
  Setting
} from '@element-plus/icons-vue'
import { testCaseApi } from '@/api/modules/testcase'
import { agentApi } from '@/api/modules/agent'
import { formatDateTime } from '@/utils/dateFormat'

const router = useRouter()

// 响应式数据
const generating = ref(false)
const loadingHistory = ref(false)
const generateFormRef = ref()
const availableAgents = ref([])
const generatedCases = ref([])
const generationHistory = ref([])
const currentTask = ref(null)
const drafts = ref([])
let taskCheckInterval = null

// 计算属性
const totalGenerated = computed(() => {
  return generationHistory.value.reduce((sum, item) => {
    return sum + (item.status === 'completed' ? item.generated_count : 0)
  }, 0)
})

const successRate = computed(() => {
  const total = generationHistory.value.length
  if (total === 0) return 100
  const success = generationHistory.value.filter(item => item.status === 'completed').length
  return Math.round((success / total) * 100)
})

// 生成表单
const generateForm = reactive({
  requirement_text: '',
  test_type: 'functional',
  priority: 'medium',
  count: 10,
  agent_ids: []
})

// 表单验证规则
const generateRules = {
  requirement_text: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 10, message: '需求描述至少10个字符', trigger: 'blur' }
  ]
}

// 生命周期
onMounted(() => {
  loadAvailableAgents()
  loadGenerationHistory()
})

// 方法
const loadAvailableAgents = async () => {
  try {
    const response = await agentApi.searchAgents({ status: 'active' })
    if (response.data.success) {
      availableAgents.value = response.data.data.agents || []
    }
  } catch (error) {
    console.error('加载AI代理失败:', error)
    ElMessage.error('加载AI代理失败')
  }
}

const loadGenerationHistory = async () => {
  try {
    loadingHistory.value = true
    const response = await testCaseApi.getGenerationHistory({ page: 1, page_size: 10 })
    if (response.data.success) {
      generationHistory.value = response.data.data.history || []
    }
  } catch (error) {
    console.error('加载生成历史失败:', error)
    ElMessage.error('加载生成历史失败')
  } finally {
    loadingHistory.value = false
  }
}

const startGeneration = async () => {
  if (!generateFormRef.value) return
  
  await generateFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    generating.value = true
    try {
      const response = await testCaseApi.generateTestCases(generateForm)
      if (response.data.success) {
        currentTask.value = {
          task_id: response.data.data.task_id,
          status: 'running',
          progress: 0,
          generated_count: 0,
          total_expected: generateForm.count,
          current_stage: '初始化任务'
        }
        
        // 开始轮询任务状态
        startTaskPolling(response.data.data.task_id)
        ElMessage.success('AI生成任务已启动')
      }
    } catch (error) {
      console.error('启动生成任务失败:', error)
      ElMessage.error('启动生成任务失败')
      generating.value = false
    }
  })
}

const startTaskPolling = (taskId) => {
  taskCheckInterval = setInterval(async () => {
    try {
      const response = await testCaseApi.checkGenerationTask(taskId)
      if (response.data.success) {
        currentTask.value = response.data.data
        
        if (response.data.data.status === 'completed') {
          clearInterval(taskCheckInterval)
          generatedCases.value = response.data.data.result?.generated_cases || []
          generating.value = false
          ElMessage.success(`生成完成！共生成 ${response.data.data.generated_count} 个测试用例`)
          loadGenerationHistory()
        } else if (response.data.data.status === 'failed') {
          clearInterval(taskCheckInterval)
          generating.value = false
          ElMessage.error(`生成任务失败: ${response.data.data.error_message || '未知错误'}`)
        }
      }
    } catch (error) {
      console.error('检查任务状态失败:', error)
    }
  }, 2000)
}

const getProgressText = () => {
  if (!currentTask.value) return ''
  
  switch (currentTask.value.status) {
    case 'pending': return '任务排队中...'
    case 'running': return 'AI正在分析需求并生成测试用例...'
    case 'completed': return '生成完成'
    case 'failed': return '生成失败'
    default: return ''
  }
}

const resetForm = () => {
  ElMessageBox.confirm('确定要重置表单吗？所有输入的内容将被清空。', '确认重置', {
    type: 'warning'
  }).then(() => {
    generateFormRef.value?.resetFields()
    generatedCases.value = []
    currentTask.value = null
    ElMessage.success('表单已重置')
  }).catch(() => {
    // 用户取消
  })
}

const clearRequirement = () => {
  generateForm.requirement_text = ''
}

const saveDraft = () => {
  if (!generateForm.requirement_text.trim()) {
    ElMessage.warning('请先输入需求描述')
    return
  }
  
  const draft = {
    id: Date.now(),
    title: generateForm.requirement_text.substring(0, 50) + '...',
    content: generateForm.requirement_text,
    test_type: generateForm.test_type,
    priority: generateForm.priority,
    count: generateForm.count,
    agent_ids: generateForm.agent_ids,
    created_at: new Date().toISOString()
  }
  
  drafts.value.unshift(draft)
  // 只保留最近10个草稿
  if (drafts.value.length > 10) {
    drafts.value = drafts.value.slice(0, 10)
  }
  
  ElMessage.success('草稿已保存')
}

// 工具方法
const getPriorityTagType = (priority) => {
  const types = {
    low: 'info',
    medium: '',
    high: 'warning',
    critical: 'danger'
  }
  return types[priority] || ''
}

const getPriorityLabel = (priority) => {
  const labels = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '关键'
  }
  return labels[priority] || priority
}

const getStatusTagType = (status) => {
  const types = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || ''
}

const getStatusLabel = (status) => {
  const labels = {
    pending: '等待中',
    running: '生成中',
    completed: '已完成',
    failed: '失败'
  }
  return labels[status] || status
}

const loadTemplate = () => {
  // 提供一些常用模板
  const templates = [
    {
      name: '用户登录功能',
      requirement: '实现用户登录功能，包括用户名密码验证、记住密码、验证码验证、登录状态保持等功能。需要支持手机号和邮箱登录，密码强度验证，登录失败锁定机制。',
      type: 'functional',
      priority: 'high'
    },
    {
      name: '支付功能',
      requirement: '实现在线支付功能，支持多种支付方式（支付宝、微信、银行卡），包括支付流程、订单管理、退款处理、支付安全验证等功能。',
      type: 'functional',
      priority: 'critical'
    },
    {
      name: '文件上传功能',
      requirement: '实现文件上传功能，支持多种文件格式，包括文件大小限制、文件类型验证、上传进度显示、批量上传、断点续传等功能。',
      type: 'functional',
      priority: 'medium'
    }
  ]
  
  ElMessageBox.confirm('选择一个模板快速填充需求描述：', '选择模板', {
    type: 'info',
    showCancelButton: false,
    showConfirmButton: false,
    message: h('div', null, [
      ...templates.map((template, index) => 
        h('div', {
          key: index,
          style: 'padding: 10px; border: 1px solid #ddd; margin-bottom: 8px; cursor: pointer; border-radius: 4px;',
          onClick: () => {
            generateForm.requirement_text = template.requirement
            generateForm.test_type = template.type
            generateForm.priority = template.priority
            ElMessageBox.close()
            ElMessage.success('模板已加载')
          }
        }, [
          h('strong', template.name),
          h('p', { style: 'margin: 5px 0; font-size: 12px; color: #666;' }, template.requirement.substring(0, 100) + '...')
        ])
      )
    ])
  })
}

const loadExample = (type) => {
  const examples = {
    login: {
      requirement: '实现用户登录功能，包括以下需求：\n\n1. 基本功能：\n   - 用户名/密码登录\n   - 手机号/邮箱登录\n   - 记住密码功能\n   - 自动登录\n\n2. 安全验证：\n   - 密码强度验证\n   - 图形验证码\n   - 短信验证码\n   - 登录失败锁定\n\n3. 用户体验：\n   - 登录状态保持\n   - 单点登录\n   - 登录历史记录\n\n4. 异常处理：\n   - 网络异常处理\n   - 账号被锁定处理\n   - 密码错误次数限制',
      type: 'functional',
      priority: 'high'
    },
    payment: {
      requirement: '实现在线支付功能，包括以下需求：\n\n1. 支付方式：\n   - 支付宝支付\n   - 微信支付\n   - 银行卡支付\n   - 余额支付\n\n2. 支付流程：\n   - 订单创建\n   - 支付金额计算\n   - 支付渠道选择\n   - 支付结果处理\n\n3. 订单管理：\n   - 订单状态跟踪\n   - 支付超时处理\n   - 订单取消\n   - 退款处理\n\n4. 安全控制：\n   - 支付密码验证\n   - 风险控制\n   - 交易限额\n   - 异常监控',
      type: 'functional',
      priority: 'critical'
    },
    upload: {
      requirement: '实现文件上传功能，包括以下需求：\n\n1. 文件支持：\n   - 图片文件（jpg, png, gif）\n   - 文档文件（pdf, doc, docx）\n   - 压缩文件（zip, rar）\n   - 视频文件（mp4, avi）\n\n2. 上传限制：\n   - 文件大小限制（单文件最大10MB）\n   - 文件类型验证\n   - 上传数量限制\n   - 存储空间限制\n\n3. 上传功能：\n   - 单文件上传\n   - 批量上传\n   - 拖拽上传\n   - 断点续传\n\n4. 用户体验：\n   - 上传进度显示\n   - 上传预览\n   - 上传失败重试\n   - 上传历史记录',
      type: 'functional',
      priority: 'medium'
    }
  }
  
  const example = examples[type]
  if (example) {
    generateForm.requirement_text = example.requirement
    generateForm.test_type = example.type
    generateForm.priority = example.priority
    ElMessage.success('示例已加载')
  }
}

const viewHistory = (row) => {
  // 显示历史记录详情
  ElMessageBox.alert(
    h('div', null, [
      h('p', `任务ID: ${row.task_id}`),
      h('p', `需求描述: ${row.requirement_text}`),
      h('p', `测试类型: ${getTestTypeLabel(row.test_type)}`),
      h('p', `优先级: ${getPriorityLabel(row.priority)}`),
      h('p', `生成数量: ${row.generated_count}/${row.count}`),
      h('p', `代理: ${row.agent_names?.join(', ') || '默认'}`),
      h('p', `状态: ${getStatusLabel(row.status)}`),
      h('p', `创建时间: ${formatDateTime(row.created_at)}`)
    ]),
    '生成历史详情',
    {
      confirmButtonText: '确定'
    }
  )
}

const regenerate = (row) => {
  generateForm.requirement_text = row.requirement_text
  generateForm.test_type = row.test_type
  generateForm.priority = row.priority
  generateForm.count = row.count
  generateForm.agent_ids = row.agent_ids || []
  ElMessage.success('已加载历史配置，可以重新生成')
}

const cancelGeneration = async () => {
  if (!currentTask.value?.task_id) return
  
  try {
    await ElMessageBox.confirm('确定要取消当前生成任务吗？', '确认取消', {
      type: 'warning'
    })
    
    const response = await testCaseApi.cancelGenerationTask(currentTask.value.task_id)
    if (response.data.success) {
      clearInterval(taskCheckInterval)
      currentTask.value = null
      generating.value = false
      ElMessage.success('生成任务已取消')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消任务失败:', error)
      ElMessage.error('取消任务失败')
    }
  }
}

const exportCases = async () => {
  if (!generatedCases.value.length) return
  
  try {
    const caseIds = generatedCases.value.map(c => c.id)
    const blob = await testCaseApi.exportTestCases(caseIds, 'excel')
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `generated_test_cases_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('测试用例导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const showAllCases = () => {
  // 跳转到测试用例列表页面，显示生成的用例
  router.push({
    path: '/test/cases',
    query: {
      generated: 'true',
      task_id: currentTask.value?.task_id
    }
  })
}

const getTestTypeLabel = (type) => {
  const labels = {
    functional: '功能测试',
    performance: '性能测试',
    security: '安全测试',
    integration: '集成测试',
    unit: '单元测试'
  }
  return labels[type] || type
}

const getTestTypeTagType = (type) => {
  const types = {
    functional: '',
    performance: 'warning',
    security: 'danger',
    integration: 'success',
    unit: 'info'
  }
  return types[type] || ''
}

const getAgentStatusType = (status) => {
  const types = {
    active: 'success',
    inactive: 'info',
    error: 'danger'
  }
  return types[status] || 'info'
}

const getAgentStatusLabel = (status) => {
  const labels = {
    active: '运行中',
    inactive: '已停止',
    error: '错误'
  }
  return labels[status] || status
}

const getTaskStatusType = (status) => {
  const types = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getTaskStatusLabel = (status) => {
  const labels = {
    pending: '等待中',
    running: '生成中',
    completed: '已完成',
    failed: '失败'
  }
  return labels[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const viewTestCase = (testCase) => {
  // 查看测试用例详情
  ElMessageBox.alert(
    h('div', null, [
      h('h3', testCase.title),
      h('p', testCase.description),
      h('div', { style: 'margin-top: 10px;' }, [
        h('strong', '测试步骤:'),
        ...testCase.steps?.map((step, index) => 
          h('div', { style: 'margin-left: 20px; margin-top: 5px;' }, `${index + 1}. ${step}`)
        ) || [h('p', '暂无测试步骤')]
      ])
    ]),
    '测试用例详情',
    {
      confirmButtonText: '确定'
    }
  )
}

const editTestCase = (testCase) => {
  // 编辑测试用例
  ElMessage.info('编辑功能开发中...')
}

const deleteHistory = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条生成历史吗？', '确认删除', {
      type: 'warning'
    })
    
    // 这里应该调用删除API
    // await testCaseApi.deleteGenerationHistory(row.id)
    
    generationHistory.value = generationHistory.value.filter(item => item.id !== row.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped lang="scss">
.testcase-generate {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

// 页面头部样式
.page-header {
  margin-bottom: 32px;
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 32px;
    color: white;
    
    .header-text {
      h1 {
        margin: 0 0 12px 0;
        font-size: 32px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 12px;
        
        .header-icon {
          font-size: 36px;
        }
      }
      
      p {
        margin: 0;
        font-size: 16px;
        opacity: 0.9;
        line-height: 1.5;
      }
    }
    
    .header-stats {
      display: flex;
      gap: 32px;
      
      .stat-item {
        text-align: center;
        
        .stat-number {
          font-size: 28px;
          font-weight: 700;
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          opacity: 0.8;
        }
      }
    }
  }
}

// 卡片头部样式
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .header-icon {
      color: #409eff;
    }
  }
  
  .header-right {
    display: flex;
    gap: 8px;
  }
}

// 需求卡片样式
.requirement-card {
  margin-bottom: 24px;
  border-radius: 12px;
  
  // 配置选项区域样式
  .config-section {
    margin: 24px 0;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    
    .config-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 20px;
      font-weight: 600;
      color: #495057;
      font-size: 16px;
      
      .el-icon {
        color: #409eff;
        font-size: 18px;
      }
    }
    
    .config-item {
      margin-bottom: 16px;
      
      .config-label {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
        font-weight: 500;
        color: #606266;
        font-size: 14px;
        
        .el-icon {
          color: #909399;
          font-size: 16px;
        }
      }
    }
  }
  
  // 操作按钮区域样式
  .action-section {
    margin-top: 24px;
    padding: 20px;
    background: #f0f9ff;
    border-radius: 8px;
    border: 1px solid #e0f2fe;
    
    .action-buttons {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .primary-action {
        flex: 1;
        max-width: 200px;
        height: 48px;
        font-size: 16px;
        font-weight: 600;
      }
      
      .secondary-actions {
        display: flex;
        gap: 12px;
        
        .el-button {
          height: 40px;
        }
      }
    }
  }
  
  .requirement-input-wrapper {
    .requirement-label {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      font-weight: 600;
      color: #303133;
      font-size: 16px;
      
      .el-icon {
        color: #409eff;
        font-size: 18px;
      }
      
      .el-tag {
        margin-left: auto;
      }
    }
    
    .requirement-textarea {
      :deep(.el-textarea__inner) {
        border-radius: 8px;
        border: 2px solid #e4e7ed;
        transition: all 0.3s ease;
        font-size: 14px;
        line-height: 1.6;
        
        &:focus {
          border-color: #409eff;
          box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
        }
        
        &::placeholder {
          color: #c0c4cc;
          font-size: 14px;
        }
      }
    }
    
    .requirement-examples {
      margin: 16px 0;
      padding: 16px;
      background: #f8f9fa;
      border-radius: 8px;
      border: 1px solid #e9ecef;
      
      .examples-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-weight: 600;
        color: #495057;
        font-size: 14px;
        
        .el-icon {
          color: #ffc107;
          font-size: 16px;
        }
      }
      
      .examples-content {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        
        .example-item {
          padding: 12px;
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            border-color: #409eff;
            box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
            transform: translateY(-2px);
          }
          
          .example-title {
            font-weight: 600;
            color: #303133;
            margin-bottom: 4px;
            font-size: 14px;
          }
          
          .example-desc {
            font-size: 12px;
            color: #606266;
            line-height: 1.4;
          }
        }
      }
    }
    
    .requirement-tips {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 12px;
      padding: 8px 12px;
      background: #e8f4fd;
      border-radius: 6px;
      font-size: 13px;
      color: #409eff;
      
      .el-icon {
        color: #409eff;
        font-size: 14px;
      }
    }
  }
  
  .count-input-wrapper {
    .count-tips {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }
  
  .agent-selection {
    .agent-option {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      
      .agent-info {
        .agent-name {
          font-weight: 500;
        }
        
        .agent-type {
          font-size: 12px;
          color: #909399;
        }
      }
    }
    
    .agent-tips {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 8px;
      font-size: 12px;
      color: #909399;
      
      .el-icon {
        color: #409eff;
      }
    }
  }
  
  .form-actions {
    display: flex;
    gap: 12px;
    margin-top: 16px;
  }
}

// 结果区域样式
.result-section {
  margin-bottom: 24px;
  
  .progress-card, .result-card {
    margin-bottom: 16px;
    border-radius: 12px;
  }
}

// 进度卡片样式
.progress-card {
  border-radius: 12px;
  
  .progress-content {
    text-align: center;
    
    .progress-circle {
      margin-bottom: 20px;
    }
    
    .progress-info {
      .progress-text {
        margin: 0 0 16px 0;
        color: #606266;
        font-size: 16px;
        font-weight: 500;
      }
      
      .progress-details {
        .detail-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #f0f0f0;
          
          &:last-child {
            border-bottom: none;
          }
          
          .detail-label {
            color: #909399;
            font-size: 14px;
          }
          
          .detail-value {
            color: #303133;
            font-weight: 500;
          }
        }
      }
    }
    
    .progress-actions {
      margin-top: 20px;
    }
  }
}

// 结果卡片样式
.result-card {
  margin-bottom: 24px;
  border-radius: 12px;
  
  .case-list {
    .case-item {
      padding: 16px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      margin-bottom: 12px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: #409eff;
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
        transform: translateY(-2px);
      }
      
      .case-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
        
        .case-title-wrapper {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 12px;
          
          .case-title {
            font-weight: 600;
            color: #303133;
            font-size: 16px;
          }
        }
        
        .case-actions {
          .el-button {
            padding: 4px;
          }
        }
      }
      
      .case-desc {
        margin: 0 0 12px 0;
        color: #606266;
        font-size: 14px;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      
      .case-meta {
        display: flex;
        gap: 20px;
        font-size: 12px;
        color: #909399;
        
        .meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
          
          .el-icon {
            font-size: 14px;
          }
        }
      }
    }
    
    .show-more {
      text-align: center;
      padding: 16px;
      border-top: 1px solid #f0f0f0;
    }
  }
}

// 历史记录卡片样式
.history-card {
  border-radius: 12px;
  
  .time-cell {
    .time-date {
      font-weight: 500;
      color: #303133;
    }
    
    .time-time {
      font-size: 12px;
      color: #909399;
    }
  }
  
  .requirement-cell {
    .requirement-title {
      font-weight: 500;
      color: #303133;
      margin-bottom: 4px;
    }
    
    .requirement-preview {
      font-size: 12px;
      color: #909399;
      line-height: 1.4;
    }
  }
  
  .count-cell {
    .count-number {
      font-weight: 600;
      color: #409eff;
      font-size: 16px;
    }
    
    .count-total {
      color: #909399;
      font-size: 12px;
    }
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
    
    .danger-btn {
      color: #f56c6c;
      
      &:hover {
        color: #f56c6c;
        background-color: #fef0f0;
      }
    }
  }
  
  .empty-history {
    padding: 40px 0;
  }
}

// 选项内容样式
:deep(.el-select-dropdown__item) {
  .option-content {
    .option-title {
      font-weight: 500;
      margin-bottom: 2px;
    }
    
    .option-desc {
      font-size: 12px;
      color: #909399;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .testcase-generate {
    padding: 16px;
  }
  
  .page-header {
    .header-content {
      flex-direction: column;
      gap: 24px;
      text-align: center;
      
      .header-stats {
        justify-content: center;
      }
    }
  }
}

@media (max-width: 768px) {
  .testcase-generate {
    padding: 12px;
  }
  
  .page-header {
    .header-content {
      padding: 24px 16px;
      
      .header-text {
        h1 {
          font-size: 24px;
          
          .header-icon {
            font-size: 28px;
          }
        }
        
        p {
          font-size: 14px;
        }
      }
      
      .header-stats {
        gap: 24px;
        
        .stat-item {
          .stat-number {
            font-size: 24px;
          }
          
          .stat-label {
            font-size: 12px;
          }
        }
      }
    }
  }
  
  .requirement-card {
    .requirement-input-wrapper {
      .requirement-examples {
        .examples-content {
          grid-template-columns: 1fr;
          gap: 8px;
          
          .example-item {
            padding: 10px;
            
            .example-title {
              font-size: 13px;
            }
            
            .example-desc {
              font-size: 11px;
            }
          }
        }
      }
    }
    
    .config-section {
      padding: 16px;
      
      .config-header {
        font-size: 14px;
        margin-bottom: 16px;
      }
      
      .config-item {
        margin-bottom: 12px;
        
        .config-label {
          font-size: 13px;
        }
      }
    }
    
    .action-section {
      padding: 16px;
      
      .action-buttons {
        flex-direction: column;
        gap: 12px;
        
        .primary-action {
          max-width: none;
          width: 100%;
        }
        
        .secondary-actions {
          width: 100%;
          justify-content: space-between;
          
          .el-button {
            flex: 1;
          }
        }
      }
    }
  }
  
  .progress-card {
    .progress-content {
      .progress-circle {
        :deep(.el-progress-circle) {
          width: 80px !important;
          height: 80px !important;
        }
      }
    }
  }
  
  .result-card {
    .case-list {
      .case-item {
        padding: 12px;
        
        .case-header {
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;
          
          .case-title-wrapper {
            width: 100%;
          }
        }
        
        .case-meta {
          flex-direction: column;
          gap: 8px;
        }
      }
    }
  }
  
  .history-card {
    .action-buttons {
      flex-direction: column;
      gap: 4px;
      
      .el-button {
        width: 100%;
        justify-content: center;
      }
    }
  }
}

@media (max-width: 576px) {
  .page-header {
    .header-content {
      padding: 20px 12px;
      
      .header-text {
        h1 {
          font-size: 20px;
          flex-direction: column;
          gap: 8px;
          
          .header-icon {
            font-size: 24px;
          }
        }
      }
      
      .header-stats {
        gap: 16px;
        
        .stat-item {
          .stat-number {
            font-size: 20px;
          }
          
          .stat-label {
            font-size: 11px;
          }
        }
      }
    }
  }
}
</style>
<!-- AI测试用例生成页面 -->
<template>
  <div class="testcase-generate">
    <div class="page-header">
      <h1>AI智能测试用例生成</h1>
      <p>基于需求描述，使用多智能体协作自动生成高质量测试用例</p>
    </div>

    <el-row :gutter="20">
      <!-- 需求输入区域 -->
      <el-col :span="14">
        <el-card title="需求描述" class="requirement-card">
          <template #header>
            <div class="card-header">
              <span>需求描述</span>
              <el-button type="text" @click="loadTemplate">使用模板</el-button>
            </div>
          </template>
          
          <el-form :model="generateForm" :rules="generateRules" ref="generateFormRef">
            <el-form-item prop="requirement_text">
              <el-input
                v-model="generateForm.requirement_text"
                type="textarea"
                :rows="8"
                placeholder="请详细描述功能需求、业务场景和期望的测试覆盖范围..."
                show-word-limit
                maxlength="2000"
              />
            </el-form-item>
            
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="测试类型">
                  <el-select v-model="generateForm.test_type" placeholder="选择测试类型">
                    <el-option label="功能测试" value="functional" />
                    <el-option label="性能测试" value="performance" />
                    <el-option label="安全测试" value="security" />
                    <el-option label="集成测试" value="integration" />
                    <el-option label="单元测试" value="unit" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="优先级">
                  <el-select v-model="generateForm.priority" placeholder="选择优先级">
                    <el-option label="低" value="low" />
                    <el-option label="中" value="medium" />
                    <el-option label="高" value="high" />
                    <el-option label="关键" value="critical" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="生成数量">
                  <el-input-number v-model="generateForm.count" :min="1" :max="50" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="选择AI代理">
              <el-select v-model="generateForm.agent_ids" multiple placeholder="选择参与生成的AI代理">
                <el-option
                  v-for="agent in availableAgents"
                  :key="agent.id"
                  :label="`${agent.name} (${agent.type})`"
                  :value="agent.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="startGeneration" 
                :loading="generating"
                size="large"
              >
                <el-icon><MagicStick /></el-icon>
                开始AI生成
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 生成状态和预览 -->
      <el-col :span="10">
        <el-card v-if="currentTask" title="生成进度" class="progress-card">
          <div class="progress-content">
            <el-progress 
              :percentage="currentTask.progress" 
              :status="currentTask.status === 'failed' ? 'exception' : undefined"
            />
            <p class="progress-text">{{ getProgressText() }}</p>
            <p class="generated-count">已生成: {{ currentTask.generated_count }} 个用例</p>
            
            <div v-if="currentTask.status === 'running'" class="progress-actions">
              <el-button @click="cancelGeneration" type="danger" size="small">取消生成</el-button>
            </div>
          </div>
        </el-card>

        <el-card v-if="generatedCases.length" title="生成结果" class="result-card">
          <template #header>
            <div class="card-header">
              <span>生成结果 ({{ generatedCases.length }})</span>
              <el-button @click="exportCases" size="small">导出</el-button>
            </div>
          </template>
          
          <div class="case-list">
            <div 
              v-for="(testCase, index) in generatedCases.slice(0, 5)" 
              :key="testCase.id"
              class="case-item"
            >
              <div class="case-header">
                <span class="case-title">{{ testCase.title }}</span>
                <el-tag :type="getPriorityTagType(testCase.priority)" size="small">
                  {{ getPriorityLabel(testCase.priority) }}
                </el-tag>
              </div>
              <p class="case-desc">{{ testCase.description }}</p>
              <div class="case-meta">
                <span>{{ testCase.steps.length }} 个步骤</span>
                <span>{{ testCase.tags.join(', ') }}</span>
              </div>
            </div>
            
            <div v-if="generatedCases.length > 5" class="show-more">
              <el-button @click="showAllCases" type="text">
                查看全部 {{ generatedCases.length }} 个用例
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史记录 -->
    <el-card title="生成历史" class="history-card">
      <el-table :data="generationHistory" v-loading="loadingHistory">
        <el-table-column prop="created_at" label="生成时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="requirement_summary" label="需求摘要" min-width="200" />
        <el-table-column prop="test_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ getTestTypeLabel(row.test_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="generated_count" label="生成数量" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button @click="viewHistory(row)" size="small">查看</el-button>
            <el-button @click="regenerate(row)" size="small" type="primary">重新生成</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { testCaseApi } from '@/api/modules/testcase'
import { agentApi } from '@/api/modules/agent'
import { formatDateTime } from '@/utils/dateFormat'

// 响应式数据
const generating = ref(false)
const loadingHistory = ref(false)
const generateFormRef = ref()
const availableAgents = ref([])
const generatedCases = ref([])
const generationHistory = ref([])
const currentTask = ref(null)
let taskCheckInterval = null

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
    const response = await agentApi.getAgentList({ status: 'active' })
    if (response.success) {
      availableAgents.value = response.data.agents
    }
  } catch (error) {
    console.error('加载AI代理失败:', error)
  }
}

const startGeneration = async () => {
  if (!generateFormRef.value) return
  
  await generateFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    generating.value = true
    try {
      const response = await testCaseApi.generateTestCases(generateForm)
      if (response.success) {
        currentTask.value = {
          task_id: response.data.task_id,
          status: 'running',
          progress: 0,
          generated_count: 0
        }
        
        // 开始轮询任务状态
        startTaskPolling(response.data.task_id)
        ElMessage.success('AI生成任务已启动')
      }
    } catch (error) {
      ElMessage.error('启动生成任务失败')
      generating.value = false
    }
  })
}

const startTaskPolling = (taskId) => {
  taskCheckInterval = setInterval(async () => {
    try {
      const response = await testCaseApi.checkGenerationTask(taskId)
      if (response.success) {
        currentTask.value = response.data
        
        if (response.data.status === 'completed') {
          clearInterval(taskCheckInterval)
          generatedCases.value = response.data.result?.generated_cases || []
          generating.value = false
          ElMessage.success(`生成完成！共生成 ${response.data.generated_count} 个测试用例`)
          loadGenerationHistory()
        } else if (response.data.status === 'failed') {
          clearInterval(taskCheckInterval)
          generating.value = false
          ElMessage.error('生成任务失败')
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
  generateFormRef.value?.resetFields()
  generatedCases.value = []
  currentTask.value = null
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
</script>

<style scoped>
.testcase-generate {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2329;
}

.page-header p {
  margin: 0;
  color: #646a73;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.requirement-card, .progress-card, .result-card, .history-card {
  margin-bottom: 20px;
}

.progress-content {
  text-align: center;
}

.progress-text {
  margin: 12px 0 8px 0;
  color: #646a73;
  font-size: 14px;
}

.generated-count {
  margin: 8px 0;
  font-weight: 500;
  color: #1f2329;
}

.case-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.case-title {
  font-weight: 500;
  color: #1f2329;
}

.case-desc {
  margin: 8px 0;
  color: #646a73;
  font-size: 13px;
  line-height: 1.4;
}

.case-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.show-more {
  text-align: center;
  padding: 12px;
}
</style>
<!-- AI代理管理主页面 -->
<template>
  <div class="agent-management">
    <div class="page-header">
      <div class="header-content">
        <h1>AI代理管理</h1>
        <p>管理和监控您的AI代理，包括创建、配置、启动和停止代理</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建代理
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><DataBoard /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.total_agents }}</div>
          <div class="stat-label">总代理数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.active_agents }}</div>
          <div class="stat-label">激活代理</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon running">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.running_agents }}</div>
          <div class="stat-label">运行中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><SuccessFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.overall_success_rate }}%</div>
          <div class="stat-label">成功率</div>
        </div>
      </div>
    </div>

    <!-- 搜索和过滤 -->
    <div class="search-section">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索代理名称或描述"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.type" placeholder="代理类型" clearable>
            <el-option label="聊天代理" value="chat" />
            <el-option label="任务代理" value="task" />
            <el-option label="分析代理" value="analysis" />
            <el-option label="测试代理" value="testing" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.status" placeholder="状态" clearable>
            <el-option label="未激活" value="inactive" />
            <el-option label="激活" value="active" />
            <el-option label="运行中" value="running" />
            <el-option label="已停止" value="stopped" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 代理列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="agentList"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="代理名称" min-width="150">
          <template #default="{ row }">
            <div class="agent-name">
              <el-avatar :size="32" :src="getAgentAvatar(row.type)" />
              <div class="name-content">
                <div class="name">{{ row.name }}</div>
                <div class="version">v{{ row.version }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="运行统计" width="120">
          <template #default="{ row }">
            <div class="stats">
              <div class="run-count">{{ row.run_count }} 次</div>
              <div class="success-rate">{{ row.success_rate }}% 成功</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                v-if="row.status === 'active'"
                type="success"
                size="small"
                @click="handleStart(row)"
              >
                启动
              </el-button>
              <el-button
                v-if="row.status === 'running'"
                type="warning"
                size="small"
                @click="handleStop(row)"
              >
                停止
              </el-button>
              <el-button size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button size="small" @click="handleConfig(row)">配置</el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDelete(row)"
                :disabled="row.status === 'running'"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>

    <!-- 批量操作 -->
    <div v-if="selectedAgents.length" class="batch-actions">
      <el-card>
        <div class="batch-content">
          <span>已选择 {{ selectedAgents.length }} 个代理</span>
          <div class="batch-buttons">
            <el-button @click="handleBatchActivate">批量激活</el-button>
            <el-button @click="handleBatchDeactivate">批量停用</el-button>
            <el-button type="danger" @click="handleBatchDelete">批量删除</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingAgent ? '编辑代理' : '创建代理'"
      width="600px"
      @close="handleCloseDialog"
    >
      <el-form
        ref="agentFormRef"
        :model="agentForm"
        :rules="agentFormRules"
        label-width="100px"
      >
        <el-form-item label="代理名称" prop="name">
          <el-input v-model="agentForm.name" placeholder="请输入代理名称" />
        </el-form-item>
        <el-form-item label="代理类型" prop="type">
          <el-select v-model="agentForm.type" placeholder="请选择代理类型">
            <el-option label="聊天代理" value="chat" />
            <el-option label="任务代理" value="task" />
            <el-option label="分析代理" value="analysis" />
            <el-option label="测试代理" value="testing" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本号" prop="version">
          <el-input v-model="agentForm.version" placeholder="例如: 1.0.0" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="agentForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入代理描述"
          />
        </el-form-item>
        <el-form-item label="配置">
          <el-input
            v-model="configJsonStr"
            type="textarea"
            :rows="4"
            placeholder="请输入JSON格式的配置信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingAgent ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { 
  Plus, Search, Refresh, DataBoard, CircleCheck, 
  VideoPlay, SuccessFilled 
} from '@element-plus/icons-vue'
import { agentApi } from '@/api/modules/agent'
import { formatDateTime } from '@/utils/dateFormat'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingAgent = ref(null)
const agentFormRef = ref<FormInstance>()
const selectedAgents = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 统计数据
const statistics = ref({
  total_agents: 0,
  active_agents: 0,
  running_agents: 0,
  overall_success_rate: 0
})

// 代理列表
const agentList = ref([])

// 代理表单
const agentForm = reactive({
  name: '',
  type: '',
  version: '1.0.0',
  description: '',
  config: {}
})

// 配置JSON字符串
const configJsonStr = ref('{}')

// 表单验证规则
const agentFormRules = {
  name: [
    { required: true, message: '请输入代理名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择代理类型', trigger: 'change' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' }
  ]
}

// 生命周期
onMounted(() => {
  loadStatistics()
  loadAgentList()
})

// 方法
const loadStatistics = async () => {
  try {
    const response = await agentApi.getStatistics()
    if (response.code === 200) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadAgentList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      keyword: searchForm.keyword,
      type: searchForm.type,
      status: searchForm.status
    }
    
    const response = await agentApi.searchAgents(params)
    if (response.code === 200) {
      agentList.value = response.data.agents
      pagination.total = response.data.total
    }
  } catch (error) {
    ElMessage.error('加载代理列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadAgentList()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.type = ''
  searchForm.status = ''
  handleSearch()
}

const handleRefresh = () => {
  loadStatistics()
  loadAgentList()
}

const handleSelectionChange = (selection: any[]) => {
  selectedAgents.value = selection
}

const handleStart = async (agent: any) => {
  try {
    const response = await agentApi.startAgent(agent.id)
    if (response.code === 200) {
      ElMessage.success('代理启动成功')
      loadAgentList()
      loadStatistics()
    }
  } catch (error) {
    ElMessage.error('启动代理失败')
  }
}

const handleStop = async (agent: any) => {
  try {
    const response = await agentApi.stopAgent(agent.id)
    if (response.code === 200) {
      ElMessage.success('代理停止成功')
      loadAgentList()
      loadStatistics()
    }
  } catch (error) {
    ElMessage.error('停止代理失败')
  }
}

const handleEdit = (agent: any) => {
  editingAgent.value = agent
  Object.assign(agentForm, {
    name: agent.name,
    type: agent.type,
    version: agent.version,
    description: agent.description,
    config: agent.config || {}
  })
  configJsonStr.value = JSON.stringify(agent.config || {}, null, 2)
  showCreateDialog.value = true
}

const handleConfig = (agent: any) => {
  // 跳转到配置页面
  window.open(`/agent/${agent.id}/config`, '_blank')
}

const handleDelete = async (agent: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除代理 "${agent.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await agentApi.deleteAgent(agent.id)
    if (response.code === 200) {
      ElMessage.success('删除成功')
      loadAgentList()
      loadStatistics()
    }
  } catch (error) {
    // 用户取消删除或删除失败
  }
}

const handleSubmit = async () => {
  if (!agentFormRef.value) return
  
  await agentFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      // 解析配置JSON
      let config = {}
      try {
        config = JSON.parse(configJsonStr.value)
      } catch (e) {
        ElMessage.error('配置JSON格式错误')
        return
      }
      
      const params = {
        ...agentForm,
        config
      }
      
      let response
      if (editingAgent.value) {
        response = await agentApi.updateAgent(editingAgent.value.id, params)
      } else {
        response = await agentApi.createAgent(params)
      }
      
      if (response.code === 200) {
        ElMessage.success(`${editingAgent.value ? '更新' : '创建'}成功`)
        showCreateDialog.value = false
        loadAgentList()
        loadStatistics()
      }
    } catch (error) {
      ElMessage.error(`${editingAgent.value ? '更新' : '创建'}失败`)
    } finally {
      submitting.value = false
    }
  })
}

const handleCloseDialog = () => {
  editingAgent.value = null
  agentFormRef.value?.resetFields()
  configJsonStr.value = '{}'
}

const handleBatchActivate = async () => {
  if (!selectedAgents.value.length) return
  
  try {
    const ids = selectedAgents.value.map((agent: any) => agent.id)
    const response = await agentApi.batchOperation({
      agent_ids: ids,
      operation: 'activate'
    })
    
    if (response.code === 200) {
      ElMessage.success(`批量激活完成: ${response.data.success_count}/${response.data.total} 成功`)
      loadAgentList()
      loadStatistics()
    }
  } catch (error) {
    ElMessage.error('批量激活失败')
  }
}

const handleBatchDeactivate = async () => {
  if (!selectedAgents.value.length) return
  
  try {
    const ids = selectedAgents.value.map((agent: any) => agent.id)
    const response = await agentApi.batchOperation({
      agent_ids: ids,
      operation: 'deactivate'
    })
    
    if (response.code === 200) {
      ElMessage.success(`批量停用完成: ${response.data.success_count}/${response.data.total} 成功`)
      loadAgentList()
      loadStatistics()
    }
  } catch (error) {
    ElMessage.error('批量停用失败')
  }
}

const handleBatchDelete = async () => {
  if (!selectedAgents.value.length) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedAgents.value.length} 个代理吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const ids = selectedAgents.value.map((agent: any) => agent.id)
    const response = await agentApi.batchOperation({
      agent_ids: ids,
      operation: 'delete'
    })
    
    if (response.code === 200) {
      ElMessage.success(`批量删除完成: ${response.data.success_count}/${response.data.total} 成功`)
      loadAgentList()
      loadStatistics()
    }
  } catch (error) {
    // 用户取消或删除失败
  }
}

// 工具方法
const getAgentAvatar = (type: string) => {
  const avatars = {
    chat: '/avatars/chat-agent.png',
    task: '/avatars/task-agent.png',
    analysis: '/avatars/analysis-agent.png',
    testing: '/avatars/testing-agent.png',
    custom: '/avatars/custom-agent.png'
  }
  return avatars[type] || avatars.custom
}

const getTypeLabel = (type: string) => {
  const labels = {
    chat: '聊天',
    task: '任务',
    analysis: '分析',
    testing: '测试',
    custom: '自定义'
  }
  return labels[type] || type
}

const getTypeTagType = (type: string) => {
  const types = {
    chat: 'primary',
    task: 'success',
    analysis: 'warning',
    testing: 'info',
    custom: ''
  }
  return types[type] || ''
}

const getStatusLabel = (status: string) => {
  const labels = {
    inactive: '未激活',
    active: '激活',
    running: '运行中',
    stopped: '已停止',
    error: '错误',
    maintenance: '维护中'
  }
  return labels[status] || status
}

const getStatusTagType = (status: string) => {
  const types = {
    inactive: 'info',
    active: 'success',
    running: 'primary',
    stopped: 'warning',
    error: 'danger',
    maintenance: 'warning'
  }
  return types[status] || 'info'
}
</script>

<style scoped>
.agent-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2329;
}

.header-content p {
  margin: 0;
  color: #646a73;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
}

.stat-icon.total {
  background: #e6f4ff;
  color: #1890ff;
}

.stat-icon.active {
  background: #f6ffed;
  color: #52c41a;
}

.stat-icon.running {
  background: #fff2e8;
  color: #fa8c16;
}

.stat-icon.success {
  background: #f6ffed;
  color: #52c41a;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #1f2329;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #646a73;
  margin-top: 4px;
}

.search-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.agent-name {
  display: flex;
  align-items: center;
}

.name-content {
  margin-left: 12px;
}

.name {
  font-weight: 500;
  color: #1f2329;
}

.version {
  font-size: 12px;
  color: #646a73;
}

.stats .run-count {
  font-size: 12px;
  color: #1f2329;
}

.stats .success-rate {
  font-size: 12px;
  color: #52c41a;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
}

.batch-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 400px;
}

.batch-buttons {
  display: flex;
  gap: 8px;
}
</style>
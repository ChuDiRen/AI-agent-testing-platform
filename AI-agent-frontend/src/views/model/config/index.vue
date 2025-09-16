<!-- AI模型配置管理页面 -->
<template>
  <div class="model-config">
    <div class="page-header">
      <h1>AI模型配置管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        添加配置
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><Setting /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.total_configs }}</div>
          <div class="stat-label">总配置数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon active">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.active_configs }}</div>
          <div class="stat-label">激活配置</div>
        </div>
      </div>
    </div>

    <!-- 搜索过滤 -->
    <div class="search-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-input v-model="searchForm.keyword" placeholder="搜索配置名称" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.provider" placeholder="提供商" clearable>
            <el-option label="OpenAI" value="openai" />
            <el-option label="Azure" value="azure" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Google" value="google" />
            <el-option label="本地" value="local" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 配置列表 -->
    <el-table :data="configList" v-loading="loading" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="配置名称" min-width="150" />
      <el-table-column prop="provider" label="提供商" width="100">
        <template #default="{ row }">
          <el-tag>{{ getProviderLabel(row.provider) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="model_name" label="模型" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="usage_count" label="使用次数" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button @click="handleTest(row)" size="small">测试</el-button>
          <el-button @click="handleEdit(row)" size="small">编辑</el-button>
          <el-button @click="handleDelete(row)" type="danger" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadConfigList"
        @current-change="loadConfigList"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingConfig ? '编辑配置' : '添加配置'" width="600px">
      <el-form :model="configForm" :rules="configRules" ref="configFormRef" label-width="100px">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="configForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="configForm.provider" placeholder="选择提供商" @change="onProviderChange">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Azure OpenAI" value="azure" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Google" value="google" />
            <el-option label="本地模型" value="local" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="configForm.model_name" placeholder="例如: gpt-4" />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="configForm.api_key" type="password" show-password placeholder="请输入API Key" />
        </el-form-item>
        <el-form-item label="API Base" v-if="needsApiBase">
          <el-input v-model="configForm.api_base" placeholder="API Base URL" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最大Token">
              <el-input-number v-model="configForm.max_tokens" :min="1" :max="32000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="温度">
              <el-input-number v-model="configForm.temperature" :min="0" :max="2" :step="0.1" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingConfig ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Setting, CircleCheck } from '@element-plus/icons-vue'
import { modelConfigApi } from '@/api/modules/modelconfig'
import { formatDateTime } from '@/utils/dateFormat'

const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingConfig = ref(null)
const configFormRef = ref()
const configList = ref([])
const selectedConfigs = ref([])

const searchForm = reactive({ keyword: '', provider: '' })
const pagination = reactive({ page: 1, page_size: 20, total: 0 })
const statistics = ref({ total_configs: 0, active_configs: 0 })

const configForm = reactive({
  name: '',
  provider: '',
  model_name: '',
  api_key: '',
  api_base: '',
  max_tokens: 4000,
  temperature: 0.7
})

const configRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }]
}

const needsApiBase = computed(() => {
  return ['azure', 'local'].includes(configForm.provider)
})

onMounted(() => {
  loadStatistics()
  loadConfigList()
})

const loadStatistics = async () => {
  try {
    const response = await modelConfigApi.getStatistics()
    if (response.success) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadConfigList = async () => {
  loading.value = true
  try {
    const params = { ...pagination, ...searchForm }
    const response = await modelConfigApi.getModelConfigList(params)
    if (response.success) {
      configList.value = response.data.model_configs
      pagination.total = response.data.total
    }
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadConfigList()
}

const handleEdit = (config) => {
  editingConfig.value = config
  Object.assign(configForm, config)
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  await configFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingConfig.value) {
        await modelConfigApi.updateModelConfig(editingConfig.value.id, configForm)
      } else {
        await modelConfigApi.createModelConfig(configForm)
      }
      ElMessage.success('操作成功')
      showCreateDialog.value = false
      loadConfigList()
      loadStatistics()
    } catch (error) {
      ElMessage.error('操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const getProviderLabel = (provider) => {
  const labels = { openai: 'OpenAI', azure: 'Azure', anthropic: 'Anthropic', google: 'Google', local: '本地' }
  return labels[provider] || provider
}

const getStatusTagType = (status) => {
  const types = { active: 'success', inactive: 'info', error: 'danger' }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = { active: '激活', inactive: '未激活', error: '错误' }
  return labels[status] || status
}
</script>

<style scoped>
.model-config { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.stat-card { display: flex; align-items: center; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.stat-icon { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 16px; font-size: 24px; }
.stat-icon.total { background: #e6f4ff; color: #1890ff; }
.stat-icon.active { background: #f6ffed; color: #52c41a; }
.stat-number { font-size: 24px; font-weight: 600; color: #1f2329; }
.stat-label { font-size: 14px; color: #646a73; margin-top: 4px; }
.search-section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 16px; }
.pagination { display: flex; justify-content: center; margin-top: 20px; }
</style>
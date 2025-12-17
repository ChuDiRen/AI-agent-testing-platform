<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="提供商">
        <el-select v-model="searchForm.provider" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option v-for="p in providers" :key="p" :label="p" :value="p" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.is_enabled" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option label="已启用" :value="true" />
          <el-option label="已禁用" :value="false" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="AI模型管理"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      v-model:pagination="paginationModel"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="success" @click="handleSync">
          <el-icon><Refresh /></el-icon>
          同步模型
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增模型
        </el-button>
      </template>

      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="model_name" label="模型名称" min-width="150" />
      <el-table-column prop="model_code" label="模型代码" min-width="150" />
      <el-table-column prop="provider" label="提供商" width="120" />
      <el-table-column prop="api_url" label="API地址" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_enabled" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_enabled ? 'success' : 'info'">
            {{ row.is_enabled ? '已启用' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="create_time" label="创建时间" width="160" />
      <el-table-column label="操作" width="280" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleTest(row)">测试连接</el-button>
          <el-button link type="primary" @click="handleToggle(row)">
            {{ row.is_enabled ? '禁用' : '启用' }}
          </el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 表单对话框组件 -->
    <AiModelForm 
      v-model="dialogVisible" 
      :formData="formData"
      @success="handleFormSuccess"
    />

    <!-- 同步模型对话框 -->
    <el-dialog
      v-model="syncDialogVisible"
      title="同步AI模型"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="syncForm" label-width="100px">
        <el-form-item label="同步方式">
          <el-radio-group v-model="syncForm.syncType">
            <el-radio value="single">单个提供商</el-radio>
            <el-radio value="all">全部提供商</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="syncForm.syncType === 'single'" label="提供商">
          <el-select v-model="syncForm.provider" placeholder="请选择提供商" style="width: 100%">
            <el-option 
              v-for="p in syncProviders" 
              :key="p.name" 
              :label="p.display_name" 
              :value="p.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API密钥">
          <el-input 
            v-model="syncForm.api_key" 
            type="password" 
            placeholder="留空则使用环境变量配置"
            show-password
          />
          <div class="form-tip">如果服务器已配置环境变量，可以留空</div>
        </el-form-item>
        
        <el-form-item label="更新选项">
          <el-checkbox v-model="syncForm.update_existing">更新已存在的模型</el-checkbox>
        </el-form-item>
      </el-form>
      
      <!-- 同步结果显示 -->
      <div v-if="syncResult" class="sync-result">
        <el-divider content-position="left">同步结果</el-divider>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="新增模型">
            <el-tag type="success">{{ syncResult.added || 0 }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="更新模型">
            <el-tag type="warning">{{ syncResult.updated || 0 }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="跳过模型">
            <el-tag type="info">{{ syncResult.skipped || 0 }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总计">
            <el-tag>{{ syncResult.total || 0 }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <p class="sync-message" :class="{ 'success': syncResult.success, 'error': !syncResult.success }">
          {{ syncResult.message }}
        </p>
      </div>
      
      <template #footer>
        <el-button @click="syncDialogVisible = false">关闭</el-button>
        <el-button type="primary" :loading="syncLoading" @click="handleDoSync">
          {{ syncLoading ? '同步中...' : '开始同步' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { queryByPage, deleteData, testConnection, toggleStatus, getSyncProviders, syncProvider, syncAllProviders } from './aimodel'
import AiModelForm from './AiModelForm.vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

// 搜索表单
const searchForm = reactive({
  provider: '',
  is_enabled: ''
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 分页模型（适配 BaseTable）
const paginationModel = computed({
  get: () => ({ page: pagination.page, limit: pagination.page_size }),
  set: (val) => {
    pagination.page = val.page
    pagination.page_size = val.limit
  }
})

// 提供商列表
const providers = ref([])

// 对话框控制
const dialogVisible = ref(false)
const formData = ref({})

// 同步相关
const syncDialogVisible = ref(false)
const syncLoading = ref(false)
const syncProviders = ref([])
const syncResult = ref(null)
const syncForm = reactive({
  syncType: 'single',
  provider: 'siliconflow',
  api_key: '',
  update_existing: true
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...(searchForm.provider && { provider: searchForm.provider }),
      ...(searchForm.is_enabled !== '' && { is_enabled: searchForm.is_enabled })
    }
    const res = await queryByPage(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data
      pagination.total = res.data.total
      // 提取提供商列表
      const providerSet = new Set(res.data.data.map(item => item.provider))
      providers.value = Array.from(providerSet)
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 提供商列表已在loadData中提取

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.provider = ''
  searchForm.is_enabled = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  formData.value = {}
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  formData.value = { ...row }
  dialogVisible.value = true
}

// 表单提交成功回调
const handleFormSuccess = () => {
  loadData()
}

// 测试连接
const handleTest = async (row) => {
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在测试连接...',
    background: 'rgba(0, 0, 0, 0.7)'
  })
  try {
    const res = await testConnection(row.id)
    loadingInstance.close()
    if (res.data.code === 200) {
      ElMessage.success('连接测试成功！')
    } else {
      ElMessage.error(res.data.message || res.data.msg || '连接测试失败')
    }
  } catch (error) {
    loadingInstance.close()
    ElMessage.error('连接测试失败: ' + (error.message || '网络错误'))
  }
}

// 切换启用/禁用
const handleToggle = async (row) => {
  try {
    const res = await toggleStatus(row.id)
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || res.data.message)
      loadData()
    } else {
      ElMessage.error(res.data.msg || res.data.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除模型"${row.model_name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await deleteData(row.id)
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// ==================== 同步相关方法 ====================

// 打开同步对话框
const handleSync = async () => {
  syncResult.value = null
  syncDialogVisible.value = true
  
  // 加载提供商列表
  try {
    const res = await getSyncProviders()
    if (res.data.code === 200) {
      syncProviders.value = res.data.data || []
      if (syncProviders.value.length > 0 && !syncForm.provider) {
        syncForm.provider = syncProviders.value[0].name
      }
    }
  } catch (error) {
    console.error('获取提供商列表失败:', error)
  }
}

// 执行同步
const handleDoSync = async () => {
  syncLoading.value = true
  syncResult.value = null
  
  try {
    let res
    if (syncForm.syncType === 'single') {
      // 单个提供商同步
      if (!syncForm.provider) {
        ElMessage.warning('请选择提供商')
        syncLoading.value = false
        return
      }
      
      res = await syncProvider({
        provider: syncForm.provider,
        api_key: syncForm.api_key || undefined,
        update_existing: syncForm.update_existing
      })
    } else {
      // 全部提供商同步
      const apiKeys = {}
      if (syncForm.api_key) {
        // 如果提供了API密钥，应用到当前选择的提供商
        apiKeys[syncForm.provider] = syncForm.api_key
      }
      
      res = await syncAllProviders({
        api_keys: Object.keys(apiKeys).length > 0 ? apiKeys : undefined,
        update_existing: syncForm.update_existing
      })
    }
    
    if (res.data.code === 200) {
      syncResult.value = res.data.data
      ElMessage.success('同步完成')
      // 刷新列表
      loadData()
    } else {
      syncResult.value = {
        success: false,
        message: res.data.message || res.data.msg || '同步失败'
      }
      ElMessage.error(res.data.message || res.data.msg || '同步失败')
    }
  } catch (error) {
    console.error('同步失败:', error)
    syncResult.value = {
      success: false,
      message: error.message || '网络错误'
    }
    ElMessage.error('同步失败: ' + (error.message || '网络错误'))
  } finally {
    syncLoading.value = false
  }
}



// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.sync-result {
  margin-top: 16px;
}

.sync-message {
  margin-top: 12px;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
}

.sync-message.success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.sync-message.error {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>


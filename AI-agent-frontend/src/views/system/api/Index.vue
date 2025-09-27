<template>
  <div class="api-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>API端点管理</h2>
      <p>管理系统中的API端点，监控调用统计和性能数据</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><Operation /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.total_apis }}</div>
                <div class="stat-label">API总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon active">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.active_apis }}</div>
                <div class="stat-label">激活API</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon calls">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.total_calls_today }}</div>
                <div class="stat-label">今日调用</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon response">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.avg_response_time }}ms</div>
                <div class="stat-label">平均响应时间</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="handleCreate" v-permission="'api:create'">
          <el-icon><Plus /></el-icon>
          新增API
        </el-button>
        <el-button @click="handleSync" v-permission="'api:create'">
          <el-icon><Refresh /></el-icon>
          同步路由
        </el-button>
        <el-dropdown @command="handleBatchAction" v-if="selectedRows.length > 0">
          <el-button>
            批量操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="activate">激活</el-dropdown-item>
              <el-dropdown-item command="deactivate">停用</el-dropdown-item>
              <el-dropdown-item command="deprecate">废弃</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索API名称、路径..."
          style="width: 250px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-form :model="searchForm" inline>
        <el-form-item label="HTTP方法">
          <el-select v-model="searchForm.method" placeholder="选择方法" clearable style="width: 120px">
            <el-option
              v-for="method in methods"
              :key="method"
              :label="method"
              :value="method"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable style="width: 120px">
            <el-option
              v-for="(label, value) in API_STATUS_LABELS"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="searchForm.module" placeholder="选择模块" clearable style="width: 150px">
            <el-option
              v-for="module in modules"
              :key="module"
              :label="module"
              :value="module"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="权限">
          <el-select v-model="searchForm.permission" placeholder="选择权限" clearable style="width: 150px">
            <el-option
              v-for="permission in permissions"
              :key="permission"
              :label="permission"
              :value="permission"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- API列表表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="apiList"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="HTTP_METHOD_COLORS[row.method]" size="small">
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="module" label="模块" width="120" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : row.status === 'deprecated' ? 'danger' : 'warning'"
              size="small"
            >
              {{ API_STATUS_LABELS[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_calls" label="调用次数" width="100" />
        <el-table-column prop="success_rate" label="成功率" width="80">
          <template #default="{ row }">
            <span :class="{ 'success-rate-high': row.success_rate >= 95, 'success-rate-low': row.success_rate < 90 }">
              {{ row.success_rate.toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="avg_response_time" label="平均响应时间" width="120">
          <template #default="{ row }">
            {{ row.avg_response_time.toFixed(1) }}ms
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
              v-permission="'api:view'"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEdit(row)"
              v-permission="'api:update'"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              v-permission="'api:delete'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- API详情/编辑对话框 -->
    <ApiDialog
      v-model:visible="dialogVisible"
      :mode="dialogMode"
      :api-data="currentApi"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  ArrowDown,
  Operation,
  CircleCheck,
  DataLine,
  Timer
} from '@element-plus/icons-vue'
import { ApiEndpointApi, type ApiEndpoint, type ApiStatistics, API_STATUS_LABELS, HTTP_METHOD_COLORS } from '@/api/modules/apiEndpoint'
import ApiDialog from './components/ApiDialog.vue'

// 响应式数据
const loading = ref(false)
const apiList = ref<ApiEndpoint[]>([])
const selectedRows = ref<ApiEndpoint[]>([])
const modules = ref<string[]>([])
const permissions = ref<string[]>([])
const methods = ref<string[]>([])

// 统计数据
const statistics = ref<ApiStatistics>({
  total_apis: 0,
  active_apis: 0,
  deprecated_apis: 0,
  maintenance_apis: 0,
  total_calls_today: 0,
  success_calls_today: 0,
  error_calls_today: 0,
  avg_response_time: 0,
  top_apis: [],
  error_apis: []
})

// 搜索表单
const searchForm = reactive({
  keyword: '',
  method: '',
  status: '',
  module: '',
  permission: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('create')
const currentApi = ref<ApiEndpoint | null>(null)

// 生命周期
onMounted(() => {
  loadApiList()
  loadStatistics()
  loadMetadata()
})

// 方法
const loadApiList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    const response = await ApiEndpointApi.getApiEndpoints(params)
    if (response.success && response.data) {
      apiList.value = response.data.items
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('获取API列表失败:', error)
    ElMessage.error('获取API列表失败')
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await ApiEndpointApi.getApiStatistics()
    if (response.success && response.data) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const loadMetadata = async () => {
  try {
    const [modulesRes, permissionsRes, methodsRes] = await Promise.all([
      ApiEndpointApi.getModules(),
      ApiEndpointApi.getPermissions(),
      ApiEndpointApi.getMethods()
    ])
    
    if (modulesRes.success) modules.value = modulesRes.data || []
    if (permissionsRes.success) permissions.value = permissionsRes.data || []
    if (methodsRes.success) methods.value = methodsRes.data || []
  } catch (error) {
    console.error('获取元数据失败:', error)
  }
}

const handleCreate = () => {
  dialogMode.value = 'create'
  currentApi.value = null
  dialogVisible.value = true
}

const handleEdit = (row: ApiEndpoint) => {
  dialogMode.value = 'edit'
  currentApi.value = { ...row }
  dialogVisible.value = true
}

const handleView = (row: ApiEndpoint) => {
  dialogMode.value = 'view'
  currentApi.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row: ApiEndpoint) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除API "${row.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await ApiEndpointApi.deleteApiEndpoint(row.id)
    if (response.success) {
      ElMessage.success('删除成功')
      loadApiList()
      loadStatistics()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleSync = async () => {
  try {
    loading.value = true
    const response = await ApiEndpointApi.syncApiEndpoints()
    if (response.success && response.data) {
      const { new_created, updated, skipped } = response.data
      ElMessage.success(`同步完成：新增${new_created}个，更新${updated}个，跳过${skipped}个`)
      loadApiList()
      loadStatistics()
    }
  } catch (error) {
    console.error('同步失败:', error)
    ElMessage.error('同步失败')
  } finally {
    loading.value = false
  }
}

const handleBatchAction = async (command: string) => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要操作的API')
    return
  }
  
  const statusMap = {
    activate: 'active',
    deactivate: 'inactive',
    deprecate: 'deprecated'
  }
  
  const actionMap = {
    activate: '激活',
    deactivate: '停用',
    deprecate: '废弃'
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要${actionMap[command]}选中的${selectedRows.value.length}个API吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const apiIds = selectedRows.value.map(row => row.id)
    const response = await ApiEndpointApi.batchUpdateStatus(apiIds, statusMap[command])
    
    if (response.success) {
      ElMessage.success(`批量${actionMap[command]}成功`)
      loadApiList()
      loadStatistics()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量操作失败:', error)
      ElMessage.error('批量操作失败')
    }
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadApiList()
}

const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    method: '',
    status: '',
    module: '',
    permission: ''
  })
  pagination.page = 1
  loadApiList()
}

const handleSelectionChange = (selection: ApiEndpoint[]) => {
  selectedRows.value = selection
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadApiList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadApiList()
}

const handleDialogSuccess = () => {
  loadApiList()
  loadStatistics()
  loadMetadata()
}
</script>

<style scoped lang="scss">
.api-management {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h2 {
      margin: 0 0 8px 0;
      color: #303133;
      font-size: 24px;
      font-weight: 600;
    }

    p {
      margin: 0;
      color: #606266;
      font-size: 14px;
    }
  }

  .stats-cards {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;

        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;

          .el-icon {
            font-size: 24px;
            color: white;
          }

          &.total {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          &.active {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }

          &.calls {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }

          &.response {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          }
        }

        .stat-info {
          .stat-value {
            font-size: 24px;
            font-weight: 600;
            color: #303133;
            line-height: 1;
            margin-bottom: 4px;
          }

          .stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .toolbar-left {
      display: flex;
      gap: 12px;
    }

    .toolbar-right {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .filter-bar {
    margin-bottom: 16px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .table-card {
    .success-rate-high {
      color: #67c23a;
      font-weight: 600;
    }

    .success-rate-low {
      color: #f56c6c;
      font-weight: 600;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>

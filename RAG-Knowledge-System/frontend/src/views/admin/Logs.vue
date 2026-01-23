<template>
  <div class="logs-page">
    <div class="page-header">
      <h2>操作日志</h2>
      <div class="header-actions">
        <el-button type="primary" @click="exportLogs" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出日志
        </el-button>
        <el-button type="danger" @click="clearLogs" :loading="clearing">
          <el-icon><Delete /></el-icon>
          清空日志
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filters-card">
      <el-form :model="filters" inline>
        <el-form-item label="用户">
          <el-select
            v-model="filters.userId"
            placeholder="选择用户"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.full_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="操作类型">
          <el-select
            v-model="filters.action"
            placeholder="选择操作"
            clearable
            style="width: 150px"
          >
            <el-option label="用户登录" value="user_login" />
            <el-option label="用户登出" value="user_logout" />
            <el-option label="文档上传" value="document_upload" />
            <el-option label="文档删除" value="document_delete" />
            <el-option label="文档索引" value="document_index" />
            <el-option label="智能问答" value="chat_message" />
            <el-option label="用户创建" value="user_create" />
            <el-option label="用户更新" value="user_update" />
            <el-option label="用户删除" value="user_delete" />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 350px"
          />
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索关键词"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadLogs">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilters">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志列表 -->
    <el-card class="logs-card">
      <el-table
        :data="logs"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="log-detail">
              <div class="detail-item">
                <span class="label">日志ID：</span>
                <span class="value">{{ row.id }}</span>
              </div>
              <div class="detail-item">
                <span class="label">详细信息：</span>
                <pre class="value">{{ JSON.stringify(row.details, null, 2) }}</pre>
              </div>
              <div class="detail-item" v-if="row.ip_address">
                <span class="label">IP地址：</span>
                <span class="value">{{ row.ip_address }}</span>
              </div>
              <div class="detail-item" v-if="row.user_agent">
                <span class="label">用户代理：</span>
                <span class="value">{{ row.user_agent }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="timestamp" label="时间" width="180" fixed="left">
          <template #default="{ row }">
            {{ formatDateTime(row.timestamp) }}
          </template>
        </el-table-column>

        <el-table-column prop="user_name" label="用户" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.user_name" size="small">{{ row.user_name }}</el-tag>
            <span v-else class="system-user">系统</span>
          </template>
        </el-table-column>

        <el-table-column prop="action" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" size="small">
              {{ getActionText(row.action) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="resource" label="资源" width="150" show-overflow-tooltip />

        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />

        <el-table-column prop="ip_address" label="IP地址" width="120" show-overflow-tooltip />

        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="viewLogDetail(row)"
              :icon="View"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="日志详情"
      width="800px"
    >
      <div v-if="currentLog" class="log-detail-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日志ID">
            {{ currentLog.id }}
          </el-descriptions-item>
          <el-descriptions-item label="时间">
            {{ formatDateTime(currentLog.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="用户">
            {{ currentLog.user_name || '系统' }}
          </el-descriptions-item>
          <el-descriptions-item label="操作类型">
            <el-tag :type="getActionType(currentLog.action)">
              {{ getActionText(currentLog.action) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="资源">
            {{ currentLog.resource || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentLog.status === 'success' ? 'success' : 'danger'">
              {{ currentLog.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="IP地址" span="2">
            {{ currentLog.ip_address || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" span="2">
            {{ currentLog.description }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" v-if="currentLog.details">
          <h4>详细信息</h4>
          <pre class="json-content">{{ JSON.stringify(currentLog.details, null, 2) }}</pre>
        </div>

        <div class="detail-section" v-if="currentLog.user_agent">
          <h4>用户代理</h4>
          <p>{{ currentLog.user_agent }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Delete,
  Search,
  RefreshLeft,
  View
} from '@element-plus/icons-vue'
import { getLogs, getUsers } from '../../api/user'

const loading = ref(false)
const exporting = ref(false)
const clearing = ref(false)
const showDetailDialog = ref(false)
const currentLog = ref(null)

const logs = ref([])
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive({
  userId: '',
  action: '',
  dateRange: [],
  keyword: ''
})

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      user_id: filters.userId || undefined,
      action: filters.action || undefined,
      start_time: filters.dateRange?.[0] || undefined,
      end_time: filters.dateRange?.[1] || undefined,
      keyword: filters.keyword || undefined
    }
    
    const response = await getLogs(params)
    logs.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const response = await getUsers({ page_size: 1000 })
    users.value = response.data.items || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const resetFilters = () => {
  Object.assign(filters, {
    userId: '',
    action: '',
    dateRange: [],
    keyword: ''
  })
  currentPage.value = 1
  loadLogs()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadLogs()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadLogs()
}

const viewLogDetail = (log) => {
  currentLog.value = log
  showDetailDialog.value = true
}

const exportLogs = async () => {
  exporting.value = true
  try {
    // 这里应该调用导出API
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('日志导出成功')
  } catch (error) {
    ElMessage.error('日志导出失败')
  } finally {
    exporting.value = false
  }
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    clearing.value = true
    // 这里应该调用清空日志API
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('日志清空成功')
    loadLogs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空日志失败')
    }
  } finally {
    clearing.value = false
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getActionType = (action) => {
  const types = {
    user_login: 'primary',
    user_logout: 'info',
    document_upload: 'success',
    document_delete: 'danger',
    document_index: 'warning',
    chat_message: 'primary',
    user_create: 'success',
    user_update: 'warning',
    user_delete: 'danger'
  }
  return types[action] || 'info'
}

const getActionText = (action) => {
  const texts = {
    user_login: '用户登录',
    user_logout: '用户登出',
    document_upload: '文档上传',
    document_delete: '文档删除',
    document_index: '文档索引',
    chat_message: '智能问答',
    user_create: '用户创建',
    user_update: '用户更新',
    user_delete: '用户删除'
  }
  return texts[action] || action
}

onMounted(() => {
  loadLogs()
  loadUsers()
})
</script>

<style scoped>
.logs-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filters-card,
.logs-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.log-detail {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 4px;
}

.detail-item {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.detail-item .label {
  min-width: 80px;
  color: #606266;
  font-weight: 500;
}

.detail-item .value {
  flex: 1;
  color: #303133;
}

.detail-item pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: white;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.system-user {
  color: #909399;
  font-style: italic;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.log-detail-dialog {
  padding: 20px 0;
}

.detail-section {
  margin-top: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.json-content {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .logs-page {
    padding: 0;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .filters-card .el-form {
    display: block;
  }
  
  .filters-card .el-form-item {
    margin-bottom: 16px;
    display: block;
  }
  
  .filters-card .el-form-item__label {
    display: block;
    margin-bottom: 8px;
  }
}
</style>

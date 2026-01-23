<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>仪表盘</h2>
      <p>系统概览和关键指标</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon documents">
            <el-icon size="32"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalDocuments }}</div>
            <div class="stat-label">总文档数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon users">
            <el-icon size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon messages">
            <el-icon size="32"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalMessages }}</div>
            <div class="stat-label">总问答数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon storage">
            <el-icon size="32"><FolderOpened /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatFileSize(stats.totalStorage) }}</div>
            <div class="stat-label">存储空间</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <h3>文档上传趋势</h3>
            <el-select v-model="uploadPeriod" size="small" style="width: 120px">
              <el-option label="最近7天" value="7d" />
              <el-option label="最近30天" value="30d" />
              <el-option label="最近90天" value="90d" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <div class="chart-placeholder">
            <el-icon size="60" color="#e4e7ed"><TrendCharts /></el-icon>
            <p>文档上传趋势图表</p>
          </div>
        </div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <h3>问答活跃度</h3>
            <el-select v-model="chatPeriod" size="small" style="width: 120px">
              <el-option label="最近7天" value="7d" />
              <el-option label="最近30天" value="30d" />
              <el-option label="最近90天" value="90d" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <div class="chart-placeholder">
            <el-icon size="60" color="#e4e7ed"><DataLine /></el-icon>
            <p>问答活跃度图表</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 最近活动 -->
    <div class="activity-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>最近活动</h3>
            <el-button type="text" @click="refreshActivities">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        
        <el-table :data="recentActivities" style="width: 100%">
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getActivityTypeColor(row.type)">
                {{ getActivityTypeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="description" label="描述" min-width="200" />
          
          <el-table-column prop="user" label="用户" width="120" />
          
          <el-table-column prop="time" label="时间" width="150">
            <template #default="{ row }">
              {{ formatTime(row.time) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-card>
        <template #header>
          <h3>快速操作</h3>
        </template>
        
        <div class="actions-grid">
          <el-button type="primary" @click="$router.push('/admin/documents')">
            <el-icon><Upload /></el-icon>
            上传文档
          </el-button>
          
          <el-button type="success" @click="$router.push('/admin/users')">
            <el-icon><UserFilled /></el-icon>
            添加用户
          </el-button>
          
          <el-button type="warning" @click="$router.push('/admin/settings')">
            <el-icon><Setting /></el-icon>
            系统设置
          </el-button>
          
          <el-button type="info" @click="$router.push('/admin/logs')">
            <el-icon><Document /></el-icon>
            查看日志
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  User,
  ChatDotRound,
  FolderOpened,
  TrendCharts,
  DataLine,
  Refresh,
  Upload,
  UserFilled,
  Setting
} from '@element-plus/icons-vue'

const uploadPeriod = ref('7d')
const chatPeriod = ref('7d')

const stats = reactive({
  totalDocuments: 0,
  totalUsers: 0,
  totalMessages: 0,
  totalStorage: 0
})

const recentActivities = ref([
  {
    type: 'document_upload',
    description: '上传了文档 "产品说明书.pdf"',
    user: '张三',
    time: new Date(Date.now() - 1000 * 60 * 5).toISOString()
  },
  {
    type: 'user_login',
    description: '用户登录系统',
    user: '李四',
    time: new Date(Date.now() - 1000 * 60 * 15).toISOString()
  },
  {
    type: 'chat_message',
    description: '进行了智能问答',
    user: '王五',
    time: new Date(Date.now() - 1000 * 60 * 30).toISOString()
  },
  {
    type: 'document_index',
    description: '重建了文档索引',
    user: '系统',
    time: new Date(Date.now() - 1000 * 60 * 60).toISOString()
  }
])

const loadStats = async () => {
  try {
    // 这里应该调用实际的API获取统计数据
    // 暂时使用模拟数据
    stats.totalDocuments = 156
    stats.totalUsers = 42
    stats.totalMessages = 1289
    stats.totalStorage = 1024 * 1024 * 512 // 512MB
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

const refreshActivities = async () => {
  try {
    // 这里应该调用实际的API获取活动数据
    ElMessage.success('活动列表已刷新')
  } catch (error) {
    ElMessage.error('刷新活动列表失败')
  }
}

const formatFileSize = (size) => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let fileSize = size

  while (fileSize >= 1024 && unitIndex < units.length - 1) {
    fileSize /= 1024
    unitIndex++
  }

  return `${fileSize.toFixed(1)} ${units[unitIndex]}`
}

const formatTime = (timeStr) => {
  const time = new Date(timeStr)
  const now = new Date()
  const diff = now - time

  if (diff < 1000 * 60) {
    return '刚刚'
  } else if (diff < 1000 * 60 * 60) {
    return `${Math.floor(diff / (1000 * 60))}分钟前`
  } else if (diff < 1000 * 60 * 60 * 24) {
    return `${Math.floor(diff / (1000 * 60 * 60))}小时前`
  } else {
    return time.toLocaleDateString('zh-CN')
  }
}

const getActivityTypeColor = (type) => {
  const colors = {
    document_upload: 'success',
    user_login: 'primary',
    chat_message: 'info',
    document_index: 'warning',
    user_create: 'success',
    document_delete: 'danger'
  }
  return colors[type] || 'info'
}

const getActivityTypeText = (type) => {
  const texts = {
    document_upload: '文档上传',
    user_login: '用户登录',
    chat_message: '智能问答',
    document_index: '文档索引',
    user_create: '用户创建',
    document_delete: '文档删除'
  }
  return texts[type] || type
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 32px;
}

.dashboard-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.dashboard-header p {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.documents {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.users {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.messages {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.storage {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.chart-card {
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

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #909399;
}

.chart-placeholder p {
  margin-top: 16px;
  font-size: 14px;
}

.activity-section,
.quick-actions {
  margin-bottom: 32px;
}

.activity-section .el-card,
.quick-actions .el-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.actions-grid .el-button {
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 0;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .chart-container {
    height: 200px;
  }
}
</style>

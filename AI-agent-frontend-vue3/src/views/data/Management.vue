<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="data-management">
    <el-card class="stats-card">
      <template #header>
        <div class="card-header">
          <span>数据库统计</span>
          <el-button type="primary" size="small" @click="loadStats">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <el-row :gutter="20" v-loading="statsLoading">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">数据表数量</div>
            <div class="stat-value">{{ stats.total_tables }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总记录数</div>
            <div class="stat-value">{{ stats.total_records }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">数据库大小</div>
            <div class="stat-value">{{ formatSize(stats.database_size) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">备份数量</div>
            <div class="stat-value">{{ stats.backup_count }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 数据备份 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据备份</span>
              <el-button type="primary" size="small" @click="handleCreateBackup" :loading="backupLoading">
                <el-icon><FolderAdd /></el-icon>
                创建备份
              </el-button>
            </div>
          </template>
          <el-table :data="backupList" v-loading="backupListLoading" max-height="400">
            <el-table-column prop="filename" label="文件名" min-width="200" />
            <el-table-column prop="size" label="大小" width="100">
              <template #default="{ row }">
                {{ formatSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_time" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="danger" size="small" link @click="handleDeleteBackup(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 数据维护 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>数据维护</span>
          </template>
          <div class="maintenance-actions">
            <el-card shadow="hover" class="action-card">
              <div class="action-icon">
                <el-icon :size="32" color="#409EFF"><Delete /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">清理旧数据</div>
                <div class="action-desc">清理30天前的已读通知</div>
                <el-button type="primary" size="small" @click="handleCleanup" :loading="cleanupLoading">
                  执行清理
                </el-button>
              </div>
            </el-card>

            <el-card shadow="hover" class="action-card">
              <div class="action-icon">
                <el-icon :size="32" color="#67C23A"><Tools /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">优化数据库</div>
                <div class="action-desc">压缩数据库文件,提升性能</div>
                <el-button type="success" size="small" @click="handleOptimize" :loading="optimizeLoading">
                  执行优化
                </el-button>
              </div>
            </el-card>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 表统计详情 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>数据表统计</span>
      </template>
      <el-table :data="stats.table_stats" v-loading="statsLoading" max-height="300">
        <el-table-column prop="table" label="表名" />
        <el-table-column prop="records" label="记录数" width="150" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, FolderAdd, Delete, Tools } from '@element-plus/icons-vue'
import {
  getDatabaseStats,
  getBackupList,
  createBackup,
  deleteBackup,
  cleanupData,
  optimizeDatabase,
  type DatabaseStats,
  type BackupFile
} from '@/api/data'

// 统计数据
const stats = ref<DatabaseStats>({
  total_tables: 0,
  total_records: 0,
  database_size: 0,
  backup_count: 0,
  table_stats: []
})
const statsLoading = ref(false)

// 备份列表
const backupList = ref<BackupFile[]>([])
const backupListLoading = ref(false)
const backupLoading = ref(false)

// 维护操作
const cleanupLoading = ref(false)
const optimizeLoading = ref(false)

// 加载统计数据
const loadStats = async () => {
  try {
    statsLoading.value = true
    const response = await getDatabaseStats()
    if (response.success && response.data) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    statsLoading.value = false
  }
}

// 加载备份列表
const loadBackupList = async () => {
  try {
    backupListLoading.value = true
    const response = await getBackupList()
    if (response.success && response.data) {
      backupList.value = response.data
    }
  } catch (error) {
    console.error('加载备份列表失败:', error)
  } finally {
    backupListLoading.value = false
  }
}

// 创建备份
const handleCreateBackup = async () => {
  try {
    await ElMessageBox.confirm('确定要创建数据库备份吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    backupLoading.value = true
    const response = await createBackup()
    
    if (response.success) {
      ElMessage.success(response.message || '备份创建成功')
      await loadBackupList()
      await loadStats()
    } else {
      ElMessage.error(response.message || '备份创建失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('备份创建失败')
    }
  } finally {
    backupLoading.value = false
  }
}

// 删除备份
const handleDeleteBackup = async (backup: BackupFile) => {
  try {
    await ElMessageBox.confirm(`确定要删除备份文件 ${backup.filename} 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await deleteBackup(backup.filename)
    
    if (response.success) {
      ElMessage.success(response.message || '备份删除成功')
      await loadBackupList()
      await loadStats()
    } else {
      ElMessage.error(response.message || '备份删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('备份删除失败')
    }
  }
}

// 清理数据
const handleCleanup = async () => {
  try {
    await ElMessageBox.confirm('确定要清理30天前的已读通知吗?此操作不可恢复!', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    cleanupLoading.value = true
    const response = await cleanupData(30)
    
    if (response.success) {
      ElMessage.success(response.message || '数据清理成功')
      await loadStats()
    } else {
      ElMessage.error(response.message || '数据清理失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('数据清理失败')
    }
  } finally {
    cleanupLoading.value = false
  }
}

// 优化数据库
const handleOptimize = async () => {
  try {
    await ElMessageBox.confirm('确定要优化数据库吗?此操作可能需要一些时间。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    optimizeLoading.value = true
    const response = await optimizeDatabase()
    
    if (response.success) {
      ElMessage.success(response.message || '数据库优化成功')
      await loadStats()
    } else {
      ElMessage.error(response.message || '数据库优化失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('数据库优化失败')
    }
  } finally {
    optimizeLoading.value = false
  }
}

// 格式化文件大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 格式化时间
const formatTime = (time: string): string => {
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadStats()
  loadBackupList()
})
</script>

<style scoped>
.data-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.maintenance-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.action-card {
  display: flex;
  align-items: center;
  padding: 15px;
}

.action-icon {
  margin-right: 15px;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.action-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}
</style>


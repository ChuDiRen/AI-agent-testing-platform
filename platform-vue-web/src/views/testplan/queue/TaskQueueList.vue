<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <el-card shadow="never" class="stat-card running">
        <div class="stat-icon">
          <el-icon :size="32"><VideoPlay /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.running }}</div>
          <div class="stat-label">正在执行</div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card waiting">
        <div class="stat-icon">
          <el-icon :size="32"><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.waiting }}</div>
          <div class="stat-label">队列等待</div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card completed">
        <div class="stat-icon">
          <el-icon :size="32"><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.completed }}</div>
          <div class="stat-label">今日完成</div>
        </div>
      </el-card>
      <el-card shadow="never" class="stat-card failed">
        <div class="stat-icon">
          <el-icon :size="32"><CircleClose /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.failed }}</div>
          <div class="stat-label">今日失败</div>
        </div>
      </el-card>
    </div>

    <!-- 当前执行任务 -->
    <el-card shadow="never" class="mb-4" v-if="runningTask">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-bold text-blue-600">
            <el-icon class="mr-1"><Loading /></el-icon>
            当前执行中
          </span>
          <el-button type="danger" size="small" @click="handleStop(runningTask)">
            <el-icon><VideoPause /></el-icon>停止执行
          </el-button>
        </div>
      </template>
      <div class="running-task">
        <div class="flex items-center justify-between mb-4">
          <div>
            <span class="text-lg font-bold">{{ runningTask.task_name }}</span>
            <el-tag size="small" class="ml-2" :type="runningTask.type === 'web' ? 'success' : 'primary'">
              {{ runningTask.type === 'web' ? 'Web 自动化' : '接口测试' }}
            </el-tag>
          </div>
          <span class="text-gray-500">提交人: {{ runningTask.submitter }}</span>
        </div>
        <el-progress 
          :percentage="runningTask.progress" 
          :stroke-width="20"
          :format="(p) => `${runningTask.current}/${runningTask.total} (${p}%)`"
        />
        <div class="flex items-center justify-between mt-4 text-sm text-gray-500">
          <span>开始时间: {{ runningTask.start_time }}</span>
          <span>已运行: {{ runningTask.duration }}</span>
          <span>预计剩余: {{ runningTask.remaining }}</span>
        </div>
      </div>
    </el-card>

    <!-- 队列列表 -->
    <BaseTable
      title="执行队列"
      :data="tableData"
      :total="total"
      :loading="loading"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="danger" :disabled="tableData.length === 0" @click="handleClearQueue">
          <el-icon><Delete /></el-icon>清空队列
        </el-button>
        <el-button @click="loadData">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </template>

      <el-table-column prop="position" label="位置" width="80" align="center">
        <template #default="scope">
          <el-tag size="small" :type="scope.$index === 0 ? 'danger' : 'info'">
            #{{ scope.$index + 1 }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="优先级" width="100">
        <template #default="scope">
          <el-tag :type="getPriorityTag(scope.row.priority)" size="small">
            {{ getPriorityName(scope.row.priority) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="task_name" label="任务名称" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="scope">
          <el-tag effect="plain" size="small" :type="scope.row.type === 'web' ? 'success' : 'primary'">
            {{ scope.row.type === 'web' ? 'Web 自动化' : '接口测试' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="case_count" label="用例数" width="80" align="center" />
      <el-table-column prop="submitter" label="提交人" width="100" />
      <el-table-column prop="submit_time" label="提交时间" width="160" />
      <el-table-column prop="wait_time" label="等待时间" width="120">
        <template #default="scope">
          <span class="text-orange-500">{{ scope.row.wait_time }}</span>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="180">
        <template #default="scope">
          <el-button link type="primary" @click="handleMoveUp(scope.row)" :disabled="scope.$index === 0">
            上移
          </el-button>
          <el-button link type="primary" @click="handleMoveTop(scope.row)" :disabled="scope.$index === 0">
            置顶
          </el-button>
          <el-button link type="danger" @click="handleCancel(scope.row)">取消</el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  VideoPlay, Clock, CircleCheck, CircleClose, Loading, 
  VideoPause, Delete, Refresh 
} from '@element-plus/icons-vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { getQueueList, cancelQueueTask, clearQueue, moveQueueTask, stopRunningTask } from './queue'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const runningTask = ref(null)
let refreshTimer = null

const stats = reactive({
  running: 1,
  waiting: 0,
  completed: 12,
  failed: 2
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getQueueList()
    if (res?.data?.code === 200) {
      tableData.value = res.data.data.queue || []
      runningTask.value = res.data.data.running || null
      stats.waiting = tableData.value.length
      stats.running = runningTask.value ? 1 : 0
      stats.completed = res.data.data.completed_today || 12
      stats.failed = res.data.data.failed_today || 2
      total.value = tableData.value.length
    } else {
      mockData()
    }
  } catch (e) {
    mockData()
  } finally {
    loading.value = false
  }
}

const mockData = () => {
  runningTask.value = {
    id: 100,
    task_name: 'API 核心流程回归测试',
    type: 'api',
    submitter: 'admin',
    start_time: '2026-01-06 14:30:00',
    duration: '5m 23s',
    remaining: '约 3m',
    progress: 65,
    current: 29,
    total: 45
  }
  
  tableData.value = [
    { id: 101, priority: 'high', task_name: '紧急线上巡检', type: 'api', case_count: 15, submitter: 'admin', submit_time: '2026-01-06 14:32:00', wait_time: '3m 15s' },
    { id: 102, priority: 'normal', task_name: 'Web 冒烟测试计划', type: 'web', case_count: 28, submitter: 'tester1', submit_time: '2026-01-06 14:28:00', wait_time: '7m 05s' },
    { id: 103, priority: 'low', task_name: '用户中心功能验证', type: 'web', case_count: 18, submitter: 'dev', submit_time: '2026-01-06 14:20:00', wait_time: '15m 23s' }
  ]
  
  stats.waiting = tableData.value.length
  stats.running = 1
  total.value = tableData.value.length
}

const getPriorityTag = (priority) => {
  const map = { high: 'danger', normal: 'info', low: 'success' }
  return map[priority] || 'info'
}

const getPriorityName = (priority) => {
  const map = { high: '极高', normal: '普通', low: '低' }
  return map[priority] || priority
}

// 停止当前执行
const handleStop = (task) => {
  ElMessageBox.confirm('确定要停止当前正在执行的任务吗？已执行的用例结果将被保留。', '警告', {
    type: 'warning'
  }).then(async () => {
    try {
      await stopRunningTask(task.id)
      ElMessage.success('已停止执行')
      loadData()
    } catch (e) {
      ElMessage.success('已停止执行 (Mock)')
      runningTask.value = null
      loadData()
    }
  })
}

// 取消排队任务
const handleCancel = (row) => {
  ElMessageBox.confirm(`确定取消任务 "${row.task_name}" 的排队吗？`, '提示').then(async () => {
    try {
      await cancelQueueTask(row.id)
      ElMessage.success('已取消任务')
      loadData()
    } catch (e) {
      ElMessage.success('已取消任务 (Mock)')
      tableData.value = tableData.value.filter(item => item.id !== row.id)
      stats.waiting--
      total.value--
    }
  })
}

// 上移任务
const handleMoveUp = async (row) => {
  try {
    await moveQueueTask(row.id, 'up')
    ElMessage.success('已上移')
    loadData()
  } catch (e) {
    ElMessage.success('已上移 (Mock)')
    const index = tableData.value.findIndex(item => item.id === row.id)
    if (index > 0) {
      const temp = tableData.value[index]
      tableData.value[index] = tableData.value[index - 1]
      tableData.value[index - 1] = temp
    }
  }
}

// 置顶任务
const handleMoveTop = async (row) => {
  try {
    await moveQueueTask(row.id, 'top')
    ElMessage.success('已置顶')
    loadData()
  } catch (e) {
    ElMessage.success('已置顶 (Mock)')
    const index = tableData.value.findIndex(item => item.id === row.id)
    if (index > 0) {
      const task = tableData.value.splice(index, 1)[0]
      tableData.value.unshift(task)
    }
  }
}

// 清空队列
const handleClearQueue = () => {
  ElMessageBox.confirm('确定清空所有排队任务吗？此操作不可恢复！', '警告', {
    type: 'error'
  }).then(async () => {
    try {
      await clearQueue()
      ElMessage.success('队列已清空')
      loadData()
    } catch (e) {
      ElMessage.success('队列已清空 (Mock)')
      tableData.value = []
      stats.waiting = 0
      total.value = 0
    }
  })
}

// 自动刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    loadData()
  }, 10000) // 每10秒刷新一次
}

onMounted(() => {
  loadData()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-card.running {
  background: linear-gradient(135deg, #e6f4ff 0%, #bae0ff 100%);
  border-color: #91caff;
}

.stat-card.waiting {
  background: linear-gradient(135deg, #fff7e6 0%, #ffd591 100%);
  border-color: #ffc069;
}

.stat-card.completed {
  background: linear-gradient(135deg, #f6ffed 0%, #b7eb8f 100%);
  border-color: #95de64;
}

.stat-card.failed {
  background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
  border-color: #ffa39e;
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  margin-right: 16px;
}

.stat-card.running .stat-icon {
  color: #1677ff;
}

.stat-card.waiting .stat-icon {
  color: #fa8c16;
}

.stat-card.completed .stat-icon {
  color: #52c41a;
}

.stat-card.failed .stat-icon {
  color: #ff4d4f;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  line-height: 1.2;
}

.stat-card.running .stat-value {
  color: #1677ff;
}

.stat-card.waiting .stat-value {
  color: #fa8c16;
}

.stat-card.completed .stat-value {
  color: #52c41a;
}

.stat-card.failed .stat-value {
  color: #ff4d4f;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.running-task {
  padding: 10px 0;
}
</style>

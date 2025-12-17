<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="queryForm" :loading="loading" @search="handleQuery" @reset="handleReset">
      <el-form-item label="项目" prop="project_id">
        <el-select v-model="queryForm.project_id" placeholder="选择项目" clearable filterable style="width: 150px">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="任务名称" prop="task_name">
        <el-input v-model="queryForm.task_name" placeholder="任务名称" clearable style="width: 150px" />
      </el-form-item>
      <el-form-item label="任务类型" prop="task_type">
        <el-select v-model="queryForm.task_type" placeholder="任务类型" clearable style="width: 120px">
          <el-option label="手动任务" value="manual" />
          <el-option label="定时任务" value="scheduled" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="task_status">
        <el-select v-model="queryForm.task_status" placeholder="状态" clearable style="width: 120px">
          <el-option label="待执行" value="pending" />
          <el-option label="执行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
          <el-option label="已禁用" value="disabled" />
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增任务
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="测试任务"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="handleQuery"
    >
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="task_name" label="任务名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="task_type" label="类型" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.task_type === 'scheduled' ? 'warning' : ''">
            {{ scope.row.task_type === 'scheduled' ? '定时' : '手动' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="plan_name" label="关联计划" width="150" show-overflow-tooltip>
        <template #default="scope">
          {{ scope.row.plan_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="case_count" label="用例数" width="80" align="center" />
      <el-table-column prop="executor_code" label="执行引擎" width="110" align="center">
        <template #default="scope">
          <el-tag size="small" :type="getEngineTagType(scope.row.executor_code)">
            {{ getEngineShortName(scope.row.executor_code) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="task_status" label="状态" width="90" align="center">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.task_status)">
            {{ getStatusText(scope.row.task_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行统计" width="140" align="center">
        <template #default="scope">
          <span class="stat-text">
            {{ scope.row.run_count }}次 
            <span class="success-text">{{ scope.row.success_count }}成功</span>
            <span class="fail-text" v-if="scope.row.fail_count > 0">{{ scope.row.fail_count }}失败</span>
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="last_run_time" label="上次执行" width="160" show-overflow-tooltip>
        <template #default="scope">
          {{ scope.row.last_run_time || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button 
            link 
            type="success" 
            @click="handleExecute(scope.row)" 
            :disabled="scope.row.task_status === 'disabled' || scope.row.task_status === 'running'"
          >
            执行
          </el-button>
          <el-button link type="info" @click="handleViewExecutions(scope.row)">记录</el-button>
          <el-button 
            link 
            :type="scope.row.task_status === 'disabled' ? 'success' : 'warning'" 
            @click="handleToggleStatus(scope.row)"
          >
            {{ scope.row.task_status === 'disabled' ? '启用' : '禁用' }}
          </el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 执行记录弹窗 -->
    <el-dialog v-model="executionDialogVisible" title="执行记录" width="900px" destroy-on-close>
      <el-table :data="executionList" v-loading="executionLoading" max-height="400">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="execution_uuid" label="执行批次" width="150" show-overflow-tooltip />
        <el-table-column prop="trigger_type" label="触发类型" width="90" align="center">
          <template #default="scope">
            <el-tag size="small">{{ getTriggerTypeText(scope.row.trigger_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag :type="getExecutionStatusType(scope.row.status)" size="small">
              {{ getExecutionStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用例统计" width="150" align="center">
          <template #default="scope">
            <span>{{ scope.row.total_cases }}总 </span>
            <span class="success-text">{{ scope.row.passed_cases }}通过 </span>
            <span class="fail-text">{{ scope.row.failed_cases }}失败</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时(秒)" width="90" align="center">
          <template #default="scope">
            {{ scope.row.duration || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="160" />
      </el-table>
      <template #footer>
        <el-button @click="executionDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, executeTask, updateStatus, queryExecutions } from './testTask.js'
import { queryAll as queryProjects } from '~/views/apitest/project/apiProject.js'
import { useRouter } from 'vue-router'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 查询表单
const queryForm = reactive({
  project_id: null,
  task_name: '',
  task_type: null,
  task_status: null
})

// 表格数据
const tableData = ref([])

// 项目列表
const projectList = ref([])

// 执行记录相关
const executionDialogVisible = ref(false)
const executionList = ref([])
const executionLoading = ref(false)
const currentTaskId = ref(null)

// 获取引擎简称
const getEngineShortName = (pluginCode) => {
  const names = {
    'api_engine': 'API引擎',
    'web_engine': 'Web引擎',
    'perf_engine': '性能引擎'
  }
  return names[pluginCode] || pluginCode
}

// 获取引擎标签类型
const getEngineTagType = (pluginCode) => {
  const types = {
    'api_engine': '',
    'web_engine': 'success',
    'perf_engine': 'warning'
  }
  return types[pluginCode] || 'info'
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'disabled': ''
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    'pending': '待执行',
    'running': '执行中',
    'completed': '已完成',
    'failed': '失败',
    'disabled': '已禁用'
  }
  return texts[status] || status
}

// 获取触发类型文本
const getTriggerTypeText = (type) => {
  const texts = {
    'manual': '手动',
    'scheduled': '定时',
    'api': '接口'
  }
  return texts[type] || type
}

// 获取执行状态类型
const getExecutionStatusType = (status) => {
  const types = {
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'info'
  }
  return types[status] || 'info'
}

// 获取执行状态文本
const getExecutionStatusText = (status) => {
  const texts = {
    'running': '执行中',
    'completed': '已完成',
    'failed': '失败',
    'cancelled': '已取消'
  }
  return texts[status] || status
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await queryProjects()
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 查询数据
const handleQuery = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      ...queryForm,
      page: pagination.value.page,
      pageSize: pagination.value.limit
    })
    if (res.data.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    } else {
      ElMessage.error(res.data.msg || '查询失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置
const handleReset = () => {
  queryForm.project_id = null
  queryForm.task_name = ''
  queryForm.task_type = null
  queryForm.task_status = null
  pagination.value.page = 1
  handleQuery()
}

// 新增
const handleCreate = () => {
  router.push('/TestTaskForm')
}

// 编辑
const handleEdit = (row) => {
  router.push({
    path: '/TestTaskForm',
    query: { id: row.id }
  })
}

// 执行任务
const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm(`确定执行任务 "${row.task_name}" 吗？`, '提示', {
      type: 'warning'
    })

    const res = await executeTask({
      task_id: row.id,
      trigger_type: 'manual'
    })

    if (res.data.code === 200) {
      ElMessage.success(`任务已提交执行，共 ${res.data.data?.total_cases || 0} 个用例`)
      handleQuery()
    } else {
      ElMessage.error(res.data.msg || '执行失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('执行失败:', error)
      ElMessage.error('执行失败，请稍后重试')
    }
  }
}

// 查看执行记录
const handleViewExecutions = async (row) => {
  currentTaskId.value = row.id
  executionDialogVisible.value = true
  executionLoading.value = true
  
  try {
    const res = await queryExecutions({
      task_id: row.id,
      page: 1,
      pageSize: 20
    })
    if (res.data.code === 200) {
      executionList.value = res.data.data || []
    }
  } catch (error) {
    console.error('查询执行记录失败:', error)
  } finally {
    executionLoading.value = false
  }
}

// 切换状态
const handleToggleStatus = async (row) => {
  const newStatus = row.task_status === 'disabled' ? 'pending' : 'disabled'
  const actionText = newStatus === 'disabled' ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(`确定${actionText}任务 "${row.task_name}" 吗？`, '提示', {
      type: 'warning'
    })

    const res = await updateStatus(row.id, newStatus)
    if (res.data.code === 200) {
      ElMessage.success(`${actionText}成功`)
      handleQuery()
    } else {
      ElMessage.error(res.data.msg || `${actionText}失败`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除任务 "${row.task_name}" 吗？`, '提示', {
      type: 'warning'
    })

    const res = await deleteData(row.id)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      handleQuery()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

onMounted(() => {
  loadProjects()
  handleQuery()
})
</script>

<style scoped>
@import '~/styles/common-list.css';

.stat-text {
  font-size: 12px;
}

.success-text {
  color: #67c23a;
}

.fail-text {
  color: #f56c6c;
}
</style>

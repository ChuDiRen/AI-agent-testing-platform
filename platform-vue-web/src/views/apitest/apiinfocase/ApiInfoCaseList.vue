<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="queryForm" :loading="loading" @search="handleQuery" @reset="handleReset">
      <el-form-item label="项目" prop="project_id">
        <el-select v-model="queryForm.project_id" placeholder="选择项目" clearable filterable style="width: 180px">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="用例名称" prop="case_name">
        <el-input v-model="queryForm.case_name" placeholder="用例名称" clearable style="width: 180px" />
      </el-form-item>
      <template #actions>
        <el-button type="warning" :disabled="selectedRows.length === 0" @click="handleBatchAddToPlan">
          <el-icon><FolderAdd /></el-icon>
          添加到计划 ({{ selectedRows.length }})
        </el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增用例
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="测试用例"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="handleQuery"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="case_name" label="用例名称" show-overflow-tooltip />
      <el-table-column prop="case_desc" label="用例描述" show-overflow-tooltip />
      <el-table-column prop="project_id" label="项目" width="120">
        <template #default="scope">
          {{ getProjectName(scope.row.project_id) }}
        </template>
      </el-table-column>
      <el-table-column label="使用引擎" width="150">
        <template #default="scope">
          <div class="engine-tags">
            <el-tag 
              v-for="engine in (scope.row.engines || [])" 
              :key="engine"
              size="small"
              :type="getEngineTagType(engine)"
              style="margin-right: 4px"
            >
              {{ getEngineIcon(engine) }} {{ getEngineShortName(engine) }}
            </el-tag>
            <span v-if="!scope.row.engines || scope.row.engines.length === 0" class="no-engine">-</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="170" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button link type="success" @click="handleExecute(scope.row)" :loading="scope.row.executing">
            执行
          </el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 批量添加到计划弹窗 -->
    <el-dialog v-model="batchAddDialogVisible" title="添加用例到测试计划" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择计划" required>
          <el-select v-model="selectedPlanId" placeholder="请选择测试计划" filterable style="width: 100%">
            <el-option
              v-for="plan in planList"
              :key="plan.id"
              :label="plan.plan_name"
              :value="plan.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="已选用例">
          <div class="selected-cases">
            <el-tag v-for="row in selectedRows" :key="row.id" size="small" style="margin: 2px;">
              {{ row.case_name }}
            </el-tag>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchAddDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchAdding" @click="confirmBatchAdd">确定添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, FolderAdd } from '@element-plus/icons-vue'
import { queryByPage, deleteData, getCaseEngines, executeCase } from './apiInfoCase.js'
import { queryAll as queryProjects } from '../project/apiProject.js'
import { useRouter } from 'vue-router'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { queryByPage as queryPlans, batchAddCases } from '../testplan/testPlan.js'

const router = useRouter()

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 查询表单
const queryForm = reactive({
  project_id: null,
  case_name: ''
})

// 表格数据
const tableData = ref([])

// 项目列表
const projectList = ref([])

// 批量添加到计划相关
const selectedRows = ref([])
const batchAddDialogVisible = ref(false)
const selectedPlanId = ref(null)
const planList = ref([])
const batchAdding = ref(false)

// 获取引擎图标
const getEngineIcon = (pluginCode) => {
  const icons = {
    'api_engine': '📡',
    'web_engine': '🌐',
    'perf_engine': '⚡'
  }
  return icons[pluginCode] || '🔧'
}

// 获取引擎简称
const getEngineShortName = (pluginCode) => {
  const names = {
    'api_engine': 'API',
    'web_engine': 'Web',
    'perf_engine': 'Perf'
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

// 加载测试计划列表
const loadPlans = async () => {
  try {
    const res = await queryPlans({ page: 1, pageSize: 100 })
    if (res.data.code === 200) {
      planList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载测试计划列表失败:', error)
  }
}

// 表格选择变化
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 打开批量添加到计划弹窗
const handleBatchAddToPlan = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择用例')
    return
  }
  selectedPlanId.value = null
  batchAddDialogVisible.value = true
}

// 确认批量添加
const confirmBatchAdd = async () => {
  if (!selectedPlanId.value) {
    ElMessage.warning('请选择测试计划')
    return
  }
  
  batchAdding.value = true
  try {
    const caseIds = selectedRows.value.map(row => row.id)
    const res = await batchAddCases({
      plan_id: selectedPlanId.value,
      case_ids: caseIds
    })
    
    if (res.data.code === 200) {
      ElMessage.success(`成功添加 ${res.data.data?.added_count || caseIds.length} 个用例到计划`)
      batchAddDialogVisible.value = false
      selectedRows.value = []
    } else {
      ElMessage.error(res.data.msg || '添加失败')
    }
  } catch (error) {
    console.error('批量添加失败:', error)
    ElMessage.error('添加失败，请稍后重试')
  } finally {
    batchAdding.value = false
  }
}

// 获取项目名称
const getProjectName = (projectId) => {
  const project = projectList.value.find(p => p.id === projectId)
  return project ? project.project_name : '-'
}

// 加载用例使用的引擎
const loadCaseEngines = async (caseId) => {
  try {
    const res = await getCaseEngines(caseId)
    if (res.data.code === 200 && res.data.data) {
      return res.data.data.engines?.map(e => e.plugin_code) || []
    }
  } catch (error) {
    console.error('加载用例引擎失败:', error)
  }
  return []
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
      
      // 异步加载每个用例的引擎信息
      tableData.value.forEach(async (row) => {
        row.engines = await loadCaseEngines(row.id)
      })
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
  queryForm.case_name = ''
  pagination.value.page = 1
  handleQuery()
}

// 新增
const handleCreate = () => {
  router.push('/ApiInfoCaseForm')
}

// 编辑
const handleEdit = (row) => {
  router.push({
    path: '/ApiInfoCaseForm',
    query: { id: row.id }
  })
}

// 执行用例（自动检测引擎）
const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm(`确定执行用例 "${row.case_name}" 吗？\n系统将自动识别执行引擎`, '提示', {
      type: 'warning'
    })

    row.executing = true

    // 调用后端统一执行接口，不传 executor_code，后端自动检测
    const res = await executeCase({
      case_id: row.id,
      test_name: row.case_name
      // executor_code 不传，后端自动检测
    })

    if (res.data.code === 200) {
      const executor = res.data.data?.executor || '自动检测'
      ElMessage.success(`用例已提交执行 (引擎: ${executor})`)
      // 跳转到测试历史页面查看执行结果
      setTimeout(() => {
        router.push('/ApiHistoryList')
      }, 1000)
    } else {
      ElMessage.error(res.data.msg || '执行失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('执行失败:', error)
      ElMessage.error('执行失败，请稍后重试')
    }
  } finally {
    row.executing = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除用例 "${row.case_name}" 吗？`, '提示', {
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
  loadPlans()
  handleQuery()
})
</script>

<style scoped>
@import '~/styles/common-list.css';

.engine-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
}

.no-engine {
  color: #909399;
  font-size: 12px;
}
</style>


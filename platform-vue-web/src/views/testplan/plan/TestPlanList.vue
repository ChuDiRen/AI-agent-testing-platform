<template>
  <div class="page-container">
    <BaseSearch :model="searchForm" @search="loadData" @reset="resetSearch">
      <el-form-item label="计划名称">
        <el-input v-model="searchForm.name" placeholder="请输入计划名称" clearable />
      </el-form-item>
      <el-form-item label="测试类型">
        <el-select v-model="searchForm.type" placeholder="全部" clearable>
          <el-option label="API 测试" value="api" />
          <el-option label="Web 测试" value="web" />
          <el-option label="混合测试" value="mixed" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
          <el-option label="已归档" value="archived" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="测试计划管理"
      :data="tableData"
      :total="total"
      :loading="loading"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
      @selection-change="handleSelectionChange"
      type="selection"
    >
      <template #header>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>新建计划
        </el-button>
        <el-button 
          type="danger" 
          :disabled="selectedRows.length === 0"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedRows.length }})
        </el-button>
      </template>

      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="计划名称" min-width="180" show-overflow-tooltip>
        <template #default="scope">
          <span class="text-blue-600 cursor-pointer hover:underline" @click="handleDetail(scope.row)">
            {{ scope.row.name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="测试类型" width="100">
        <template #default="scope">
          <el-tag size="small" :type="getTypeTag(scope.row.type)">
            {{ getTypeName(scope.row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="case_count" label="用例数" width="80" align="center" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag size="small" :type="getStatusTag(scope.row.status)">
            {{ getStatusName(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_run" label="最近执行" width="160" />
      <el-table-column prop="pass_rate" label="通过率" width="120">
        <template #default="scope">
          <el-progress 
            :percentage="scope.row.pass_rate || 0" 
            :color="getPassRateColor(scope.row.pass_rate)"
            :stroke-width="10"
          />
        </template>
      </el-table-column>
      <el-table-column prop="creator" label="创建人" width="100" />
      <el-table-column prop="create_time" label="创建时间" width="160" />
      <el-table-column fixed="right" label="操作" width="280">
        <template #default="scope">
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button link type="success" @click="handleExecute(scope.row)">执行</el-button>
          <el-button link type="warning" @click="handleCopy(scope.row)">复制</el-button>
          <el-button link type="info" @click="handleHistory(scope.row)">历史</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 新建/编辑弹窗 -->
    <el-dialog 
      v-model="formVisible" 
      :title="currentPlan.id ? '编辑测试计划' : '新建测试计划'" 
      width="700px"
      destroy-on-close
    >
      <el-form :model="currentPlan" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="currentPlan.name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item label="测试类型" prop="type">
          <el-select v-model="currentPlan.type" class="w-full">
            <el-option label="API 测试" value="api" />
            <el-option label="Web 测试" value="web" />
            <el-option label="混合测试" value="mixed" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划描述" prop="description">
          <el-input 
            v-model="currentPlan.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入计划描述"
          />
        </el-form-item>
        <el-form-item label="执行环境">
          <el-select v-model="currentPlan.env" class="w-full">
            <el-option label="开发环境" value="dev" />
            <el-option label="测试环境" value="test" />
            <el-option label="预发布环境" value="staging" />
            <el-option label="生产环境" value="prod" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知配置">
          <el-checkbox-group v-model="currentPlan.notify">
            <el-checkbox label="email">邮件通知</el-checkbox>
            <el-checkbox label="wechat">企业微信</el-checkbox>
            <el-checkbox label="dingtalk">钉钉</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="失败策略">
          <el-radio-group v-model="currentPlan.fail_strategy">
            <el-radio label="continue">继续执行</el-radio>
            <el-radio label="stop">停止执行</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 执行弹窗 -->
    <el-dialog v-model="executeVisible" title="执行测试计划" width="500px">
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="执行环境">
          <el-select v-model="executeForm.env" class="w-full">
            <el-option label="开发环境" value="dev" />
            <el-option label="测试环境" value="test" />
            <el-option label="预发布环境" value="staging" />
            <el-option label="生产环境" value="prod" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行模式">
          <el-radio-group v-model="executeForm.mode">
            <el-radio label="all">执行全部用例</el-radio>
            <el-radio label="failed">仅执行失败用例</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="并发数">
          <el-input-number v-model="executeForm.concurrency" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute">开始执行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { getPlanList, deletePlan, batchDeletePlan, savePlan, copyPlan, executePlan } from './plan'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const selectedRows = ref([])
const formVisible = ref(false)
const executeVisible = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  name: '',
  type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  limit: 10
})

const currentPlan = reactive({
  id: null,
  name: '',
  type: 'api',
  description: '',
  env: 'test',
  notify: ['wechat'],
  fail_strategy: 'continue'
})

const executeForm = reactive({
  plan_id: null,
  env: 'test',
  mode: 'all',
  concurrency: 1
})

const formRules = {
  name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择测试类型', trigger: 'change' }]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getPlanList({ ...searchForm, ...pagination })
    if (res?.data?.code === 200) {
      tableData.value = res.data.data.list
      total.value = res.data.data.total
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
  tableData.value = [
    { id: 1, name: 'API 核心流程回归', type: 'api', case_count: 45, status: 'published', last_run: '2026-01-06 10:30:00', pass_rate: 95, creator: 'admin', create_time: '2025-12-20 09:00:00' },
    { id: 2, name: 'Web 冒烟测试计划', type: 'web', case_count: 28, status: 'published', last_run: '2026-01-05 14:20:00', pass_rate: 88, creator: 'tester', create_time: '2025-12-22 11:30:00' },
    { id: 3, name: '混合场景端到端测试', type: 'mixed', case_count: 120, status: 'draft', last_run: null, pass_rate: 0, creator: 'dev', create_time: '2025-12-25 16:45:00' },
    { id: 4, name: '支付模块专项测试', type: 'api', case_count: 35, status: 'published', last_run: '2026-01-04 08:00:00', pass_rate: 100, creator: 'admin', create_time: '2025-12-28 10:00:00' },
    { id: 5, name: '用户中心功能验证', type: 'web', case_count: 18, status: 'archived', last_run: '2025-12-30 17:30:00', pass_rate: 72, creator: 'tester', create_time: '2025-12-15 14:20:00' }
  ]
  total.value = 5
}

const resetSearch = () => {
  Object.assign(searchForm, { name: '', type: '', status: '' })
  loadData()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 类型和状态映射
const getTypeTag = (type) => {
  const map = { api: 'primary', web: 'success', mixed: 'warning' }
  return map[type] || 'info'
}

const getTypeName = (type) => {
  const map = { api: 'API', web: 'Web', mixed: '混合' }
  return map[type] || type
}

const getStatusTag = (status) => {
  const map = { draft: 'info', published: 'success', archived: 'warning' }
  return map[status] || 'info'
}

const getStatusName = (status) => {
  const map = { draft: '草稿', published: '已发布', archived: '已归档' }
  return map[status] || status
}

const getPassRateColor = (rate) => {
  if (rate >= 90) return '#67c23a'
  if (rate >= 70) return '#e6a23c'
  return '#f56c6c'
}

// 新建计划
const handleCreate = () => {
  Object.assign(currentPlan, {
    id: null,
    name: '',
    type: 'api',
    description: '',
    env: 'test',
    notify: ['wechat'],
    fail_strategy: 'continue'
  })
  formVisible.value = true
}

// 编辑计划
const handleEdit = (row) => {
  Object.assign(currentPlan, row)
  formVisible.value = true
}

// 保存计划
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    await savePlan(currentPlan)
    ElMessage.success('保存成功')
    formVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.success('保存成功 (Mock)')
    formVisible.value = false
    loadData()
  }
}

// 查看详情
const handleDetail = (row) => {
  router.push({
    path: '/TestPlanDetail',
    query: { id: row.id }
  })
}

// 执行计划
const handleExecute = (row) => {
  executeForm.plan_id = row.id
  executeForm.env = row.env || 'test'
  executeForm.mode = 'all'
  executeForm.concurrency = 1
  executeVisible.value = true
}

const confirmExecute = async () => {
  try {
    await executePlan(executeForm)
    ElMessage.success('测试计划已提交执行')
    executeVisible.value = false
    // 跳转到执行历史
    router.push({
      path: '/ApiHistoryList',
      query: { plan_id: executeForm.plan_id }
    })
  } catch (e) {
    ElMessage.success('测试计划已提交执行 (Mock)')
    executeVisible.value = false
  }
}

// 复制计划
const handleCopy = async (row) => {
  try {
    await copyPlan(row.id)
    ElMessage.success('复制成功')
    loadData()
  } catch (e) {
    ElMessage.success('复制成功 (Mock)')
    // Mock 添加新数据
    const newPlan = { ...row, id: Date.now(), name: `${row.name} (副本)`, status: 'draft' }
    tableData.value.unshift(newPlan)
    total.value++
  }
}

// 查看历史
const handleHistory = (row) => {
  router.push({
    path: '/ApiHistoryList',
    query: { plan_id: row.id }
  })
}

// 删除计划
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除测试计划 "${row.name}" 吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deletePlan(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('删除成功 (Mock)')
      tableData.value = tableData.value.filter(item => item.id !== row.id)
      total.value--
    }
  })
}

// 批量删除
const handleBatchDelete = () => {
  const ids = selectedRows.value.map(row => row.id)
  ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 个测试计划吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeletePlan(ids)
      ElMessage.success('批量删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('批量删除成功 (Mock)')
      tableData.value = tableData.value.filter(row => !ids.includes(row.id))
      total.value -= ids.length
    }
  })
}

onMounted(() => loadData())
</script>

<style scoped>
@import '~/styles/common-list.css';
</style>

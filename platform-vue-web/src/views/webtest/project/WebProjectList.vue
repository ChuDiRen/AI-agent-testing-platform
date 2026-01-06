<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch 
      :model="searchForm" 
      @search="handleSearch" 
      @reset="resetSearch"
    >
      <el-form-item label="项目名称">
        <el-input v-model="searchForm.project_name" placeholder="请输入项目名称" clearable />
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="Web 项目管理"
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
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增项目
        </el-button>
        <el-button 
          type="danger" 
          @click="onBatchDelete"
          :disabled="selectedRows.length === 0"
        >
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedRows.length > 0 ? selectedRows.length : 0 }})
        </el-button>
      </template>

      <el-table-column prop="id" label="项目编号" width="100" />
      <el-table-column prop="project_name" label="项目名称" show-overflow-tooltip>
        <template #default="scope">
          <span class="font-medium text-blue-600 cursor-pointer hover:underline" @click="handleDetail(scope.row)">
            {{ scope.row.project_name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="project_desc" label="项目描述" show-overflow-tooltip />
      <el-table-column prop="case_count" label="用例数量" width="100" align="center" />
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="180">
        <template #default="scope">
          <el-button link type="primary" @click.prevent="onDataForm(scope.$index)">编辑</el-button>
          <el-button link type="primary" @click.prevent="handleExecution(scope.row)">执行测试</el-button>
          <el-button link type="danger" @click.prevent="onDelete(scope.$index)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 表单弹窗 -->
    <WebProjectForm ref="formRef" @success="loadData" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import WebProjectForm from './WebProjectForm.vue'
import { getWebProjectList, deleteWebProject, batchDeleteWebProject } from './webProject'
import { formatDateTime } from '~/utils/timeFormatter'

const router = useRouter()
const formRef = ref(null)

// 搜索表单
const searchForm = reactive({
  project_name: ''
})

// 分页配置
const pagination = reactive({
  page: 1,
  limit: 10
})

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const selectedRows = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 使用 Mock 数据，如果后端接口没好
    const res = await getWebProjectList({
      ...searchForm,
      ...pagination
    })
    
    // 如果返回 404，使用 Mock
    if (res?.data?.code === 200) {
      tableData.value = res.data.data.list
      total.value = res.data.data.total
    } else {
      mockData()
    }
  } catch (error) {
    console.error('获取列表失败:', error)
    mockData()
  } finally {
    loading.value = false
  }
}

// Mock 数据
const mockData = () => {
  tableData.value = [
    { id: 1, project_name: '商城系统 Web 测试', project_desc: '针对商城前端页面的自动化测试项目', case_count: 45, create_time: '2025-12-20T10:00:00' },
    { id: 2, project_name: '用户中心 UI 校验', project_desc: '用户注册、登录及个人中心页面的 UI 测试', case_count: 28, create_time: '2025-12-22T14:30:00' },
    { id: 3, project_name: '后台管理系统自动化', project_desc: '管理后台各项功能的冒烟测试', case_count: 120, create_time: '2025-12-25T09:15:00' }
  ]
  total.value = 3
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const resetSearch = () => {
  searchForm.project_name = ''
  handleSearch()
}

// 选中行
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 打开表单
const onDataForm = (index) => {
  const data = index > -1 ? tableData.value[index] : null
  formRef.value.open(data)
}

// 删除
const onDelete = (index) => {
  const row = tableData.value[index]
  ElMessageBox.confirm('确定要删除该项目吗？将会删除关联的所有用例和元素。', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteWebProject(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      // Mock 删除成功
      ElMessage.success('删除成功 (Mock)')
      tableData.value.splice(index, 1)
      total.value--
    }
  })
}

// 批量删除
const onBatchDelete = () => {
  const ids = selectedRows.value.map(row => row.id)
  ElMessageBox.confirm(`确定要批量删除这 ${ids.length} 个项目吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeleteWebProject(ids)
      ElMessage.success('批量删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('批量删除成功 (Mock)')
      tableData.value = tableData.value.filter(row => !ids.includes(row.id))
      total.value -= ids.length
    }
  })
}

// 进入详情（用例管理）
const handleDetail = (row) => {
  router.push({
    path: '/WebCaseList',
    query: { project_id: row.id, project_name: row.project_name }
  })
}

// 执行测试
const handleExecution = (row) => {
  router.push({
    path: '/WebExecution',
    query: { project_id: row.id }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}
</style>

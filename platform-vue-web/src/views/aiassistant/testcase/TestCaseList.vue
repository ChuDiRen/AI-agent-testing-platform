<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="项目">
        <el-select v-model="searchForm.project_id" placeholder="全部项目" clearable style="width: 200px">
          <el-option label="全部项目" value="" />
          <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="测试类型">
        <el-select v-model="searchForm.test_type" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option label="API" value="API" />
          <el-option label="Web" value="Web" />
          <el-option label="App" value="App" />
          <el-option label="通用" value="通用" />
        </el-select>
      </el-form-item>
      <el-form-item label="优先级">
        <el-select v-model="searchForm.priority" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option label="P0" value="P0" />
          <el-option label="P1" value="P1" />
          <el-option label="P2" value="P2" />
          <el-option label="P3" value="P3" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="测试用例管理"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      :pagination="paginationModel"
      @update:pagination="paginationModel = $event"
      @refresh="loadData"
      @selection-change="handleSelectionChange"
    >
      <template #header>
        <el-button type="success" :disabled="selectedIds.length === 0" @click="handleBatchExport">
          <el-icon><Download /></el-icon>
          批量导出YAML
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增用例
        </el-button>
      </template>

      <el-table-column type="selection" width="55" align="center" />
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="case_name" label="用例名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="test_type" label="测试类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getTestTypeColor(row.test_type)">{{ row.test_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="优先级" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="getPriorityColor(row.priority)">{{ row.priority }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="case_format" label="格式" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.case_format === 'yaml' ? 'warning' : 'success'">
            {{ row.case_format?.toUpperCase() || 'JSON' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module_name" label="模块" width="120" show-overflow-tooltip />
      <el-table-column prop="expected_result" label="预期结果" min-width="200" show-overflow-tooltip />
      <el-table-column prop="create_time" label="创建时间" width="160" />
      <el-table-column label="操作" width="300" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleView(row)">查看</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleCopy(row)">复制</el-button>
          <el-button link type="primary" @click="handleExport(row)">导出YAML</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 表单对话框组件 -->
    <TestCaseForm 
      v-model="dialogVisible" 
      :formData="formData"
      :viewMode="viewMode"
      :projects="projects"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import { queryByPage, deleteData, exportYaml, exportBatchYaml } from './testcase'
import { queryAllProject as getProjects } from '~/views/apitest/project/apiProject.js'
import TestCaseForm from './TestCaseForm.vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

// 搜索表单
const searchForm = reactive({
  project_id: '',
  test_type: '',
  priority: ''
})

// 表格数据
const tableData = ref([])
const loading = ref(false)
const selectedIds = ref([])

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

// 项目列表
const projects = ref([])

// 对话框控制
const dialogVisible = ref(false)
const formData = ref({})
const viewMode = ref(false)

// 测试类型颜色
const getTestTypeColor = (type) => {
  const colorMap = { 'API': 'success', 'Web': 'primary', 'App': 'warning', '通用': 'info' }
  return colorMap[type] || 'info'
}

// 优先级颜色
const getPriorityColor = (priority) => {
  const colorMap = { 'P0': 'danger', 'P1': 'warning', 'P2': '', 'P3': 'info' }
  return colorMap[priority] || 'info'
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await getProjects()
    if (res.data.code === 200) {
      projects.value = res.data.data
    }
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const data = {
      page: pagination.page,
      pageSize: pagination.page_size,
      project_id: searchForm.project_id || null,
      test_type: searchForm.test_type || null,
      priority: searchForm.priority || null
    }
    const res = await queryByPage(data)
    if (res.data.code === 200) {
      tableData.value = res.data.data
      pagination.total = res.data.total
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.project_id = ''
  searchForm.test_type = ''
  searchForm.priority = ''
  handleSearch()
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

// 新增
const handleAdd = () => {
  viewMode.value = false
  formData.value = {}
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  viewMode.value = true
  formData.value = { ...row }
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  viewMode.value = false
  formData.value = { ...row }
  dialogVisible.value = true
}

// 表单提交成功回调
const handleFormSuccess = () => {
  loadData()
}

// 复制
const handleCopy = (row) => {
  viewMode.value = false
  const copyData = { ...row }
  delete copyData.id
  copyData.case_name = `${row.case_name}_副本`
  formData.value = copyData
  dialogVisible.value = true
}

// 导出YAML
const handleExport = async (row) => {
  try {
    const res = await exportYaml(row.id)
    const blob = new Blob([res.data], { type: 'application/x-yaml' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${row.case_name}.yaml`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 批量导出
const handleBatchExport = async () => {
  try {
    const res = await exportBatchYaml(selectedIds.value)
    const blob = new Blob([res.data], { type: 'application/x-yaml' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test_cases_batch.yaml`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success(`成功导出${selectedIds.value.length}个测试用例`)
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除用例"${row.case_name}"吗？`, '提示', {
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



// 初始化
onMounted(() => {
  loadProjects()
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.card-header div {
  display: flex;
  gap: 10px;
}
</style>


<template>
  <div class="test-case-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目">
          <el-select v-model="searchForm.project_id" placeholder="全部项目" clearable @change="handleSearch" style="width: 200px">
            <el-option label="全部项目" value="" />
            <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试类型">
          <el-select v-model="searchForm.test_type" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="API" value="API" />
            <el-option label="Web" value="Web" />
            <el-option label="App" value="App" />
            <el-option label="通用" value="通用" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleSearch">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="handleReset">重置</el-button>
          <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增用例</el-button>
          <el-button type="success" icon="el-icon-download" :disabled="selectedIds.length === 0" @click="handleBatchExport">批量导出YAML</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table 
        :data="tableData" 
        v-loading="loading" 
        border 
        stripe 
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
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
            <el-button type="text" icon="el-icon-view" @click="handleView(row)">查看</el-button>
            <el-button type="text" icon="el-icon-edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="text" icon="el-icon-document-copy" @click="handleCopy(row)">复制</el-button>
            <el-button type="text" icon="el-icon-download" @click="handleExport(row)">导出YAML</el-button>
            <el-button type="text" icon="el-icon-delete" style="color: #f56c6c" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="pagination.page"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.page_size"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
        style="margin-top: 20px; text-align: right"
      />
    </el-card>

    <!-- 查看/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="900px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用例名称" prop="case_name">
              <el-input v-model="form.case_name" placeholder="请输入用例名称" :disabled="viewMode" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属项目" prop="project_id">
              <el-select v-model="form.project_id" placeholder="请选择项目" :disabled="viewMode" style="width: 100%">
                <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="测试类型" prop="test_type">
              <el-select v-model="form.test_type" placeholder="请选择" :disabled="viewMode" style="width: 100%">
                <el-option label="API" value="API" />
                <el-option label="Web" value="Web" />
                <el-option label="App" value="App" />
                <el-option label="通用" value="通用" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择" :disabled="viewMode" style="width: 100%">
                <el-option label="P0" value="P0" />
                <el-option label="P1" value="P1" />
                <el-option label="P2" value="P2" />
                <el-option label="P3" value="P3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="模块名称">
              <el-input v-model="form.module_name" placeholder="请输入模块名称" :disabled="viewMode" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="前置条件">
          <el-input v-model="form.precondition" type="textarea" :rows="2" placeholder="请输入前置条件" :disabled="viewMode" />
        </el-form-item>
        <el-form-item label="测试步骤" prop="test_steps">
          <JsonEditor 
            v-model="testStepsJson" 
            title="测试步骤（JSON数组格式）" 
            :readonly="viewMode"
            :show-preview="false"
            @save="handleStepsSave"
          />
        </el-form-item>
        <el-form-item label="预期结果" prop="expected_result">
          <el-input v-model="form.expected_result" type="textarea" :rows="3" placeholder="请输入预期结果" :disabled="viewMode" />
        </el-form-item>
        <el-form-item label="测试数据">
          <JsonEditor 
            v-model="testDataJson" 
            title="测试数据（JSON格式）" 
            :readonly="viewMode"
            :show-preview="false"
            @save="handleDataSave"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ viewMode ? '关闭' : '取消' }}</el-button>
        <el-button v-if="!viewMode" type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryByPage, queryById, insertData, updateData, deleteData, exportYaml, exportBatchYaml } from './testcase'
import { queryAll as getProjects } from '../../apitest/project/project'
import JsonEditor from '@/components/JsonEditor.vue'

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

// 项目列表
const projects = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增用例')
const isEdit = ref(false)
const viewMode = ref(false)
const submitLoading = ref(false)

// 表单
const formRef = ref(null)
const form = reactive({
  id: null,
  case_name: '',
  project_id: null,
  module_name: '',
  test_type: 'API',
  priority: 'P1',
  precondition: '',
  test_steps: '',
  expected_result: '',
  test_data: '',
  case_format: 'json'
})

const testStepsJson = ref([])
const testDataJson = ref({})

// 表单验证规则
const rules = {
  case_name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  test_type: [{ required: true, message: '请选择测试类型', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  test_steps: [{ required: true, message: '请输入测试步骤', trigger: 'blur' }],
  expected_result: [{ required: true, message: '请输入预期结果', trigger: 'blur' }]
}

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
  isEdit.value = false
  viewMode.value = false
  dialogTitle.value = '新增用例'
  resetForm()
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  viewMode.value = true
  dialogTitle.value = '查看用例'
  loadFormData(row)
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  viewMode.value = false
  dialogTitle.value = '编辑用例'
  loadFormData(row)
  dialogVisible.value = true
}

// 加载表单数据
const loadFormData = (row) => {
  Object.assign(form, row)
  
  // 解析JSON字段
  try {
    testStepsJson.value = row.test_steps ? JSON.parse(row.test_steps) : []
  } catch (e) {
    testStepsJson.value = []
  }
  
  try {
    testDataJson.value = row.test_data ? JSON.parse(row.test_data) : {}
  } catch (e) {
    testDataJson.value = {}
  }
}

// 测试步骤保存回调
const handleStepsSave = (data) => {
  form.test_steps = JSON.stringify(data)
}

// 测试数据保存回调
const handleDataSave = (data) => {
  form.test_data = JSON.stringify(data)
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    // 确保JSON字段被序列化
    form.test_steps = JSON.stringify(testStepsJson.value)
    form.test_data = JSON.stringify(testDataJson.value)
    
    submitLoading.value = true
    
    const data = { ...form }
    delete data.id
    delete data.create_time
    delete data.modify_time
    delete data.created_by
    
    let res
    if (isEdit.value) {
      data.id = form.id
      res = await updateData(data)
    } else {
      res = await insertData(data)
    }
    
    if (res.data.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.data.message || '操作失败')
    }
  } catch (error) {
    console.error('提交失败', error)
  } finally {
    submitLoading.value = false
  }
}

// 复制
const handleCopy = (row) => {
  isEdit.value = false
  viewMode.value = false
  dialogTitle.value = '复制用例'
  loadFormData(row)
  form.id = null
  form.case_name = `${row.case_name}_副本`
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

// 重置表单
const resetForm = () => {
  form.id = null
  form.case_name = ''
  form.project_id = null
  form.module_name = ''
  form.test_type = 'API'
  form.priority = 'P1'
  form.precondition = ''
  form.test_steps = ''
  form.expected_result = ''
  form.test_data = ''
  form.case_format = 'json'
  testStepsJson.value = []
  testDataJson.value = {}
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.clearValidate()
  resetForm()
}

// 分页处理
const handleSizeChange = (val) => {
  pagination.page_size = val
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadData()
}

// 初始化
onMounted(() => {
  loadProjects()
  loadData()
})
</script>

<style scoped>
.test-case-list {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 0;
}

.table-card {
  margin-top: 20px;
}
</style>


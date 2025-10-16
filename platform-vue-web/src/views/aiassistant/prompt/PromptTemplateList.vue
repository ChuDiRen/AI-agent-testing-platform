<template>
  <div class="prompt-template-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="测试类型">
          <el-select v-model="searchForm.test_type" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="API" value="API" />
            <el-option label="Web" value="Web" />
            <el-option label="App" value="App" />
            <el-option label="通用" value="通用" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="searchForm.template_type" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="system" value="system" />
            <el-option label="user" value="user" />
            <el-option label="assistant" value="assistant" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="已激活" :value="true" />
            <el-option label="已停用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleSearch">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="handleReset">重置</el-button>
          <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增模板</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="模板名称" min-width="200" />
        <el-table-column prop="template_type" label="模板类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getTemplateTypeColor(row.template_type)">
              {{ row.template_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="test_type" label="测试类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.test_type">{{ row.test_type }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="模板内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '已激活' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="text" icon="el-icon-view" @click="handleView(row)">查看</el-button>
            <el-button type="text" icon="el-icon-edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="text" 
              :icon="row.is_active ? 'el-icon-circle-close' : 'el-icon-circle-check'" 
              @click="handleToggle(row)">
              {{ row.is_active ? '停用' : '激活' }}
            </el-button>
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
      width="800px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入模板名称" :disabled="viewMode" />
        </el-form-item>
        <el-form-item label="模板类型" prop="template_type">
          <el-select v-model="form.template_type" placeholder="请选择" :disabled="viewMode" style="width: 100%">
            <el-option label="system" value="system" />
            <el-option label="user" value="user" />
            <el-option label="assistant" value="assistant" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试类型" prop="test_type">
          <el-select v-model="form.test_type" placeholder="请选择" :disabled="viewMode" style="width: 100%">
            <el-option label="API" value="API" />
            <el-option label="Web" value="Web" />
            <el-option label="App" value="App" />
            <el-option label="通用" value="通用" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="请输入模板内容，支持变量如{case_count}" :disabled="viewMode" />
        </el-form-item>
        <el-form-item label="变量说明">
          <el-input v-model="form.variables" placeholder='如:["case_count", "test_type"]' :disabled="viewMode" />
        </el-form-item>
        <el-form-item label="是否激活" prop="is_active">
          <el-switch v-model="form.is_active" :disabled="viewMode" />
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
import { queryByPage, queryById, insertData, updateData, deleteData, toggleActive, queryByTestType } from './prompttemplate'

// 搜索表单
const searchForm = reactive({
  test_type: '',
  template_type: '',
  is_active: ''
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增模板')
const isEdit = ref(false)
const viewMode = ref(false)
const submitLoading = ref(false)

// 表单
const formRef = ref(null)
const form = reactive({
  id: null,
  name: '',
  template_type: 'system',
  test_type: 'API',
  content: '',
  variables: '',
  is_active: true
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  template_type: [{ required: true, message: '请选择模板类型', trigger: 'change' }],
  test_type: [{ required: true, message: '请选择测试类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入模板内容', trigger: 'blur' }]
}

// 模板类型颜色
const getTemplateTypeColor = (type) => {
  const colorMap = {
    'system': '',
    'user': 'success',
    'assistant': 'warning'
  }
  return colorMap[type] || 'info'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...(searchForm.test_type && { test_type: searchForm.test_type }),
      ...(searchForm.template_type && { template_type: searchForm.template_type }),
      ...(searchForm.is_active !== '' && { is_active: searchForm.is_active })
    }
    const res = await queryByPage(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data.items
      pagination.total = res.data.data.total
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
  searchForm.test_type = ''
  searchForm.template_type = ''
  searchForm.is_active = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  viewMode.value = false
  dialogTitle.value = '新增模板'
  resetForm()
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  viewMode.value = true
  dialogTitle.value = '查看模板'
  Object.assign(form, row)
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  viewMode.value = false
  dialogTitle.value = '编辑模板'
  Object.assign(form, row)
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    const data = { ...form }
    if (isEdit.value) {
      delete data.create_time
      delete data.modify_time
      delete data.created_by
    } else {
      delete data.id
      delete data.create_time
      delete data.modify_time
      delete data.created_by
    }
    
    let res
    if (isEdit.value) {
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

// 切换激活/停用
const handleToggle = async (row) => {
  try {
    const res = await toggleActive(row.id, !row.is_active)
    if (res.data.code === 200) {
      ElMessage.success(res.data.message)
      loadData()
    } else {
      ElMessage.error(res.data.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除模板"${row.name}"吗？`, '提示', {
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
  form.name = ''
  form.template_type = 'system'
  form.test_type = 'API'
  form.content = ''
  form.variables = ''
  form.is_active = true
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
  loadData()
})
</script>

<style scoped>
.prompt-template-list {
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


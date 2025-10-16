<template>
  <div class="ai-model-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="提供商">
          <el-select v-model="searchForm.provider" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option v-for="p in providers" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_enabled" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value="" />
            <el-option label="已启用" :value="true" />
            <el-option label="已禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleSearch">搜索</el-button>
          <el-button icon="el-icon-refresh" @click="handleReset">重置</el-button>
          <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增模型</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="model_name" label="模型名称" min-width="150" />
        <el-table-column prop="model_code" label="模型代码" min-width="150" />
        <el-table-column prop="provider" label="提供商" width="120" />
        <el-table-column prop="api_url" label="API地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_enabled" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled ? 'success' : 'info'">
              {{ row.is_enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="text" icon="el-icon-edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="text" icon="el-icon-connection" @click="handleTest(row)">测试连接</el-button>
            <el-button type="text" 
              :icon="row.is_enabled ? 'el-icon-circle-close' : 'el-icon-circle-check'" 
              @click="handleToggle(row)">
              {{ row.is_enabled ? '禁用' : '启用' }}
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

    <!-- 编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="form.model_name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型代码" prop="model_code">
          <el-input v-model="form.model_code" placeholder="如:deepseek-chat" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-input v-model="form.provider" placeholder="如:DeepSeek" />
        </el-form-item>
        <el-form-item label="API地址" prop="api_url">
          <el-input v-model="form.api_url" placeholder="请输入API地址" />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="form.api_key" type="password" show-password placeholder="请输入API Key" />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_enabled">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入模型描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryByPage, queryById, insertData, updateData, deleteData, toggleEnable, testConnection } from './aimodel'

// 搜索表单
const searchForm = reactive({
  provider: '',
  is_enabled: ''
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

// 提供商列表
const providers = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增模型')
const isEdit = ref(false)
const submitLoading = ref(false)

// 表单
const formRef = ref(null)
const form = reactive({
  id: null,
  model_name: '',
  model_code: '',
  provider: '',
  api_url: '',
  api_key: '',
  is_enabled: true,
  description: ''
})

// 表单验证规则
const rules = {
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  model_code: [{ required: true, message: '请输入模型代码', trigger: 'blur' }],
  provider: [{ required: true, message: '请输入提供商', trigger: 'blur' }],
  api_url: [{ required: true, message: '请输入API地址', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...(searchForm.provider && { provider: searchForm.provider }),
      ...(searchForm.is_enabled !== '' && { is_enabled: searchForm.is_enabled })
    }
    const res = await queryByPage(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data.items
      pagination.total = res.data.data.total
      // 提取提供商列表
      const providerSet = new Set(res.data.data.items.map(item => item.provider))
      providers.value = Array.from(providerSet)
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 提供商列表已在loadData中提取

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.provider = ''
  searchForm.is_enabled = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增模型'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑模型'
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
    } else {
      delete data.id
      delete data.create_time
      delete data.modify_time
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

// 测试连接
const handleTest = async (row) => {
  const loading = ElMessage.loading('正在测试连接...')
  try {
    const res = await testConnection(row.id)
    loading.close()
    if (res.data.code === 200) {
      ElMessage.success('连接测试成功！')
    } else {
      ElMessage.error(res.data.message || '连接测试失败')
    }
  } catch (error) {
    loading.close()
    ElMessage.error('连接测试失败')
  }
}

// 切换启用/禁用
const handleToggle = async (row) => {
  try {
    const res = await toggleEnable(row.id, !row.is_enabled)
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
  ElMessageBox.confirm(`确定要删除模型"${row.model_name}"吗？`, '提示', {
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
  form.model_name = ''
  form.model_code = ''
  form.provider = ''
  form.api_url = ''
  form.api_key = ''
  form.is_enabled = true
  form.description = ''
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
.ai-model-list {
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


<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <div class="search-container">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目">
          <el-select v-model="searchForm.project_id" placeholder="选择项目" clearable @change="handleSearch">
            <el-option v-for="item in projectList" :key="item.id" :label="item.project_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="环境名称">
          <el-input v-model="searchForm.env_name" placeholder="请输入环境名称" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="环境代码">
          <el-select v-model="searchForm.env_code" placeholder="选择环境" clearable>
            <el-option label="开发环境" value="dev" />
            <el-option label="测试环境" value="test" />
            <el-option label="生产环境" value="prod" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格区域 -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">环境管理</span>
        <div class="table-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增环境
          </el-button>
          <el-button @click="handleInitDefault" :disabled="!searchForm.project_id">
            <el-icon><MagicStick /></el-icon>初始化默认环境
          </el-button>
        </div>
      </div>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="env_name" label="环境名称" min-width="150">
          <template #default="{ row }">
            <el-tag :type="getEnvTagType(row.env_code)" effect="plain">
              {{ row.env_name }}
            </el-tag>
            <el-tag v-if="row.is_default === 1" type="success" size="small" class="ml-2">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="env_code" label="环境代码" width="100" />
        <el-table-column prop="base_url" label="基础URL" min-width="200" show-overflow-tooltip />
        <el-table-column label="环境变量" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="showVariables(row)">
              {{ getVariableCount(row.env_variables) }} 个
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.is_enabled" :active-value="1" :inactive-value="0" 
                       @change="handleToggleEnabled(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleSetDefault(row)" :disabled="row.is_default === 1">
              设为默认
            </el-button>
            <el-button link type="primary" @click="handleCopy(row)">复制</el-button>
            <el-popconfirm title="确定删除该环境吗？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="formData.project_id" placeholder="选择项目" :disabled="isEdit">
            <el-option v-for="item in projectList" :key="item.id" :label="item.project_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="环境名称" prop="env_name">
          <el-input v-model="formData.env_name" placeholder="请输入环境名称" />
        </el-form-item>
        <el-form-item label="环境代码" prop="env_code">
          <el-select v-model="formData.env_code" placeholder="选择或输入环境代码" filterable allow-create>
            <el-option label="dev - 开发环境" value="dev" />
            <el-option label="test - 测试环境" value="test" />
            <el-option label="prod - 生产环境" value="prod" />
            <el-option label="uat - UAT环境" value="uat" />
            <el-option label="pre - 预发布环境" value="pre" />
          </el-select>
        </el-form-item>
        <el-form-item label="基础URL" prop="base_url">
          <el-input v-model="formData.base_url" placeholder="如: https://api.example.com" />
        </el-form-item>
        <el-form-item label="环境变量">
          <div class="variable-editor">
            <div v-for="(item, index) in variables" :key="index" class="variable-row">
              <el-input v-model="item.key" placeholder="变量名" class="var-key" />
              <el-input v-model="item.value" placeholder="变量值" class="var-value" />
              <el-input v-model="item.description" placeholder="描述" class="var-desc" />
              <el-button type="danger" link @click="removeVariable(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" link @click="addVariable">
              <el-icon><Plus /></el-icon>添加变量
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="全局请求头">
          <div class="variable-editor">
            <div v-for="(item, index) in headers" :key="index" class="variable-row">
              <el-input v-model="item.key" placeholder="Header名" class="var-key" />
              <el-input v-model="item.value" placeholder="Header值" class="var-value" />
              <el-button type="danger" link @click="removeHeader(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" link @click="addHeader">
              <el-icon><Plus /></el-icon>添加请求头
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 复制对话框 -->
    <el-dialog v-model="copyDialogVisible" title="复制环境" width="500px">
      <el-form ref="copyFormRef" :model="copyFormData" :rules="copyFormRules" label-width="100px">
        <el-form-item label="新环境名称" prop="new_env_name">
          <el-input v-model="copyFormData.new_env_name" placeholder="请输入新环境名称" />
        </el-form-item>
        <el-form-item label="新环境代码" prop="new_env_code">
          <el-input v-model="copyFormData.new_env_code" placeholder="请输入新环境代码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCopySubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 变量查看对话框 -->
    <el-dialog v-model="variableDialogVisible" title="环境变量" width="600px">
      <el-table :data="viewVariables" border>
        <el-table-column prop="key" label="变量名" width="150" />
        <el-table-column prop="value" label="变量值" />
        <el-table-column prop="description" label="描述" width="150" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete, MagicStick } from '@element-plus/icons-vue'
import { queryByPage, insertData, updateData, deleteData, setDefault, toggleEnabled, copyEnv, initDefaultEnvs } from './apiEnvironment'
import { queryAll as queryAllProjects } from '~/views/apitest/project/apiProject'

// 项目列表
const projectList = ref([])

// 搜索表单
const searchForm = reactive({
  project_id: null,
  env_name: '',
  env_code: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10
})
const total = ref(0)

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增环境')
const isEdit = ref(false)
const formRef = ref(null)
const submitLoading = ref(false)

// 表单数据
const formData = reactive({
  id: null,
  project_id: null,
  env_name: '',
  env_code: '',
  base_url: '',
  env_variables: '',
  env_headers: '',
  sort_order: 0
})

// 环境变量
const variables = ref([])
const headers = ref([])

// 表单验证规则
const formRules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  env_name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  env_code: [{ required: true, message: '请选择环境代码', trigger: 'change' }]
}

// 复制对话框
const copyDialogVisible = ref(false)
const copyFormRef = ref(null)
const copyFormData = reactive({
  source_id: null,
  new_env_name: '',
  new_env_code: ''
})
const copyFormRules = {
  new_env_name: [{ required: true, message: '请输入新环境名称', trigger: 'blur' }],
  new_env_code: [{ required: true, message: '请输入新环境代码', trigger: 'blur' }]
}

// 变量查看
const variableDialogVisible = ref(false)
const viewVariables = ref([])

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await queryAllProjects()
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
      if (projectList.value.length > 0 && !searchForm.project_id) {
        searchForm.project_id = projectList.value[0].id
      }
    }
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      ...searchForm,
      ...pagination
    })
    if (res.data.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.env_name = ''
  searchForm.env_code = ''
  handleSearch()
}

// 获取环境标签类型
const getEnvTagType = (code) => {
  const typeMap = {
    dev: 'info',
    test: 'warning',
    prod: 'danger',
    uat: 'success',
    pre: ''
  }
  return typeMap[code] || 'info'
}

// 获取变量数量
const getVariableCount = (variablesJson) => {
  if (!variablesJson) return 0
  try {
    const vars = JSON.parse(variablesJson)
    return Array.isArray(vars) ? vars.length : 0
  } catch {
    return 0
  }
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增环境'
  Object.assign(formData, {
    id: null,
    project_id: searchForm.project_id,
    env_name: '',
    env_code: '',
    base_url: '',
    env_variables: '',
    env_headers: '',
    sort_order: 0
  })
  variables.value = []
  headers.value = []
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑环境'
  Object.assign(formData, row)
  
  // 解析变量
  try {
    variables.value = row.env_variables ? JSON.parse(row.env_variables) : []
  } catch {
    variables.value = []
  }
  
  // 解析请求头
  try {
    headers.value = row.env_headers ? JSON.parse(row.env_headers) : []
  } catch {
    headers.value = []
  }
  
  dialogVisible.value = true
}

// 添加变量
const addVariable = () => {
  variables.value.push({ key: '', value: '', description: '' })
}

// 删除变量
const removeVariable = (index) => {
  variables.value.splice(index, 1)
}

// 添加请求头
const addHeader = () => {
  headers.value.push({ key: '', value: '' })
}

// 删除请求头
const removeHeader = (index) => {
  headers.value.splice(index, 1)
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    // 序列化变量和请求头
    const submitData = {
      ...formData,
      env_variables: JSON.stringify(variables.value.filter(v => v.key)),
      env_headers: JSON.stringify(headers.value.filter(h => h.key))
    }
    
    const res = isEdit.value 
      ? await updateData(submitData)
      : await insertData(submitData)
    
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '操作成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    const res = await deleteData(row.id)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 设为默认
const handleSetDefault = async (row) => {
  try {
    const res = await setDefault(row.id)
    if (res.data.code === 200) {
      ElMessage.success('设置成功')
      loadData()
    } else {
      ElMessage.error(res.data.msg || '设置失败')
    }
  } catch (error) {
    console.error('设置失败:', error)
  }
}

// 切换启用状态
const handleToggleEnabled = async (row) => {
  try {
    const res = await toggleEnabled(row.id)
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg)
    } else {
      ElMessage.error(res.data.msg || '操作失败')
      row.is_enabled = row.is_enabled === 1 ? 0 : 1
    }
  } catch (error) {
    console.error('操作失败:', error)
    row.is_enabled = row.is_enabled === 1 ? 0 : 1
  }
}

// 复制
const handleCopy = (row) => {
  copyFormData.source_id = row.id
  copyFormData.new_env_name = `${row.env_name} - 副本`
  copyFormData.new_env_code = `${row.env_code}_copy`
  copyDialogVisible.value = true
}

// 提交复制
const handleCopySubmit = async () => {
  try {
    await copyFormRef.value.validate()
    submitLoading.value = true
    
    const res = await copyEnv(copyFormData)
    if (res.data.code === 200) {
      ElMessage.success('复制成功')
      copyDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.data.msg || '复制失败')
    }
  } catch (error) {
    console.error('复制失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 初始化默认环境
const handleInitDefault = async () => {
  if (!searchForm.project_id) {
    ElMessage.warning('请先选择项目')
    return
  }
  try {
    const res = await initDefaultEnvs(searchForm.project_id)
    if (res.data.code === 200) {
      ElMessage.success('初始化成功')
      loadData()
    } else {
      ElMessage.error(res.data.msg || '初始化失败')
    }
  } catch (error) {
    console.error('初始化失败:', error)
  }
}

// 查看变量
const showVariables = (row) => {
  try {
    viewVariables.value = row.env_variables ? JSON.parse(row.env_variables) : []
  } catch {
    viewVariables.value = []
  }
  variableDialogVisible.value = true
}

onMounted(() => {
  loadProjects().then(() => {
    loadData()
  })
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.search-container {
  background: var(--el-bg-color);
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.table-container {
  background: var(--el-bg-color);
  padding: 20px;
  border-radius: 4px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.variable-editor {
  width: 100%;
}

.variable-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.var-key {
  width: 120px;
}

.var-value {
  flex: 1;
}

.var-desc {
  width: 120px;
}

.ml-2 {
  margin-left: 8px;
}
</style>

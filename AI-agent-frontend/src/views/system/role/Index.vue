<template>
  <div class="role-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>角色管理</h2>
      <p>管理系统角色，配置权限和菜单</p>
    </div>

    <!-- 搜索和操作区 -->
    <el-card class="search-card">
      <el-row :gutter="20" justify="space-between">
        <el-col :span="16">
          <el-form :model="searchForm" inline>
            <el-form-item label="角色名称">
              <el-input 
                v-model="searchForm.keyword" 
                placeholder="请输入角色名称" 
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="handleReset">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="8" class="text-right">
          <el-button type="primary" @click="handleAdd" v-permission="['role:create']">
            <el-icon><Plus /></el-icon>
            新增角色
          </el-button>
          <el-button 
            type="danger" 
            :disabled="selectedRoles.length === 0"
            @click="handleBatchDelete"
            v-permission="['role:delete']"
          >
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 角色列表 -->
    <el-card class="table-card">
      <CommonTable
        :data="tableData"
        :columns="tableColumns"
        :loading="loading"
        :pagination="pagination"
        :show-selection="true"
        :row-key="'role_id'"
        :action-width="200"
        @selectionChange="handleSelectionChange"
        @pageChange="handlePageChange"
        @sizeChange="handleSizeChange"
      >
        <template #status="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
        
        <template #actions="{ row }">
          <el-button 
            type="primary" 
            size="small" 
            link
            @click="handlePermission(row)"
            v-permission="['role:permission']"
          >
            权限配置
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            link
            @click="handleEdit(row)"
            v-permission="['role:update']"
          >
            编辑
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            link
            @click="handleCopy(row)"
            v-permission="['role:create']"
          >
            复制
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            link
            @click="handleDelete(row)"
            v-permission="['role:delete']"
          >
            删除
          </el-button>
        </template>
      </CommonTable>
    </el-card>

    <!-- 角色表单对话框 -->
    <FormDialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑角色' : '新增角色'"
      :loading="formLoading"
      :fields="formFields"
      :form-data="formData"
      @confirm="handleFormConfirm"
    />

    <!-- 权限配置对话框 -->
    <PermissionDialog
      v-model="permissionDialogVisible"
      :role-info="currentRole"
      @success="handlePermissionSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import CommonTable from '@/components/Common/CommonTable.vue'
import FormDialog from '@/components/Common/FormDialog.vue'
import PermissionDialog from '@/components/Permission/PermissionDialog.vue'
import { RoleApi } from '@/api/modules/role'
import { formatStandardDateTime } from '@/utils/dateFormat'
import type { RoleInfo, TableColumn, FormField } from '@/api/types'

// 数据和状态
const loading = ref(false)
const formLoading = ref(false)
const tableData = ref<RoleInfo[]>([])
const selectedRoles = ref<RoleInfo[]>([])
const currentRole = ref<RoleInfo | null>(null)

// 对话框状态
const formDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const isEdit = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 表单数据
const formData = reactive({
  role_name: '',
  remark: ''
})



// 表格列配置
const tableColumns = ref<TableColumn[]>([
  { prop: 'role_id', label: 'ID', width: 80 },
  { prop: 'role_name', label: '角色名称', minWidth: 120 },
  { prop: 'remark', label: '描述', minWidth: 150, showOverflowTooltip: true },
  { prop: 'create_time', label: '创建时间', width: 180, formatter: (row: any) => formatStandardDateTime(row.create_time) },
])

// 表单字段配置
const formFields = ref<FormField[]>([
  {
    prop: 'role_name',
    label: '角色名称',
    component: 'input',
    required: true,
    placeholder: '请输入角色名称',
    maxlength: 10,
    rules: [
      { required: true, message: '请输入角色名称', trigger: 'blur' },
      { min: 2, max: 10, message: '角色名称长度在 2 到 10 个字符', trigger: 'blur' }
    ],
    props: {
      'show-word-limit': true
    }
  },
  {
    prop: 'remark',
    label: '角色描述',
    component: 'input',
    inputType: 'textarea',
    placeholder: '请输入角色描述',
    maxlength: 100,
    rows: 3,
    rules: [
      { max: 100, message: '描述不能超过 100 个字符', trigger: 'blur' }
    ],
    props: {
      'show-word-limit': true
    }
  }
])

// 初始化表单数据
const initFormData = () => {
  Object.assign(formData, {
    role_name: '',
    remark: ''
  })
}

// 加载角色列表
const loadRoleList = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword && searchForm.keyword.trim() ? searchForm.keyword.trim() : undefined
    }

    const response = await RoleApi.getRoleList(params)
    if (response.success && response.data) {
      // 后端返回的是 PageData 格式，与用户管理一致
      tableData.value = Array.isArray(response.data) ? response.data : []
      pagination.total = (response as any).total || 0
    } else {
      tableData.value = []
      pagination.total = 0
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadRoleList()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  pagination.page = 1
  loadRoleList()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  initFormData()
  formDialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  isEdit.value = true
  // 重置表单数据
  initFormData()
  // 设置编辑数据
  Object.assign(formData, {
    role_name: row.role_name,
    remark: row.remark || ''
  })
  currentRole.value = row
  formDialogVisible.value = true
}

// 复制
const handleCopy = async (row: RoleInfo) => {
  try {
    const { value: newRoleName } = await ElMessageBox.prompt('请输入新角色名称', '复制角色', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '角色名称不能为空'
    })
    
    const response = await RoleApi.copyRole(row.role_id, newRoleName)
    if (response.success) {
      ElMessage.success('复制成功')
      loadRoleList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('复制角色失败:', error)
      ElMessage.error('复制角色失败')
    }
  }
}

// 删除
const handleDelete = async (row: RoleInfo) => {
  try {
    await ElMessageBox.confirm(
      `确认删除角色「${row.role_name}」吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await RoleApi.deleteRole(row.role_id)
    if (response.success) {
      ElMessage.success('删除成功')
      loadRoleList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除角色失败:', error)
      // 检查是否是角色不存在的错误
      if (error?.response?.status === 404 || error?.message?.includes('角色不存在')) {
        ElMessage.warning('角色已不存在，将刷新列表')
        loadRoleList() // 角色不存在时也要刷新列表
      } else {
        ElMessage.error('删除角色失败')
      }
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (!selectedRoles.value || selectedRoles.value.length === 0) {
    ElMessage.warning('请选择要删除的角色')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认删除选中的 ${selectedRoles.value.length} 个角色吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const roleIds = (selectedRoles.value || []).map(role => role.role_id)
    const response = await RoleApi.batchDeleteRoles(roleIds)
    if (response.success) {
      ElMessage.success(response.message || '批量删除成功')
      selectedRoles.value = []
      loadRoleList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除角色失败:', error)
      // 检查是否是具体的错误信息
      if (error?.response?.data?.detail) {
        ElMessage.error(error.response.data.detail)
      } else if (error?.message) {
        ElMessage.error(error.message)
      } else {
        ElMessage.error('批量删除角色失败')
      }
    }
  }
}

// 表单提交
const handleFormConfirm = async (data: any) => {
  try {
    formLoading.value = true
    
    if (isEdit.value && currentRole.value) {
      const updateData = { ...data }
      const response = await RoleApi.updateRole(currentRole.value.role_id, updateData)
      if (response.success) {
        ElMessage.success('更新成功')
        formDialogVisible.value = false
        loadRoleList()
      }
    } else {
      const response = await RoleApi.createRole(data)
      if (response.success) {
        ElMessage.success('创建成功')
        formDialogVisible.value = false
        loadRoleList()
      }
    }
  } catch (error) {
    console.error('保存角色失败:', error)
    ElMessage.error('保存角色失败')
  } finally {
    formLoading.value = false
  }
}

// 权限配置
const handlePermission = (row: RoleInfo) => {
  currentRole.value = row
  permissionDialogVisible.value = true
}

// 权限配置成功回调
const handlePermissionSuccess = () => {
  // 可以在这里添加成功后的逻辑，比如刷新列表等
  console.log('权限配置保存成功')
}

// 表格选中变化
const handleSelectionChange = (selection: RoleInfo[]) => {
  selectedRoles.value = selection
}

// 分页变化
const handlePageChange = (page: number) => {
  pagination.page = page
  loadRoleList()
}

// 页面大小变化
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadRoleList()
}

// 初始化
onMounted(() => {
  loadRoleList()
})
</script>

<style scoped lang="scss">
.role-management {
  .page-header {
    margin-bottom: 20px;
    
    h2 {
      font-size: 24px;
      margin: 0 0 8px 0;
      color: #2c3e50;
    }
    
    p {
      color: #7f8c8d;
      margin: 0;
    }
  }
  
  .search-card {
    margin-bottom: 20px;
    
    .text-right {
      text-align: right;
    }
  }
  
  .table-card {
    .el-card__body {
      padding: 0;
    }
  }
  
}
</style>
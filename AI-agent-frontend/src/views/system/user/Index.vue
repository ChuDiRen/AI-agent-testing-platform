# Copyright (c) 2025 左岚. All rights reserved.

<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <p>管理系统用户，包括用户信息、角色分配等</p>
    </div>
    
    <!-- 搜索表单 -->
    <SearchForm
      v-model="searchParams"
      :fields="searchFields"
      :loading="loading"
      @search="handleSearch"
      @reset="handleReset"
    />
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <el-button
          type="primary"
          :icon="Plus"
          @click="handleAdd"
        >
          新增用户
        </el-button>
        <el-button
          type="danger"
          :icon="Delete"
          :disabled="!selectedUsers.length"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
        <el-button
          type="success"
          :icon="Download"
          @click="handleExport"
        >
          导出数据
        </el-button>
        <el-upload
          :action="uploadAction"
          :show-file-list="false"
          :before-upload="beforeUpload"
          :on-success="handleImportSuccess"
          :on-error="handleImportError"
        >
          <el-button type="warning" :icon="Upload">
            导入数据
          </el-button>
        </el-upload>
      </div>
    </div>
    
        <!-- 数据表格 -->
    <div class="table-container">
      <CommonTable
        v-model:loading="loading"
        :data="userList"
        :columns="tableColumns"
        :pagination="pagination"
        :show-selection="true"
        :show-index="false"
        :show-actions="true"
        :action-width="280"
        @selection-change="handleSelectionChange"
        @page-change="handlePageChange"
        @size-change="handleSizeChange"
        @edit="handleEdit"
        @delete="handleDelete"
      >
        <!-- 状态列 -->
      <template #status="{ row }">
        <el-tag
          :type="row.status === '1' ? 'success' : 'danger'"
          size="small"
        >
          {{ row.status === '1' ? '启用' : '禁用' }}
        </el-tag>
      </template>
      
      <!-- 性别列 -->
      <template #ssex="{ row }">
        <span>
          {{ getSexText(row.ssex) }}
        </span>
      </template>

      <!-- 角色列 -->
      <template #roles="{ row }">
        <div>
          <el-tag
            v-for="name in (rolesMap[row.user_id] || [])"
            :key="name"
            size="small"
            type="info"
            style="margin-right:4px;margin-bottom:2px;"
          >
            {{ name }}
          </el-tag>
          <span v-if="!(rolesMap[row.user_id] && rolesMap[row.user_id].length)">-</span>
        </div>
      </template>

      <!-- 头像列 -->
      <template #avatar="{ row }">
        <el-avatar
          :src="row.avatar"
          :size="32"
          :icon="UserFilled"
        />
      </template>

      <!-- 操作列 -->
      <template #actions="{ row }">
        <el-button
          type="primary"
          size="small"
          @click="handleEdit(row)"
        >
          编辑
        </el-button>
        <el-button
          :type="row.status === '0' ? 'success' : 'danger'"
          size="small"
          @click="handleToggleStatus(row)"
        >
          {{ row.status === '0' ? '启用' : '禁用' }}
        </el-button>
        <el-button
          type="info"
          size="small"
          @click="handleResetPassword(row)"
        >
          重置密码
        </el-button>
        <el-button
          type="danger"
          size="small"
          @click="handleDelete(row)"
        >
          删除
        </el-button>
              </template>
      </CommonTable>
    </div>
    
    <!-- 用户表单对话框 -->
    <FormDialog
      v-model="userDialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      :fields="userFormFields"
      :form-data="currentUser"
      :rules="userFormRules"
      :loading="formLoading"
      width="800px"
      @confirm="handleUserFormConfirm"
      @cancel="handleUserFormCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Delete,
  Download,
  Upload,
  UserFilled
} from '@element-plus/icons-vue'
import CommonTable from '@/components/Common/CommonTable.vue'
import SearchForm from '@/components/Common/SearchForm.vue'
import FormDialog from '@/components/Common/FormDialog.vue'
import { UserApi } from '@/api/modules/user'
import { RoleApi } from '@/api/modules/role'
import { DepartmentApi } from '@/api/modules/department'
import type {
  UserInfo,
  TableColumn,
  SearchField,
  FormField,
  FormRule,
  DeptInfo,
  RoleInfo
} from '@/api/types'

// 响应式数据
const loading = ref(false)
const formLoading = ref(false)
const userList = ref<UserInfo[]>([])
const selectedUsers = ref<UserInfo[]>([])
const userDialogVisible = ref(false)
const isEdit = ref(false)
const currentUser = ref<Partial<UserInfo & { roles?: number[] }>>({})
const departmentList = ref<DeptInfo[]>([])
const roleList = ref<RoleInfo[]>([])
const rolesMap = ref<Record<number, string[]>>({})

// 搜索参数
const searchParams = reactive({
  keyword: '',
  status: null,
  dept_id: null,
  ssex: null
})

// 分页参数
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 上传配置
const uploadAction = computed(() => '/api/v1/users/import')

// 搜索字段配置
const searchFields: SearchField[] = [
  {
    prop: 'keyword',
    label: '关键词',
    component: 'input',
    placeholder: '用户名/邮箱/手机号',
    defaultValue: ''
  },
  {
    prop: 'status',
    label: '状态',
    component: 'select',
    options: [
      { label: '启用', value: '1' },
      { label: '禁用', value: '0' }
    ],
    defaultValue: null
  },
  {
    prop: 'dept_id',
    label: '部门',
    component: 'select',
    get options() {
      return departmentList.value.map(dept => ({
        label: dept.dept_name,
        value: dept.dept_id
      }))
    },
    defaultValue: null
  },
  {
    prop: 'ssex',
    label: '性别',
    component: 'select',
    options: [
      { label: '男', value: '0' },
      { label: '女', value: '1' },
      { label: '保密', value: '2' }
    ],
    defaultValue: null
  }
]

// 表格列配置
const tableColumns: TableColumn[] = [
  { prop: 'user_id', label: 'ID', width: 60, fixed: 'left' },
  { prop: 'username', label: '用户名', width: 100, fixed: 'left' },
  { prop: 'email', label: '邮箱', width: 160, fixed: 'left' },
  { prop: 'mobile', label: '手机号', width: 110 },
  { prop: 'avatar', label: '头像', width: 60, slot: 'avatar' },
  { prop: 'ssex', label: '性别', width: 60, slot: 'ssex' },
  { prop: 'dept_name', label: '部门', width: 120 },
  { prop: 'status', label: '状态', width: 70, slot: 'status' },
  { prop: 'create_time', label: '创建时间', width: 140 },
  { prop: 'roles', label: '角色', width: 200, slot: 'roles' },
  { prop: 'last_login_time', label: '最后登录', width: 140 }
]

// 用户表单字段配置
const userFormFields: FormField[] = [
  {
    prop: 'username',
    label: '用户名',
    component: 'input',
    required: true,
    span: 12,
    rules: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
    ]
  },
  {
    prop: 'password',
    label: '密码',
    component: 'input',
    inputType: 'password',
    get required() {
      return !isEdit.value
    },
    span: 12,
    showPassword: true,
    get rules() {
      return !isEdit.value ? [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
      ] : []
    }
  },
  {
    prop: 'email',
    label: '邮箱',
    component: 'input',
    span: 12,
    rules: [
      { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ]
  },
  {
    prop: 'mobile',
    label: '手机号',
    component: 'input',
    span: 12
  },
  {
    prop: 'dept_id',
    label: '所属部门',
    component: 'select',
    span: 12,
    get options() {
      return departmentList.value.map(dept => ({
        label: dept.dept_name,
        value: dept.dept_id
      }))
    },
    placeholder: '请选择部门'
  },
  {
    prop: 'ssex',
    label: '性别',
    component: 'radio',
    span: 12,
    defaultValue: '2',
    options: [
      { label: '男', value: '0' },
      { label: '女', value: '1' },
      { label: '保密', value: '2' }
    ]
  },
  {
    prop: 'status',
    label: '状态',
    component: 'radio',
    span: 12,
    defaultValue: '0', // 默认状态改为禁用
    options: [
      { label: '启用', value: '1' },
      { label: '禁用', value: '0' }
    ]
  },
  {
    prop: 'roles',
    label: '分配角色',
    component: 'checkbox',
    span: 24,
    get options() {
      return roleList.value.map(role => ({
        label: role.role_name,
        value: role.role_id
      }))
    },
    placeholder: '请选择角色'
  },
  {
    prop: 'description',
    label: '描述',
    component: 'input',
    inputType: 'textarea',
    span: 24,
    rows: 3
  }
]

// 表单验证规则
const userFormRules: Record<string, FormRule[]> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 获取性别文本
const getSexText = (sex: string) => {
  const sexMap: Record<string, string> = {
    '0': '男',
    '1': '女',
    '2': '保密'
  }
  return sexMap[sex] || '未知'
}

// 加载部门列表
const loadDepartmentList = async () => {
  try {
    const response = await DepartmentApi.getDepartmentList()
    const raw: any = (response as any)?.data
    const list = Array.isArray(raw) ? raw : (raw?.departments || raw?.items || [])
    departmentList.value = Array.isArray(list) ? list : []
  } catch (error) {
    console.error('加载部门列表失败:', error)
    departmentList.value = []
  }
}

// 加载角色列表
const loadRoleList = async () => {
  try {
    const response = await RoleApi.getAllRoles()
    if (response.success && response.data) {
      roleList.value = response.data
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

// 获取用户列表
const getUserList = async () => {
  try {
    loading.value = true
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchParams.keyword && searchParams.keyword.trim()) params.keyword = searchParams.keyword.trim()
    if (searchParams.status !== null && searchParams.status !== undefined && searchParams.status !== '') params.status = searchParams.status
    if (searchParams.dept_id) params.dept_id = searchParams.dept_id
    if (searchParams.ssex !== null && searchParams.ssex !== undefined && searchParams.ssex !== '') params.ssex = searchParams.ssex

    const response = await UserApi.getUserList(params)
    if (response.success && response.data) {
      const list: any[] = Array.isArray(response.data) ? response.data : []
      userList.value = list
      pagination.total = (response as any).total || 0

      // 若后端已返回 roles，则直接填充 rolesMap；否则降级为逐个请求
      const ids = list.map(u => u.user_id)
      const hasRoles = list.some(u => Array.isArray((u as any).roles))
      if (hasRoles) {
        const map: Record<number, string[]> = {}
        list.forEach((u: any) => { map[u.user_id] = (u.roles || []).map((r: any) => r.role_name) })
        rolesMap.value = map
      } else {
        await loadRolesForUsers(ids)
      }
    } else {
      ElMessage.error(response.message || '获取用户列表失败')
      userList.value = []
      pagination.total = 0
      rolesMap.value = {}
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
    userList.value = []
    pagination.total = 0
    rolesMap.value = {}
  } finally {
    loading.value = false
  }
}

// 批量加载角色（逐个请求，保证最小改动；若后端没返回roles时使用）
const loadRolesForUsers = async (userIds: number[]) => {
  const map: Record<number, string[]> = { ...rolesMap.value }
  await Promise.all(userIds.map(async (id) => {
    try {
      const res = await UserApi.getUserRoles(id)
      const names = (res?.data?.roles || []).map((r: any) => r.role_name)
      map[id] = names
    } catch (e) {
      map[id] = []
    }
  }))
  rolesMap.value = map
}

// 搜索
const handleSearch = (searchData?: Record<string, any>) => {
  // 如果传入了搜索数据，更新searchParams
  if (searchData) {
    Object.assign(searchParams, searchData)
  }
  pagination.page = 1
  getUserList()
}

// 重置
const handleReset = () => {
  Object.assign(searchParams, {
    keyword: '',
    status: null,
    dept_id: null,
    ssex: null
  })
  pagination.page = 1
  getUserList()
}

// 分页变化
const handlePageChange = (page: number) => {
  pagination.page = page
  getUserList()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  getUserList()
}

// 多选变化
const handleSelectionChange = (selection: UserInfo[]) => {
  selectedUsers.value = selection
}

// 新增用户
const handleAdd = async () => {
  isEdit.value = false
  currentUser.value = {
    ssex: '2',
    status: '0', // 默认状态改为禁用
    roles: []
  }
  await loadDepartmentList()
  await loadRoleList()
  userDialogVisible.value = true
}

// 编辑用户
const handleEdit = async (row: UserInfo) => {
  try {
    isEdit.value = true

    // 预加载部门和角色选项，确保下拉显示真实名称
    await loadDepartmentList()
    await loadRoleList()

    // 获取用户当前角色
    const userRolesResponse = await UserApi.getUserRoles(row.user_id)
    const userRoles = userRolesResponse.data?.roles?.map((role: any) => role.role_id) || []

    currentUser.value = {
      ...row,
      roles: userRoles
    }
    userDialogVisible.value = true
  } catch (error) {
    console.error('获取用户角色信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 删除用户
const handleDelete = async (row: UserInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await UserApi.deleteUser(row.user_id)
    ElMessage.success('删除成功')
    getUserList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (!selectedUsers.value.length) {
    ElMessage.warning('请选择要删除的用户')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedUsers.value.length} 个用户吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const userIds = selectedUsers.value.map(user => user.user_id)
    await UserApi.batchDeleteUsers(userIds)
    ElMessage.success('批量删除成功')
    selectedUsers.value = []
    getUserList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 切换用户状态
const handleToggleStatus = async (row: UserInfo) => {
  const newStatus = row.status === '0' ? '1' : '0'
  const action = row.status === '0' ? '启用' : '禁用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.username}" 吗？`,
      `${action}确认`,
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await UserApi.toggleUserStatus(row.user_id, newStatus)
    ElMessage.success(`${action}成功`)
    getUserList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`)
    }
  }
}

// 重置密码
const handleResetPassword = async (row: UserInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户 "${row.username}" 的密码吗？重置后密码为：123456`,
      '重置密码确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await UserApi.resetPassword(row.user_id, '123456')
    ElMessage.success('密码重置成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('密码重置失败')
    }
  }
}

// 用户表单确认
const handleUserFormConfirm = async (data: any) => {
  try {
    formLoading.value = true
    
    // 分离用户基本信息和角色信息
    const { roles, password, ...userData } = data
    
    if (isEdit.value) {
      // 编辑用户 - 更新基本信息
      await UserApi.updateUser(currentUser.value.user_id!, userData)
      
      // 更新角色分配
      if (roles !== undefined) {
        await UserApi.assignUserRoles(currentUser.value.user_id!, {
          role_ids: roles || []
        })
      }
      
      ElMessage.success('用户更新成功')
    } else {
      // 新增用户 - 包含密码
      const createUserData = { ...userData, password }
      const createResponse = await UserApi.createUser(createUserData)
      
      // 如果新增成功且指定了角色，分配角色
      if (createResponse.success && roles && roles.length > 0) {
        const newUserId = createResponse.data?.user_id
        if (newUserId) {
          await UserApi.assignUserRoles(newUserId, {
            role_ids: roles
          })
        }
      }
      
      ElMessage.success('用户创建成功')
    }
    
    userDialogVisible.value = false
    getUserList()
  } catch (error) {
    console.error('用户操作失败:', error)
    ElMessage.error(isEdit.value ? '用户更新失败' : '用户创建失败')
  } finally {
    formLoading.value = false
  }
}

// 用户表单取消
const handleUserFormCancel = () => {
  userDialogVisible.value = false
  currentUser.value = {}
}

// 导出数据
const handleExport = async () => {
  try {
    loading.value = true
    // 构建导出参数
    const exportParams: any = {}
    
    if (searchParams.dept_id) exportParams.dept_id = searchParams.dept_id
    if (searchParams.status) exportParams.user_status = searchParams.status
    if (searchParams.ssex) exportParams.ssex = searchParams.ssex
    exportParams.include_roles = true
    
    await UserApi.exportUsers(exportParams)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    loading.value = false
  }
}

// 上传前检查
const beforeUpload = (file: File) => {
  const isExcel = file.type === 'application/vnd.ms-excel' || 
                  file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  
  if (!isExcel) {
    ElMessage.error('只能上传Excel文件！')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB！')
    return false
  }
  
  return true
}

// 导入成功
const handleImportSuccess = (response: any) => {
  console.log('Import response:', response)
  if (response.success) {
    const data = response.data
    if (data.failed_count > 0) {
      // 显示详细的导入结果
      let message = `导入完成！成功：${data.success_count}，失败：${data.failed_count}`
      if (data.error_messages && data.error_messages.length > 0) {
        message += `\n错误信息：\n${data.error_messages.slice(0, 5).join('\n')}`
        if (data.error_messages.length > 5) {
          message += `\n...还有${data.error_messages.length - 5}个错误`
        }
      }
      ElMessage.warning({
        message,
        duration: 10000,
        showClose: true
      })
    } else {
      ElMessage.success(`导入成功！共导入 ${data.success_count} 个用户`)
    }
    getUserList()
  } else {
    ElMessage.error(response.message || '导入失败')
  }
}

// 导入失败
const handleImportError = (error: any) => {
  console.error('Import error:', error)
  ElMessage.error('导入失败，请检查文件格式')
}

// 页面加载时获取数据
onMounted(async () => {
  await Promise.all([
    loadDepartmentList(),
    loadRoleList(),
    getUserList()
  ])
})
</script>

<style scoped lang="scss">
.user-management {
  .table-container {
    overflow-x: auto;
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
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
  
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding: 16px;
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    
    .action-left {
      display: flex;
      gap: 8px;
    }
    
    .action-right {
      display: flex;
      gap: 8px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .user-management {
    .page-header {
      padding: 15px 0;

      h2 {
        font-size: 22px;
      }

      p {
        font-size: 13px;
      }
    }
  }
}

@media (max-width: 992px) {
  .user-management {
    .action-bar {
      flex-wrap: wrap;
      gap: 10px;

      .action-left {
        flex-wrap: wrap;
        gap: 8px;
      }
    }
  }
}

@media (max-width: 768px) {
  .user-management {
    .page-header {
      padding: 12px 0;
      text-align: center;

      h2 {
        font-size: 20px;
        margin-bottom: 8px;
      }

      p {
        font-size: 12px;
      }
    }

    .action-bar {
      flex-direction: column;
      gap: 12px;

      .action-left {
        width: 100%;
        justify-content: center;
        flex-wrap: wrap;
        gap: 8px;
      }
    }

    // 表格在移动端的优化
    :deep(.el-table) {
      .el-table__header-wrapper,
      .el-table__body-wrapper {
        overflow-x: auto;
      }

      .el-table__header th,
      .el-table__body td {
        min-width: 80px;
        white-space: nowrap;
      }
    }
  }
}

@media (max-width: 576px) {
  .user-management {
    .page-header {
      padding: 10px 0;

      h2 {
        font-size: 18px;
        margin-bottom: 6px;
      }

      p {
        font-size: 11px;
      }
    }

    .action-bar {
      .action-left {
        .el-button {
          padding: 8px 12px;
          font-size: 12px;
        }
      }
    }

    // 移动端表格进一步优化
    :deep(.el-table) {
      font-size: 12px;

      .el-table__header th {
        padding: 8px 4px;
        font-size: 11px;
      }

      .el-table__body td {
        padding: 8px 4px;
      }

      .el-button {
        padding: 4px 8px;
        font-size: 11px;
      }

      .el-tag {
        font-size: 10px;
        padding: 2px 6px;
      }
    }

    // 分页组件优化
    :deep(.el-pagination) {
      .el-pagination__sizes,
      .el-pagination__jump {
        display: none;
      }

      .el-pager li {
        min-width: 28px;
        height: 28px;
        line-height: 28px;
        font-size: 12px;
      }

      .btn-prev,
      .btn-next {
        min-width: 28px;
        height: 28px;
        line-height: 28px;
      }
    }
  }
}
</style>
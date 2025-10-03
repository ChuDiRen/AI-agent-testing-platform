<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="user-manage-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="启用" value="1" />
            <el-option label="禁用" value="0" />
          </el-select>
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
          <el-button type="success" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="userStore.loading"
        :data="userStore.users"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="dept_name" label="部门" width="120" />
        <el-table-column label="角色" width="150">
          <template #default="{ row }">
            <el-tag
              v-for="role in row.roles"
              :key="role.id"
              size="small"
              style="margin-right: 5px"
            >
              {{ role.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="warning" size="small" @click="handleResetPassword(row)">
              重置密码
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="userStore.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item v-if="!formData.id" label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="formData.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { User } from '@/api/user'

const userStore = useUserStore()

// 搜索表单
const searchForm = reactive({
  username: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => formData.id ? '编辑用户' : '新增用户')

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<User> & { password?: string }>({
  username: '',
  password: '',
  nickname: '',
  email: '',
  phone: ''
})

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 初始化
onMounted(() => {
  handleSearch()
})

// 搜索
const handleSearch = () => {
  userStore.fetchUserList({
    ...searchForm,
    page: pagination.page,
    page_size: pagination.pageSize
  })
}

// 重置
const handleReset = () => {
  searchForm.username = ''
  searchForm.status = ''
  pagination.page = 1
  handleSearch()
}

// 新增
const handleCreate = () => {
  Object.assign(formData, {
    id: undefined,
    username: '',
    password: '',
    nickname: '',
    email: '',
    phone: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: User) => {
  Object.assign(formData, {
    id: row.id,
    username: row.username,
    nickname: row.nickname,
    email: row.email,
    phone: row.phone
  })
  delete formData.password
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    let success = false
    if (formData.id) {
      // 编辑
      success = await userStore.updateUser(formData as any)
    } else {
      // 新增
      success = await userStore.createUser(formData as any)
    }
    
    if (success) {
      dialogVisible.value = false
      handleSearch()
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 修改状态
const handleStatusChange = async (row: User) => {
  await userStore.changeStatus(row.id, row.status)
}

// 重置密码
const handleResetPassword = async (row: User) => {
  ElMessageBox.prompt('请输入新密码', '重置密码', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.{6,20}/,
    inputErrorMessage: '密码长度在 6 到 20 个字符'
  }).then(async ({ value }) => {
    await userStore.resetPassword(row.id, value)
  }).catch(() => {})
}

// 删除
const handleDelete = async (row: User) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const success = await userStore.deleteUser(row.id)
    if (success) {
      handleSearch()
    }
  }).catch(() => {})
}
</script>

<style scoped>
.user-manage-container {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 0;
}

.table-card {
  min-height: calc(100vh - 200px);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>


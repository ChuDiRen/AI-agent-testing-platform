<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<!-- 用户管理页面 - 适配 FastAPI RBAC 权限系统 -->
<template>
  <div class="user-manage-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入用户名或邮箱"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
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
          <el-button type="success" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
          <el-button type="success" @click="handleExportCSV">
            <el-icon><Download /></el-icon>
            导出CSV
          </el-button>
          <el-button type="success" @click="handleExportJSON">
            <el-icon><Download /></el-icon>
            导出JSON
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
        <el-table-column prop="user_id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="mobile" label="手机号" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'danger'">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" />
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
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
      :title="isEdit ? '编辑用户' : '新增用户'"
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
          <el-input v-model="formData.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="formData.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model="formData.mobile" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="1">启用</el-radio>
            <el-radio label="0">禁用</el-radio>
          </el-radio-group>
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
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { User } from '@/api/user'
import { Download, Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'

const userStore = useUserStore()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  is_active: undefined as boolean | undefined
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<User> & { password?: string }>({
  user_id: undefined,
  username: '',
  password: '',
  email: '',
  mobile: '',
  description: '',
  status: '1'
})

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  mobile: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

// 初始化
onMounted(() => {
  handleSearch()
})

// 搜索
const handleSearch = () => {
  userStore.fetchUserList({
    keyword: searchForm.keyword,
    is_active: searchForm.is_active,
    page: pagination.page,
    page_size: pagination.pageSize
  })
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.is_active = undefined
  pagination.page = 1
  handleSearch()
}

// 导出CSV
const handleExportCSV = () => {
  userStore.exportCSV(searchForm.keyword)
}

// 导出JSON
const handleExportJSON = () => {
  userStore.exportJSON(searchForm.keyword)
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  Object.assign(formData, {
    user_id: undefined,
    username: '',
    password: '',
    email: '',
    mobile: '',
    description: '',
    status: '1'
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: User) => {
  isEdit.value = true
  Object.assign(formData, {
    user_id: row.user_id,
    username: row.username,
    password: '',
    email: row.email,
    mobile: row.mobile,
    description: row.description,
    status: row.status
  })
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    let success = false
    if (isEdit.value) {
      // 编辑用户
      if (!formData.user_id) {
        ElMessage.error('用户ID不存在')
        return
      }
      success = await userStore.updateUser(formData.user_id, {
        email: formData.email,
        mobile: formData.mobile,
        description: formData.description,
        status: formData.status
      })
    } else {
      // 新增用户
      success = await userStore.createUser({
        username: formData.username!,
        password: formData.password!,
        email: formData.email,
        mobile: formData.mobile,
        description: formData.description,
        status: formData.status
      })
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

// 删除
const handleDelete = async (row: User) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const success = await userStore.deleteUser(row.user_id)
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

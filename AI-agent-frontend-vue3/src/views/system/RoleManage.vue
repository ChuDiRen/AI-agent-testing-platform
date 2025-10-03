<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="role-manage-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="角色名称">
          <el-input
            v-model="searchForm.role_name"
            placeholder="请输入角色名称"
            clearable
            @clear="handleSearch"
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
          <el-button type="success" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增角色
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 角色列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="roles"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色代码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
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
          :total="total"
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
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入角色代码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
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
import {
  getRoleList,
  createRole,
  updateRole,
  deleteRole,
  type Role
} from '@/api/role'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

// 数据
const roles = ref<Role[]>([])
const total = ref(0)
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  role_name: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => formData.id ? '编辑角色' : '新增角色')

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<Role>>({
  name: '',
  code: '',
  description: ''
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '角色代码只能包含字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
  ]
}

// 初始化
onMounted(() => {
  handleSearch()
})

// 获取角色列表
const handleSearch = async () => {
  try {
    loading.value = true
    const response = await getRoleList({
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    
    if (response.code === 200 && response.data) {
      roles.value = response.data.items
      total.value = response.data.total
    }
  } catch (error) {
    console.error('获取角色列表失败:', error)
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

// 重置
const handleReset = () => {
  searchForm.role_name = ''
  pagination.page = 1
  handleSearch()
}

// 新增
const handleCreate = () => {
  Object.assign(formData, {
    id: undefined,
    name: '',
    code: '',
    description: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: Role) => {
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    code: row.code,
    description: row.description
  })
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      loading.value = true
      let response
      
      if (formData.id) {
        // 编辑
        response = await updateRole(formData as any)
      } else {
        // 新增
        response = await createRole(formData as any)
      }
      
      if (response.code === 200) {
        ElMessage.success(formData.id ? '更新角色成功' : '创建角色成功')
        dialogVisible.value = false
        handleSearch()
      } else {
        ElMessage.error(response.msg || '操作失败')
      }
    } catch (error: any) {
      console.error('操作失败:', error)
      ElMessage.error(error.message || '操作失败')
    } finally {
      loading.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 删除
const handleDelete = async (row: Role) => {
  ElMessageBox.confirm(`确定要删除角色 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      loading.value = true
      const response = await deleteRole(row.id)
      
      if (response.code === 200) {
        ElMessage.success('删除角色成功')
        handleSearch()
      } else {
        ElMessage.error(response.msg || '删除失败')
      }
    } catch (error: any) {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    } finally {
      loading.value = false
    }
  }).catch(() => {})
}
</script>

<style scoped>
.role-manage-container {
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


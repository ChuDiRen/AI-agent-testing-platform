<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<!-- 部门管理页面 - 适配 FastAPI RBAC 权限系统 -->
<template>
  <div class="department-manage-container">
    <!-- 操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-button type="primary" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新列表
          </el-button>
          <el-button type="success" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增部门
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 部门列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="departmentStore.loading"
        :data="departmentStore.departments"
        border
        stripe
        style="width: 100%"
        row-key="dept_id"
      >
        <el-table-column prop="dept_id" label="ID" width="80" />
        <el-table-column prop="dept_name" label="部门名称" min-width="200" />
        <el-table-column prop="parent_id" label="上级部门ID" width="120" />
        <el-table-column prop="order_num" label="排序" width="100" />
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
        <el-form-item label="部门名称" prop="dept_name">
          <el-input v-model="formData.dept_name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="上级部门" prop="parent_id">
          <el-select v-model="formData.parent_id" placeholder="请选择上级部门" clearable>
            <el-option label="顶级部门" :value="0" />
            <el-option
              v-for="dept in departmentStore.departments"
              :key="dept.dept_id"
              :label="dept.dept_name"
              :value="dept.dept_id"
              :disabled="formData.dept_id === dept.dept_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序号" prop="order_num">
          <el-input-number
            v-model="formData.order_num"
            :min="0"
            :max="9999"
            placeholder="请输入排序号"
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
import { useDepartmentStore } from '@/store/department'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Department } from '@/api/department'

const departmentStore = useDepartmentStore()

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => formData.dept_id ? '编辑部门' : '新增部门')

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<Department>>({
  dept_id: undefined,
  dept_name: '',
  parent_id: 0,
  order_num: 0
})

const formRules: FormRules = {
  dept_name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' }
  ],
  parent_id: [
    { required: true, message: '请选择上级部门', trigger: 'change' }
  ]
}

// 初始化
onMounted(() => {
  handleRefresh()
})

// 刷新列表
const handleRefresh = () => {
  departmentStore.fetchDepartmentList()
}

// 新增
const handleCreate = () => {
  Object.assign(formData, {
    dept_id: undefined,
    dept_name: '',
    parent_id: 0,
    order_num: 0
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: Department) => {
  Object.assign(formData, {
    dept_id: row.dept_id,
    dept_name: row.dept_name,
    parent_id: row.parent_id,
    order_num: row.order_num
  })
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    let success = false
    if (formData.dept_id) {
      // 编辑
      success = await departmentStore.updateDepartment(formData.dept_id, {
        dept_name: formData.dept_name,
        parent_id: formData.parent_id,
        order_num: formData.order_num
      })
    } else {
      // 新增
      success = await departmentStore.createDepartment({
        dept_name: formData.dept_name!,
        parent_id: formData.parent_id || 0,
        order_num: formData.order_num
      })
    }
    
    if (success) {
      dialogVisible.value = false
      handleRefresh()
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 删除
const handleDelete = async (row: Department) => {
  ElMessageBox.confirm(`确定要删除部门 "${row.dept_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const success = await departmentStore.deleteDepartment(row.dept_id)
    if (success) {
      handleRefresh()
    }
  }).catch(() => {})
}
</script>

<style scoped>
.department-manage-container {
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
</style>


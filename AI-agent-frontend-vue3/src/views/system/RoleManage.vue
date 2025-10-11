<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<!-- 角色管理页面 - 适配 FastAPI RBAC 权限系统 -->
<template>
  <div class="role-manage-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Refresh /></el-icon>
            刷新列表
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
        v-loading="roleStore.loading"
        :data="roleStore.roles"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="role_id" label="ID" width="80" />
        <el-table-column prop="role_name" label="角色名称" width="200" />
        <el-table-column prop="remark" label="备注" min-width="250" />
        <el-table-column label="菜单权限" min-width="300">
          <template #default="{ row }">
            <el-tag
              v-for="menu in row.menus"
              :key="menu.menu_id"
              size="small"
              style="margin: 2px"
            >
              {{ menu.menu_name }}
            </el-tag>
            <el-text v-if="!row.menus || row.menus.length === 0" type="info">
              暂无权限
            </el-text>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="warning" size="small" @click="handlePermission(row)">
              分配权限
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
        <el-form-item label="角色名称" prop="role_name">
          <el-input v-model="formData.role_name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配权限对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="分配菜单权限"
      width="600px"
    >
      <el-tree
        ref="menuTreeRef"
        :data="menuTreeData"
        :props="{ children: 'children', label: 'menu_name' }"
        show-checkbox
        node-key="menu_id"
        :default-checked-keys="checkedMenuIds"
      />
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePermissionSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoleStore } from '@/store/role'
import { getMenuTree } from '@/api/menu'
import { assignRoleMenus } from '@/api/role-menu'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { RoleWithMenus } from '@/api/role'
import type { MenuTree } from '@/api/menu'

const roleStore = useRoleStore()

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => formData.role_id ? '编辑角色' : '新增角色')

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<RoleWithMenus>>({
  role_id: undefined,
  role_name: '',
  remark: ''
})

const formRules: FormRules = {
  role_name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ]
}

// 权限对话框
const permissionDialogVisible = ref(false)
const menuTreeRef = ref()
const menuTreeData = ref<MenuTree[]>([])
const checkedMenuIds = ref<number[]>([])
const currentRoleId = ref<number>()

// 初始化
onMounted(() => {
  handleSearch()
  loadMenuTree()
})

// 获取角色列表
const handleSearch = () => {
  roleStore.fetchRoleList()
}

// 加载菜单树
const loadMenuTree = async () => {
  try {
    const response = await getMenuTree()
    if (response.success && response.data) {
      menuTreeData.value = response.data
    }
  } catch (error) {
    console.error('获取菜单树失败:', error)
  }
}

// 新增
const handleCreate = () => {
  Object.assign(formData, {
    role_id: undefined,
    role_name: '',
    remark: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: RoleWithMenus) => {
  Object.assign(formData, {
    role_id: row.role_id,
    role_name: row.role_name,
    remark: row.remark
  })
  dialogVisible.value = true
}

// 提交状态
const submitting = ref(false)

// 提交
const handleSubmit = async () => {
  if (!formRef.value || submitting.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      let success = false
      if (formData.role_id) {
        // 编辑
        success = await roleStore.updateRole(formData.role_id, {
          role_name: formData.role_name,
          remark: formData.remark
        })
      } else {
        // 新增
        success = await roleStore.createRole({
          role_name: formData.role_name!,
          remark: formData.remark
        })
      }

      if (success) {
        dialogVisible.value = false
        handleSearch()
      }
    } finally {
      submitting.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 分配权限
const handlePermission = (row: RoleWithMenus) => {
  currentRoleId.value = row.role_id
  checkedMenuIds.value = row.menus?.map(m => m.menu_id) || []
  permissionDialogVisible.value = true
}

// 提交权限
const handlePermissionSubmit = async () => {
  if (!currentRoleId.value) return
  
  try {
    const checkedKeys = menuTreeRef.value.getCheckedKeys()
    const halfCheckedKeys = menuTreeRef.value.getHalfCheckedKeys()
    const menuIds = [...checkedKeys, ...halfCheckedKeys]
    
    const response = await assignRoleMenus({
      role_id: currentRoleId.value,
      menu_ids: menuIds
    })
    
    if (response.success) {
      ElMessage.success(response.message || '分配权限成功')
      permissionDialogVisible.value = false
      handleSearch()
    } else {
      ElMessage.error(response.message || '分配权限失败')
    }
  } catch (error: any) {
    console.error('分配权限失败:', error)
    ElMessage.error(error.message || '分配权限失败')
  }
}

// 删除
const handleDelete = async (row: RoleWithMenus) => {
  ElMessageBox.confirm(`确定要删除角色 "${row.role_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const success = await roleStore.deleteRole(row.role_id)
    if (success) {
      handleSearch()
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
</style>

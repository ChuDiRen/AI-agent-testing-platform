<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<!-- 菜单管理页面 - 适配 FastAPI RBAC 权限系统 -->
<template>
  <div class="menu-manage-container">
    <!-- 操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-button type="primary" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新列表
          </el-button>
          <el-button type="success" @click="handleCreate('menu')">
            <el-icon><Plus /></el-icon>
            新增菜单
          </el-button>
          <el-button type="warning" @click="handleCreate('button')">
            <el-icon><Plus /></el-icon>
            新增按钮
          </el-button>
          <el-button @click="handleToggleTree">
            <el-icon><View /></el-icon>
            {{ showTree ? '列表视图' : '树形视图' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 菜单列表（列表视图） -->
    <el-card v-if="!showTree" class="table-card">
      <el-table
        v-loading="menuStore.loading"
        :data="menuStore.menus"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="menu_id" label="ID" width="80" />
        <el-table-column prop="menu_name" label="菜单名称" min-width="150" />
        <el-table-column prop="parent_id" label="上级菜单ID" width="120" />
        <el-table-column prop="path" label="路由路径" min-width="180" />
        <el-table-column prop="component" label="组件路径" min-width="180" />
        <el-table-column prop="perms" label="权限标识" width="150" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === '0' ? 'primary' : 'success'">
              {{ row.type === '0' ? '菜单' : '按钮' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="icon" label="图标" width="100" />
        <el-table-column prop="order_num" label="排序" width="80" />
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

    <!-- 菜单树（树形视图） -->
    <el-card v-else class="tree-card">
      <el-tree
        v-loading="menuStore.loading"
        :data="menuStore.menuTree"
        :props="{ children: 'children', label: 'menu_name' }"
        node-key="menu_id"
        default-expand-all
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span class="tree-label">
              <el-tag :type="data.type === '0' ? 'primary' : 'success'" size="small">
                {{ data.type === '0' ? '菜单' : '按钮' }}
              </el-tag>
              <span style="margin-left: 10px">{{ node.label }}</span>
              <span v-if="data.perms" style="margin-left: 10px; color: #909399; font-size: 12px">
                ({{ data.perms }})
              </span>
            </span>
            <span class="tree-actions">
              <el-button type="primary" size="small" @click.stop="handleEdit(data)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click.stop="handleDelete(data)">
                删除
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="菜单类型" prop="type">
          <el-radio-group v-model="formData.type">
            <el-radio label="0">菜单</el-radio>
            <el-radio label="1">按钮</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="菜单名称" prop="menu_name">
          <el-input v-model="formData.menu_name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="上级菜单" prop="parent_id">
          <el-tree-select
            v-model="formData.parent_id"
            :data="menuTreeOptions"
            :props="{ children: 'children', label: 'menu_name', value: 'menu_id' }"
            placeholder="请选择上级菜单"
            check-strictly
            clearable
          />
        </el-form-item>
        <el-form-item v-if="formData.type === '0'" label="路由路径" prop="path">
          <el-input v-model="formData.path" placeholder="请输入路由路径，如：/system/user" />
        </el-form-item>
        <el-form-item v-if="formData.type === '0'" label="组件路径" prop="component">
          <el-input v-model="formData.component" placeholder="请输入组件路径，如：Layout 或 system/UserManage" />
        </el-form-item>
        <el-form-item label="权限标识" prop="perms">
          <el-input v-model="formData.perms" placeholder="请输入权限标识，如：user:view" />
        </el-form-item>
        <el-form-item v-if="formData.type === '0'" label="图标" prop="icon">
          <el-input v-model="formData.icon" placeholder="请输入图标，如：el-icon-user" />
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
import { useMenuStore } from '@/store/menu'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Menu, MenuTree } from '@/api/menu'

const menuStore = useMenuStore()

// 视图切换
const showTree = ref(false)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => formData.menu_id ? '编辑菜单' : '新增' + (formData.type === '0' ? '菜单' : '按钮'))

// 菜单树选项（包含顶级选项）
const menuTreeOptions = computed(() => {
  return [
    { menu_id: 0, menu_name: '顶级菜单', children: menuStore.menuTree }
  ]
})

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<Partial<Menu>>({
  menu_id: undefined,
  menu_name: '',
  parent_id: 0,
  path: '',
  component: '',
  perms: '',
  icon: '',
  type: '0',
  order_num: 0
})

const formRules: FormRules = {
  menu_name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择菜单类型', trigger: 'change' }
  ]
}

// 初始化
onMounted(() => {
  handleRefresh()
})

// 刷新列表
const handleRefresh = () => {
  menuStore.fetchMenuList()
  menuStore.fetchMenuTree()
}

// 切换视图
const handleToggleTree = () => {
  showTree.value = !showTree.value
}

// 新增
const handleCreate = (type: 'menu' | 'button') => {
  Object.assign(formData, {
    menu_id: undefined,
    menu_name: '',
    parent_id: 0,
    path: '',
    component: '',
    perms: '',
    icon: '',
    type: type === 'menu' ? '0' : '1',
    order_num: 0
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: Menu | MenuTree) => {
  Object.assign(formData, {
    menu_id: row.menu_id,
    menu_name: row.menu_name,
    parent_id: row.parent_id,
    path: row.path || '',
    component: row.component || '',
    perms: row.perms || '',
    icon: row.icon || '',
    type: row.type,
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
    const data = {
      menu_name: formData.menu_name!,
      parent_id: formData.parent_id || 0,
      path: formData.path || '',
      component: formData.component || '',
      perms: formData.perms || null,
      icon: formData.icon || '',
      type: formData.type!,
      order_num: formData.order_num
    }
    
    if (formData.menu_id) {
      // 编辑
      success = await menuStore.updateMenu(formData.menu_id, data)
    } else {
      // 新增
      success = await menuStore.createMenu(data)
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
const handleDelete = async (row: Menu | MenuTree) => {
  ElMessageBox.confirm(`确定要删除菜单 "${row.menu_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const success = await menuStore.deleteMenu(row.menu_id)
    if (success) {
      handleRefresh()
    }
  }).catch(() => {})
}
</script>

<style scoped>
.menu-manage-container {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 0;
}

.table-card,
.tree-card {
  min-height: calc(100vh - 200px);
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
}

.tree-label {
  display: flex;
  align-items: center;
}

.tree-actions {
  display: flex;
  gap: 8px;
}
</style>


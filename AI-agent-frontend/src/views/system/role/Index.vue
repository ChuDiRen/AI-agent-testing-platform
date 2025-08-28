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
      :fields="[]"
      @confirm="handleFormConfirm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="角色名称" prop="role_name">
          <el-input 
            v-model="formData.role_name" 
            placeholder="请输入角色名称"
            maxlength="10"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="角色描述" prop="remark">
          <el-input 
            v-model="formData.remark" 
            type="textarea"
            placeholder="请输入角色描述"
            :rows="3"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- 权限配置对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="权限配置"
      width="60%"
      :close-on-click-modal="false"
    >
      <div class="permission-config">
        <div class="role-info">
          <span>角色：{{ currentRole?.role_name }}</span>
        </div>
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="菜单权限" name="menu">
            <div class="menu-tree-container">
              <div class="tree-header">
                <el-checkbox 
                  v-model="menuCheckAll" 
                  :indeterminate="menuIndeterminate"
                  @change="handleMenuCheckAll"
                >
                  全选/反选
                </el-checkbox>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="expandAllMenus"
                >
                  展开全部
                </el-button>
                <el-button 
                  size="small"
                  @click="collapseAllMenus"
                >
                  折叠全部
                </el-button>
              </div>
              
              <el-tree
                ref="menuTreeRef"
                :data="menuTreeData"
                :props="menuTreeProps"
                node-key="menu_id"
                show-checkbox
                :check-strictly="false"
                :default-expand-all="false"
                @check="handleMenuCheck"
              >
                <template #default="{ data }">
                  <span class="menu-node">
                    <el-icon v-if="data.icon" class="menu-icon">
                      <component :is="data.icon" />
                    </el-icon>
                    <span>{{ data.menu_name }}</span>
                    <el-tag v-if="data.menu_type === 'button'" size="small" type="info">
                      按钮
                    </el-tag>
                  </span>
                </template>
              </el-tree>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handlePermissionSave" :loading="permissionLoading">
          保 存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type ElTree } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import CommonTable from '@/components/Common/CommonTable.vue'
import FormDialog from '@/components/Common/FormDialog.vue'
import { RoleApi } from '@/api/modules/role'
import { MenuApi } from '@/api/modules/menu'
import type { RoleInfo, MenuTreeNode, TableColumn } from '@/api/types'

// 表单引用
const formRef = ref<FormInstance>()
const menuTreeRef = ref<typeof ElTree>()

// 数据和状态
const loading = ref(false)
const formLoading = ref(false)
const permissionLoading = ref(false)
const tableData = ref<RoleInfo[]>([])
const selectedRoles = ref<RoleInfo[]>([])
const menuTreeData = ref<MenuTreeNode[]>([])
const currentRole = ref<RoleInfo | null>(null)

// 对话框状态
const formDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const isEdit = ref(false)

// 权限配置相关
const activeTab = ref('menu')
const menuCheckAll = ref(false)
const menuIndeterminate = ref(false)

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

// 表单验证规则
const formRules = {
  role_name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 10, message: '角色名称长度在 2 到 10 个字符', trigger: 'blur' }
  ],
  remark: [
    { max: 100, message: '描述不能超过 100 个字符', trigger: 'blur' }
  ]
}

// 表格列配置
const tableColumns = ref<TableColumn[]>([
  { prop: 'role_id', label: 'ID', width: 80 },
  { prop: 'role_name', label: '角色名称', minWidth: 120 },
  { prop: 'remark', label: '描述', minWidth: 150, showOverflowTooltip: true },
  { prop: 'create_time', label: '创建时间', width: 180 },
])

// 菜单树配置
const menuTreeProps = {
  children: 'children',
  label: 'menu_name'
}

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
      keyword: searchForm.keyword || undefined
    }
    
    const response = await RoleApi.getRoleList(params)
    if (response.success && response.data) {
      // 后端返回的是 RoleListResponse 格式，包含 roles 数组
      tableData.value = Array.isArray(response.data.roles) ? response.data.roles : []
      pagination.total = response.data.total || 0
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

// 加载菜单树
const loadMenuTree = async () => {
  try {
    const response = await MenuApi.getMenuTree()
    if (response.success && response.data) {
      menuTreeData.value = Array.isArray(response.data) ? response.data : []
    } else {
      menuTreeData.value = []
    }
  } catch (error) {
    console.error('加载菜单树失败:', error)
    menuTreeData.value = []
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
      ElMessage.error('删除角色失败')
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
      ElMessage.success('批量删除成功')
      selectedRoles.value = []
      loadRoleList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除角色失败:', error)
      ElMessage.error('批量删除角色失败')
    }
  }
}

// 表单提交
const handleFormConfirm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    formLoading.value = true
    
    if (isEdit.value && currentRole.value) {
      const updateData = { ...formData }
      const response = await RoleApi.updateRole(currentRole.value.role_id, updateData)
      if (response.success) {
        ElMessage.success('更新成功')
        formDialogVisible.value = false
        loadRoleList()
      }
    } else {
      const response = await RoleApi.createRole(formData)
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
const handlePermission = async (row: RoleInfo) => {
  currentRole.value = row
  await loadMenuTree()
  
  // 加载角色已有权限
  try {
    const response = await RoleApi.getRoleMenus(row.role_id)
    if (response.success && response.data) {
      nextTick(() => {
        const menuIds = Array.isArray(response.data) ? response.data : []
        menuTreeRef.value?.setCheckedKeys(menuIds)
        updateMenuCheckStatus()
      })
    }
  } catch (error) {
    console.error('加载角色权限失败:', error)
  }
  
  permissionDialogVisible.value = true
}

// 菜单全选/反选
const handleMenuCheckAll = (checked: boolean) => {
  if (checked) {
    const allKeys = getAllMenuKeys(menuTreeData.value || [])
    menuTreeRef.value?.setCheckedKeys(allKeys || [])
  } else {
    menuTreeRef.value?.setCheckedKeys([])
  }
  updateMenuCheckStatus()
}

// 菜单选中变化
const handleMenuCheck = () => {
  updateMenuCheckStatus()
}

// 更新菜单选中状态
const updateMenuCheckStatus = () => {
  const checkedKeys = menuTreeRef.value?.getCheckedKeys(false) || []
  const allKeys = getAllMenuKeys(menuTreeData.value || [])
  
  menuCheckAll.value = checkedKeys.length > 0 && checkedKeys.length === allKeys.length
  menuIndeterminate.value = checkedKeys.length > 0 && checkedKeys.length < allKeys.length
}

// 获取所有菜单键
const getAllMenuKeys = (menus: MenuTreeNode[]): number[] => {
  const keys: number[] = []
  const traverse = (nodes: MenuTreeNode[]) => {
    if (!nodes || !Array.isArray(nodes)) return
    (nodes || []).forEach(node => {
      if (node && node.menu_id) {
        keys.push(node.menu_id)
        if (node.children && Array.isArray(node.children) && node.children.length > 0) {
          traverse(node.children)
        }
      }
    })
  }
  traverse(menus || [])
  return keys
}

// 展开全部菜单
const expandAllMenus = () => {
  const allKeys = getAllMenuKeys(menuTreeData.value)
  allKeys.forEach(key => {
    menuTreeRef.value?.store.nodesMap[key]?.expand()
  })
}

// 折叠全部菜单
const collapseAllMenus = () => {
  const allKeys = getAllMenuKeys(menuTreeData.value)
  allKeys.forEach(key => {
    menuTreeRef.value?.store.nodesMap[key]?.collapse()
  })
}

// 保存权限配置
const handlePermissionSave = async () => {
  if (!currentRole.value) return
  
  try {
    permissionLoading.value = true
    
    const checkedKeys = (menuTreeRef.value?.getCheckedKeys(false) as number[]) || []
    const halfCheckedKeys = (menuTreeRef.value?.getHalfCheckedKeys() as number[]) || []
    const menuIds = [...checkedKeys, ...halfCheckedKeys]
    
    const response = await RoleApi.assignRoleMenus(currentRole.value.role_id, {
      menu_ids: menuIds
    })
    
    if (response.success) {
      ElMessage.success('权限配置保存成功')
      permissionDialogVisible.value = false
    }
  } catch (error) {
    console.error('保存权限配置失败:', error)
    ElMessage.error('保存权限配置失败')
  } finally {
    permissionLoading.value = false
  }
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
  loadMenuTree()
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
  
  .permission-config {
    .role-info {
      margin-bottom: 20px;
      padding: 10px;
      background-color: #f5f7fa;
      border-radius: 4px;
      
      span {
        font-size: 14px;
        color: #606266;
        font-weight: 500;
      }
    }
    
    .menu-tree-container {
      .tree-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
      }
      
      .menu-node {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .menu-icon {
          font-size: 16px;
          color: #909399;
        }
      }
    }
  }
}

:deep(.el-tree-node__content) {
  height: 36px;
}

:deep(.el-tree-node__label) {
  font-size: 14px;
}
</style>
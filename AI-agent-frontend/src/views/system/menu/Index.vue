<template>
  <div class="menu-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>菜单管理</h2>
      <p>管理系统菜单，配置导航结构</p>
    </div>

    <!-- 搜索和操作区 -->
    <el-card class="search-card">
      <el-row :gutter="20" justify="space-between">
        <el-col :span="16">
          <el-form :model="searchForm" inline>
            <el-form-item label="菜单名称">
              <el-input 
                v-model="searchForm.keyword" 
                placeholder="请输入菜单名称" 
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="菜单状态">
              <el-select 
                v-model="searchForm.is_active" 
                placeholder="请选择状态" 
                clearable
                style="width: 120px"
              >
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
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="8" class="text-right">
          <el-button type="primary" @click="handleAdd" v-permission="['menu:create']">
            <el-icon><Plus /></el-icon>
            新增菜单
          </el-button>
          <el-button 
            type="success" 
            @click="expandAll"
          >
            <el-icon><DCaret /></el-icon>
            展开全部
          </el-button>
          <el-button 
            @click="collapseAll"
          >
            <el-icon><CaretRight /></el-icon>
            折叠全部
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 菜单树表格 -->
    <el-card class="table-card">
      <el-table
        ref="tableRef"
        :data="tableData"
        :loading="loading"
        row-key="menu_id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        :default-expand-all="false"
        border
        stripe
      >
        <el-table-column prop="menu_name" label="菜单名称" min-width="200">
          <template #default="{ row }">
            <div class="menu-name-cell">
              <el-icon v-if="row.icon" class="menu-icon">
                <component :is="row.icon" />
              </el-icon>
              <span>{{ row.menu_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="menu_type" label="菜单类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.menu_type === '0' ? 'primary' : 'info'"
              size="small"
            >
              {{ row.menu_type === '0' ? '菜单' : '按钮' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="path" label="路由路径" min-width="150" show-overflow-tooltip />

        <el-table-column prop="component" label="组件路径" min-width="180" show-overflow-tooltip />

        <el-table-column prop="perms" label="权限标识" min-width="150" show-overflow-tooltip />

        <el-table-column prop="order_num" label="排序" width="80" align="center" />
        
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="create_time" label="创建时间" width="180" align="center" />
        
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              link
              @click="handleEdit(row)"
              v-permission="['menu:update']"
            >
              编辑
            </el-button>
            <el-button 
              type="primary" 
              size="small" 
              link
              @click="handleAddChild(row)"
              v-permission="['menu:create']"
              v-if="row.TYPE !== '1'"
            >
              新增子菜单
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              link
              @click="handleDelete(row)"
              v-permission="['menu:delete']"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 菜单表单对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑菜单' : '新增菜单'"
      width="800px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上级菜单" prop="parent_id">
              <el-tree-select
                v-model="formData.parent_id"
                :data="menuTreeOptions"
                :props="menuTreeProps"
                placeholder="请选择上级菜单"
                clearable
                check-strictly
                :render-after-expand="false"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单类型" prop="menu_type">
              <el-radio-group v-model="formData.menu_type" @change="handleMenuTypeChange">
                <el-radio label="0">菜单</el-radio>
                <el-radio label="1">按钮</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单名称" prop="menu_name">
              <el-input
                v-model="formData.menu_name"
                placeholder="请输入菜单名称"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单图标" prop="icon">
              <el-input
                v-model="formData.icon"
                placeholder="请输入图标名称"
                maxlength="50"
              >
                <template #prefix>
                  <el-icon v-if="formData.icon">
                    <component :is="formData.icon" />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" v-if="formData.menu_type !== '1'">
          <el-col :span="12">
            <el-form-item label="路由地址" prop="path">
              <el-input
                v-model="formData.path"
                placeholder="请输入路由地址"
                maxlength="200"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="formData.menu_type === '0'">
            <el-form-item label="组件路径" prop="component">
              <el-input
                v-model="formData.component"
                placeholder="请输入组件路径"
                maxlength="200"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="权限标识" prop="perms">
              <el-input
                v-model="formData.perms"
                placeholder="请输入权限标识"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="order_num">
              <el-input-number
                v-model="formData.order_num"
                :min="0"
                :max="999"
                placeholder="请输入排序"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleFormCancel" :disabled="formLoading">
            取消
          </el-button>
          <el-button
            type="primary"
            @click="handleFormConfirm"
            :loading="formLoading"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type ElTable } from 'element-plus'
import { Search, Refresh, Plus, DCaret, CaretRight } from '@element-plus/icons-vue'
// import FormDialog from '@/components/Common/FormDialog.vue' // 不再使用FormDialog组件
import { MenuApi } from '@/api/modules/menu'
import type { MenuInfo, MenuTreeNode } from '@/api/types'

// 表单引用
const formRef = ref<FormInstance>()
const tableRef = ref<typeof ElTable>()

// 数据和状态
const loading = ref(false)
const formLoading = ref(false)
const tableData = ref<MenuInfo[]>([])
const menuTreeOptions = ref<MenuTreeNode[]>([])
const currentMenu = ref<MenuInfo | null>(null)

// 对话框状态
const formDialogVisible = ref(false)
const isEdit = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  is_active: undefined as boolean | undefined
})

// 表单数据 - 使用小写字段名与后端保持一致
const formData = reactive({
  parent_id: 0,
  menu_name: '',
  menu_type: '0' as '0' | '1',
  icon: '',
  path: '',
  component: '',
  perms: '',
  order_num: 0
})

// 表单验证规则
const formRules = computed(() => {
  const rules: Record<string, any[]> = {
    menu_name: [
      { required: true, message: '请输入菜单名称', trigger: 'blur' },
      { min: 2, max: 50, message: '菜单名称长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    menu_type: [
      { required: true, message: '请选择菜单类型', trigger: 'change' }
    ],
    perms: [
      { max: 100, message: '权限标识不能超过 100 个字符', trigger: 'blur' }
    ]
  }

  // 根据菜单类型动态添加验证规则
  if (formData.menu_type !== '1') {
    rules.path = [
      { required: true, message: '请输入路由地址', trigger: 'blur' }
    ]
  }

  if (formData.menu_type === '0') {
    rules.component = [
      { required: true, message: '请输入组件路径', trigger: 'blur' }
    ]
  }

  return rules
})

// 菜单树配置
const menuTreeProps = {
  children: 'children',
  label: 'MENU_NAME',
  value: 'MENU_ID'
}

// 初始化表单数据
const initFormData = () => {
  Object.assign(formData, {
    parent_id: 0,
    menu_name: '',
    menu_type: '0' as '0' | '1',
    icon: '',
    path: '',
    component: '',
    perms: '',
    order_num: 0
  })
}

// 加载菜单列表
const loadMenuList = async () => {
  try {
    loading.value = true
    // const params = {
    //   keyword: searchForm.keyword || undefined,
    //   is_active: searchForm.is_active
    // } // 暂时注释掉未使用的参数
    
    const response = await MenuApi.getMenuTree()
    if (response.success) {
      const data = (Array.isArray(response.data) ? response.data : (response.data as any)?.tree) || []
      tableData.value = data
    } else {
      tableData.value = []
    }
  } catch (error) {
    console.error('加载菜单列表失败:', error)
    ElMessage.error('加载菜单列表失败')
  } finally {
    loading.value = false
  }
}

// 加载菜单树选项
const loadMenuTreeOptions = async () => {
  try {
    const response = await MenuApi.getMenuTree()
    if (response.success) {
      const data = (Array.isArray(response.data) ? response.data : (response.data as any)?.tree) || []
      // 过滤出按钮类型，只显示目录和菜单
      menuTreeOptions.value = filterMenuOptions(data)
    } else {
      menuTreeOptions.value = []
    }
  } catch (error) {
    console.error('加载菜单树选项失败:', error)
  }
}

// 过滤菜单选项（只显示菜单，不显示按钮）
const filterMenuOptions = (menus: MenuTreeNode[]): MenuTreeNode[] => {
  return menus.filter(menu => menu.menu_type !== '1').map(menu => ({
    ...menu,
    children: menu.children ? filterMenuOptions(menu.children) : []
  }))
}

// 搜索
const handleSearch = () => {
  loadMenuList()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.is_active = undefined
  loadMenuList()
}

// 展开全部
const expandAll = () => {
  nextTick(() => {
    const expandNodes = (data: MenuInfo[]) => {
      data.forEach(node => {
        tableRef.value?.toggleRowExpansion(node, true)
        if (node.children && node.children.length > 0) {
          expandNodes(node.children)
        }
      })
    }
    expandNodes(tableData.value)
  })
}

// 折叠全部
const collapseAll = () => {
  nextTick(() => {
    const collapseNodes = (data: MenuInfo[]) => {
      data.forEach(node => {
        tableRef.value?.toggleRowExpansion(node, false)
        if (node.children && node.children.length > 0) {
          collapseNodes(node.children)
        }
      })
    }
    collapseNodes(tableData.value)
  })
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  initFormData()
  formDialogVisible.value = true
  loadMenuTreeOptions()
}

// 新增子菜单
const handleAddChild = (row: MenuInfo) => {
  isEdit.value = false
  initFormData()
  formData.parent_id = row.menu_id
  formDialogVisible.value = true
  loadMenuTreeOptions()
}

// 编辑
const handleEdit = (row: MenuInfo) => {
  isEdit.value = true
  Object.assign(formData, {
    parent_id: row.parent_id,
    menu_name: row.menu_name,
    menu_type: row.menu_type,
    icon: row.icon || '',
    path: row.path || '',
    component: row.component || '',
    perms: row.perms || '',
    order_num: row.order_num || 0
  })
  currentMenu.value = row
  formDialogVisible.value = true
  loadMenuTreeOptions()
}

// 删除
const handleDelete = async (row: MenuInfo) => {
  // 检查是否有子菜单
  if (row.children && row.children.length > 0) {
    ElMessage.warning('该菜单包含子菜单，请先删除子菜单')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认删除菜单「${row.menu_name}」吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await MenuApi.deleteMenu(row.menu_id)
    if (response.success) {
      ElMessage.success('删除成功')
      loadMenuList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除菜单失败:', error)
      // 显示具体的错误信息，兼容 FastAPI 的 detail 字段
      const errorMessage = error?.response?.data?.detail || error?.response?.data?.message || error?.message || '删除菜单失败'
      ElMessage.error(errorMessage)
    }
  }
}

// 表单提交
const handleFormConfirm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    formLoading.value = true

    // 直接使用小写字段名数据
    const apiData = {
      parent_id: formData.parent_id,
      menu_name: formData.menu_name,
      menu_type: formData.menu_type,
      path: formData.path || undefined,
      component: formData.component || undefined,
      perms: formData.perms || undefined,
      icon: formData.icon || undefined,
      order_num: formData.order_num || undefined
    }

    if (isEdit.value && currentMenu.value) {
      const response = await MenuApi.updateMenu(currentMenu.value.menu_id, apiData)
      if (response.success) {
        ElMessage.success('更新成功')
        formDialogVisible.value = false
        loadMenuList()
      }
    } else {
      const response = await MenuApi.createMenu(apiData)
      if (response.success) {
        ElMessage.success('创建成功')
        formDialogVisible.value = false
        loadMenuList()
      }
    }
  } catch (error) {
    console.error('保存菜单失败:', error)
    ElMessage.error('保存菜单失败')
  } finally {
    formLoading.value = false
  }
}

// 表单取消
const handleFormCancel = () => {
  formDialogVisible.value = false
  formRef.value?.clearValidate()
}

// 菜单类型变化
const handleMenuTypeChange = (type: string) => {
  if (type === '1') {
    // 按钮类型
    formData.path = ''
    formData.component = ''
  } else if (type === '0') {
    // 菜单类型
    // 可以设置默认值
  }
}

// 初始化
onMounted(() => {
  loadMenuList()
})
</script>

<style scoped lang="scss">
.menu-management {
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
  
  .menu-name-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .menu-icon {
      font-size: 16px;
      color: #409eff;
    }
  }
}

:deep(.el-table) {
  .el-table__row {
    &.el-table__row--level-1 {
      background-color: #fafafa;
    }
    
    &.el-table__row--level-2 {
      background-color: #f5f5f5;
    }
  }
}

:deep(.el-tree-select) {
  width: 100%;
}

// 对话框样式
:deep(.el-dialog) {
  .el-dialog__body {
    padding: 20px;
  }
  
  .dialog-footer {
    text-align: right;
    padding-top: 10px;
  }
}
</style>

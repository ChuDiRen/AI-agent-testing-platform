<template>
  <div class="department-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>部门管理</h2>
      <p>管理组织架构，配置部门信息</p>
    </div>

    <!-- 搜索和操作区 -->
    <el-card class="search-card">
      <el-row :gutter="20" justify="space-between">
        <el-col :span="16">
          <el-form :model="searchForm" inline>
            <el-form-item label="部门名称">
              <el-input 
                v-model="searchForm.keyword" 
                placeholder="请输入部门名称" 
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="部门状态">
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
          <el-button type="primary" @click="handleAdd" v-permission="['dept:create']">
            <el-icon><Plus /></el-icon>
            新增部门
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

    <!-- 部门树表格 -->
    <el-card class="table-card">
      <el-table
        ref="tableRef"
        :data="tableData"
        :loading="loading"
        row-key="dept_id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        :default-expand-all="false"
        border
        stripe
      >
        <el-table-column prop="dept_name" label="部门名称" min-width="200">
          <template #default="{ row }">
            <div class="dept-name-cell">
              <el-icon class="dept-icon">
                <OfficeBuilding />
              </el-icon>
              <span>{{ row.dept_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="dept_code" label="部门编码" min-width="120" />
        
        <el-table-column prop="leader_name" label="部门负责人" min-width="120" />
        
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        
        <el-table-column prop="sort" label="排序" width="80" align="center" />
        
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" />
        
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              link
              @click="handleEdit(row)"
              v-permission="['dept:update']"
            >
              编辑
            </el-button>
            <el-button 
              type="primary" 
              size="small" 
              link
              @click="handleAddChild(row)"
              v-permission="['dept:create']"
            >
              新增子部门
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              link
              @click="handleDelete(row)"
              v-permission="['dept:delete']"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 部门表单对话框 -->
    <FormDialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑部门' : '新增部门'"
      :loading="formLoading"
      @confirm="handleFormConfirm"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="上级部门" prop="parent_id">
          <el-tree-select
            v-model="formData.parent_id"
            :data="deptTreeOptions"
            :props="deptTreeProps"
            placeholder="请选择上级部门"
            clearable
            check-strictly
            :render-after-expand="false"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门名称" prop="dept_name">
              <el-input 
                v-model="formData.dept_name" 
                placeholder="请输入部门名称"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门编码" prop="dept_code">
              <el-input 
                v-model="formData.dept_code" 
                placeholder="请输入部门编码"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门负责人" prop="leader_id">
              <el-select 
                v-model="formData.leader_id" 
                placeholder="请选择部门负责人"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option 
                  v-for="user in userOptions" 
                  :key="user.user_id" 
                  :label="user.username" 
                  :value="user.user_id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input 
                v-model="formData.phone" 
                placeholder="请输入联系电话"
                maxlength="20"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input 
                v-model="formData.email" 
                placeholder="请输入邮箱"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="sort">
              <el-input-number 
                v-model="formData.sort" 
                :min="0" 
                :max="999"
                placeholder="请输入排序"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch 
            v-model="formData.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
        
        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="formData.remark" 
            type="textarea"
            placeholder="请输入备注"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type ElTable } from 'element-plus'
import { Search, Refresh, Plus, DCaret, CaretRight, OfficeBuilding } from '@element-plus/icons-vue'
import FormDialog from '@/components/Common/FormDialog.vue'
import { DepartmentApi } from '@/api/modules/department'
import { UserApi } from '@/api/modules/user'
import type { DeptTreeNode, UserInfo } from '@/api/types'

// 表单引用
const formRef = ref<FormInstance>()
const tableRef = ref<InstanceType<typeof ElTable>>()

// 数据和状态
const loading = ref(false)
const formLoading = ref(false)
const tableData = ref<DeptTreeNode[]>([])
const deptTreeOptions = ref<DeptTreeNode[]>([])
// const selectedDepts = ref<DeptTreeNode[]>([]) // 暂时注释掉未使用的变量
const userOptions = ref<UserInfo[]>([])
const currentDept = ref<DeptTreeNode | null>(null)

// 对话框状态
const formDialogVisible = ref(false)
const isEdit = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  is_active: undefined as boolean | undefined
})

// 表单数据
const formData = reactive<Record<string, any>>({
  parent_id: null,
  dept_name: '',
  dept_code: '',
  leader_id: null,
  phone: '',
  email: '',
  sort: 0,
  is_active: true,
  remark: ''
})

// 表单验证规则
const formRules = {
  dept_name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '部门名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  dept_code: [
    { required: true, message: '请输入部门编码', trigger: 'blur' },
    { min: 2, max: 50, message: '部门编码长度在 2 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '部门编码只能包含字母、数字、下划线和中划线', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 部门树配置
const deptTreeProps = {
  children: 'children',
  label: 'dept_name',
  value: 'dept_id'
}

// 初始化表单数据
const initFormData = () => {
  Object.assign(formData, {
    parent_id: null,
    dept_name: '',
    dept_code: '',
    leader_id: null,
    phone: '',
    email: '',
    sort: 0,
    is_active: true,
    remark: ''
  })
}

// 加载部门列表
const loadDeptList = async () => {
  try {
    loading.value = true
    const response = await DepartmentApi.getDepartmentTree()
    if (response.success && response.data) {
      tableData.value = Array.isArray(response.data) ? response.data : []
    } else {
      tableData.value = []
    }
  } catch (error) {
    console.error('加载部门列表失败:', error)
    ElMessage.error('加载部门列表失败')
  } finally {
    loading.value = false
  }
}

// 加载部门树选项
const loadDeptTreeOptions = async () => {
  try {
    const response = await DepartmentApi.getDepartmentTree()
    if (response.success && response.data) {
      deptTreeOptions.value = Array.isArray(response.data) ? response.data : []
    } else {
      deptTreeOptions.value = []
    }
  } catch (error) {
    console.error('加载部门树选项失败:', error)
  }
}

// 加载用户选项
const loadUserOptions = async () => {
  try {
    const response = await UserApi.getAllUsers()
    if (response.success && response.data) {
      userOptions.value = Array.isArray(response.data) ? response.data : []
    } else {
      userOptions.value = []
    }
  } catch (error) {
    console.error('加载用户选项失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  loadDeptList()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.is_active = undefined
  loadDeptList()
}

// 展开全部
const expandAll = () => {
  nextTick(() => {
    const expandNodes = (data: any[]) => {
      (data || []).forEach((node: any) => {
        tableRef.value?.toggleRowExpansion?.(node, true)
        if (node?.children && node.children.length > 0) {
          expandNodes(node.children)
        }
      })
    }
    expandNodes(tableData.value || [])
  })
}

// 折叠全部
const collapseAll = () => {
  nextTick(() => {
    const collapseNodes = (data: any[]) => {
      (data || []).forEach((node: any) => {
        tableRef.value?.toggleRowExpansion?.(node, false)
        if (node?.children && node.children.length > 0) {
          collapseNodes(node.children)
        }
      })
    }
    collapseNodes(tableData.value || [])
  })
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  initFormData()
  formDialogVisible.value = true
  loadDeptTreeOptions()
  loadUserOptions()
}

// 新增子部门
const handleAddChild = (row: any) => {
  isEdit.value = false
  initFormData()
  formData.parent_id = row.dept_id
  formDialogVisible.value = true
  loadDeptTreeOptions()
  loadUserOptions()
}

// 编辑
const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(formData, {
    parent_id: row.parent_id,
    dept_name: row.dept_name,
    dept_code: row.dept_code,
    leader_id: row.leader_id,
    phone: row.phone || '',
    email: row.email || '',
    sort: row.sort,
    is_active: row.is_active,
    remark: row.remark || ''
  })
  currentDept.value = row
  formDialogVisible.value = true
  loadDeptTreeOptions()
  loadUserOptions()
}

// 删除
const handleDelete = async (row: any) => {
  // 检查是否有子部门
  if (row.children && row.children.length > 0) {
    ElMessage.warning('该部门包含子部门，请先删除子部门')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认删除部门「${row.dept_name}」吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await DepartmentApi.deleteDepartment(row.dept_id)
    if (response.success) {
      ElMessage.success('删除成功')
      loadDeptList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除部门失败:', error)
      ElMessage.error('删除部门失败')
    }
  }
}

// 表单提交
const handleFormConfirm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    formLoading.value = true
    
    if (isEdit.value && currentDept.value) {
      const updateData = { ...formData }
      const response = await DepartmentApi.updateDepartment(currentDept.value.dept_id, updateData)
      if (response.success) {
        ElMessage.success('更新成功')
        formDialogVisible.value = false
        loadDeptList()
      }
    } else {
      const response = await DepartmentApi.createDepartment(formData as any)
      if (response.success) {
        ElMessage.success('创建成功')
        formDialogVisible.value = false
        loadDeptList()
      }
    }
  } catch (error) {
    console.error('保存部门失败:', error)
    ElMessage.error('保存部门失败')
  } finally {
    formLoading.value = false
  }
}

// 初始化
onMounted(() => {
  loadDeptList()
})
</script>

<style scoped lang="scss">
.department-management {
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
  
  .dept-name-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .dept-icon {
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
</style>

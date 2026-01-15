<template>
  <div class="page-container">
    <BaseSearch 
      :model="searchForm" 
      @search="loadData" 
      @reset="resetSearch"
    >
      <el-form-item label="角色名称">
        <el-input v-model="searchForm.role_name" placeholder="根据角色名称筛选" clearable>
          <template #prefix>
            <el-icon><Key /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 150px;">
          <el-option label="正常" value="1" />
          <el-option label="停用" value="0" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="角色管理"
      :data="tableData"
      :loading="loading"
      :total="total"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
      @selection-change="handleSelectionChange"
    >
      <template #header>
        <el-button type="primary" v-permission="'system:role:add'" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
        <el-button type="danger" v-permission="'system:role:delete'" :disabled="!selectedIds.length" @click="onBatchDelete">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </template>

      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="角色ID" width="100" />
      <el-table-column prop="role_name" label="角色名称" width="150" show-overflow-tooltip>
        <template #default="scope">
          <div class="role-name-cell">
            <el-icon><User /></el-icon>
            <span>{{ scope.row.role_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="role_key" label="角色标识" width="120" show-overflow-tooltip>
        <template #default="scope">
          <el-tag type="info" size="small">{{ scope.row.role_key }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="role_sort" label="排序" width="80" align="center" />
      <el-table-column prop="data_scope" label="数据权限" width="150">
        <template #default="scope">
          <el-tag :type="getDataScopeType(scope.row.data_scope)">
            {{ getDataScopeText(scope.row.data_scope) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === '1' ? 'success' : 'info'">
            {{ scope.row.status === '1' ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="角色描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="440" align="center">
        <template #default="scope">
          <el-button link type="primary" size="small" v-permission="'system:role:view'" @click.prevent="onDataView(scope.$index)">
            <el-icon><View /></el-icon>
            查看
          </el-button>
          <el-button link type="success" size="small" v-permission="'system:role:edit'" @click.prevent="onDataForm(scope.$index)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button link type="warning" size="small" v-permission="'system:role:assign'" @click.prevent="onAssignMenus(scope.$index)">
            <el-icon><Setting /></el-icon>
            分配权限
          </el-button>
          <el-button link type="primary" size="small" v-permission="'system:role:copy'" @click.prevent="onCopyRole(scope.$index)">
            <el-icon><CopyDocument /></el-icon>
            复制角色
          </el-button>
          <el-button link type="info" size="small" v-permission="'system:role:users'" @click.prevent="onViewUsers(scope.$index)">
            <el-icon><User /></el-icon>
            查看用户
          </el-button>
          <el-button link type="danger" size="small" v-permission="'system:role:delete'" @click.prevent="onDelete(scope.$index)" :disabled="scope.row.role_key === 'admin'">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 权限分配对话框 -->
    <el-dialog v-model="menuDialogVisible" title="分配菜单权限" width="500px" :close-on-click-modal="false">
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 16px;"
      >
        选择菜单后，拥有该角色的用户将自动获得对应的菜单权限。
      </el-alert>
      <el-tree
        ref="menuTreeRef"
        :data="menuTree"
        show-checkbox
        node-key="id"
        :props="{ children: 'children', label: 'menu_name' }"
        default-expand-all
        :height="300"
      />
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveMenus" :loading="submittingMenus">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看角色用户对话框 -->
    <el-dialog v-model="userDialogVisible" title="角色下的用户列表" width="800px">
      <el-table :data="roleUsers" v-loading="userLoading" border>
        <el-table-column prop="id" label="用户ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120">
          <template #default="scope">
            <div class="user-info">
              <el-avatar :size="24" :src="scope.row.avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span>{{ scope.row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="mobile" label="手机号" width="120" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === '1' ? 'success' : 'info'">
              {{ scope.row.status === '1' ? '正常' : '锁定' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 复制角色对话框 -->
    <el-dialog v-model="copyDialogVisible" title="复制角色" width="500px" :close-on-click-modal="false">
      <el-form :model="copyForm" label-width="100px" :rules="copyRules" ref="copyFormRef">
        <el-form-item label="新角色名称" prop="role_name">
          <el-input v-model="copyForm.role_name" placeholder="请输入角色名称" clearable />
        </el-form-item>
        <el-form-item label="角色标识" prop="role_key">
          <el-input v-model="copyForm.role_key" placeholder="请输入角色标识（英文）" clearable />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="copyForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="copyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCopyRole" :loading="submittingCopy">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, watch } from "vue"
import { queryByPage, deleteData, assignMenus, getRoleMenus, copyRole, batchDelete } from './role'
import { queryByPage as getUserList } from '~/views/system/users/user'
import { getMenuTree } from '~/views/system/menu/menu'
import { formatDateTime } from '~/utils/timeFormatter'
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// ========== 变量定义 ==========

// 分页参数
const pagination = reactive({
  page: 1,
  limit: 10
})
const total = ref(0)
const loading = ref(false)

// 搜索功能 - 筛选表单
const searchForm = reactive({
  role_name: null,
  status: null
})

// 表格数据
const tableData = ref([])

// 权限分配相关
const menuDialogVisible = ref(false)
const menuTreeRef = ref(null)
const menuTree = ref([])
const currentRoleId = ref(null)
const selectedMenuIds = ref([])
const submittingMenus = ref(false)

// 查看用户相关
const userDialogVisible = ref(false)
const roleUsers = ref([])
const userLoading = ref(false)

// 批量选择
const selectedIds = ref([])
const handleSelectionChange = (selection) => {
    selectedIds.value = selection.map(item => item.id)
}

// 角色复制对话框
const copyDialogVisible = ref(false)
const copyFormRef = ref(null)
const copyForm = reactive({
    sourceRoleId: null,
    role_name: '',
    role_key: '',
    remark: ''
})
const submittingCopy = ref(false)

// 复制角色表单验证规则
const copyRules = {
    role_name: [
        { required: true, message: '请输入角色名称', trigger: 'blur' },
        { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    role_key: [
        { required: true, message: '请输入角色标识', trigger: 'blur' },
        { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '角色标识只能包含字母、数字和下划线，且必须以字母或下划线开头', trigger: 'blur' }
    ]
}

// ========== 函数定义 ==========

// 数据权限映射
const getDataScopeText = (scope) => {
    const map = {
        '1': '全部数据',
        '2': '自定义',
        '3': '本部门',
        '4': '本部门及下级',
        '5': '仅本人'
    }
    return map[scope] || '未知'
}

const getDataScopeType = (scope) => {
    const typeMap = {
        '1': 'danger',
        '2': 'warning',
        '3': 'primary',
        '4': 'success',
        '5': 'info'
    }
    return typeMap[scope] || 'info'
}

// 加载页面数据
const loadData = () => {
    loading.value = true
    let searchData = { ...searchForm }
    searchData["page"] = pagination.page
    searchData["pageSize"] = pagination.limit

    queryByPage(searchData).then((res) => {
        if (res.data.code === 200) {
            tableData.value = res.data.data || []
            total.value = res.data.total || 0
        } else {
            ElMessage.error(res.data.msg || '查询失败')
        }
    }).catch((error) => {
        console.error('查询失败:', error)
        ElMessage.error('查询失败，请稍后重试')
    }).finally(() => {
        loading.value = false
    })
}

// 重置搜索
const resetSearch = () => {
    searchForm.role_name = null
    searchForm.status = null
    pagination.page = 1
    loadData()
}

// 查看角色详情
const onDataView = (index) => {
    const item = tableData.value[index]
    router.push({
        path: '/roleForm',
        query: {
            id: item.id,
            view: 'true'
        }
    })
}

// 打开表单 （编辑/新增）
const onDataForm = (index) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path: '/roleForm',
        query: params_data
    })
}

// 删除数据
const onDelete = (index) => {
    const item = tableData.value[index]
    if (item.role_key === 'admin') {
        ElMessage.warning('超级管理员角色不允许删除')
        return
    }
    
    ElMessageBox.confirm(
        `确定要删除角色"${item.role_name}"吗？`,
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        deleteData(item.id).then((res) => {
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            } else {
                ElMessage.error(res.data.msg || '删除失败')
            }
        }).catch(() => {
            ElMessage.info('已取消删除')
        })
    })
}

// 权限分配相关
// 打开权限分配对话框
const onAssignMenus = async (index) => {
    const role = tableData.value[index]
    if (role.role_key === 'admin') {
        ElMessage.warning('超级管理员角色拥有所有权限，无需分配')
        return
    }
    
    currentRoleId.value = role.id
    
    try {
        // 加载菜单树
        const menuRes = await getMenuTree()
        if (menuRes.data.code === 200) {
            menuTree.value = menuRes.data.data
        }
        
        // 加载角色已有权限
        const roleMenuRes = await getRoleMenus(currentRoleId.value)
        if (roleMenuRes.data.code === 200) {
            selectedMenuIds.value = roleMenuRes.data.data || []
        }
        
        menuDialogVisible.value = true
    } catch (error) {
        ElMessage.error('加载菜单数据失败')
    }
}

// 监听对话框显示状态
watch(menuDialogVisible, async (visible) => {
    if (visible && selectedMenuIds.value.length > 0) {
        await nextTick()
        setTimeout(() => {
            menuTreeRef.value?.setCheckedKeys(selectedMenuIds.value)
        }, 100)
    }
})

// 保存菜单权限
const handleSaveMenus = async () => {
    const checkedKeys = menuTreeRef.value.getCheckedKeys()
    const halfCheckedKeys = menuTreeRef.value.getHalfCheckedKeys()
    const menuIds = [...checkedKeys, ...halfCheckedKeys].filter((id) => id !== null && id !== undefined)
    
    if (menuIds.length === 0) {
        ElMessage.warning('请至少选择一个菜单权限')
        return
    }
    
    submittingMenus.value = true
    try {
        const res = await assignMenus({
            id: currentRoleId.value,
            menu_ids: menuIds
        })
        
        if (res.data.code === 200) {
            menuDialogVisible.value = false
            ElMessage.success('权限分配成功')
            loadData()
        } else {
            ElMessage.error(res.data.msg || '权限分配失败')
        }
    } catch (error) {
        console.error('分配权限失败:', error)
        ElMessage.error('分配权限失败，请稍后重试')
    } finally {
        submittingMenus.value = false
    }
}

// 查看角色下的用户
const onViewUsers = async (index) => {
    const role = tableData.value[index]
    userLoading.value = true
    userDialogVisible.value = true
    
    try {
        const res = await getUserList({ page: 1, pageSize: 1000 })
        if (res.data.code === 200) {
            const allUsers = res.data.data || []
            roleUsers.value = allUsers.filter(user => 
                user.roles && user.roles.includes(role.role_name)
            )
        }
    } catch (error) {
        ElMessage.error('加载用户列表失败')
    } finally {
        userLoading.value = false
    }
}

// 复制角色
const onCopyRole = (index) => {
    const role = tableData.value[index]
    copyForm.sourceRoleId = role.id
    copyForm.role_name = `${role.role_name}_副本`
    copyForm.role_key = `${role.role_key}_copy`
    copyForm.remark = `从${role.role_name}复制`
    copyDialogVisible.value = true
}

// 提交角色复制
const submitCopyRole = async () => {
    if (!copyFormRef.value) return
    
    await copyFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        submittingCopy.value = true
        try {
            const res = await copyRole({
                source_role_id: copyForm.sourceRoleId,
                role_name: copyForm.role_name,
                role_key: copyForm.role_key,
                remark: copyForm.remark
            })
            if (res.data.code === 200) {
                ElMessage.success('角色复制成功')
                copyDialogVisible.value = false
                loadData()
            } else {
                ElMessage.error(res.data.msg || '角色复制失败')
            }
        } catch (error) {
            ElMessage.error('角色复制失败，请稍后重试')
        } finally {
            submittingCopy.value = false
        }
    })
}

// 批量删除角色
const onBatchDelete = async () => {
    ElMessageBox.confirm(
        `确定要删除选中的 ${selectedIds.value.length} 个角色吗？此操作不可恢复！`,
        '批量删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'error',
        }
    ).then(async () => {
        try {
            const res = await batchDelete({
                role_ids: selectedIds.value
            })
            if (res.data.code === 200) {
                ElMessage.success(res.data.msg || '批量删除成功')
                selectedIds.value = []
                loadData()
            } else {
                ElMessage.error(res.data.msg || '批量删除失败')
            }
        } catch (error) {
            ElMessage.error('批量删除失败，请稍后重试')
        }
    }).catch(() => {
        ElMessage.info('已取消操作')
    })
}

// 初始化加载数据
loadData()
</script>

<style scoped>
.role-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 树组件样式优化 */
:deep(.el-tree) {
  background: transparent;
}

:deep(.el-tree-node__content) {
  height: 36px;
}

:deep(.el-checkbox__inner) {
  border-radius: 4px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  :deep(.el-table-column--selection .cell) {
    padding-left: 8px;
  }
  
  :deep(.el-table .cell) {
    padding-left: 8px;
    padding-right: 8px;
  }
}

/* 操作按钮优化 */
:deep(.el-button--small.is-link) {
  padding: 0 4px;
}
</style>

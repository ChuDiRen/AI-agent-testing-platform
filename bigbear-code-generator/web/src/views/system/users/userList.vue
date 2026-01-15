<template>
  <div class="page-container">
    <BaseSearch 
      :model="searchForm" 
      @search="loadData" 
      @reset="resetSearch"
    >
      <el-form-item label="用户名">
        <el-input v-model="searchForm.username" placeholder="根据用户名筛选" clearable>
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 150px;">
          <el-option label="有效" value="1" />
          <el-option label="锁定" value="0" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="用户管理"
      :data="tableData"
      :loading="loading"
      :total="total"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
      @selection-change="handleSelectionChange"
    >
      <template #header>
        <el-button type="primary" v-permission="'system:user:add'" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
        <el-button type="success" v-permission="'system:user:enable'" :disabled="!selectedIds.length" @click="onBatchEnable">
          <el-icon><Check /></el-icon>
          批量启用
        </el-button>
        <el-button type="warning" v-permission="'system:user:lock'" :disabled="!selectedIds.length" @click="onBatchLock">
          <el-icon><Lock /></el-icon>
          批量锁定
        </el-button>
        <el-button type="danger" v-permission="'system:user:delete'" :disabled="!selectedIds.length" @click="onBatchDelete">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </template>

      <!-- 数据列 -->
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="用户ID" width="100" />
      <el-table-column prop="username" label="用户名" width="120" show-overflow-tooltip>
        <template #default="scope">
          <div class="user-info">
            <el-avatar :size="32" :src="scope.row.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="username">{{ scope.row.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip />
      <el-table-column prop="mobile" label="联系电话" width="130" />
      <el-table-column prop="roles" label="角色" width="180">
        <template #default="scope">
          <el-tag v-for="role in scope.row.roles" :key="role" size="small" type="primary" style="margin-right: 4px;">
            {{ role }}
          </el-tag>
          <el-tag v-if="!scope.row.roles || scope.row.roles.length === 0" size="small" type="info">
            无角色
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="dept_id" label="部门" width="150">
        <template #default="scope">
          <el-tag type="success" size="small">
            {{ deptMap[scope.row.dept_id] || scope.row.dept_id }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            active-value="1"
            inactive-value="0"
            @change="onStatusChange(scope.row)"
            :disabled="scope.row.username === 'admin'"
          />
        </template>
      </el-table-column>
      <el-table-column prop="ssex" label="性别" width="80" align="center">
        <template #default="scope">
          <el-tag :type="getGenderType(scope.row.ssex)" size="small">
            {{ genderMap[scope.row.ssex] || '未知' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="320" align="center">
        <template #default="scope">
          <el-button link type="primary" size="small" v-permission="'system:user:view'" @click.prevent="onDataView(scope.$index)">
            <el-icon><View /></el-icon>
            查看
          </el-button>
          <el-button link type="success" size="small" v-permission="'system:user:edit'" @click.prevent="onDataForm(scope.$index)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button link type="warning" size="small" v-permission="'system:user:assign'" @click.prevent="onAssignRoles(scope.$index)">
            <el-icon><Setting /></el-icon>
            分配角色
          </el-button>
          <el-button link type="danger" size="small" v-permission="'system:user:delete'" @click.prevent="onDelete(scope.$index)" :disabled="scope.row.username === 'admin'">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 分配角色对话框 -->
    <el-dialog 
      v-model="roleDialogVisible" 
      title="分配角色" 
      width="500px"
      @close="resetRoleDialog"
      :close-on-click-modal="false"
    >
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 16px;"
      >
        为用户分配角色后，用户将拥有对应角色的所有权限。
      </el-alert>
      <el-form :model="roleForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="roleForm.username" disabled>
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="选择角色">
          <el-select 
            v-model="roleForm.roleIds" 
            multiple 
            placeholder="请选择角色"
            style="width: 100%"
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option
              v-for="role in allRoles"
              :key="role.id"
              :label="role.role_name"
              :value="role.id"
            >
              <span>{{ role.role_name }}</span>
              <span style="float: right; color: var(--text-tertiary); font-size: 12px;">
                {{ role.role_key }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRoleAssignment" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { queryByPage, deleteData, assignRoles, getUserRoles, updateStatus, batchUpdateStatus, batchDelete } from './user'
import { getDeptTree } from '~/views/system/dept/dept'
import { queryByPage as getRoleList } from '~/views/system/role/role'
import { useRouter } from "vue-router"
import { formatDateTime } from '~/utils/timeFormatter'
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 分页参数
const pagination = reactive({
  page: 1,
  limit: 10
})
const total = ref(0)
const loading = ref(false)

// 搜索功能 - 筛选表单
const searchForm = reactive({
  username: null,
  status: null
})

// 数据字典映射
const genderMap = {
    '0': '男',
    '1': '女',
    '2': '保密'
}

// 性别标签类型
const getGenderType = (gender) => {
    const typeMap = {
        '0': 'primary',
        '1': 'danger',
        '2': 'info'
    }
    return typeMap[gender] || 'info'
}

// 部门映射（从后端加载）
const deptMap = ref({})

// 加载部门数据
const loadDeptData = async () => {
    try {
        const res = await getDeptTree()
        if (res.data.code === 200) {
            const depts = res.data.data
            const flattenDepts = (deptList, map = {}) => {
                if (!deptList || !Array.isArray(deptList)) {
                    return map
                }
                deptList.forEach(dept => {
                    if (dept.id !== undefined && dept.id !== null) {
                        map[dept.id] = dept.dept_name
                    }
                    if (dept.children && dept.children.length > 0) {
                        flattenDepts(dept.children, map)
                    }
                })
                return map
            }
            deptMap.value = flattenDepts(depts)
        }
    } catch (error) {
        ElMessage.error('加载部门数据失败，请稍后重试')
    }
}

// 表格数据
const tableData = ref([])

// 批量选择
const selectedIds = ref([])
const handleSelectionChange = (selection) => {
    selectedIds.value = selection.map(item => item.id)
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
    }).catch(() => {
        ElMessage.error('查询失败，请稍后重试')
    }).finally(() => {
        loading.value = false
    })
}

// 重置搜索
const resetSearch = () => {
    searchForm.username = null
    searchForm.status = null
    pagination.page = 1
    loadData()
}

// 页面初始化
onMounted(() => {
    loadDeptData()
    loadRoleData()
    loadData()
})

// 加载角色数据
const allRoles = ref([])
const loadRoleData = async () => {
    try {
        const res = await getRoleList({ page: 1, pageSize: 100 })
        if (res.data.code === 200) {
            allRoles.value = res.data.data || []
        }
    } catch (error) {
        ElMessage.error('加载角色数据失败')
    }
}

// 角色分配对话框
const roleDialogVisible = ref(false)
const roleForm = reactive({
    userId: null,
    username: '',
    roleIds: []
})
const submitting = ref(false)

// 打开分配角色对话框
const onAssignRoles = async (index) => {
    const user = tableData.value[index]
    if (user.username === 'admin') {
        ElMessage.warning('超级管理员不允许修改角色')
        return
    }
    
    roleForm.userId = user.id
    roleForm.username = user.username
    
    try {
        const res = await getUserRoles(user.id)
        if (res.data.code === 200) {
            roleForm.roleIds = res.data.data || []
        }
    } catch (error) {
        ElMessage.error('获取用户角色失败')
    }
    
    roleDialogVisible.value = true
}

// 提交角色分配
const submitRoleAssignment = async () => {
    if (roleForm.roleIds.length === 0) {
        ElMessage.warning('请至少选择一个角色')
        return
    }
    
    submitting.value = true
    try {
        const res = await assignRoles({
            user_id: roleForm.userId,
            role_ids: roleForm.roleIds
        })
        if (res.data.code === 200) {
            ElMessage.success('角色分配成功')
            roleDialogVisible.value = false
            loadData()
        } else {
            ElMessage.error(res.data.msg || '角色分配失败')
        }
    } catch (error) {
        const errorMsg = error.response?.data?.msg || error.message || '角色分配失败，请稍后重试'
        ElMessage.error(errorMsg)
    } finally {
        submitting.value = false
    }
}

// 重置角色对话框
const resetRoleDialog = () => {
    roleForm.userId = null
    roleForm.username = ''
    roleForm.roleIds = []
    submitting.value = false
}

// 用户状态切换
const onStatusChange = async (row) => {
    if (row.username === 'admin') {
        ElMessage.warning('超级管理员不允许修改状态')
        row.status = '1'
        return
    }
    
    try {
        const res = await updateStatus({
            user_id: row.id,
            status: row.status
        })
        if (res.data.code === 200) {
            ElMessage.success(`已${row.status === '1' ? '启用' : '锁定'}用户`)
            loadData()
        } else {
            ElMessage.error(res.data.msg || '状态更新失败')
            row.status = row.status === '1' ? '0' : '1'
        }
    } catch (error) {
        ElMessage.error('状态更新失败，请稍后重试')
        row.status = row.status === '1' ? '0' : '1'
    }
}

// 查看用户详情
const onDataView = (index) => {
    const item = tableData.value[index]
    router.push({
        path: 'userForm',
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
        path: 'userForm',
        query: params_data
    });
}

// 删除数据
const onDelete = (index) => {
    const item = tableData.value[index]
    if (item.username === 'admin') {
        ElMessage.warning('超级管理员不允许删除')
        return
    }
    
    ElMessageBox.confirm(
        `确定要删除用户"${item.username}"吗？`,
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
            ElMessage.error('删除失败，请稍后重试')
        })
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}

// 批量启用用户
const onBatchEnable = async () => {
    ElMessageBox.confirm(
        `确定要启用选中的 ${selectedIds.value.length} 个用户吗？`,
        '批量启用确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'info',
        }
    ).then(async () => {
        try {
            const res = await batchUpdateStatus({
                user_ids: selectedIds.value,
                status: '1'
            })
            if (res.data.code === 200) {
                ElMessage.success(res.data.msg || '批量启用成功')
                selectedIds.value = []
                loadData()
            } else {
                ElMessage.error(res.data.msg || '批量启用失败')
            }
        } catch (error) {
            ElMessage.error('批量启用失败，请稍后重试')
        }
    }).catch(() => {
        ElMessage.info('已取消操作')
    })
}

// 批量锁定用户
const onBatchLock = async () => {
    ElMessageBox.confirm(
        `确定要锁定选中的 ${selectedIds.value.length} 个用户吗？`,
        '批量锁定确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(async () => {
        try {
            const res = await batchUpdateStatus({
                user_ids: selectedIds.value,
                status: '0'
            })
            if (res.data.code === 200) {
                ElMessage.success(res.data.msg || '批量锁定成功')
                selectedIds.value = []
                loadData()
            } else {
                ElMessage.error(res.data.msg || '批量锁定失败')
            }
        } catch (error) {
            ElMessage.error('批量锁定失败，请稍后重试')
        }
    }).catch(() => {
        ElMessage.info('已取消操作')
    })
}

// 批量删除用户
const onBatchDelete = async () => {
    ElMessageBox.confirm(
        `确定要删除选中的 ${selectedIds.value.length} 个用户吗？此操作不可恢复！`,
        '批量删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'error',
        }
    ).then(async () => {
        try {
            const res = await batchDelete({
                user_ids: selectedIds.value
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
</script>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-weight: 500;
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